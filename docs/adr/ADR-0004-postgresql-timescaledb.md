# ADR-0004

# Adopt PostgreSQL with TimescaleDB

Status

Accepted

Date

2026-06-29

---

# Context

STA processes large amounts of time-series market data.

Requirements include:

* Historical OHLC data
* Tick data
* Portfolio history
* Order history
* Backtesting datasets
* Efficient aggregation
* SQL querying
* ACID compliance

A traditional relational database alone is not optimized for high-volume time-series workloads.

---

# Decision

STA will use:

* PostgreSQL as the primary relational database.
* TimescaleDB as the time-series extension.

TimescaleDB extends PostgreSQL rather than replacing it, allowing the project to use standard SQL while benefiting from optimized time-series storage and querying.

---

# Consequences

## Positive

* Mature and reliable database
* Excellent SQL support
* Native time-series optimizations
* Hypertables
* Compression
* Continuous aggregates
* Strong ecosystem
* Excellent backup tooling

## Negative

* Slight learning curve
* Additional extension management

---

# Alternatives Considered

## SQLite

Rejected because it is unsuitable for production-scale concurrent workloads.

## MongoDB

Rejected because relational consistency and SQL querying are better suited to STA's domain.

## InfluxDB

Rejected because TimescaleDB provides relational capabilities alongside excellent time-series support.

---

# Future Impact

This decision supports future analytics, reporting, backtesting, and SaaS scalability while maintaining a single primary database technology.
