# Phase 0 Implementation Plan — STA V0 Foundations (through Market Data)

> **This is the execution guide for the implementation chat.** It was produced in a separate
> planning session. Read it top-to-bottom and work through the milestones **in order**. The
> planning session wrote no code — all code/doc edits happen here, in the implementation chat.
> Before starting, confirm architecture decisions **A1–A4** below with Khanishk (or proceed on
> the stated recommendations if pre-approved).

---

## Context — why this exists

CLAUDE.md's "What is DONE" section claims six foundational files are complete
(`core/types.py`, `core/events.py`, `adapters/broker/base.py`, `config/settings.py`,
`infrastructure/logging_config.py`, `api/main.py`). **They are not.** Verified ground truth:

- **Every file under `src/sta/` is empty (0 bytes)** — all 22 Python files are bare stubs.
- **Alembic is not initialized** — no `migrations/`, no `alembic.ini`, no `env.py`.
- **No tests exist** — `tests/` has only empty `__init__.py` files.
- Most root docs are empty too (README, PROJECT, ARCHITECTURE, DECISIONS, ROADMAP, SECURITY).

What **is** real and correct, and must be respected (do not rewrite):
- `pyproject.toml` — deps + tool config (ruff line-length 100 / py311 / E,F,I,UP,B,SIM;
  pytest `asyncio_mode=auto`, `--cov=sta`; **mypy strict**). `indicators` extra is separate.
- `docker-compose.yml` — `timescale/timescaledb:latest-pg16` (db `sta_dev`, user `sta_user`,
  pw `sta_dev_password`, :5432) + `redis:7-alpine` (:6379), both with healthchecks.
- `.env.example` — `APP_ENV`, `LOG_LEVEL`, `DATABASE_URL` (postgresql+asyncpg), `REDIS_URL`,
  `KITE_API_KEY/SECRET/ACCESS_TOKEN`, `MAX_POSITION_SIZE_PCT/PORTFOLIO_DRAWDOWN_PCT/DAILY_LOSS_PCT`.

**Scope of Phase 0:** build the entire V0 foundation up to and including the **Market Data
module** (CLAUDE.md Steps 1–4). **Strategy Engine is explicitly excluded** — CLAUDE.md says it
is not architecturally designed yet; do not implement it.

**Intended outcome:** `docker compose up -d` → `alembic upgrade head` → `uvicorn` serves
`/health` ok → a tick driven through the single quality gate appears on the Redis hot path AND
is persisted to the `ticks` hypertable → `pytest`, `ruff`, and `mypy --strict` all pass.

---

## Non-negotiable rules that bind every milestone (from CLAUDE.md)

1. **Module isolation** — modules never import each other; only `src/sta/core/` is shared.
   All inter-module talk is via the event bus. (`from sta.modules.X import ...` inside module Y = violation.)
2. **UTC only** — `datetime.now(tz=timezone.utc)`. IST is display-only; never stored.
3. **No secrets in code** — everything via `config/settings.py` ← `.env`.
4. **Idempotency keys on orders** — `Order` carries `idempotency_key`.
5. **Indicators behind interface** — N/A this phase (no Strategy Engine), but don't import pandas-ta anywhere.
6. **No `print()`** — `logging.getLogger(__name__)` everywhere.
7. **Single quality gate** — live + replay ticks pass through exactly one validate/normalize/dedup chokepoint.
8. **Deterministic replay** — historical ticks travel the identical code path as live ticks.
9. **Kill switch** — design-aware from V0; no execution path exists yet, so nothing to retrofit here.

---

## ⚠️ Architecture decisions to confirm BEFORE coding (do not invent)

Per CLAUDE.md ("when unsure, ask Khanishk; do not invent a new pattern"), these are not
specified and must be confirmed in the **architecture chat** before implementation proceeds:

- **A1 — Domain type representation.** `Tick/Bar/Signal/Order`: Pydantic v2 `BaseModel`
  (consistent with settings + validation) vs. plain dataclass/`msgspec` (faster for the hot
  tick path). **Recommendation: Pydantic v2 for V0** (simplicity > micro-perf); revisit if hot
  path profiling demands it.
