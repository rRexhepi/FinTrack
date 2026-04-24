# FinTrack

A personal-finance dashboard: track expenses, plan budgets, and monitor
investments with real-time market data. Django REST backend + React
frontend, JWT auth, PostgreSQL.

> **Status:** portfolio project. Backend and frontend run end-to-end;
> rolling cleanup underway — see [Roadmap](#roadmap).

## Stack

| Layer | Tech |
|---|---|
| API | Django 5.1 + Django REST Framework 3.15 |
| Auth | JWT via `djangorestframework-simplejwt` |
| DB | PostgreSQL (psycopg2) |
| Static | WhiteNoise (compressed manifest storage) |
| Market data | `yfinance` |
| Frontend | React 18 + Material UI + Recharts + Formik |
| Deploy | Gunicorn on Render |

## Features

- JWT-authenticated REST API for expenses, investments, budgets, and
  auto-generated spending suggestions.
- Per-user scoping on every list / detail endpoint (no cross-tenant
  leakage).
- Investment valuation against live `yfinance` quotes.
- Pagination on every list endpoint (DRF `PageNumberPagination`, 10/page).
- React SPA with charts, tables, and form validation via Formik + Yup.

## Quickstart

### Backend (Docker — recommended)

```bash
git clone https://github.com/rRexhepi/FinTrack.git
cd FinTrack

cp .env.example .env
python get_secret.py >> .env       # generates a SECRET_KEY line
docker compose up --build
```

`docker-compose.yaml` boots Postgres 15, applies migrations, and starts
gunicorn on `http://127.0.0.1:8000/api/`.

### Backend (native)

```bash
python3 -m venv venv
source venv/bin/activate          # or venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env
python get_secret.py >> .env       # generates a SECRET_KEY line

# Make sure Postgres is running and the DB from .env exists.
createdb fintrack_db

python manage.py migrate
python manage.py runserver
```

API is at `http://127.0.0.1:8000/api/`.

### Frontend

```bash
cd fintrack_frontend
npm install
npm start
```

Dev server is at `http://localhost:3000/` and proxies API calls via the
axios client configured in `fintrack_frontend/src/`.

## Environment variables

See [`.env.example`](.env.example) for the full list.

| Var | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | *(required in production)* |
| `DEBUG` | Django debug mode | `True` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | Postgres connection | `fintrack_db` / `postgres` / *(empty)* / `localhost` / `5432` |

## Tests

```bash
python manage.py test
```

Covers model `__str__` / creation, expense CRUD via DRF, and
authenticated vs unauthenticated access on the expense list endpoint.
Broader coverage (investment serializer with mocked `yfinance`,
validation edge cases) is on the roadmap.

## Deployment

`Procfile` runs `gunicorn fintrack_backend.wsgi`. The production target
is Render — see `ALLOWED_HOSTS` in `fintrack_backend/settings.py`. On
deploy, run `python manage.py collectstatic --noinput` so WhiteNoise
has the manifest it needs.

## Roadmap

What a reviewer would expect from a full-stack Django portfolio project:

- [x] `requirements.txt` + `.env.example` committed
- [x] Tracked `venv/` / `__pycache__/` / `staticfiles/` purged from history
- [x] Proper `.gitignore` (Python + Django + Node)
- [ ] `yfinance` called outside model properties + cached per ticker
      (current `Investment.current_value` is a synchronous network call
      per instance — N+1 on the dashboard list)
- [ ] Expanded test suite: investment serializer with mocked `yfinance`,
      validation edge cases, JWT flow
- [x] GitHub Actions CI: Django check + test (+ Docker build)
- [x] Dockerfile + `docker-compose.yaml` (app + Postgres)
- [ ] Lint (ruff) added to CI

## License

MIT — see [LICENSE](LICENSE).
