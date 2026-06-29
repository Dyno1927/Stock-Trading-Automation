"""Hot path: fan out validated ticks via Redis Pub/Sub and refresh the
latest-price cache. Disposable — see CLAUDE.md ADR 006.
"""

from __future__ import annotations

import logging

from sta.core.types import Tick
from sta.infrastructure.redis_client import publish, set_latest_price

logger = logging.getLogger(__name__)


def tick_channel(exchange: str, symbol: str) -> str:
    """Pub/Sub channel naming convention per architecture decision A4."""
    return f"ticks:{exchange}:{symbol}"


async def publish_tick(tick: Tick) -> None:
    channel = tick_channel(tick.exchange.value, tick.symbol)
    await publish(channel, tick.model_dump_json())
    await set_latest_price(
        tick.exchange.value,
        tick.symbol,
        {
            "last_price": str(tick.last_price),
            "timestamp": tick.timestamp.isoformat(),
        },
    )
