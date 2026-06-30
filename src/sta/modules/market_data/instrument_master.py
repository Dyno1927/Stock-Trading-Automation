"""Instrument master: symbol<->token mapping, refreshed once per trading
session via the broker adapter.
"""

from __future__ import annotations

import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert

from sta.adapters.broker.base import BrokerAdapter
from sta.core.types import Exchange
from sta.infrastructure.database import session_scope
from sta.modules.market_data.models import InstrumentModel

logger = logging.getLogger(__name__)


async def refresh_instruments(broker: BrokerAdapter, exchange: Exchange | None = None) -> int:
    """Fetch the latest instrument list from the broker and upsert it into
    the `instruments` table. Returns the number of instruments upserted.
    """
    instruments = await broker.get_instruments(exchange)
    if not instruments:
        return 0

    rows = [
        {
            "instrument_token": inst.instrument_token,
            "exchange": inst.exchange.value,
            "symbol": inst.symbol,
            "name": inst.name,
            "instrument_type": inst.instrument_type,
            "tick_size": inst.tick_size,
            "lot_size": inst.lot_size,
            # NOTE: domain Instrument.expiry is a UTC datetime; the DB column
            # is a plain Date — drop the time component here, not earlier,
            # so the domain type stays precise.
            "expiry": inst.expiry.date() if inst.expiry else None,
        }
        for inst in instruments
    ]

    stmt = pg_insert(InstrumentModel).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["instrument_token"],
        set_={
            "symbol": stmt.excluded.symbol,
            "name": stmt.excluded.name,
            "instrument_type": stmt.excluded.instrument_type,
            "tick_size": stmt.excluded.tick_size,
            "lot_size": stmt.excluded.lot_size,
            "expiry": stmt.excluded.expiry,
        },
    )

    async with session_scope() as session:
        await session.execute(stmt)
        await session.commit()

    logger.info("refreshed %d instruments", len(rows))
    return len(rows)
