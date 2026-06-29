# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Initial project scaffold: modular monolith structure, eight domain module
  stubs, FastAPI entrypoint, Docker Compose infra (PostgreSQL + TimescaleDB,
  Redis), config/settings, logging setup.
- Git & GitHub workflow conventions (`CONTRIBUTING.md`).
- V0 Phase 0 implementation (per `Implement.md`): foundation skeleton
  (settings, structured logging, core domain types/events, abstract
  `BrokerAdapter` port, FastAPI `/health`); async SQLAlchemy + Redis
  infrastructure; Alembic schema (`instruments`, `market_sessions`, `ticks`
  hypertable); the Market Data module (quality gate, hot/cold path,
  instrument master, calendar, gap backfiller, `MarketDataService`).
- 40 unit + integration tests for the above; mypy --strict clean.
