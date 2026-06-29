"""Unit tests for core.types — UTC enforcement, idempotency key on Order."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from sta.core.types import Direction, Exchange, Order, OrderType, Tick


def test_tick_accepts_utc_timestamp() -> None:
    tick = Tick(
        instrument_token=1,
        exchange=Exchange.NSE,
        symbol="X",
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal("10"),
    )
    assert tick.timestamp.tzinfo is not None


def test_tick_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError):
        Tick(
            instrument_token=1,
            exchange=Exchange.NSE,
            symbol="X",
            timestamp=datetime.now(),  # naive
            last_price=Decimal("10"),
        )


def test_tick_rejects_non_utc_offset() -> None:
    ist = timezone(timedelta(hours=5, minutes=30))
    with pytest.raises(ValidationError):
        Tick(
            instrument_token=1,
            exchange=Exchange.NSE,
            symbol="X",
            timestamp=datetime.now(ist),
            last_price=Decimal("10"),
        )


def test_order_carries_idempotency_key_and_utc_timestamps() -> None:
    order = Order(
        idempotency_key="abc-123",
        instrument_token=1,
        exchange=Exchange.NSE,
        symbol="X",
        direction=Direction.BUY,
        order_type=OrderType.MARKET,
        quantity=10,
    )
    assert order.idempotency_key == "abc-123"
    assert order.created_at.tzinfo is not None
    assert order.updated_at.tzinfo is not None
