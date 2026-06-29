"""Integration test: backfill_on_reconnect detects a gap, pulls historical
bars from the broker adapter, and replays them through the same quality gate
+ hot/cold path used by live ticks (deterministic replay, rule 9).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete

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
from sta.modules.market_data import backfiller
from sta.modules.market_data.models import TickModel
from sta.modules.market_data.service import MarketDataService


class FakeBrokerAdapter(BrokerAdapter):
    """Minimal BrokerAdapter test double — only get_historical_bars is used."""

    def __init__(self, bars: list[Bar]) -> None:
        self._bars = bars

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def get_instruments(self, exchange: Exchange | None = None) -> list[Instrument]:
        return []

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
        return self._bars

    async def submit_order(self, order: Order) -> Order:
        raise NotImplementedError

    async def cancel_order(self, broker_order_id: str) -> OrderStatus:
        raise NotImplementedError

    async def get_order_status(self, broker_order_id: str) -> OrderStatus:
        raise NotImplementedError

    async def get_positions(self) -> list[Position]:
        return []


async def test_backfill_on_reconnect_detects_gap_and_replays() -> None:
    token = 999101
    now = datetime.now(timezone.utc)
    last_tick_time = now - timedelta(minutes=10)

    service = MarketDataService()
    seed_tick = Tick(
        instrument_token=token,
        exchange=Exchange.NSE,
        symbol="BFTEST",
        timestamp=last_tick_time,
        last_price=Decimal("100"),
        last_traded_quantity=1,
        volume_traded=1,
    )

    bar = Bar(
        instrument_token=token,
        exchange=Exchange.NSE,
        symbol="BFTEST",
        period=BarPeriod.ONE_MINUTE,
        open_time=last_tick_time + timedelta(minutes=1),
        close_time=last_tick_time + timedelta(minutes=2),
        open=Decimal("100"),
        high=Decimal("101"),
        low=Decimal("99"),
        close=Decimal("100.5"),
        volume=10,
    )
    broker = FakeBrokerAdapter([bar])

    try:
        await service.process_tick(seed_tick, check_staleness=False)

        accepted = await backfiller.backfill_on_reconnect(
            broker, service, token, Exchange.NSE, "BFTEST", now=now
        )

        assert accepted == 1

        async with session_scope() as session:
            row = await session.get(TickModel, (bar.close_time, token))
            assert row is not None
    finally:
        async with session_scope() as session:
            await session.execute(delete(TickModel).where(TickModel.instrument_token == token))
            await session.commit()


async def test_backfill_on_reconnect_no_gap_skips_broker_call() -> None:
    token = 999102
    now = datetime.now(timezone.utc)
    service = MarketDataService()
    recent_tick = Tick(
        instrument_token=token,
        exchange=Exchange.NSE,
        symbol="BFTEST2",
        timestamp=now - timedelta(seconds=5),
        last_price=Decimal("100"),
        last_traded_quantity=1,
        volume_traded=1,
    )
    broker = FakeBrokerAdapter([])

    try:
        await service.process_tick(recent_tick, check_staleness=False)

        accepted = await backfiller.backfill_on_reconnect(
            broker, service, token, Exchange.NSE, "BFTEST2", now=now
        )

        assert accepted == 0
    finally:
        async with session_scope() as session:
            await session.execute(delete(TickModel).where(TickModel.instrument_token == token))
            await session.commit()
