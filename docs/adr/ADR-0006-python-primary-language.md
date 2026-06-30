# ADR-0006

# Adopt Python as the Primary Backend Language

Status

Accepted

Date

2026-06-29

---

# Context

STA requires:

* Technical analysis
* Data processing
* Market analysis
* Machine learning (future)
* Automation
* Scientific computing
* API development

Several programming languages were evaluated.

---

# Decision

Python is the primary — and only — backend language (all modules, the API, and
WebSockets run on a single Python runtime).

Other languages are limited to clearly separate roles:

* SQL — the database layer (PostgreSQL + TimescaleDB)
* TypeScript — planned for the future dashboard frontend; deferred until a
  Confirmation-mode UI is needed

No second backend runtime is introduced. Python remains the core implementation
language.

---

# Consequences

## Positive

* Largest financial ecosystem
* Excellent AI ecosystem
* Fast development
* Rich scientific libraries
* Large community
* Strong testing tools

## Negative

* Lower raw performance than C++
* Global Interpreter Lock (GIL)
* Higher memory usage

---

# Alternatives Considered

## C#

Rejected. It has no defined role in STA; network latency dominates execution
timing (so a faster runtime buys little), and adding it would introduce a
cross-runtime seam.

## Node.js

Not a backend language. The frontend will use TypeScript (deferred until the
Confirmation-mode UI is needed); Node.js appears only as the tooling runtime for
that future dashboard, never as an application language.

## C++

Rejected for the core project because development speed, maintainability, and ecosystem support are less favorable for the current project stage.

Future performance-critical components may still be implemented in C++ if justified.

---

# Future Impact

Python enables rapid development today while providing a clear path toward future AI and machine learning capabilities.
