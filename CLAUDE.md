# STA — Claude Code Master Context

This file is read automatically by Claude Code every session.
You have full context of this project. Never ask Khanishk to re-explain decisions already made here.
Follow every rule here without exception. When in doubt, re-read this file.

---

## What this project is

**Stock Trading Automation (STA)** — a personal algorithmic trading platform for
Indian equity markets (NSE, BSE). Built production-grade from day one.
Long-term goal: commercial SaaS product (V5).

**Owner/Developer:** Khanishk (strong Python + JS/web; intermediate overall)
**Your role:** implement what the architecture defines. Do not invent new patterns.
**Architecture decisions:** already made. See ADRs below. Do not re-litigate them.

---

## Current state

**Version:** V0 — Foundations
**Stage:** Phase 0 of `Implement.md` (Milestones A–E) implemented: foundation
skeleton, DB/Redis infrastructure, Alembic schema, and the Market Data module.
No trading logic exists yet — that starts at the Strategy Engine, which is
not designed.

> **Status corrected 2026-06-29.** Re-verify file contents directly before


### What is DONE
- GitHub repo + full folder skeleton, Git/GitHub workflow, repo config
  (labels, milestones, branch protection), `LICENSE`.
- Foundation skeleton: `core/types.py` (Tick/Bar/Signal/Order/Instrument/
  Position), `core/events.py` (TickIngested/BarClosed/GapDetected),
  `config/settings.py`, `infrastructure/logging_config.py` (JSON), abstract
  `adapters/broker/base.py`, `api/main.py` (`/health`).
- Infrastructure: async SQLAlchemy engine/session (`infrastructure/database.py`)
  + async Redis client with Streams/Pub-Sub/price-cache helpers
  (`infrastructure/redis_client.py`), both wired into the API lifespan.
- Alembic schema: `instruments`, `market_sessions`, `ticks` (TimescaleDB
  hypertable). Continuous aggregates deferred (ADR A3).
- Market Data module (`src/sta/modules/market_data/`): quality gate, hot
  path, cold path, instrument master, calendar, gap backfiller, and the
  `MarketDataService` coordinator.
- 40 tests (unit + integration), mypy `--strict` clean.

### What is NOT done yet
- [ ] Long-form docs (README, PROJECT, ARCHITECTURE, DECISIONS, ROADMAP,
      SECURITY) — still placeholders; `.github/workflows/ci.yml` not written
- [ ] Strategy Engine architecture design (next major milestone) and
      implementation
- [ ] Signal Engine, Risk Engine, Order Manager, Execution Engine, Portfolio
      Tracker, Audit & Notify — none designed yet
- [ ] Zerodha Kite Connect broker adapter implementation (only the abstract
      port exists)
- [ ] Any actual trading logic

### Verify it runs
```powershell
docker compose up -d
alembic upgrade head
uvicorn sta.api.main:app --reload
# GET http://localhost:8000/health → {"status":"ok","env":"development"}
pytest
```

---

## Architecture

### Pattern
Modular Monolith with planned microservices evolution path.
Single deployable unit. Strict internal module boundaries enforced at code level.

### Five layers
```
External World      NSE/BSE market feeds · Zerodha Kite Connect broker API
      ↕
Adapter Layer       Market adapter (normalises feeds) · Broker adapter (pluggable)
      ↕
Event Bus           Redis Streams — ALL inter-module communication goes here
      ↕
Domain Modules      Eight modules (see below) — isolated, event-driven
      ↕
Infrastructure      PostgreSQL + TimescaleDB · Redis · Structured logging
```

### Eight domain modules
| # | Module | Location | Responsibility |
|---|---|---|---|
| 1 | Market Data | `src/sta/modules/market_data/` | Ingest ticks + OHLCV bars; quality gate; hot/cold path split |
| 2 | Strategy Engine | `src/sta/modules/strategy/` | Apply TA indicators; generate raw signals |
| 3 | Signal Engine | `src/sta/modules/signal/` | Filter and rank signals before risk evaluation |
| 4 | **Risk Engine** | `src/sta/modules/risk/` | **MANDATORY. NEVER BYPASSED. Pre-trade checks.** |
| 5 | Order Manager | `src/sta/modules/orders/` | Order lifecycle; hold for confirmation or route to execution |
| 6 | Execution Engine | `src/sta/modules/execution/` | Submit orders to broker via adapter; handle fills |
| 7 | Portfolio Tracker | `src/sta/modules/portfolio/` | Track positions, P&L (realized + unrealized) |
| 8 | Audit & Notify | `src/sta/modules/audit/` | Immutable event log; alerts; SEBI compliance trail |

