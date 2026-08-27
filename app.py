import logging
import os
import re

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

logger = logging.getLogger(__name__)

CURRENCIES = ("USD", "BRL", "EUR", "JPY")

API_URL = "https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"

SUBSCRIPTIONS_TABLE = "emails"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_exchange_rates():
    """Retorna as taxas de câmbio para as moedas configuradas."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        return {}

    try:
        response = requests.get(API_URL.format(api_key=api_key), timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return {}

    if data.get("result") != "success":
        return {}

    rates = data.get("conversion_rates", {})
    return {currency: rates.get(currency) for currency in CURRENCIES}


@app.route("/")
def index():
    quotations = get_exchange_rates()
    if not quotations or any(value is None for value in quotations.values()):
        error = "Não foi possível carregar as cotações no momento. Tente novamente mais tarde."
        return render_template("index.html", quotations=None, error=error)

    return render_template("index.html", quotations=quotations, error=None)


def is_valid_email(email):
    """Valida o formato básico de um endereço de e-mail."""
    return bool(EMAIL_RE.match(email or ""))


def _supabase_headers():
    headers = {
        "apikey": os.getenv("SUPABASE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
        "Content-Type": "application/json",
    }
    return headers


def _supabase_configured():
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))


def email_exists(email):
    """Verifica se o e-mail já está cadastrado no Supabase."""
    if not _supabase_configured():
        return False

    url = f"{os.getenv('SUPABASE_URL')}/rest/v1/{SUBSCRIPTIONS_TABLE}"
    params = {"select": "id", "email": f"eq.{email}"}
    try:
        response = requests.get(url, params=params, headers=_supabase_headers(), timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    return bool(response.json())


def subscribe_email(email):
    """Cadastra um e-mail para receber atualizações do sistema.

    Retorna um dicionário com chave "ok" e, se falhar, uma razão em "error".
    """
    email = (email or "").strip().lower()

    if not is_valid_email(email):
        return {"ok": False, "error": "invalid_email"}

    if not _supabase_configured():
        logger.warning("Supabase não configurado; e-mail não persistido: %s", email)
        return {"ok": True, "queued": True}

    existing = email_exists(email)
    if existing is None:
        return {"ok": False, "error": "unavailable"}
    if existing:
        return {"ok": True, "already_subscribed": True}

    url = f"{os.getenv('SUPABASE_URL')}/rest/v1/{SUBSCRIPTIONS_TABLE}"
    try:
        response = requests.post(url, json={"email": email}, headers=_supabase_headers(), timeout=10)
    except requests.exceptions.RequestException:
        return {"ok": False, "error": "unavailable"}

    if response.status_code in (200, 201):
        return {"ok": True}
    return {"ok": False, "error": "unavailable"}


@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    result = subscribe_email(email)

    if not result.get("ok"):
        status = 400 if result.get("error") == "invalid_email" else 503
        return jsonify(result), status
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)
