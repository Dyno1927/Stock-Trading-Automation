"""Market calendar: trading hours, pre-open, holiday, and session state.

NSE/BSE cash-market hours are fixed-offset IST (no DST in India), so a plain
UTC+5:30 `timezone` is used rather than pulling in a tz database dependency.
Explicit `market_sessions` rows (holidays, special hours) always take
precedence over the standard-hours default.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from enum import Enum

from sqlalchemy import select

from sta.core.types import Exchange
from sta.infrastructure.database import session_scope
from sta.modules.market_data.models import MarketSessionModel

IST = timezone(timedelta(hours=5, minutes=30))

PRE_OPEN_START_IST = time(9, 0)
MARKET_OPEN_IST = time(9, 15)
MARKET_CLOSE_IST = time(15, 30)


class SessionState(str, Enum):
    CLOSED = "CLOSED"
    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    HOLIDAY = "HOLIDAY"


@dataclass
class SessionInfo:
    is_holiday: bool
    pre_open_start: datetime | None
    open_time: datetime | None
    close_time: datetime | None


def _ist_to_utc(d: date, t: time) -> datetime:
    return datetime.combine(d, t, tzinfo=IST).astimezone(timezone.utc)


async def get_session_info(exchange: Exchange, session_date: date) -> SessionInfo:
    """Look up the session for a date. Falls back to standard weekday hours
    if no explicit `market_sessions` row exists (no holiday calendar is
    seeded yet in V0 — only explicit overrides + the weekend default apply).
    """
    async with session_scope() as session:
        result = await session.execute(
            select(MarketSessionModel).where(
                MarketSessionModel.exchange == exchange.value,
                MarketSessionModel.session_date == session_date,
            )
        )
        row = result.scalar_one_or_none()

    if row is not None:
        return SessionInfo(row.is_holiday, row.pre_open_start, row.open_time, row.close_time)

    if session_date.weekday() >= 5:  # Saturday=5, Sunday=6
        return SessionInfo(True, None, None, None)

    return SessionInfo(
        is_holiday=False,
        pre_open_start=_ist_to_utc(session_date, PRE_OPEN_START_IST),
        open_time=_ist_to_utc(session_date, MARKET_OPEN_IST),
        close_time=_ist_to_utc(session_date, MARKET_CLOSE_IST),
    )


def resolve_state(info: SessionInfo, now: datetime) -> SessionState:
    if info.is_holiday:
        return SessionState.HOLIDAY
    if info.pre_open_start is None or info.open_time is None or info.close_time is None:
        return SessionState.CLOSED
    if now < info.pre_open_start:
        return SessionState.CLOSED
    if now < info.open_time:
        return SessionState.PRE_OPEN
    if now < info.close_time:
        return SessionState.OPEN
    return SessionState.CLOSED


async def current_session_state(exchange: Exchange, now: datetime | None = None) -> SessionState:
    now = now or datetime.now(timezone.utc)
    info = await get_session_info(exchange, now.astimezone(IST).date())
    return resolve_state(info, now)
