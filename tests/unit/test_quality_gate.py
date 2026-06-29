"""Unit tests for the Market Data quality gate — each rejection rule, dedup,
and replay (staleness-skipped) behavior.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pytest

from sta.core.types import Exchange, Tick
from sta.modules.market_data.quality_gate import QualityGate, TickRejected


def _tick(**overrides: Any) -> Tick:
    defaults: dict[str, Any] = dict(
        instrument_token=1,
        exchange=Exchange.NSE,
        symbol="TEST",
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal("100"),
        last_traded_quantity=10,
        volume_traded=100,
    )
    defaults.update(overrides)
    return Tick(**defaults)


def test_accepts_valid_tick() -> None:
    gate = QualityGate()
    tick = _tick()
    assert gate.validate(tick) is tick


@pytest.mark.parametrize("price", [Decimal("0"), Decimal("-5")])
def test_rejects_non_positive_price(price: Decimal) -> None:
    gate = QualityGate()
    with pytest.raises(TickRejected) as exc_info:
        gate.validate(_tick(last_price=price))
    assert exc_info.value.reason == "price_non_positive"


def test_rejects_zero_trade_volume() -> None:
    gate = QualityGate()
    with pytest.raises(TickRejected) as exc_info:
        gate.validate(_tick(last_traded_quantity=0))
    assert exc_info.value.reason == "zero_trade_volume"


def test_rejects_stale_tick() -> None:
    gate = QualityGate(stale_after=timedelta(seconds=5))
    old = datetime.now(timezone.utc) - timedelta(seconds=10)
    with pytest.raises(TickRejected) as exc_info:
        gate.validate(_tick(timestamp=old))
    assert exc_info.value.reason == "stale_tick"


def test_check_staleness_false_accepts_old_tick() -> None:
    gate = QualityGate(stale_after=timedelta(seconds=5))
    old = datetime.now(timezone.utc) - timedelta(days=1)
    accepted = gate.validate(_tick(timestamp=old), check_staleness=False)
    assert accepted.timestamp == old


def test_rejects_duplicate_tick() -> None:
    gate = QualityGate()
    ts = datetime.now(timezone.utc)
    gate.validate(_tick(timestamp=ts))
    with pytest.raises(TickRejected) as exc_info:
        gate.validate(_tick(timestamp=ts))
    assert exc_info.value.reason == "duplicate_tick"


def test_allows_same_timestamp_different_instrument() -> None:
    gate = QualityGate()
    ts = datetime.now(timezone.utc)
    gate.validate(_tick(timestamp=ts, instrument_token=1))
    accepted = gate.validate(_tick(timestamp=ts, instrument_token=2))
    assert accepted.instrument_token == 2


def test_rejects_circuit_limit_breach() -> None:
    gate = QualityGate()
    with pytest.raises(TickRejected) as exc_info:
        gate.validate(_tick(last_price=Decimal("200"), close=Decimal("100")))
    assert exc_info.value.reason == "circuit_limit_breach"


def test_accepts_within_circuit_limit() -> None:
    gate = QualityGate()
    accepted = gate.validate(_tick(last_price=Decimal("115"), close=Decimal("100")))
    assert accepted.last_price == Decimal("115")


def test_accepts_tick_without_previous_close() -> None:
    gate = QualityGate()
    accepted = gate.validate(_tick(last_price=Decimal("1000"), close=None))
    assert accepted.last_price == Decimal("1000")
