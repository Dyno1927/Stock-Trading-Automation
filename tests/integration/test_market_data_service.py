"""Integration test: MarketDataService.process_tick — accepted ticks land on
both the hot path (cache) and cold path (DB); rejected ticks land on neither.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import delete

from sta.core.types import Exchange, Tick
from sta.infrastructure.database import session_scope
from sta.infrastructure.redis_client import get_redis
from sta.modules.market_data.models import TickModel
from sta.modules.market_data.service import MarketDataService


async def test_process_tick_accepted_persists_and_publishes() -> None:
    service = MarketDataService()
    tick = Tick(
        instrument_token=999001,
        exchange=Exchange.NSE,
        symbol="SVCTEST",
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal("500.00"),
        last_traded_quantity=1,
        volume_traded=1,
    )

    try:
        result = await service.process_tick(tick)
        assert result is not None

        async with session_scope() as session:
            row = await session.get(TickModel, (tick.timestamp, tick.instrument_token))
            assert row is not None

        cached = await get_redis().hgetall(f"price:{tick.exchange.value}:{tick.symbol}")
        assert cached["last_price"] == str(tick.last_price)
    finally:
        async with session_scope() as session:
            await session.execute(
                delete(TickModel).where(TickModel.instrument_token == tick.instrument_token)
            )
            await session.commit()


async def test_process_tick_rejected_not_persisted() -> None:
    service = MarketDataService()
    tick = Tick(
        instrument_token=999002,
        exchange=Exchange.NSE,
        symbol="SVCTEST2",
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal("0"),  # invalid: price <= 0
        last_traded_quantity=1,
        volume_traded=1,
    )

    result = await service.process_tick(tick)
    assert result is None

    async with session_scope() as session:
        row = await session.get(TickModel, (tick.timestamp, tick.instrument_token))
        assert row is None