---

## Tech stack

| Layer | Technology | Notes |
|---|---|---|
| Backend (all modules + API) | Python 3.12 | Single backend language |
| API + WebSockets | FastAPI + Uvicorn | FastAPI handles WebSockets natively — no Node.js needed |
| Frontend dashboard | TypeScript | Deferred until Confirmation mode needs a UI |
| Config | Pydantic Settings | Reads from `.env` — no secrets in code |
| Database | PostgreSQL 16 + TimescaleDB | TimescaleDB extension mandatory for time-series |
| Migrations | Alembic | |
| Event bus | Redis Streams | Durable paths: signals, orders, audit |
| Live tick fan-out | Redis Pub/Sub | Disposable only — hot path ticks to strategies |
| Cache | Redis | Latest price per instrument |
| Data processing | pandas, NumPy | |
| Indicators | pandas-ta | Behind swappable interface. Install: `pip install -e ".[indicators]"` |
| HTTP client | httpx | Broker REST API calls |
| Broker | Zerodha Kite Connect | First adapter. ₹500/mo for data plan. Others via same adapter interface. |
| Testing | pytest + pytest-asyncio | |
| Linting | ruff | |
| Type checking | mypy (strict) | |
| Tooling | Git, GitHub, Markdown, Mermaid | |

---

## Non-negotiable rules

### 1. Module isolation — most important rule
- Modules **NEVER** import from each other directly.
- All inter-module communication goes through the event bus (Redis Streams/Pub/Sub).
- The only shared code across modules is `src/sta/core/` — types and event definitions.
- If you write `from sta.modules.X import ...` inside module Y, that is a violation. Use an event.

### 2. Risk Engine is mandatory
- No signal ever reaches Order Manager or Execution Engine without passing through Risk Engine.
- There is no code path that bypasses it. If you are creating one, stop.

### 3. Timestamps — UTC only
- All internal timestamps: `datetime.now(tz=timezone.utc)` or `datetime.utcnow()`.
- IST is a display concern only. Never store IST in the database or events.

### 4. No secrets in code
- No API keys, passwords, tokens, or connection strings in source files. Ever.
- All config comes from `src/sta/config/settings.py` which reads from `.env`.

### 5. Idempotency keys on orders
- Every order command carries an `idempotency_key` set before submission.
- A network retry must never double-submit a trade.

### 6. Indicators behind interface
- No module imports pandas-ta or TA-Lib directly.
- Indicators sit behind a swappable interface in the Strategy Engine.
- The rest of the system never knows which library is underneath.

### 7. No print() statements
- Use `logging.getLogger(__name__)` in every module.
- Logging configured once in `src/sta/infrastructure/logging_config.py`.

### 8. Single quality gate for market data
- All data (live ticks AND historical replay) passes through exactly one
  validate/normalize/dedup chokepoint in the Market Data module.
- No raw broker data ever reaches a strategy directly.

### 9. Deterministic replay
- Historical ticks must travel the same code path as live ticks.
- Backtest and live behavior must be identical by construction.

### 10. Kill switch is mandatory
- A kill switch to halt all trading instantly is a hard regulatory requirement (SEBI).
- Must be built into Risk Engine and Execution Engine from V3 onwards.
- Design for it from V0 so it is not retrofitted.

---

## Architecture Decision Records (summary)

All 16 ADRs are recorded in full in `DECISIONS.md`. Summary:

| ADR | Decision |
|---|---|
| 001 | Modular Monolith with microservices evolution path |
| 002 | Python-only backend (engine, all modules, FastAPI, WebSockets) |
| 003 | C# rejected — no defined role; network dominates latency; adds cross-runtime seam |
| 004 | TypeScript frontend deferred until Confirmation UI is needed |
| 005 | PostgreSQL + TimescaleDB for storage |
| 006 | Redis Streams for signal/order/audit; Pub/Sub for disposable live ticks only |
| 007 | Risk Engine mandatory and architecturally un-bypassable |
| 008 | Pluggable broker adapter; Zerodha Kite Connect first implementation |
| 009 | Market Data hot/cold path split with single quality gate + deterministic replay |
| 010 | Indicators behind swappable interface; pandas-ta first |
| 011 | Event-driven replay is the backtest of record; VectorBT optional research only |
| 012 | Idempotency keys on all order commands |
| 013 | Single UTC clock authority; IST is presentation-only |
| 014 | Monorepo |
| 015 | Tenancy boundary in data model from day one; single-tenant deploy until V5 |
| 016 | White-box compliance posture; never take user fund custody; mandatory kill switch; audit trail: Client→Algo-ID→Static IP→API key |

