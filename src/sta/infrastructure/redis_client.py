"""Async Redis client + helpers.

Streams = durable paths (signals, orders, audit). Pub/Sub = disposable hot
path (live tick fan-out) — see CLAUDE.md ADR 006.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import cast

import redis.asyncio as redis
from redis.exceptions import ResponseError

from sta.config.settings import get_settings

# NOTE: redis-py's type stubs return loose Union types (bytes | str | int | ...)
# NOTE: for most commands. The `# type: ignore[...]` and `cast(...)` calls below are
# NOTE: deliberate boundary-narrowing to our actual str-keyed/str-valued usage
# NOTE: (decode_responses=True), not bugs being silenced.

_client: redis.Redis | None = None


def init_redis() -> None:
    """Create the Redis client. Idempotent. Call once at startup."""
    global _client
    if _client is not None:
        return
    settings = get_settings()
    _client = redis.from_url(settings.redis_url, decode_responses=True)


async def dispose_redis() -> None:
    """Close the Redis client. Call once at shutdown."""
    global _client
    if _client is not None:
        await _client.aclose()
    _client = None


def get_redis() -> redis.Redis:
    if _client is None:
        raise RuntimeError("Redis client not initialized; call init_redis() first")
    return _client


# EVENT: Streams (durable: signals, orders, audit) -------------------------


async def stream_add(stream: str, fields: Mapping[str, str]) -> str:
    return str(await get_redis().xadd(stream, dict(fields)))  # type: ignore[arg-type]


async def ensure_consumer_group(stream: str, group: str) -> None:
    try:
        await get_redis().xgroup_create(stream, group, id="0", mkstream=True)
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


async def stream_read_group(
    stream: str, group: str, consumer: str, count: int = 10, block_ms: int = 1000
) -> list[tuple[str, list[tuple[str, dict[str, str]]]]]:
    raw = await get_redis().xreadgroup(group, consumer, {stream: ">"}, count=count, block=block_ms)
    result = cast("list[tuple[str, list[tuple[str, dict[str, str]]]]] | None", raw)
    return result or []


async def stream_ack(stream: str, group: str, *message_ids: str) -> int:
    return int(await get_redis().xack(stream, group, *message_ids))


# MARKET: Pub/Sub (disposable: hot-path ticks) ------------------------------


async def publish(channel: str, message: str) -> int:
    return int(await get_redis().publish(channel, message))


async def subscribe(channel: str) -> AsyncIterator[str]:
    """Subscribe to a channel and yield each message payload as it arrives."""
    pubsub = get_redis().pubsub()
    await pubsub.subscribe(channel)
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()  # type: ignore[no-untyped-call]


# CACHE: latest-price cache -------------------------------------------------


def price_cache_key(exchange: str, symbol: str) -> str:
    return f"price:{exchange}:{symbol}"


async def set_latest_price(exchange: str, symbol: str, fields: Mapping[str, str]) -> None:
    await get_redis().hset(price_cache_key(exchange, symbol), mapping=dict(fields))  # type: ignore[arg-type]


async def get_latest_price(exchange: str, symbol: str) -> dict[str, str]:
    raw = await get_redis().hgetall(price_cache_key(exchange, symbol))
    return cast("dict[str, str]", raw)
