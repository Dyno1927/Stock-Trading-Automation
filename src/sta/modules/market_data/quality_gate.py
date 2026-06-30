"""The single quality gate for all market data.

Live ticks AND historical replay/backfill ticks travel through this exact
validate/dedup chokepoint — see CLAUDE.md rules 8 (single quality gate) and
9 (deterministic replay).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sta.core.types import Tick

logger = logging.getLogger(__name__)

CIRCUIT_LIMIT_PCT = Decimal("0.20")
DEFAULT_STALE_AFTER = timedelta(seconds=60)
DEFAULT_DEDUP_WINDOW = timedelta(seconds=60)


class TickRejected(Exception):
    """Raised when a tick fails the quality gate. `reason` is machine-readable."""

    def __init__(self, reason: str, tick: Tick) -> None:
        super().__init__(reason)
        self.reason = reason
        self.tick = tick


@dataclass
class QualityGate:
    """Stateful dedup tracking.

    One instance must be reused across both the live stream and any
    replay/backfill calls for a run, so they share dedup state and travel the
    identical `validate()` codepath (rule 9).
    """

    stale_after: timedelta = DEFAULT_STALE_AFTER
    dedup_window: timedelta = DEFAULT_DEDUP_WINDOW
    _seen: set[tuple[int, datetime]] = field(default_factory=set)
    _watermark: datetime | None = field(default=None)

    def validate(
        self, tick: Tick, *, now: datetime | None = None, check_staleness: bool = True
    ) -> Tick:
        """Validate a tick. Raises `TickRejected` if it fails any rule.

        `check_staleness` is False for replay/backfill ticks: staleness measures
        lag behind wall-clock time, which is meaningless for historical data.
        Every other rule (price, volume, dedup, circuit limit) still applies
        identically, preserving the single-codepath guarantee (rule 9). Dedup
        pruning is keyed off the max tick timestamp seen so far, not
        wall-clock time, so replay dedup behavior is reproducible regardless
        of when the replay is actually run.
        """
        if tick.last_price <= 0:
            raise TickRejected("price_non_positive", tick)

        if tick.last_traded_quantity == 0:
            raise TickRejected("zero_trade_volume", tick)

        # IMPORTANT: staleness is wall-clock-relative and meaningless for
        # replay/backfill ticks (rule 9) — skip it when check_staleness=False,
        # everything else below still runs identically.
        if check_staleness:
            now = now or datetime.now(timezone.utc)
            if now - tick.timestamp > self.stale_after:
                raise TickRejected("stale_tick", tick)

        # NOTE: watermark tracks the max *tick* timestamp seen, not wall-clock
        # time, so dedup pruning behaves identically on every replay run
        # regardless of when it's actually executed.
        self._watermark = (
            tick.timestamp if self._watermark is None else max(self._watermark, tick.timestamp)
        )
        self._prune()

        key = (tick.instrument_token, tick.timestamp)
        if key in self._seen:
            raise TickRejected("duplicate_tick", tick)

        if tick.close is not None and tick.close > 0:
            lower = tick.close * (1 - CIRCUIT_LIMIT_PCT)
            upper = tick.close * (1 + CIRCUIT_LIMIT_PCT)
            if not (lower <= tick.last_price <= upper):
                raise TickRejected("circuit_limit_breach", tick)

        self._seen.add(key)
        return tick

    def _prune(self) -> None:
        # NOTE: type-narrowing assertion, not validation — validate() always
        # sets _watermark before calling _prune(), this never actually fires.
        assert self._watermark is not None
        cutoff = self._watermark - self.dedup_window
        self._seen = {k for k in self._seen if k[1] >= cutoff}