---

## Market Data module — fully designed

This is the only module with a completed design. Implement this first.

### Data flow
```
Broker feed
    ↓
Broker adapter (implements BrokerAdapter port)
    ↓
Quality gate — validate · normalize · dedup (SINGLE entry point)
    ↓                          ↓
Hot path                  Cold path
Redis Pub/Sub             Batched writes
(live ticks to            to TimescaleDB
strategies)               (authoritative record)
```

### Supporting services (build these too)
- **Instrument master** — symbol↔token mapping, refreshed each session
- **Market calendar** — trading hours, pre-open, holidays, session state
- **Gap detector/backfiller** — on WebSocket reconnect: detect gap, pull missing
  window from REST API, re-inject through quality gate before resuming live

### Quality gate must reject
- Price = 0 or negative
- Volume = 0 on a trade tick
- Timestamp older than N seconds (stale tick)
- Duplicate tick (same instrument + timestamp already seen)
- Price outside circuit breaker limits (±20% from previous close)

### TimescaleDB schema (implement via Alembic)
- `ticks` hypertable — raw tick storage, partitioned by time
- `bars_1m`, `bars_5m` etc. — via continuous aggregates from ticks
- `instruments` — master table
- `market_sessions` — calendar data

### Redis usage
- Pub/Sub channel per instrument for live tick fan-out (hot path)
- Hash key `price:{exchange}:{symbol}` for latest-price cache

---

## SEBI regulatory context (researched, Feb-2025 framework)

**Personal use (V1–V4): fully unobstructed.**
- Under 10 orders/second, own account, transparent logic = regular API user.
- No registration required.

**SaaS (V5): heavier but walkable.**
- Must partner with a registered broker (empanelment).
- Cannot connect directly to exchanges.
- Stay white-box (rule-based) to avoid Research Analyst registration.
- Never take custody of user funds — orders only in user's own account.

**Mandatory for all versions:**
- Audit trail: Client → Algo-ID → Static IP → API key (every order)
- Kill switch (regulatory requirement, not optional)
- Static IP for live API (provision at VPS stage — not needed for local dev)
- Daily re-auth with 2FA (Kite access token expires daily — human checkpoint by design)

**Fund movement reality:**
- In-account allocation (buy/sell) = fully supported via API
- Bank ↔ broker transfers = NOT via API, manual/user-initiated only

---

## Trading modes

Both modes use the same pipeline. Mode is configuration, not separate architecture.

| Mode | Flow |
|---|---|
| Confirmation (Mode 1) | Signal → Risk Engine → Order Manager → **wait for user approval** → Execution |
| Fully Automated (Mode 2) | Signal → Risk Engine → Order Manager → Execution (automatic) |

### Risk profiles (both must exist from V1)
- **Conservative** — tight position limits, low drawdown tolerance (default)
- **Aggressive** — wider limits, higher risk tolerance

Risk management is never bypassed regardless of mode or profile.

---

## Version roadmap

| Version | Scope | Status |
|---|---|---|
| V0 | Foundations — skeleton, infra, event bus, no trading | **In progress** |
| V1 | Confirmation mode, paper trading, one strategy, Conservative profile | Not started |
| V2 | Confirmation mode, small live capital, hardened Risk Engine, monitoring | Not started |
| V3 | Fully automated mode, kill switch mandatory, circuit breakers | Not started |
| V4 | Multi-broker, multi-strategy, optional ML interfaces | Not started |
| V5 | SaaS / multi-tenant (requires legal groundwork first) | Not started |

**Deployment path:** Local machine (V0–V1) → VPS/cloud with static IP (V2+)

---

## V0 implementation order

Do these in this exact order. Do not skip ahead.

### Step 1 — Verify skeleton runs
```powershell
docker compose up -d
uvicorn sta.api.main:app --reload
# GET http://localhost:8000/health must return {"status":"ok"}
```

### Step 2 — Database infrastructure
File: `src/sta/infrastructure/database.py`
- Async SQLAlchemy engine using `settings.database_url`
- Session factory
- Base declarative model

