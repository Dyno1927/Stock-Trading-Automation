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

Python is the primary backend language.

Supporting languages include:

* Node.js
* C#

Each language is used where it provides clear advantages.

Python remains the core implementation language.

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

Strong candidate.

Retained as a secondary language for desktop tooling.

## Node.js

Excellent for web development.

Retained primarily for frontend tooling and supporting services.

## C++

Rejected for the core project because development speed, maintainability, and ecosystem support are less favorable for the current project stage.

Future performance-critical components may still be implemented in C++ if justified.

---

# Future Impact

Python enables rapid development today while providing a clear path toward future AI and machine learning capabilities.
