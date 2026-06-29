"""Cold path: batched, authoritative writes of validated ticks to the
`ticks` hypertable.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from sqlalchemy.dialects.postgresql import insert as pg_insert

from sta.core.types import Tick
from sta.infrastructure.database import session_scope
from sta.modules.market_data.models import TickModel

logger = logging.getLogger(__name__)


async def write_ticks(ticks: Sequence[Tick]) -> None:
    """Batch-insert ticks. Rows that collide on (time, instrument_token) are
    ignored — the quality gate is the source of truth for dedup; this is
    defense in depth, not a substitute for it.
    """
    if not ticks:
        return

    rows = [
        {
            "time": tick.timestamp,
            "instrument_token": tick.instrument_token,
            "exchange": tick.exchange.value,
            "symbol": tick.symbol,
            "last_price": tick.last_price,
            "last_traded_quantity": tick.last_traded_quantity,
            "volume_traded": tick.volume_traded,
        }
        for tick in ticks
    ]

    stmt = pg_insert(TickModel).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["time", "instrument_token"])

    async with session_scope() as session:
        await session.execute(stmt)
        await session.commit()
