import os
import requests
from flask import Flask, render_template
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria uma instância do aplicativo Flask
app = Flask(__name__)

# Função para obter as cotações usando a chave de API do `.env`
def get_exchange_rates():
    # Obtém a chave de API do arquivo .env
    api_key = os.getenv("API_KEY")

    # URL base da API com a chave de API obtida do arquivo .env
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"

    try:
        # Fazendo a requisição HTTP
        response = requests.get(url)
        response.raise_for_status()  # Lança um erro se o status não for 200
        data = response.json()  # Parsing do JSON

        # Verifica se o resultado da API foi bem-sucedido
        if data['result'] == 'success':
            # Extraindo as taxas de câmbio para BRL, EUR e JPY
            rates = data['conversion_rates']
            return {
                "USD": rates.get("USD", "Taxa não encontrada"),
                "BRL": rates.get("BRL", "Taxa não encontrada"),
                "EUR": rates.get("EUR", "Taxa não encontrada"),
                "JPY": rates.get("JPY", "Taxa não encontrada")
            }
        else:
            print("Erro ao obter os dados da API:", data.get('error-type', 'Erro desconhecido'))
            return {}

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API: {e}")
        return {}

# Rota principal que renderiza o arquivo `index.html` e passa as cotações para ele
@app.route("/")
def index():
    # Obter as cotações
    quotations = get_exchange_rates()
    return render_template("index.html", quotations=quotations)

if __name__ == "__main__":
    app.run(debug=True)
