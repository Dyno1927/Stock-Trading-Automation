# Contributing Guide

# Stock Trading Automation (STA)

Version: Draft

Status: Foundation Phase

---

# Welcome

Thank you for your interest in contributing to Stock Trading Automation (STA).

Although the project is currently in active personal development, contributions may be welcomed in future releases.

This document describes the expected workflow, engineering standards, and contribution process.

---

# Philosophy

Every contribution should improve the project.

Contributors should prioritize:

* Maintainability
* Simplicity
* Security
* Reliability
* Documentation
* Testing

The goal is not to write more code.

The goal is to build better software.

---

# Before Contributing

Before making any contribution:

* Read the README.
* Read PROJECT.md.
* Read ARCHITECTURE.md.
* Read DEVELOPMENT.md.
* Review existing ADRs.
* Search existing Issues and Pull Requests.

Understanding the existing architecture is more important than writing code quickly.

---

# Branch Strategy

Never commit directly to `main`.

Development should follow the Git workflow.

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

Examples:

```text
feature/market-data
feature/risk-engine
fix/order-validation
docs/update-readme
hotfix/security-patch
```

---

# Development Process

Every feature should follow the same workflow.

1. Create a branch.
2. Implement the feature.
3. Add or update tests.
4. Update documentation.
5. Verify code quality.
6. Open a Pull Request.
7. Review changes.
8. Merge into the appropriate branch.

---

# Coding Standards

Code should be:

* Readable
* Modular
* Consistent
* Testable
* Maintainable

Avoid:

* Duplicate logic
* Hardcoded values
* Large functions
* Unnecessary abstraction
* Premature optimization

---

# Documentation

Documentation is part of every contribution.

When implementation changes, review whether the following should also be updated:

* README.md
* PROJECT.md
* ARCHITECTURE.md
* DEVELOPMENT.md
* ROADMAP.md
* CHANGELOG.md
* RELEASES.md

Documentation should never fall behind implementation.

---

# Testing

Every significant contribution should include appropriate tests.

At minimum:

* Unit tests for new functionality
* Integration tests where applicable

A Pull Request is not considered complete without validating the implemented behavior.

---

# Security

Security should be considered for every change.

Review:

* Input validation
* Authentication
* Authorization
* Secrets management
* Error handling
* Logging

Security issues should be reported privately whenever appropriate.

---

# Pull Requests

A Pull Request should:

* Solve a single problem.
* Be easy to review.
* Include related documentation.
* Include relevant tests.
* Follow existing architecture.

Avoid combining unrelated changes into one Pull Request.

---

# Commit Messages

STA follows Conventional Commits.

Examples:

```text
feat: implement market data provider
fix: resolve order validation issue
docs: update architecture documentation
refactor: simplify strategy engine
test: add broker adapter tests
security: improve token validation
```

Commits should be focused and descriptive.

---

# Code Reviews

Reviews evaluate:

* Correctness
* Architecture
* Readability
* Maintainability
* Testing
* Documentation
* Security
* Performance

Feedback should improve the project, not discourage contributors.

---

# Issues

When opening an Issue, include:

* Description
* Expected behavior
* Actual behavior
* Steps to reproduce
* Environment information
* Relevant logs or screenshots

Well-written issues are significantly easier to resolve.

---

# Feature Requests

Feature requests should include:

* Problem statement
* Proposed solution
* Alternatives considered
* Expected benefits
* Possible drawbacks

Features should align with the project's long-term vision.

---

# Architecture

Contributions should preserve the modular architecture.

Do not introduce:

* Tight coupling
* Circular dependencies
* Hidden side effects
* Unnecessary complexity

If a proposed implementation requires significant architectural changes, discuss it before implementation.

---

# Dependencies

New dependencies should only be introduced when they provide clear long-term value.

Before adding a dependency, consider:

* Maintenance status
* Community adoption
* Security history
* Performance impact
* Existing alternatives

Avoid unnecessary dependencies.

---

# Communication

Engineering discussions should remain:

* Respectful
* Technical
* Evidence-based
* Solution-oriented

Architecture decisions should prioritize objective reasoning over personal preference.

---

# Recognition

Every contributor helps improve STA.

Whether improving documentation, fixing bugs, adding tests, or implementing features, all meaningful contributions are valued.

---

# Guiding Principle

Leave the codebase better than you found it.

Every contribution should improve the project's quality, maintainability, and long-term sustainability.
