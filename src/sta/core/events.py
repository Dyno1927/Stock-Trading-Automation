"""Event definitions for the Redis Streams / Pub-Sub event bus.

Only events actually needed by the Market Data module (Phase 0 scope) are
implemented here. Other modules add their own event classes when they are
designed and built — see CLAUDE.md rule 1 (module isolation via the event bus).
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field, field_validator

from sta.core.types import Bar, Exchange, Tick

# EVENT: event-bus message definitions (Redis Streams/Pub-Sub payloads).


class Event(BaseModel):
    """Base class for all events carried on the event bus."""

    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        if v.tzinfo is None or v.utcoffset() != timezone.utc.utcoffset(None):
            raise ValueError("timestamp must be timezone-aware UTC")
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def event_type(self) -> str:
        return self.__class__.__name__

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> Event:
        return cls.model_validate_json(data)


class TickIngested(Event):
    """A tick passed the quality gate and was published/persisted."""

    tick: Tick


class BarClosed(Event):
    """A bar finished aggregating and is ready for downstream consumers."""

    # PHASE_0: declared for future use — no bar-aggregation logic exists yet
    # PHASE_0: (continuous aggregates are deferred per ADR A3), so nothing currently
    # PHASE_0: emits this event.
    bar: Bar


class GapDetected(Event):
    """A gap was detected in the live tick stream for an instrument."""

    instrument_token: int
    exchange: Exchange
    symbol: str
    gap_start: datetime
    gap_end: datetime

    @field_validator("gap_start", "gap_end")
    @classmethod
    def validate_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None or v.utcoffset() != timezone.utc.utcoffset(None):
            raise ValueError("must be timezone-aware UTC")
        return v
