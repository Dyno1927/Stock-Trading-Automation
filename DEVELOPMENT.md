# Development Guide

## Prerequisites

- Python 3.11–3.13
- Docker Desktop (Postgres + TimescaleDB, Redis)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
copy .env.example .env          # fill in real values
```

## Running locally

```bash
docker compose up -d            # start Postgres + Redis
uvicorn sta.api.main:app --reload
```

Health check: `GET http://localhost:8000/health`

## Testing

```bash
pytest
```

Unit tests (`tests/unit/`) mock everything. Integration tests
(`tests/integration/`) require the Docker services above to be running.

## Linting & type checking

```bash
ruff check src tests
mypy
```

## Branching & commits

See `CONTRIBUTING.md` for the full Git/GitHub workflow (branch naming,
commit conventions, PR flow, labels, milestones).
