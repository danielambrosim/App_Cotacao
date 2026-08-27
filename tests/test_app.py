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
