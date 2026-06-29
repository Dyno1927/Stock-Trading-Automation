"""Abstract broker adapter port.

Every broker integration (Zerodha Kite Connect first, others later) implements
this interface. No module outside `adapters/broker/` may depend on a concrete
broker SDK — see CLAUDE.md ADR 008.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

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


class BrokerAdapter(ABC):
    """Abstract port for broker connectivity. All methods are async."""

    @abstractmethod
    async def connect(self) -> None:
        """Authenticate and establish the broker session."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Tear down the broker session."""

    @abstractmethod
    async def get_instruments(self, exchange: Exchange | None = None) -> list[Instrument]:
        """Fetch the current instrument master list, optionally filtered by exchange."""

    @abstractmethod
    async def stream_ticks(self, instrument_tokens: list[int]) -> AsyncIterator[Tick]:
        """Subscribe to live ticks for the given instruments and yield them as they arrive."""
        raise NotImplementedError
        yield  # pragma: no cover - makes this an async generator for typing purposes

    @abstractmethod
    async def get_historical_bars(
        self,
        instrument_token: int,
        exchange: Exchange,
        period: BarPeriod,
        start: datetime,
        end: datetime,
    ) -> list[Bar]:
        """Fetch historical OHLCV bars for gap backfill or replay."""

    @abstractmethod
    async def submit_order(self, order: Order) -> Order:
        """Submit an order to the broker. Returns the order updated with broker_order_id/status."""

    @abstractmethod
    async def cancel_order(self, broker_order_id: str) -> OrderStatus:
        """Cancel a previously submitted order."""

    @abstractmethod
    async def get_order_status(self, broker_order_id: str) -> OrderStatus:
        """Fetch the current status of a previously submitted order."""

    @abstractmethod
    async def get_positions(self) -> list[Position]:
        """Fetch broker-reported open positions, for reconciliation."""
