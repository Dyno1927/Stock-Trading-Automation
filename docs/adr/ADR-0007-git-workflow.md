# ADR-0007

# Adopt Git Flow

Status

Accepted

Date

2026-06-29

---

# Context

STA aims to become a commercial-grade software project.

A disciplined version control strategy is required to support:

* Stable releases
* Feature development
* Documentation
* Hotfixes
* Future contributors

---

# Decision

STA adopts Git Flow.

Permanent branches:

* main
* develop

Temporary branches:

* feature/*
* fix/*
* hotfix/*
* release/*
* docs/*
* experiment/*

All work must occur on temporary branches before merging into `develop`.

Production releases originate from `release/*` branches and are merged into `main`.

---

# Consequences

## Positive

* Predictable releases
* Clean history
* Easier collaboration
* Stable production branch
* Better release management

## Negative

* Slightly more complex than GitHub Flow
* Requires branch discipline

---

# Alternatives Considered

## GitHub Flow

Rejected because STA requires structured release management.

## Trunk-Based Development

Rejected for the current project phase due to the need for explicit release branches and long-term version planning.

---

# Future Impact

The workflow scales naturally as contributors, automation, and CI/CD pipelines are introduced.
