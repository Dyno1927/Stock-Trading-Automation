"""Unit tests for backfiller's pure helpers — gap detection and bar->tick
conversion. The full reconnect flow (DB + broker) is covered in
tests/integration/test_backfiller.py.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sta.core.types import Bar, BarPeriod, Exchange
from sta.modules.market_data.backfiller import _bar_to_tick, detect_gap


def test_detect_gap_none_without_prior_tick() -> None:
    assert detect_gap(None, datetime.now(timezone.utc)) is None


def test_detect_gap_none_within_threshold() -> None:
    now = datetime.now(timezone.utc)
    last = now - timedelta(seconds=10)
    assert detect_gap(last, now, threshold=timedelta(minutes=1)) is None


def test_detect_gap_returns_window_when_exceeded() -> None:
    now = datetime.now(timezone.utc)
    last = now - timedelta(minutes=5)
    gap = detect_gap(last, now, threshold=timedelta(minutes=1))
    assert gap == (last, now)


def test_bar_to_tick_uses_close_as_last_price_and_unsets_close() -> None:
    bar = Bar(
        instrument_token=1,
        exchange=Exchange.NSE,
        symbol="X",
        period=BarPeriod.ONE_MINUTE,
        open_time=datetime.now(timezone.utc) - timedelta(minutes=1),
        close_time=datetime.now(timezone.utc),
        open=Decimal("10"),
        high=Decimal("12"),
        low=Decimal("9"),
        close=Decimal("11"),
        volume=50,
    )
    tick = _bar_to_tick(bar)
    assert tick.last_price == Decimal("11")
    assert tick.timestamp == bar.close_time
    assert tick.close is None
    assert tick.last_traded_quantity == 50
