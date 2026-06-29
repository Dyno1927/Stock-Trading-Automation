"""Unit tests for config.settings — values come from the environment, not
hardcoded defaults, for anything resembling a secret or connection string.
"""

from __future__ import annotations

import pytest

from sta.config.settings import Settings


def test_settings_reads_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings(_env_file=None)

    assert settings.app_env == "production"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql+asyncpg://u:p@localhost/db"
    assert settings.redis_url == "redis://localhost:6379/0"


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.delenv("KITE_API_KEY", raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert settings.kite_api_key == ""
    assert settings.max_position_size_pct == 0.05
