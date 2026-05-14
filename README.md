# 💱 App Cotação

Um aplicativo web simples para consultar cotações de moedas (USD, BRL, EUR, JPY) em tempo real usando Flask e a API ExchangeRate-API.

## 🚀 Tecnologias

- **Python + Flask** - Backend e servidor web
- **HTML/CSS/JS** - Interface responsiva
- **ExchangeRate-API** - Dados das cotações

## 📋 Pré-requisitos

- Python 3.7+
- Pip (gerenciador de pacotes Python)
- Chave API gratuita da [ExchangeRate-API](https://app.exchangerate-api.com/sign-up)

## 🔧 Instalação e execução

```bash
# 1. Clone o repositório
git clone https://github.com/danielambrosim/App_Cotacao.git
cd App_Cotacao
```

## 2. Crie um ambiente virtual
```bash
python -m venv venv
```

## Ative o ambiente:
## Windows:
```bash
venv\Scripts\activate
```
## Linux/Mac:
```bash
source venv/bin/activate
```

## 3. Instale as dependências
```bash
pip install -r requirements.txt
```

# 4. Crie o arquivo .env com sua chave API
```bash
echo "API_KEY=sua_chave_api_aqui" > .env
```

# 5. Execute o app
```bash
python app.py
```
