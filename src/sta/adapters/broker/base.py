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

# BROKER: abstract broker adapter port — concrete implementations (Zerodha
# BROKER: Kite Connect first) live alongside this file, never imported by name
# BROKER: elsewhere (CLAUDE.md ADR 008).


class BrokerAdapter(ABC):
    """Abstract port for broker connectivity. All methods are async."""

    # TODO PHASE_0: no concrete implementation exists yet — the Zerodha Kite
    # TODO PHASE_0: Connect adapter is the first one planned (CLAUDE.md tech stack) but is
    # TODO PHASE_0: out of scope for Phase 0 (see Implement.md).

    @abstractmethod
    async def connect(self) -> None:
        """Authenticate and establish the broker session."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Tear down the broker session."""

    @abstractmethod
    async def get_instruments(
        self, exchange: Exchange | None = None
    ) -> list[Instrument]:
        """Fetch the current instrument master list, optionally filtered by exchange."""

    @abstractmethod
    async def stream_ticks(self, instrument_tokens: list[int]) -> AsyncIterator[Tick]:
        """Subscribe to live ticks for the given instruments and yield them as they arrive."""
        raise NotImplementedError
        # NOTE: unreachable yield — makes this an async generator function so the
        # NOTE: AsyncIterator[Tick] return type checks out; concrete implementations
        # NOTE: replace this whole body.
        yield  # pragma: no cover

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
