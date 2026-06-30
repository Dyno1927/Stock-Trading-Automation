# Changelog

All notable changes to **Stock Trading Automation (STA)** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **V0 Phase 0 implementation** (per `Implement.md`, Milestones A–E):
  - **Foundation:** Pydantic settings (`config/settings.py`), structured JSON
    logging (`infrastructure/logging_config.py`), core domain types
    (`Tick`, `Bar`, `Signal`, `Order`, `Instrument`, `Position`) and events
    (`TickIngested`, `BarClosed`, `GapDetected`), the abstract `BrokerAdapter`
    port, and the FastAPI app with a `/health` endpoint.
  - **Infrastructure:** async SQLAlchemy engine/session
    (`infrastructure/database.py`) and an async Redis client with Streams,
    Pub/Sub, and price-cache helpers (`infrastructure/redis_client.py`), both
    wired into the API lifespan.
  - **Database schema (Alembic):** `instruments`, `market_sessions`, and the
    `ticks` TimescaleDB hypertable. Continuous aggregates deferred.
  - **Market Data module:** a single quality gate (validate/normalize/dedup),
    hot path (Redis Pub/Sub fan-out), cold path (batched TimescaleDB writes),
    instrument master, market calendar, gap backfiller, and the
    `MarketDataService` coordinator.
  - 40 unit + integration tests; `mypy --strict` clean.

### Notes

- No trading logic yet — the pipeline begins at the Strategy Engine, which is
  not designed or implemented (intentionally; see CLAUDE.md).

## [0.1.0] — 2026-06-28

Foundation release. Repository structure, Git/GitHub workflow, engineering
standards, and the documentation framework.

### Added

- Repository skeleton: modular-monolith layout, eight domain-module stubs,
  FastAPI entrypoint, Docker Compose infrastructure (PostgreSQL + TimescaleDB,
  Redis), config/settings, and logging setup.
- Git & GitHub workflow conventions (`CONTRIBUTING.md`, `DEVELOPMENT.md`).
- Documentation framework: README, PROJECT, ARCHITECTURE, DECISIONS, ROADMAP,
  SECURITY, RELEASES, GLOSSARY, VERSIONING, SUPPORT, and ADRs 0001–0008.
- Proprietary "All Rights Reserved" `LICENSE`.

No trading functionality.

[Unreleased]: https://github.com/Dyno1927/Stock-Trading-Automation/compare/main...develop
[0.1.0]: https://github.com/Dyno1927/Stock-Trading-Automation/releases/tag/v0.1.0
