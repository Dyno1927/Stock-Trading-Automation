# Stock Trading Automation (STA)

<div align="center">

![Status](https://img.shields.io/badge/Status-Foundation-blue)
![Version](https://img.shields.io/badge/Version-v0.1.0--draft-orange)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![License](https://img.shields.io/badge/License-Proprietary-red)

**A modular, event-driven stock trading automation platform designed for long-term reliability, maintainability, and intelligent market analysis.**

*Currently under active development.*

</div>

---

# Overview

Stock Trading Automation (STA) is a long-term engineering project focused on building a professional-grade automated trading platform.

Unlike many hobby trading bots, STA is being designed from the beginning as a scalable software system capable of evolving into a commercial SaaS platform while remaining suitable for personal automated trading.

The project follows an architecture-first development philosophy where maintainability, security, testing, and modularity take priority over rapid feature implementation.

---

# Vision

The long-term vision of STA is to provide a reliable and extensible platform capable of:

- Automated trading
- Confirmation-based trading
- Paper trading
- Technical analysis
- Candlestick pattern recognition
- Portfolio management
- Risk management
- Strategy execution
- Backtesting
- Market monitoring
- Multi-broker support
- AI-assisted market analysis (future)

STA is being developed incrementally, with every feature validated before progressing to live trading.

---

# Current Status

Current Phase:

> **Phase 0 — Foundation**

Completed:

- Repository architecture, development standards, and documentation framework
- Git/GitHub workflow and project structure
- V0 Phase 0 implementation — core infrastructure, event system, database layer
  (PostgreSQL + TimescaleDB via Alembic), Redis integration, and the Market Data
  Engine (quality gate, hot/cold paths, instrument master, calendar, backfiller).
  40 unit + integration tests passing; `mypy --strict` clean.

Currently In Progress / Next:

- Strategy Engine architecture design — the first trading-logic module

---

# Core Principles

STA follows several engineering principles throughout development.

- Architecture before implementation
- Security by design
- Modular development
- Event-driven communication
- Extensive documentation
- Testable components
- Long-term maintainability
- Production-oriented engineering
- Incremental feature delivery

---

# Planned Features

## Market Data

- Live market data
- Historical market data
- Market data validation
- Market session management
- Instrument management

---

## Technical Analysis

- Moving averages
- RSI
- MACD
- Bollinger Bands
- ATR
- VWAP
- Trend analysis
- Support & resistance

---

## Candlestick Analysis

- Doji
- Hammer
- Engulfing
- Morning Star
- Evening Star
- Harami
- Shooting Star
- Marubozu
- Three White Soldiers
- Three Black Crows
- Additional pattern recognition

---

## Trading Modes

### Confirmation Mode

STA generates trading opportunities and waits for user confirmation before placing orders.

### Fully Automated Mode

STA analyzes the market, validates risk, and executes trades automatically according to configured strategies.

---

## Risk Profiles

Two configurable operating profiles are planned.

### Conservative

Designed for consistent returns while minimizing risk.

### Aggressive

Designed to maximize opportunities while accepting increased market risk.

---

## Trading Workflow

```text
Market Data
      │
      ▼
Technical Analysis
      │
      ▼
Candlestick Detection
      │
      ▼
Strategy Engine
      │
      ▼
Risk Engine
      │
      ▼
Paper Trading
      │
      ▼
Broker Integration
      │
      ▼
Live Trading
```

---

# Supported Markets

Initial focus:

- Indian Stock Market

Planned expansion:

- Global Markets

---

# Broker Support

First adapter:

- Zerodha Kite Connect — the most mature retail trading API in India. Order and
  account APIs are free; the live + historical market-data feed (₹500/month) is
  deferred until the project generates revenue. Until then, development and paper
  trading run on free historical/replay data through the same quality gate.

Additional brokers (e.g. Groww, Upstox, Angel One) plug in through the broker
abstraction layer.

---

# Technology Stack

## Primary Languages

- Python (backend — all modules, API, WebSockets)
- SQL (PostgreSQL + TimescaleDB)
- TypeScript (planned, for the future dashboard — deferred)

---

## Core Technologies

- FastAPI
- PostgreSQL
- TimescaleDB
- Redis
- Docker
- Alembic
- SQLAlchemy
- Pydantic
- GitHub Actions

Additional technologies will be introduced as the project evolves.

---

# Repository Structure

```text
src/
docs/
tests/
scripts/
assets/
research/
.github/
```

---

# Documentation

Project documentation is maintained alongside implementation.

Key documents include:

- README.md
- PROJECT.md
- ROADMAP.md
- ARCHITECTURE.md
- DEVELOPMENT.md
- SECURITY.md
- DECISIONS.md
- CONTRIBUTING.md
- CHANGELOG.md
- RELEASES.md

---

# Development Philosophy

Features are considered complete only when:

- Implementation is finished
- Tests pass
- Documentation is updated
- Architecture remains consistent
- Security considerations have been reviewed

---

# Project Roadmap

Development progresses through structured phases.

1. Foundation
2. Market Data
3. Technical Analysis
4. Candlestick Detection
5. Strategy Engine
6. Risk Management
7. Backtesting
8. Paper Trading
9. Automation
10. Broker Integration
11. Portfolio Management
12. Dashboard
13. Notifications
14. AI Integration
15. SaaS Preparation
16. Production Release

See **ROADMAP.md** for additional details.

---

# License

This project is proprietary — Copyright (c) 2026 Dyno1927, All Rights Reserved.
The source is publicly viewable for transparency and portfolio purposes only; no
use, copying, modification, or distribution is permitted without prior written
permission. STA is personal software today and is intended to become a
commercial SaaS platform in the future.

See the LICENSE file for the full terms.

---

# Disclaimer

STA is educational and experimental software currently under active development.

Trading financial markets involves substantial risk. Past performance does not guarantee future results. Users are responsible for understanding the risks associated with automated trading before using STA with real capital.

Live trading functionality will only be introduced after extensive testing through historical analysis, paper trading, and risk validation.

---

<div align="center">

**Stock Trading Automation (STA)**

*Architecture First • Security First • Documentation First*

</div>
