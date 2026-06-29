"""Integration test: cold-path writes are persisted to the ticks hypertable."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, select

from sta.core.types import Exchange, Tick
from sta.infrastructure.database import session_scope
from sta.modules.market_data import cold_path
from sta.modules.market_data.models import TickModel


async def test_write_ticks_persists_to_hypertable() -> None:
    tick = Tick(
        instrument_token=900001,
        exchange=Exchange.NSE,
        symbol="COLDTEST",
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal("100.50"),
        last_traded_quantity=10,
        volume_traded=1000,
    )

    try:
        await cold_path.write_ticks([tick])

        async with session_scope() as session:
            result = await session.execute(
                select(TickModel).where(
                    TickModel.instrument_token == tick.instrument_token,
                    TickModel.time == tick.timestamp,
                )
            )
            row = result.scalar_one()
            assert row.last_price == tick.last_price
            assert row.symbol == tick.symbol
    finally:
        async with session_scope() as session:
            await session.execute(
                delete(TickModel).where(TickModel.instrument_token == tick.instrument_token)
            )
            await session.commit()


async def test_write_ticks_ignores_duplicate_primary_key() -> None:
    tick = Tick(
        instrument_token=900002,
        exchange=Exchange.NSE,
        symbol="COLDTEST2",
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal("50"),
        last_traded_quantity=1,
        volume_traded=1,
    )

    try:
        await cold_path.write_ticks([tick])
        await cold_path.write_ticks([tick])  # same (time, instrument_token) — must not raise

        async with session_scope() as session:
            result = await session.execute(
                select(TickModel).where(TickModel.instrument_token == tick.instrument_token)
            )
            rows = result.scalars().all()
            assert len(rows) == 1
    finally:
        async with session_scope() as session:
            await session.execute(
                delete(TickModel).where(TickModel.instrument_token == tick.instrument_token)
            )
            await session.commit()
