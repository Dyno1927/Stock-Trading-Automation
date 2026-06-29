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



# Changelog

All notable changes to **Stock Trading Automation (STA)** will be documented in this file.

The format is based on **Keep a Changelog**, and this project follows **Semantic Versioning (SemVer)** where applicable.

---

## Versioning

Version format:

MAJOR.MINOR.PATCH

Example:

- MAJOR – Breaking architectural or API changes
- MINOR – New features and significant enhancements
- PATCH – Bug fixes, documentation updates, and small improvements

---

## [Unreleased]

### Added

-

### Changed

-

### Deprecated

-

### Removed

-

### Fixed

-

### Security

-

---

## [0.1.0] - Foundation Release

## Added

### Repository

- Initial repository structure
- Git workflow
- GitHub configuration
- Project documentation
- Development standards

### Documentation

- README.md
- PROJECT.md
- ARCHITECTURE.md
- DEVELOPMENT.md
- SECURITY.md
- CONTRIBUTING.md
- DECISIONS.md
- ROADMAP.md
- CHANGELOG.md
- RELEASES.md

### Development

- Branching strategy
- Conventional Commit guidelines
- Repository standards
- Engineering principles
- Documentation standards

### Infrastructure

- Initial project architecture
- Python project configuration
- Docker foundation
- Development environment

---

## Changed

- Established long-term project architecture.
- Defined project vision and development roadmap.

---

## Security

- Established secure development guidelines.
- Introduced security-first engineering principles.

---

### Future Releases

Subsequent releases should append new versions above previous releases while preserving historical entries.

Example:

```text
[Unreleased]

[0.2.0]

[0.1.1]

[0.1.0]
```

---

### Changelog Guidelines

Every release should document changes using the following categories whenever applicable:

- Added
- Changed
- Deprecated
- Removed
- Fixed
- Security

Each entry should be concise, descriptive, and grouped logically.

---

### Principles

A good changelog should:

- Be human-readable
- Highlight meaningful changes
- Avoid implementation details
- Preserve release history
- Clearly communicate project evolution
