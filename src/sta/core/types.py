"""Core domain types shared across all STA modules.

Per architecture decision A1, domain types are Pydantic v2 models (consistent
with the rest of the stack). All timestamps are UTC — see CLAUDE.md rule 3.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

# CORE: shared domain types (Tick/Bar/Signal/Order/Instrument/Position) — the
# CORE: only thing modules may import across module boundaries (CLAUDE.md rule 1).


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware (UTC)")
    if value.utcoffset() != timezone.utc.utcoffset(None):
        raise ValueError("timestamp must be in UTC")
    return value


class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"


class Direction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL_M"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class BarPeriod(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTE = "5m"


class Instrument(BaseModel):
    """Symbol<->token master record (per-exchange)."""

    instrument_token: int
    exchange: Exchange
    symbol: str
    name: str
    instrument_type: str
    tick_size: Decimal
    lot_size: int
    expiry: datetime | None = None

    @field_validator("expiry")
    @classmethod
    def validate_expiry(cls, v: datetime | None) -> datetime | None:
        return _ensure_utc(v) if v is not None else v


class Tick(BaseModel):
    """A single normalized market tick (post quality-gate)."""

    instrument_token: int
    exchange: Exchange
    symbol: str
    timestamp: datetime
    last_price: Decimal
    last_traded_quantity: int = 0
    volume_traded: int = 0
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    # NOTE: previous trading day's closing price — used for circuit-limit checks, not today's intra-day close.
    close: Decimal | None = None

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        return _ensure_utc(v)


class Bar(BaseModel):
    """An OHLCV bar aggregated from ticks."""

    instrument_token: int
    exchange: Exchange
    symbol: str
    period: BarPeriod
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    @field_validator("open_time", "close_time")
    @classmethod
    def validate_utc(cls, v: datetime) -> datetime:
        return _ensure_utc(v)


class Signal(BaseModel):
    """A raw trading signal produced by a strategy."""

    signal_id: UUID = Field(default_factory=uuid4)
    instrument_token: int
    exchange: Exchange
    symbol: str
    direction: Direction
    strategy_name: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("generated_at")
    @classmethod
    def validate_generated_at(cls, v: datetime) -> datetime:
        return _ensure_utc(v)


class Position(BaseModel):
    """A broker-reported open position, as returned by BrokerAdapter.get_positions()."""

    instrument_token: int
    exchange: Exchange
    symbol: str
    quantity: int
    average_price: Decimal


class Order(BaseModel):
    """An order command. Carries an idempotency_key — see CLAUDE.md rule 5."""

    order_id: UUID = Field(default_factory=uuid4)
    idempotency_key: str
    instrument_token: int
    exchange: Exchange
    symbol: str
    direction: Direction
    order_type: OrderType
    quantity: int
    price: Decimal | None = None
    trigger_price: Decimal | None = None
    status: OrderStatus = OrderStatus.PENDING
    broker_order_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("created_at", "updated_at")
    @classmethod
    def validate_utc(cls, v: datetime) -> datetime:
        return _ensure_utc(v)
