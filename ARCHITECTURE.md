# Architecture

# Stock Trading Automation (STA)

Version: Draft

Status: Foundation Phase

---

# Overview

Stock Trading Automation (STA) is designed as a modular, event-driven trading platform.

The architecture prioritizes:

- Modularity
- Maintainability
- Scalability
- Reliability
- Security
- Testability

Every major component is designed to evolve independently while communicating through clearly defined interfaces.

---

# High-Level Architecture

```text
                    User Interface
                           │
                           ▼
                     REST API / CLI
                           │
                           ▼
                   Event Bus / Core
        ┌────────────┼────────────┐
        ▼            ▼            ▼
 Market Data     Strategy      Portfolio
        │            │            │
        ▼            ▼            ▼
 Technical       Risk Engine     Orders
 Analysis             │            │
        ▼             ▼            ▼
 Candlestick      Execution     Audit
 Detection          Engine
        │
        ▼
  Paper / Live Trading
        │
        ▼
 Broker Adapter Layer
        │
        ▼
 Supported Brokers
```

---

# Architectural Principles

STA follows several core architectural principles.

## Modular Design

Each module has a single responsibility.

Modules should remain independent whenever possible.

---

## Event-Driven Communication

Modules communicate through events instead of directly depending on one another.

This reduces coupling and improves maintainability.

---

## Broker Abstraction

Trading logic must never depend directly on a broker implementation.

All broker-specific functionality is isolated behind the Broker Adapter interface.

---

## Infrastructure Isolation

Infrastructure concerns such as:

- Database
- Logging
- Redis
- Configuration

must remain separate from business logic.

---

## Configuration-Driven Design

Environment-specific behavior must be controlled through configuration.

Business logic must never contain hardcoded secrets or environment values.

---

# Project Structure

```text
src/
└── sta/
    ├── adapters/
    ├── api/
    ├── config/
    ├── core/
    ├── infrastructure/
    └── modules/
```

---

# Core Layer

The Core layer contains shared domain objects used across the application.

Responsibilities include:

- Shared types
- Events
- Enums
- Common interfaces

The Core layer is the only layer intended to be shared across modules.

---

# Module Layer

Business functionality is organized into independent modules.

Current modules include:

- Market Data
- Strategy
- Signal
- Risk
- Orders
- Execution
- Portfolio
- Audit

Each module owns its own logic.

Modules should not directly import each other.

Communication should occur through the Core layer and events.

---

# API Layer

The API layer exposes STA functionality.

Responsibilities include:

- REST endpoints
- Health checks
- Future authentication
- Future administration APIs

The API layer should never contain business logic.

---

# Adapter Layer

Adapters provide integration with external systems.

Examples include:

- Brokers
- External market data providers
- Future notification services

All adapters should implement well-defined interfaces.

---

# Infrastructure Layer

Infrastructure contains technical services required by the application.

Examples:

- Database
- Logging
- Redis
- Configuration
- Future telemetry

Infrastructure should remain independent of trading logic.

---

# Data Flow

A typical trading workflow follows this sequence.

```text
Market Data
      │
      ▼
Quality Gate
      │
      ▼
Technical Analysis
      │
      ▼
Candlestick Detection
      │
      ▼
Strategy Evaluation
      │
      ▼
Risk Validation
      │
      ▼
Signal Generation
      │
      ▼
Execution Engine
      │
      ▼
Broker Adapter
      │
      ▼
Exchange
```

---

# Quality Gate

Every market tick must pass through a single validation pipeline.

Responsibilities include:

- Validation
- Normalization
- Deduplication
- Timestamp verification
- Data integrity checks

Both live data and replayed historical data must pass through the same pipeline.

---

# Event Flow

Major system components communicate through domain events.

Examples include:

- Tick Ingested
- Bar Closed
- Signal Generated
- Order Submitted
- Order Filled
- Position Updated
- Risk Triggered

The event system reduces direct module dependencies.

---

# Storage

STA separates fast-access storage from long-term persistence.

Redis

- Hot path
- Caching
- Pub/Sub
- Temporary state

PostgreSQL + TimescaleDB

- Historical market data
- Orders
- Portfolio
- Audit records
- Long-term persistence

---

# Time Standard

All timestamps are stored in UTC.

Local time zones are presentation concerns only.

---

# Configuration

Configuration is managed through environment variables.

Examples include:

- Database
- Redis
- API keys
- Risk limits
- Environment

Configuration must never be hardcoded.

---

# Logging

Logging is centralized.

Requirements:

- Structured logging
- JSON format
- Configurable log levels
- No use of print()

---

# Security Principles

The architecture follows several security principles.

- Least privilege
- Secure defaults
- Secret isolation
- Input validation
- Authentication before authorization
- Auditability

Security considerations are incorporated throughout the architecture rather than added afterward.

---

# Testing Strategy

Testing exists at multiple levels.

Unit Tests

- Individual components
- Fast execution
- Mock external dependencies

Integration Tests

- Database
- Redis
- Broker interfaces
- API

Future

- End-to-end testing
- Performance testing
- Load testing

---

# Scalability

The architecture is designed to scale horizontally where appropriate.

Future improvements may include:

- Distributed workers
- Message queues
- Cloud deployment
- Multi-user SaaS support
- Multiple broker integrations

These capabilities should not require a major architectural redesign.

---

# Architectural Decisions

Significant architectural decisions are documented separately.

See:

docs/adr/

Every major architectural change should be accompanied by a new Architecture Decision Record (ADR).

---

# Design Philosophy

STA favors:

- Simplicity over unnecessary complexity
- Clear interfaces over implicit behavior
- Composition over duplication
- Long-term maintainability over short-term convenience
- Incremental evolution over large rewrites

---

# Architecture Goals

The architecture should enable:

- Reliable automated trading
- Safe execution
- Modular development
- Independent testing
- Easy maintenance
- Future commercial expansion

Every new feature should strengthen the architecture rather than weaken it.
