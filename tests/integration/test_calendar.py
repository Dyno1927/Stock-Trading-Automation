"""Integration test: get_session_info's DB-backed path — explicit
market_sessions rows override the standard-hours default.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import delete

from sta.core.types import Exchange
from sta.infrastructure.database import session_scope
from sta.modules.market_data.calendar import get_session_info
from sta.modules.market_data.models import MarketSessionModel


async def test_get_session_info_falls_back_to_weekday_default() -> None:
    a_monday = date(2026, 1, 5)
    info = await get_session_info(Exchange.NSE, a_monday)
    assert info.is_holiday is False
    assert info.open_time is not None


async def test_get_session_info_weekend_is_holiday() -> None:
    a_sunday = date(2026, 1, 4)
    info = await get_session_info(Exchange.NSE, a_sunday)
    assert info.is_holiday is True


async def test_get_session_info_explicit_holiday_row_overrides() -> None:
    a_monday = date(2026, 1, 12)

    try:
        async with session_scope() as session:
            session.add(
                MarketSessionModel(
                    session_date=a_monday,
                    exchange=Exchange.NSE.value,
                    is_holiday=True,
                )
            )
            await session.commit()

        info = await get_session_info(Exchange.NSE, a_monday)
        assert info.is_holiday is True
    finally:
        async with session_scope() as session:
            await session.execute(
                delete(MarketSessionModel).where(MarketSessionModel.session_date == a_monday)
            )
            await session.commit()
