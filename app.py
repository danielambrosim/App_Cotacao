import os

import requests
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

app = Flask(__name__)

CURRENCIES = ("USD", "BRL", "EUR", "JPY")

API_URL = "https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"


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


if __name__ == "__main__":
    app.run(debug=True)
