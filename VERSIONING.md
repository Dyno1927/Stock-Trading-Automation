# Versioning Policy

# Stock Trading Automation (STA)

Version: Draft

Status: Active

---

# Purpose

This document defines the versioning strategy used throughout the Stock Trading Automation (STA) project.

Consistent versioning improves release management, deployment, compatibility, and project communication.

STA follows **Semantic Versioning (SemVer 2.0.0)** with additional project-specific release conventions.

---

# Semantic Versioning

Version numbers follow the format:

```text
MAJOR.MINOR.PATCH
```

Example:

```text
1.4.2
```

---

# MAJOR Version

Increment the **MAJOR** version when introducing breaking changes.

Examples:

* Major architecture redesign
* Breaking API changes
* Database incompatibilities
* Large-scale refactoring requiring migration

Examples:

```text
1.0.0 → 2.0.0
```

---

# MINOR Version

Increment the **MINOR** version when introducing new functionality while remaining backwards compatible.

Examples:

* New modules
* New indicators
* New broker support
* New trading strategies
* Dashboard improvements

Examples:

```text
1.3.0 → 1.4.0
```

---

# PATCH Version

Increment the **PATCH** version for maintenance releases.

Examples:

* Bug fixes
* Documentation improvements
* Performance optimizations
* Security patches
* Minor UI fixes

Examples:

```text
1.4.0 → 1.4.1
```

---

# Pre-Release Versions

During development the following identifiers may be used.

Alpha

```text
1.0.0-alpha.1
```

Used for early development.

---

Beta

```text
1.0.0-beta.1
```

Feature complete but still under testing.

---

Release Candidate

```text
1.0.0-rc.1
```

Expected to become the next stable release unless significant issues are discovered.

---

# Initial Project Roadmap

Expected progression:

```text
0.1.0
Foundation

↓

0.2.0
Market Data

↓

0.3.0
Technical Analysis

↓

0.4.0
Candlestick Detection

↓

0.5.0
Strategy Engine

↓

0.6.0
Risk Management

↓

0.7.0
Backtesting

↓

0.8.0
Paper Trading

↓

0.9.0
Automation

↓

1.0.0
Stable Personal Trading Platform
```

Version numbers represent meaningful engineering milestones rather than arbitrary dates.

---

# Git Tags

Every release should receive a Git tag.

Examples:

```text
v0.1.0
v0.2.0
v0.5.3
v1.0.0
```

Tags should always correspond to released versions.

---

# Release Branches

Release branches follow:

```text
release/v0.2.0
```

After release:

* Merge into `main`
* Tag release
* Merge back into `develop`
* Delete release branch

---

# Branch Version Policy

Permanent branches:

| Branch    | Purpose                      |
| --------- | ---------------------------- |
| `main`    | Stable production-ready code |
| `develop` | Active development           |

Temporary branches:

```text
feature/*
fix/*
hotfix/*
release/*
docs/*
experiment/*
```

Temporary branches should be deleted after merging.

---

# Changelog

Every released version must update:

* CHANGELOG.md
* RELEASES.md

No release is considered complete until both documents are updated.

---

# Backward Compatibility

Whenever practical:

* Preserve APIs
* Preserve configuration
* Preserve database compatibility

Breaking compatibility should only occur during major releases.

---

# Release Checklist

Before publishing:

* Architecture reviewed
* Tests passing
* Documentation updated
* CHANGELOG updated
* RELEASES updated
* Version numbers updated
* Git tag created
* Release branch merged
* Security review completed

---

# Long-Term Philosophy

Version numbers should communicate engineering progress rather than marketing.

Releases should be:

* Stable
* Well tested
* Fully documented
* Reproducible

Quality takes precedence over release frequency.

---

# Guiding Principle

Release software when it is ready—not simply because a schedule demands it.
