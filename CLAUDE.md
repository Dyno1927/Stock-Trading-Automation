# STA — Claude Code Project Context

This file is read automatically by Claude Code on every session.
Follow every rule here without exception.

---

## What this project is

Stock Trading Automation (STA) — a personal algorithmic trading platform for
Indian equity markets (NSE, BSE). Built production-grade from day one with the
long-term goal of becoming a commercial SaaS product.

**Current stage:** V0 — Foundations. No trading logic yet.

---

## Architecture — read this before touching any file

### Pattern
Modular Monolith. Single deployable unit. Strict internal module boundaries.

### Five layers (top → bottom)
1. External World — NSE/BSE feeds, Zerodha Kite Connect broker API
2. Adapter Layer — broker-agnostic interfaces (market adapter, broker adapter)
3. Event Bus — Redis Streams for all inter-module communication
4. Domain Modules — the eight modules listed below
5. Infrastructure — PostgreSQL + TimescaleDB, Redis, structured logging

### The eight domain modules
| Module | Location | Responsibility |
|---|---|---|
| Market Data | `src/sta/modules/market_data/` | Ingest ticks + bars, quality gate, hot/cold path |
| Strategy Engine | `src/sta/modules/strategy/` | Apply TA indicators, generate raw signals |
| Signal Engine | `src/sta/modules/signal/` | Filter and rank signals |
| Risk Engine | `src/sta/modules/risk/` | Pre-trade checks — MANDATORY, NEVER BYPASSED |
| Order Manager | `src/sta/modules/orders/` | Order lifecycle, confirmation or auto-route |
| Execution Engine | `src/sta/modules/execution/` | Submit orders to broker via adapter |
| Portfolio Tracker | `src/sta/modules/portfolio/` | Positions, P&L |
| Audit & Notify | `src/sta/modules/audit/` | Immutable event log, alerts |

---

## Rules — never break these

### Module isolation
- Modules NEVER import from each other directly.
- All inter-module communication goes through the event bus (Redis Streams).
- The only shared code is `src/sta/core/` — types and event definitions.
- If you are about to write `from sta.modules.X import ...` inside module Y, stop. Use an event instead.

### Risk Engine
- No signal ever reaches the Order Manager or Execution Engine without passing through the Risk Engine.
- There is no code path that bypasses it. If you are creating one, stop.

### Timestamps
- All internal timestamps are UTC. `datetime.utcnow()` or `datetime.now(tz=timezone.utc)`.
- IST is a display concern only. Never store IST in the database.

### Secrets
- No API keys, passwords, or tokens in source code. Ever.
- All config comes from `src/sta/config/settings.py` which reads from `.env`.
- Never hardcode a connection string, API key, or credential.

### Idempotency
- Every order command carries an `idempotency_key` before submission.
- A retry must never double-submit a trade.

### Indicators
- No module imports a technical indicator library (pandas-ta, TA-Lib) directly.
- Indicators sit behind a swappable interface in the Strategy Engine.
- The rest of the system never knows which library is underneath.

### Logging
- No `print()` statements anywhere in the codebase.
- Use `logging.getLogger(__name__)` in every module.
- Logging is configured once in `src/sta/infrastructure/logging_config.py`.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 |
| API + WebSockets | FastAPI + Uvicorn |
| Config | Pydantic Settings (reads `.env`) |
| Database | PostgreSQL 16 + TimescaleDB |
| Migrations | Alembic |
| Event bus | Redis Streams |
| Cache | Redis |
| Data processing | pandas, NumPy |
| Indicators | pandas-ta (behind interface, install with `pip install -e ".[indicators]"`) |
| HTTP client | httpx |
| Testing | pytest + pytest-asyncio |
| Linting | ruff |
| Type checking | mypy (strict) |

---

## Project structure

```
src/sta/
├── core/           # Shared domain types + event definitions ONLY
├── adapters/       # External-world interfaces (broker adapter port)
│   └── broker/     # base.py = abstract port; zerodha/ = first implementation
├── modules/        # Eight domain modules — isolated, event-driven
├── infrastructure/ # DB, Redis, logging wiring
├── api/            # FastAPI entrypoint
└── config/         # Settings (reads from .env)
```

---

## How to run locally

```bash
# Start infrastructure
docker compose up -d

# Run the API
uvicorn sta.api.main:app --reload

# Health check
# GET http://localhost:8000/health → {"status":"ok","env":"development"}
```

---

## Testing conventions

- Unit tests in `tests/unit/` — no external dependencies, mock everything.
- Integration tests in `tests/integration/` — requires running DB + Redis.
- Every module must have tests before it is considered complete.
- Run with: `pytest`

---

## What is DONE (V0 — Phase 0 of Implement.md)

- Foundation skeleton: settings, structured JSON logging, core domain types
  (Tick/Bar/Signal/Order/Instrument/Position), core events (TickIngested/
  BarClosed/GapDetected), abstract `BrokerAdapter` port, FastAPI `/health`.
- Database + Redis infrastructure: async SQLAlchemy engine/session factory,
  async Redis client (Streams + Pub/Sub + latest-price cache helpers), both
  wired into the API lifespan.
- Alembic schema: `instruments`, `market_sessions`, `ticks` (TimescaleDB
  hypertable). Continuous aggregates deferred (architecture decision A3).
- Market Data module: the single quality gate, hot path (Pub/Sub fan-out +
  price cache), cold path (batched hypertable writes), instrument master,
  market calendar, gap backfiller, and the `MarketDataService` coordinator
  tying them together for both live and replay ticks.
- 40 tests (unit + integration), mypy --strict clean.

## What is NOT built yet (V0 remaining / beyond V0)

- Strategy Engine (architecture not yet designed — do not implement)
- Signal Engine, Risk Engine, Order Manager, Execution Engine, Portfolio
  Tracker, Audit & Notify (none designed yet)
- Zerodha Kite Connect broker adapter implementation (only the abstract port
  exists)
- Any actual trading logic

Do not implement trading logic until the architecture for that module has been
confirmed in the architecture sessions (Claude chat).

---

## Roadmap summary

| Version | Scope |
|---|---|
| V0 (now) | Foundations — skeleton, infra, event bus, no trading |
| V1 | Confirmation trading, paper mode, one strategy |
| V2 | Confirmation trading, small live capital |
| V3 | Fully automated mode, kill switch mandatory |
| V4 | Multi-broker, multi-strategy, optional ML |
| V5 | SaaS / multi-tenant |
