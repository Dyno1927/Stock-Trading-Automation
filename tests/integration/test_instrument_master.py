"""Integration test: refresh_instruments upserts the broker's instrument
list into the `instruments` table.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from decimal import Decimal

from sqlalchemy import delete, select

from sta.adapters.broker.base import BrokerAdapter
from sta.core.types import (
    Bar,
    BarPeriod,
    Exchange,
    Instrument,
    Order,
    OrderStatus,
    Position,
    Tick,
)
from sta.infrastructure.database import session_scope
from sta.modules.market_data.instrument_master import refresh_instruments
from sta.modules.market_data.models import InstrumentModel


class FakeBrokerAdapter(BrokerAdapter):
    def __init__(self, instruments: list[Instrument]) -> None:
        self._instruments = instruments

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def get_instruments(self, exchange: Exchange | None = None) -> list[Instrument]:
        return self._instruments

    async def stream_ticks(self, instrument_tokens: list[int]) -> AsyncIterator[Tick]:
        raise NotImplementedError
        yield  # pragma: no cover

    async def get_historical_bars(
        self,
        instrument_token: int,
        exchange: Exchange,
        period: BarPeriod,
        start: datetime,
        end: datetime,
    ) -> list[Bar]:
        return []

    async def submit_order(self, order: Order) -> Order:
        raise NotImplementedError

    async def cancel_order(self, broker_order_id: str) -> OrderStatus:
        raise NotImplementedError

    async def get_order_status(self, broker_order_id: str) -> OrderStatus:
        raise NotImplementedError

    async def get_positions(self) -> list[Position]:
        return []


async def test_refresh_instruments_upserts_and_updates() -> None:
    token = 999201
    first = Instrument(
        instrument_token=token,
        exchange=Exchange.NSE,
        symbol="IMTEST",
        name="IM Test Co",
        instrument_type="EQ",
        tick_size=Decimal("0.05"),
        lot_size=1,
    )
    broker = FakeBrokerAdapter([first])

    try:
        count = await refresh_instruments(broker)
        assert count == 1

        async with session_scope() as session:
            row = await session.get(InstrumentModel, token)
            assert row is not None
            assert row.name == "IM Test Co"

        updated = first.model_copy(update={"name": "IM Test Co Renamed"})
        broker_updated = FakeBrokerAdapter([updated])
        await refresh_instruments(broker_updated)

        async with session_scope() as session:
            result = await session.execute(
                select(InstrumentModel).where(InstrumentModel.instrument_token == token)
            )
            rows = result.scalars().all()
            assert len(rows) == 1
            assert rows[0].name == "IM Test Co Renamed"
    finally:
        async with session_scope() as session:
            await session.execute(
                delete(InstrumentModel).where(InstrumentModel.instrument_token == token)
            )
            await session.commit()
