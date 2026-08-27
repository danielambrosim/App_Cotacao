import os
from unittest.mock import patch

import requests

import app

API_KEY_VALUE = "test-key"
VALID_RATES = {
    "USD": 1.0,
    "BRL": 5.4,
    "EUR": 0.92,
    "JPY": 157.3,
}


def setup_function():
    os.environ["API_KEY"] = API_KEY_VALUE


def build_payload(result="success", rates=None):
    return {
        "result": result,
        "conversion_rates": rates or VALID_RATES,
    }


def test_get_exchange_rates_success():
    with patch("app.requests.get") as mock_get:
        mock_get.return_value.json.return_value = build_payload()
        result = app.get_exchange_rates()

    assert result == {
        "USD": 1.0,
        "BRL": 5.4,
        "EUR": 0.92,
        "JPY": 157.3,
    }


def test_get_exchange_rates_missing_currency_returns_none():
    rates = dict(VALID_RATES)
    rates.pop("JPY")

    with patch("app.requests.get") as mock_get:
        mock_get.return_value.json.return_value = build_payload(rates=rates)
        result = app.get_exchange_rates()

    assert result["JPY"] is None


def test_get_exchange_rates_api_failure_returns_empty():
    with patch("app.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError("HTTP 500")
        result = app.get_exchange_rates()

    assert result == {}


def test_get_exchange_rates_result_not_success_returns_empty():
    with patch("app.requests.get") as mock_get:
        mock_get.return_value.json.return_value = build_payload(result="error")
        result = app.get_exchange_rates()

    assert result == {}


def test_get_exchange_rates_missing_api_key_returns_empty():
    os.environ["API_KEY"] = ""

    with patch("app.requests.get") as mock_get:
        result = app.get_exchange_rates()

    mock_get.assert_not_called()
    assert result == {}


def test_get_exchange_rates_request_exception_returns_empty():
    with patch("app.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("connection error")
        result = app.get_exchange_rates()

    assert result == {}


# --- Validação de e-mail ---

def test_is_valid_email_accepts_valid():
    assert app.is_valid_email("user@example.com") is True


def test_is_valid_email_accepts_valid_with_uppercase():
    assert app.is_valid_email("User.Name+tag@Example.com") is True


def test_is_valid_email_rejects_missing_at():
    assert app.is_valid_email("userexample.com") is False


def test_is_valid_email_rejects_missing_domain():
    assert app.is_valid_email("user@example") is False


def test_is_valid_email_rejects_empty_and_none():
    assert app.is_valid_email("") is False
    assert app.is_valid_email(None) is False


# --- Cadastro de e-mail (subscribe_email) ---

def setup_supabase_env():
    os.environ["SUPABASE_URL"] = "https://proj.supabase.co"
    os.environ["SUPABASE_KEY"] = "anon-key"


def teardown_supabase_env():
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_KEY", None)


def test_subscribe_email_invalid_email():
    assert app.subscribe_email("not-an-email") == {"ok": False, "error": "invalid_email"}


def test_subscribe_email_unconfigured_queues():
    teardown_supabase_env()
    result = app.subscribe_email("  User@Example.com  ")
    assert result == {"ok": True, "queued": True}


def test_subscribe_email_new_user_persists():
    setup_supabase_env()
    with patch("app.requests.get") as mock_get, patch("app.requests.post") as mock_post:
        mock_get.return_value.json.return_value = []
        mock_post.return_value.status_code = 201
        result = app.subscribe_email("user@example.com")

    assert result == {"ok": True}
    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["json"] == {"email": "user@example.com"}
    teardown_supabase_env()


def test_subscribe_email_normalizes_and_lowercases():
    setup_supabase_env()
    with patch("app.requests.get") as mock_get, patch("app.requests.post") as mock_post:
        mock_get.return_value.json.return_value = []
        mock_post.return_value.status_code = 201
        app.subscribe_email("  USER@Example.com  ")

    assert mock_post.call_args.kwargs["json"] == {"email": "user@example.com"}
    teardown_supabase_env()


def test_subscribe_email_duplicate_not_reinserted():
    setup_supabase_env()
    with patch("app.requests.get") as mock_get, patch("app.requests.post") as mock_post:
        mock_get.return_value.json.return_value = [{"id": 1}]
        result = app.subscribe_email("user@example.com")

    assert result == {"ok": True, "already_subscribed": True}
    mock_post.assert_not_called()
    teardown_supabase_env()


def test_subscribe_email_supabase_unavailable():
    setup_supabase_env()
    with patch("app.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("network down")
        result = app.subscribe_email("user@example.com")

    assert result == {"ok": False, "error": "unavailable"}
    teardown_supabase_env()


def test_subscribe_email_insert_failure():
    setup_supabase_env()
    with patch("app.requests.get") as mock_get, patch("app.requests.post") as mock_post:
        mock_get.return_value.json.return_value = []
        mock_post.return_value.status_code = 500
        result = app.subscribe_email("user@example.com")

    assert result == {"ok": False, "error": "unavailable"}
    teardown_supabase_env()


# --- Rota /api/subscribe ---

def test_subscribe_route_success():
    os.environ["SUPABASE_URL"] = "https://proj.supabase.co"
    os.environ["SUPABASE_KEY"] = "anon-key"
    try:
        with patch("app.requests.get") as mock_get, patch("app.requests.post") as mock_post:
            mock_get.return_value.json.return_value = []
            mock_post.return_value.status_code = 201
            client = app.app.test_client()
            response = client.post("/api/subscribe", json={"email": "user@example.com"})
            assert response.status_code == 200
            assert response.get_json() == {"ok": True}
    finally:
        teardown_supabase_env()


def test_subscribe_route_invalid_email_returns_400():
    teardown_supabase_env()
    client = app.app.test_client()
    response = client.post("/api/subscribe", json={"email": "invalid"})
    assert response.status_code == 400
    assert response.get_json() == {"ok": False, "error": "invalid_email"}


def test_subscribe_route_unconfigured_queues():
    teardown_supabase_env()
    client = app.app.test_client()
    response = client.post("/api/subscribe", json={"email": "user@example.com"})
    assert response.status_code == 200
    assert response.get_json() == {"ok": True, "queued": True}
