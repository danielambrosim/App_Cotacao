# AGENTS.md — App_Cotacao

Aplicativo Flask de consulta de cotações de moedas usando a ExchangeRate-API.

## Stack

- **Backend**: Python 3 + Flask
- **Frontend**: HTML/CSS (Jinja2) + JS vanilla
- **API**: ExchangeRate-API (chave em `.env` como `API_KEY`)
- **Testes**: pytest (ver `requirements-dev.txt`)

## Comandos

- Instalar dependências: `pip install -r requirements.txt`
- Instalar dependências de dev: `pip install -r requirements-dev.txt`
- Rodar o app: `python app.py`
- Rodar testes: `python -m pytest -v`

## Convenções

- Manter lógica de API isolada de rotas (ver `get_exchange_rates` em `app.py`).
- Não commitar `.env` nem chaves de API (ver `.gitignore`).
- Comentários explicam o *porquê*, não o *o quê*.
- Frontend: acessível (aria, contraste, navegação por teclado), responsivo e com estados de loading/erro.

## Skills globais disponíveis

Este projeto aproveita os skills globais do OpenCode em `~/.config/opencode/skills/`:
`clean-code`, `code-by-parts`, `qa-tester`, `frontend-pro` e `slides-prompt`.
