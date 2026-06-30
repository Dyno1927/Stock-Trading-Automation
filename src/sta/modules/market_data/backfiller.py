"""Gap detection + backfill.

On reconnect, detect the gap since the last persisted tick, pull the missing
window via the broker's historical REST API, and re-inject it through the
same `MarketDataService.process_tick()` path used by live ticks — see
CLAUDE.md rule 9 (deterministic replay).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from sta.adapters.broker.base import BrokerAdapter
from sta.core.events import GapDetected
from sta.core.types import Bar, BarPeriod, Exchange, Tick
from sta.infrastructure.database import session_scope
from sta.modules.market_data.models import TickModel
from sta.modules.market_data.service import MarketDataService

# MARKET / BROKER: gap detection + backfill on reconnect.

logger = logging.getLogger(__name__)

DEFAULT_BACKFILL_PERIOD = BarPeriod.ONE_MINUTE
DEFAULT_GAP_THRESHOLD = timedelta(minutes=1)


def _bar_to_tick(bar: Bar) -> Tick:
    """Historical REST APIs return OHLC bars, not tick-level data, so each
    bar's close is replayed as one synthetic tick at the bar's close time.

    `close` (previous trading day's close, used for the circuit-limit check)
    is deliberately left unset: a bar's own close is a different value with a
    different meaning and must not be mistaken for it.
    """
    return Tick(
        instrument_token=bar.instrument_token,
        exchange=bar.exchange,
        symbol=bar.symbol,
        timestamp=bar.close_time,
        last_price=bar.close,
        last_traded_quantity=bar.volume,
        volume_traded=bar.volume,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        # IMPORTANT: `close` intentionally omitted — see docstring above.
    )


async def get_last_tick_time(instrument_token: int) -> datetime | None:
    async with session_scope() as session:
        result = await session.execute(
            select(TickModel.time)
            .where(TickModel.instrument_token == instrument_token)
            .order_by(TickModel.time.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


def detect_gap(
    last_tick_time: datetime | None,
    now: datetime,
    threshold: timedelta = DEFAULT_GAP_THRESHOLD,
) -> tuple[datetime, datetime] | None:
    """Returns (gap_start, gap_end) if the gap since the last tick exceeds
    `threshold`, else None. No prior tick means nothing to backfill from."""
    if last_tick_time is None:
        return None
    if now - last_tick_time > threshold:
        return (last_tick_time, now)
    return None


async def backfill_on_reconnect(
    broker: BrokerAdapter,
    service: MarketDataService,
    instrument_token: int,
    exchange: Exchange,
    symbol: str,
    now: datetime | None = None,
    period: BarPeriod = DEFAULT_BACKFILL_PERIOD,
) -> int:
    """Detect a gap for this instrument and replay it through the quality
    gate. Returns the number of backfilled ticks accepted by the gate."""
    now = now or datetime.now(timezone.utc)
    last_tick_time = await get_last_tick_time(instrument_token)
    gap = detect_gap(last_tick_time, now)
    if gap is None:
        return 0
    gap_start, gap_end = gap

    event = GapDetected(
        instrument_token=instrument_token,
        exchange=exchange,
        symbol=symbol,
        gap_start=gap_start,
        gap_end=gap_end,
    )
    logger.warning("gap detected: %s", event.to_json())

    bars = await broker.get_historical_bars(instrument_token, exchange, period, gap_start, gap_end)

    accepted = 0
    for bar in sorted(bars, key=lambda b: b.close_time):
        tick = _bar_to_tick(bar)
        # NOTE: check_staleness=False — backfilled ticks are old by
        # NOTE: definition; every other quality-gate rule still applies (rule 9).
        result = await service.process_tick(tick, check_staleness=False)
        if result is not None:
            accepted += 1

    logger.info(
        "backfill complete: instrument=%s accepted=%d/%d bars",
        instrument_token,
        accepted,
        len(bars),
    )
    return accepted
