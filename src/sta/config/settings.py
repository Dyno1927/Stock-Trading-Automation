"""Application settings, read from environment / .env.

See CLAUDE.md rule 4: no secrets in code, everything comes from here.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str
    redis_url: str

    kite_api_key: str = ""
    kite_api_secret: str = ""
    kite_access_token: str = ""

    max_position_size_pct: float = 0.05
    max_portfolio_drawdown_pct: float = 0.10
    max_daily_loss_pct: float = 0.02


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
