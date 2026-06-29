"""Integration test: hot-path Pub/Sub round-trip + latest-price cache."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sta.core.types import Exchange, Tick
from sta.infrastructure.redis_client import get_redis
from sta.modules.market_data import hot_path


async def test_publish_tick_fanout_and_price_cache() -> None:
    tick = Tick(
        instrument_token=1,
        exchange=Exchange.NSE,
        symbol="HOTPATH",
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal("250.25"),
        last_traded_quantity=5,
        volume_traded=500,
    )
    channel = hot_path.tick_channel(tick.exchange.value, tick.symbol)

    pubsub = get_redis().pubsub()
    await pubsub.subscribe(channel)
    await pubsub.get_message(timeout=1)  # consume the subscribe confirmation

    try:
        await hot_path.publish_tick(tick)

        message = await pubsub.get_message(timeout=2)
        while message is not None and message["type"] != "message":
            message = await pubsub.get_message(timeout=2)

        assert message is not None
        assert tick.symbol in message["data"]
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()

    cache = await get_redis().hgetall(f"price:{tick.exchange.value}:{tick.symbol}")
    assert cache["last_price"] == str(tick.last_price)
