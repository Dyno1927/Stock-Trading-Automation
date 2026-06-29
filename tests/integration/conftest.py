"""Integration test fixtures — these tests require `docker compose up -d`
(Postgres+TimescaleDB and Redis) to be running.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from sta.infrastructure.database import dispose_engine, init_engine
from sta.infrastructure.redis_client import dispose_redis, init_redis


@pytest.fixture(autouse=True)
async def _infra() -> AsyncIterator[None]:
    init_engine()
    init_redis()
    yield
    await dispose_redis()
    await dispose_engine()
