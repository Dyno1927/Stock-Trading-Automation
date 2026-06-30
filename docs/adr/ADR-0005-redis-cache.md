# ADR-0005

# Adopt Redis as the Primary Cache

Status

Accepted

Date

2026-06-29

---

# Context

STA requires extremely fast access to transient data, including:

* Active market prices
* Session state
* Temporary calculations
* Event messaging
* Rate limiting
* Job queues (future)

Using PostgreSQL for all operations would introduce unnecessary latency.

---

# Decision

Redis will serve as the primary in-memory data store.

Redis will be used for:

* Caching (e.g. latest price per instrument, `price:{exchange}:{symbol}`)
* The event bus — **Redis Streams** for durable paths (signals, orders, audit)
  and **Pub/Sub** for disposable live-tick fan-out only (the hot path)
* Temporary state
* Session storage
* Rate limiting
* Distributed locking (future)

Redis is **not** considered the system of record.

Persistent business data remains in PostgreSQL.

---

# Consequences

## Positive

* Extremely low latency
* Mature ecosystem
* Excellent Python support
* Supports future horizontal scaling
* Simple deployment

## Negative

* Additional infrastructure component
* Memory-based storage
* Requires monitoring

---

# Alternatives Considered

### Memcached

Rejected because Redis offers significantly more functionality.

### PostgreSQL Only

Rejected because caching and messaging workloads would unnecessarily burden the database.

---

# Future Impact

Redis prepares STA for future distributed workers, background jobs, and scalable cloud deployments.
