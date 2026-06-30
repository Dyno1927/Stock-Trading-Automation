"""FastAPI entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from sta.config.settings import get_settings
from sta.infrastructure.database import dispose_engine, init_engine
from sta.infrastructure.logging_config import configure_logging
from sta.infrastructure.redis_client import dispose_redis, init_redis

# API: FastAPI entrypoint. TODO: only GET /health exists so far.


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    init_engine()
    init_redis()
    try:
        yield
    finally:
        await dispose_redis()
        await dispose_engine()


app = FastAPI(title="STA", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "env": settings.app_env}
