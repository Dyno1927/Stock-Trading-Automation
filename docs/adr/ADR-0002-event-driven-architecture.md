# ADR-0002

# Adopt Event-Driven Communication

Status

Accepted

Date

2026-06-29

---

# Context

Trading systems generate numerous independent events.

Examples include:

* New market data
* Pattern detected
* Strategy signal
* Risk alert
* Order executed
* Position closed

Direct communication between every module would create unnecessary dependencies.

---

# Decision

Modules communicate primarily through domain events.

Examples:

TickReceived

↓

IndicatorsCalculated

↓

SignalGenerated

↓

RiskValidated

↓

OrderSubmitted

↓

OrderFilled

---

# Consequences

Positive

* Loose coupling
* Easier extensibility
* Better scalability
* Independent modules

Negative

* Event tracing becomes more complex.
* Requires disciplined event naming.

---

# Alternatives Considered

Direct service calls

Rejected due to increasing coupling as the project scales.

---

# Future Impact

The event system supports future distributed processing and SaaS deployment.