File: `src/sta/infrastructure/redis_client.py`
- Async Redis client using `settings.redis_url`
- Helper for Streams publish/consume
- Helper for Pub/Sub

### Step 3 — Alembic setup + initial schema
```bash
alembic init src/sta/infrastructure/migrations
```
Initial migration must create:
- `instruments` table
- `market_sessions` table
- `ticks` hypertable (TimescaleDB)
- Enable TimescaleDB extension: `CREATE EXTENSION IF NOT EXISTS timescaledb;`

### Step 4 — Market Data module
Location: `src/sta/modules/market_data/`
Files to create:
- `service.py` — main module coordinator
- `quality_gate.py` — validation and normalization
- `hot_path.py` — Redis Pub/Sub fan-out
- `cold_path.py` — batched TimescaleDB writes
- `backfiller.py` — gap detection and backfill
- `instrument_master.py` — symbol↔token management
- `calendar.py` — market session/calendar logic

### Step 5 — Strategy Engine (design first, then implement)
This module has NOT been architecturally designed yet.
Do NOT implement it until the design is confirmed.
The design session will define: strategy interface, indicator pipeline,
signal contract, and how strategies subscribe to market data events.

---

## Project structure

```
sta/
├── .github/workflows/ci.yml
├── docs/
│   ├── adr/                    # One .md file per ADR
│   └── diagrams/               # Mermaid .mmd files
├── src/sta/
│   ├── core/
│   │   ├── types.py            # Tick, Bar, Signal, Order — EMPTY stub
│   │   └── events.py           # All event definitions — EMPTY stub
│   ├── adapters/
│   │   └── broker/
│   │       ├── base.py         # Abstract port — EMPTY stub
│   │       └── zerodha/        # Zerodha implementation — NOT YET (no folder)
│   ├── modules/
│   │   ├── market_data/        # Designed; only EMPTY __init__.py exists
│   │   ├── strategy/           # NOT YET designed or implemented
│   │   ├── signal/             # NOT YET
│   │   ├── risk/               # NOT YET
│   │   ├── orders/             # NOT YET
│   │   ├── execution/          # NOT YET
│   │   ├── portfolio/          # NOT YET
│   │   └── audit/              # NOT YET
│   ├── infrastructure/
│   │   ├── database.py         # NOT YET (does not exist)
│   │   ├── redis_client.py     # NOT YET (does not exist)
│   │   └── logging_config.py   # EMPTY stub
│   ├── api/
│   │   └── main.py             # EMPTY stub
│   └── config/
│       └── settings.py         # EMPTY stub
├── tests/
│   ├── unit/                   # only EMPTY __init__.py
│   └── integration/            # only EMPTY __init__.py
├── .env.example                # DONE
├── .gitignore                  # DONE
├── docker-compose.yml          # DONE — TimescaleDB + Redis
├── pyproject.toml              # DONE
├── setup.ps1                   # DONE
├── CLAUDE.md                   # This file — DONE
├── CONTRIBUTING.md             # DONE
├── DEVELOPMENT.md              # DONE
├── README.md                   # EMPTY stub
├── PROJECT.md                  # EMPTY stub
├── ARCHITECTURE.md             # EMPTY stub
├── DECISIONS.md                # EMPTY stub (intended: all 16 ADRs)
├── ROADMAP.md                  # EMPTY stub
└── SECURITY.md                 # EMPTY stub
```

---

## Testing conventions

- Unit tests in `tests/unit/` — mock all external dependencies
- Integration tests in `tests/integration/` — requires running Docker infra
- Every module must have tests before it is considered complete
- A feature is "done" only when its tests pass AND docs are updated
- Run all tests: `pytest`
- Run with coverage: `pytest --cov=sta`

---

## Local dev commands

```powershell
# Activate venv (Windows)
.venv\Scripts\Activate.ps1

# Start infrastructure
docker compose up -d

# Stop infrastructure
docker compose down

# Run API
uvicorn sta.api.main:app --reload

# Run tests
pytest

# Lint
ruff check src tests

# Type check
mypy src

# Install indicator library (when Strategy Engine is ready)
pip install -e ".[indicators]"
```

---

## What to do when you are unsure about an architectural decision

Do not guess. Do not invent a new pattern.
Tell Khanishk: "This requires an architecture decision — please confirm in the
architecture chat before I implement it."

The architecture chat (Claude on claude.ai) is where design decisions are made.
Claude Code (you) is where confirmed designs are implemented.