- **A2 — SQLAlchemy ORM model location.** `ticks`/`instruments`/`market_sessions` belong to the
  Market Data module, but Alembic's `env.py` must import their metadata. **Recommendation:**
  `src/sta/modules/market_data/models.py`, imported by Alembic `env.py`. Confirm this doesn't
  violate the isolation rule (it doesn't — Alembic is infrastructure, not a module).
- **A3 — Continuous aggregates (`bars_1m`, `bars_5m`).** Include in the initial migration or
  defer? TimescaleDB continuous aggregates **cannot run inside a transaction**, which fights
  Alembic's transactional DDL. **Recommendation: defer** caggs to a follow-up migration; the
  initial migration creates only the `ticks` hypertable + base tables.
- **A4 — Redis hot-path naming.** CLAUDE.md gives the latest-price cache key
  `price:{exchange}:{symbol}` and "Pub/Sub channel per instrument". Confirm channel naming
  convention (e.g. `ticks:{exchange}:{symbol}`).

> Surface A1–A4 to Khanishk and get confirmation, or proceed with the stated recommendations if
> pre-approved.

---

## Milestone A — Make the skeleton real (CLAUDE.md Step 1)

Fill the six empty foundational files so the app actually boots.

| File | What to implement |
|---|---|
| `src/sta/config/settings.py` | Pydantic-Settings v2 `Settings` with fields mirroring `.env.example` exactly. `SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")`. Provide a cached accessor `get_settings()` (`functools.lru_cache`). No secrets defaulted to real values. |
| `src/sta/infrastructure/logging_config.py` | `configure_logging()` called once; structured **JSON** formatter; honors `settings.log_level`; root logger config; modules obtain `logging.getLogger(__name__)`. No `print()`. |
| `src/sta/core/types.py` | `Tick`, `Bar`, `Signal`, `Order` (per A1). UTC timestamps. Enums: `Exchange`, `Direction` (BUY/SELL/CLOSE), `OrderType`, `OrderStatus`, `BarPeriod`. `Order` carries `idempotency_key`. |
| `src/sta/core/events.py` | Base `Event` (`event_id`, `timestamp` UTC, `version`, `to_json`/`from_json`). Concrete event classes for the 8-module map; **fully implement only those Market Data needs now** (e.g. `TickIngested`, `BarClosed`, `GapDetected`) — others may be declared. |
| `src/sta/adapters/broker/base.py` | Abstract `BrokerAdapter` (ABC), all async: `connect`, `disconnect`, `get_instruments`, tick subscription (async stream), historical fetch (for backfill), `submit_order`, `cancel_order`, `get_order_status`, `get_positions`. Types from `core/`. No Zerodha impl this phase. |
| `src/sta/api/main.py` | FastAPI app with `lifespan` async context manager that calls `configure_logging()` and initializes/disposes DB + Redis (added in Milestone B). `GET /health` → `{"status":"ok","env":settings.app_env}`. |

**Verify A:** `uvicorn sta.api.main:app --reload` → `GET http://localhost:8000/health` returns
`{"status":"ok","env":"development"}`. `mypy --strict` and `ruff check` clean on these files.

---

## Milestone B — Infrastructure utilities (CLAUDE.md Step 2)

| File | What to implement |
|---|---|
| `src/sta/infrastructure/database.py` | Async SQLAlchemy 2.0 engine from `settings.database_url`; `async_sessionmaker`; `class Base(DeclarativeBase)`; `get_session()` dependency; `init_engine()`/`dispose_engine()` for lifespan. |
| `src/sta/infrastructure/redis_client.py` | Async `redis` client from `settings.redis_url`. **Streams** helpers (`xadd`, consumer-group create + `xreadgroup`, ack) for durable signal/order/audit paths. **Pub/Sub** helpers (publish/subscribe) for disposable hot-path ticks. Latest-price cache helpers on hash key `price:{exchange}:{symbol}`. |

Wire `init/dispose` into `api/main.py` lifespan (from Milestone A).

**Verify B:** an integration test (or throwaway script) connects to the docker Postgres and Redis,
does a round-trip `SET/GET` and a `SELECT 1`. Requires `docker compose up -d`.

---

## Milestone C — Alembic + initial schema (CLAUDE.md Step 3)

1. `alembic init src/sta/infrastructure/migrations`.
2. Configure `env.py`: async engine using `settings.database_url`; `target_metadata = Base.metadata`;
   import the Market Data ORM models (A2) so they're registered.
3. **Initial migration** creates:
   - `CREATE EXTENSION IF NOT EXISTS timescaledb;` (via `op.execute`)
   - `instruments` (token↔symbol mapping: token, symbol, exchange, name, instrument_type,
     tick_size, lot_size, expiry, …)
   - `market_sessions` (calendar: date, session state, open/close, holiday flag, …)
   - `ticks` table, then `SELECT create_hypertable('ticks', 'time');` (via `op.execute`)
   - **Defer** continuous aggregates `bars_1m`/`bars_5m` per **A3** (separate later migration).

**Verify C:** `alembic upgrade head` against docker Postgres succeeds; confirm the hypertable
exists (`SELECT * FROM timescaledb_information.hypertables;`). `alembic downgrade base` is clean.

---

## Milestone D — Market Data module (CLAUDE.md Step 4)

Location `src/sta/modules/market_data/`. The **only** designed module. Flow:

```
Broker adapter → Quality gate (validate·normalize·dedup, SINGLE entry) → ├─ Hot path  (Redis Pub/Sub fan-out)
                                                                          └─ Cold path (batched TimescaleDB writes)
```

| File | Responsibility |
|---|---|
| `models.py` (per A2) | SQLAlchemy ORM for `instruments`, `market_sessions`, `ticks` (Alembic imports this). |
| `quality_gate.py` | The single chokepoint. **Reject:** price ≤ 0; volume = 0 on a trade tick; stale tick (timestamp older than N s); duplicate (instrument+timestamp already seen); price outside ±20% circuit limit from previous close. Normalize to `core.types.Tick`. |
| `hot_path.py` | Publish validated ticks to Redis Pub/Sub (channel per instrument, A4); update `price:{exchange}:{symbol}` cache. |
| `cold_path.py` | Batched writes of validated ticks to the `ticks` hypertable (authoritative record). |
| `instrument_master.py` | symbol↔token mapping; refresh each session via broker adapter. |
| `calendar.py` | trading hours, pre-open, holidays, session state. |
| `backfiller.py` | on reconnect: detect gap, pull missing window via broker historical REST, **re-inject through the quality gate** before resuming live. |
| `service.py` | module coordinator: wires adapter → gate → hot/cold; exposes the same entry for **live and replay** (deterministic replay, rule 8/9). |

**Tests (`tests/unit`, `tests/integration`):**
- Unit: each quality-gate rejection rule; dedup; normalization; `core.types`; `settings` loading.
  Mock all external deps.
- Integration: cold-path write to TimescaleDB; hot-path Pub/Sub round-trip; backfill re-injection
  through the gate. Requires docker infra.

**Verify D:** drive a sample/replay tick through `service.py` → assert it (a) is published on the
hot-path channel + cached, and (b) lands in the `ticks` hypertable. A malformed tick is rejected by
the gate and never reaches either path. `pytest` green.

---

## Milestone E — Reconcile CLAUDE.md status + housekeeping

- **Correct CLAUDE.md** "What is DONE" / "What is NOT done yet (V0 remaining)": move items to
  reflect reality **as each is actually implemented** (foundation files, database/redis utils,
  Alembic schema, Market Data module). Keep the master spec trustworthy.
- Update `CHANGELOG.md` for the V0 implementation work.
- Do **not** touch the empty long-form docs (README/ARCHITECTURE/DECISIONS/etc.) — out of scope
  for Phase 0 (code-only, per decision).

---

## End-to-end verification (run at the end of Phase 0)

```powershell
docker compose up -d                      # TimescaleDB + Redis healthy
alembic upgrade head                      # schema + ticks hypertable created
uvicorn sta.api.main:app --reload         # GET /health → {"status":"ok","env":"development"}
pytest                                     # unit + integration green, coverage reported
ruff check src tests                       # lint clean
mypy src                                   # strict type-check clean
```
Plus the manual tick round-trip from Milestone D (validated tick → hot path + hypertable;
malformed tick → rejected).

---

## Files created/modified in Phase 0 (summary)

**Implemented (currently empty):** `core/types.py`, `core/events.py`, `adapters/broker/base.py`,
`config/settings.py`, `infrastructure/logging_config.py`, `api/main.py`.
**New:** `infrastructure/database.py`, `infrastructure/redis_client.py`,
`infrastructure/migrations/**` (Alembic), `modules/market_data/{models,quality_gate,hot_path,cold_path,instrument_master,calendar,backfiller,service}.py`,
tests under `tests/unit/**` and `tests/integration/**`.
**Modified:** `CLAUDE.md` (status section), `CHANGELOG.md`.
**Untouched:** `pyproject.toml`, `docker-compose.yml`, `.env.example`, `.gitignore`, long-form docs.

**Explicitly out of scope:** Strategy Engine and all modules after it (signal/risk/orders/
execution/portfolio/audit), Zerodha adapter implementation, continuous aggregates (deferred, A3).
