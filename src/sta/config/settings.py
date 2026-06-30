"""Application settings, read from environment / .env.

See CLAUDE.md rule 4: no secrets in code, everything comes from here.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# CONFIG: single source of app configuration, read from .env.


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str
    redis_url: str

    # SECURITY: empty-string defaults only — never default these to a real
    # SECURITY: key/secret/token. Real values must come from .env (gitignored), never
    # SECURITY: from this file. See CLAUDE.md rule 4.
    kite_api_key: str = ""
    kite_api_secret: str = ""
    kite_access_token: str = ""

    max_position_size_pct: float = 0.05
    max_portfolio_drawdown_pct: float = 0.10
    max_daily_loss_pct: float = 0.02


@lru_cache
def get_settings() -> Settings:
    # NOTE: mypy sees a missing-argument error here because database_url/
    # NOTE: redis_url have no defaults — but pydantic-settings populates them from
    # NOTE: the environment/.env at runtime, which mypy can't see statically.
    return Settings()  # type: ignore[call-arg]
