"""SQLAlchemy ORM models for Market Data — instruments, market_sessions, ticks.

Imported by Alembic's env.py to register metadata (architecture decision A2).
Living here, in the Market Data module, does not violate module isolation:
Alembic is infrastructure tooling, not another domain module.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from sta.infrastructure.database import Base

# MARKET / DATABASE: ORM models for the Market Data module's tables.
# MODULE: lives here (not infrastructure/) on purpose — Alembic importing
# MODULE: this is tooling, not a module-isolation violation (see docstring above).


class InstrumentModel(Base):
    """Symbol<->token master record (per-exchange)."""

    __tablename__ = "instruments"

    instrument_token: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    exchange: Mapped[str] = mapped_column(String(8), nullable=False)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    instrument_type: Mapped[str] = mapped_column(String(16), nullable=False)
    tick_size: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    lot_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    expiry: Mapped[date | None] = mapped_column(Date, nullable=True)


class MarketSessionModel(Base):
    """Trading calendar: per-exchange session state for a given date."""

    __tablename__ = "market_sessions"

    session_date: Mapped[date] = mapped_column(Date, primary_key=True)
    exchange: Mapped[str] = mapped_column(String(8), primary_key=True)
    is_holiday: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pre_open_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    open_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    close_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TickModel(Base):
    """Raw tick storage. Maps to the `ticks` TimescaleDB hypertable, partitioned
    on `time`. Primary key (time, instrument_token) doubles as the DB-level
    duplicate guard backing the quality gate's dedup rule."""

    __tablename__ = "ticks"

    # IMPORTANT: this composite primary key is load-bearing — it's the DB-level
    # IMPORTANT: backstop for the quality gate's "duplicate (instrument+timestamp)" rule.
    # IMPORTANT: Changing it silently removes that guarantee.

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    instrument_token: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    exchange: Mapped[str] = mapped_column(String(8), nullable=False)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    last_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    last_traded_quantity: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    volume_traded: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
