# Budget Webapp

Aplicacao Django baseada no ficheiro `April_monthly_budget.xlsx`, pronta para correr em Docker no NAS.

## Funcionalidades

- Registo de utilizadores com conta inativa por defeito.
- Aprovação pelo administrador em `/admin/`, ativando o campo `Active` do utilizador.
- Dados financeiros isolados por utilizador autenticado.
- Orçamentos mensais com rendimento, despesas fixas, despesas diarias e despesas BONGO/extra.
- Base de dados SQLite persistida em volume Docker.

## Arranque no Docker

1. Edita `docker-compose.yml` e troca `DJANGO_SECRET_KEY`.
2. Ajusta `DJANGO_ALLOWED_HOSTS` para o IP ou dominio do teu NAS.
3. Arranca:

```bash
docker compose up -d --build
```

4. Cria o administrador:

```bash
docker compose exec budget python manage.py createsuperuser
```

5. Abre `http://IP-DO-NAS:8000`.

## Aprovar novos utilizadores

1. Entra em `/admin/` com o superutilizador.
2. Vai a `Users`.
3. Abre o utilizador registado.
4. Marca `Active`.
5. Guarda.

Enquanto `Active` estiver desligado, o utilizador nao consegue iniciar sessao.

## Privacidade dos dados

Cada orçamento pertence a um utilizador. As views filtram sempre por `owner=request.user`, incluindo detalhes, despesas fixas, movimentos e apagamentos.

## Desenvolvimento local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
