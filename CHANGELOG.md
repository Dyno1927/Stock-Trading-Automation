# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-06-28

### Added

- Initial project scaffold: modular monolith structure, eight domain module
  stubs, FastAPI entrypoint, Docker Compose infra (PostgreSQL + TimescaleDB,
  Redis), config/settings, logging setup.
- Git & GitHub workflow conventions (`CONTRIBUTING.md`).
- GitHub repo configuration: labels, milestones (Phase 0-10), branch
  protection on `main`.
- Proprietary `LICENSE` (all rights reserved).

### Fixed

- Consolidated duplicate `env.example` / `.env.example` into `.env.example`.
