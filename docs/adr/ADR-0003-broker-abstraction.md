# ADR-0003

# Broker Abstraction Layer

Status

Accepted

Date

2026-06-29

---

# Context

STA is expected to support multiple brokers.

Initial target:

* Zerodha Kite Connect — the most mature retail trading API in India. Order and
  account APIs are free; the market-data feed (₹500/month) is deferred until the
  project generates revenue, with development running on free historical/replay
  data through the Market Data quality gate in the meantime.

Future:

* Groww
* Upstox
* Angel One
* Interactive Brokers
* Alpaca

Directly integrating broker APIs into trading logic would tightly couple the application to specific providers.

---

# Decision

Introduce a Broker Adapter Layer.

The trading engine communicates only with broker interfaces.

Each broker implements the same contract.

Example

Trading Engine

↓

Broker Interface

↓

Zerodha Adapter (first implementation)

↓

Broker API

---

# Consequences

Positive

* Broker independence
* Easier testing
* Easier expansion
* Cleaner architecture

Negative

* Additional abstraction layer

---

# Alternatives Considered

Direct broker integration.

Rejected because replacing or adding brokers would require widespread code changes.

---

# Future Impact

Future broker integrations can be implemented with minimal impact on the trading engine.
