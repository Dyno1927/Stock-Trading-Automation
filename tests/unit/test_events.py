"""Unit tests for core.events — UTC enforcement, JSON round-trip."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from sta.core.events import TickIngested
from sta.core.types import Exchange, Tick


def _sample_tick() -> Tick:
    return Tick(
        instrument_token=1,
        exchange=Exchange.NSE,
        symbol="X",
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal("10"),
    )


def test_event_round_trips_through_json() -> None:
    event = TickIngested(tick=_sample_tick())
    restored = TickIngested.from_json(event.to_json())
    assert restored.tick.symbol == event.tick.symbol
    assert restored.event_id == event.event_id


def test_event_type_is_class_name() -> None:
    event = TickIngested(tick=_sample_tick())
    assert event.event_type == "TickIngested"


def test_event_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError):
        TickIngested(tick=_sample_tick(), timestamp=datetime.now())
