# Medi Check Backend

FastAPI backend for Medi Check with SQLite as the local development database.

## What you need on your computer

- Python 3.12 or 3.13
- `uv`
- Docker Desktop is not required for local SQLite development.

## Local Setup

1. Copy the example environment file:

```powershell
copy .env.example .env
```

2. Install dependencies:

```powershell
uv sync
uv sync --group dev
```

3. Run Alembic migrations:

```powershell
uv run alembic upgrade head
```

4. Start the API:

```powershell
uv run uvicorn app.main:app --reload
```

## Local Database

The default local database connection is:

```text
sqlite:///./app.db
```

## Useful Commands

```powershell
uv run ruff check .
uv run pytest
```

## API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`
