# Git & GitHub Workflow

The STA project follows a structured Git workflow inspired by Git Flow, optimized
for long-term maintainability and eventual commercial SaaS development.

Git history should remain clean, readable, and meaningful.

---

## Permanent Branches

### main

- Production-ready code only. Always stable and deployable. Protected branch.
- Never commit directly. Never develop directly.
- Only merge tested release branches.
- Every merge should represent a stable milestone.

### develop

- Primary development branch.
- All feature branches originate from `develop`.
- All completed work merges back into `develop`.
- `develop` should remain stable enough for daily development.

---

## Temporary Branches

Temporary branches should be deleted immediately after merging.

### Feature branches — `feature/<feature-name>`

Examples: `feature/market-data-engine`, `feature/candlestick-detection`,
`feature/technical-indicators`, `feature/strategy-engine`,
`feature/risk-management`, `feature/backtesting`, `feature/paper-trading`,
`feature/dashboard`, `feature/postgresql`, `feature/docker`,
`feature/github-actions`.

- One feature per branch.
- Do not mix unrelated work.
- Merge into `develop`.

### Bug fixes — `fix/<issue>`

Examples: `fix/login`, `fix/database-timeout`, `fix/order-validation`,
`fix/websocket-reconnect`.

Small, non-critical bug fixes.

### Hotfixes — `hotfix/<issue>`

Examples: `hotfix/security`, `hotfix/broker-api`, `hotfix/order-execution`.

Critical production fixes.

```
main → hotfix → main → develop
```

### Experimental branches — `experiment/<topic>`

Examples: `experiment/ai-engine`, `experiment/ml-model`,
`experiment/new-strategy`, `experiment/high-frequency`.

Research and prototypes. Must never be merged directly into `main`.

### Documentation branches (optional) — `docs/<topic>`

Examples: `docs/readme`, `docs/api`, `docs/security`, `docs/architecture`.

### Release branches — `release/vX.Y.Z`

Examples: `release/v0.1.0`, `release/v0.2.0`, `release/v1.0.0`.

Final testing before merging into `main`. Only bug fixes, documentation,
version updates, and release preparation are allowed — no new features.

---

## Branch Workflow

```
feature/*  →  develop  →  release/*  →  main
```

Hotfixes bypass `develop` initially and merge back afterward.

---

## Branch Protection

Protect: `main` (eventually `develop` too).

Requirements: pull request required, no force pushes, no direct commits,
passing tests (once CI is implemented).

---

## Commit Convention

[Conventional Commits](https://www.conventionalcommits.org/).

```
feat: add candlestick detection engine
fix: resolve websocket reconnect issue
docs: update architecture diagram
refactor: simplify broker abstraction
test: add strategy engine unit tests
perf: optimize indicator calculations
security: validate JWT refresh flow
build: configure docker compose
ci: add github actions workflow
chore: update dependencies
```

---

## Pull Request Workflow

```
Feature Branch → Implementation → Testing → Documentation Update
→ Pull Request → Review → Merge into develop → Delete Feature Branch
```

---

## GitHub Labels

**Priority:** `priority: critical`, `priority: high`, `priority: medium`, `priority: low`

**Type:** `feature`, `bug`, `enhancement`, `documentation`, `refactor`, `security`,
`performance`, `research`, `testing`, `ci/cd`, `dependencies`

**Area:** `frontend`, `backend`, `python-engine`, `database`, `broker`,
`dashboard`, `strategy-engine`, `risk-engine`, `paper-trading`, `backtesting`,
`deployment`, `docs`

**Status:** `blocked`, `ready`, `in-progress`, `review`, `testing`, `completed`

---

## GitHub Project Workflow

```
Ideas → Research → Architecture → Ready → In Progress → Testing → Documentation → Done
```

Every feature should move through these stages before being considered complete.

---

## GitHub Milestones

Phase 0 — Foundation
Phase 1 — Market Data Engine
Phase 2 — Technical Analysis
Phase 3 — Candlestick Detection
Phase 4 — Strategy Engine
Phase 5 — Risk Management
Phase 6 — Backtesting
Phase 7 — Paper Trading
Phase 8 — Dashboard
Phase 9 — Broker Integration
Phase 10 — Personal Live Trading

---

## Repository Philosophy

- `main` represents production-quality code.
- `develop` represents the current stable development state.
- All work should be traceable through Issues, Pull Requests, and meaningful commits.
- Documentation is considered part of the implementation.
- A feature is not complete until:
  - Implementation is finished.
  - Tests pass.
  - Documentation is updated.
  - Relevant ADRs are created or updated.
  - `CHANGELOG.md` is updated.
  - `RELEASES.md` is updated (for milestones).
  - `ROADMAP.md` is updated if project direction changes.

Maintain a clean Git history by preferring small, focused commits and deleting
merged temporary branches.
