"""Market Data module coordinator.

The single entry point both live ticks and historical replay/backfill ticks
travel through — see CLAUDE.md rule 9 (deterministic replay: live and replay
use the identical code path).
"""

from __future__ import annotations

import logging

from sta.core.types import Tick
from sta.modules.market_data import cold_path, hot_path
from sta.modules.market_data.quality_gate import QualityGate, TickRejected

# MARKET / SERVICE / MODULE: the Market Data module's single coordinator —
# MARKET / SERVICE / MODULE: the only thing outside this package that should be called to ingest a
# MARKET / SERVICE / MODULE: tick, live or replayed.

logger = logging.getLogger(__name__)


class MarketDataService:
    """Wires the quality gate to the hot path + cold path.

    Construct one instance per run and reuse it for both the live stream and
    any replay/backfill calls, so dedup state is shared and both travel the
    identical `process_tick()` codepath (rule 9).
    """

    def __init__(self, gate: QualityGate | None = None) -> None:
        self.gate = gate or QualityGate()

    async def process_tick(self, tick: Tick, *, check_staleness: bool = True) -> Tick | None:
        """Validate a tick through the single quality gate and, if accepted,
        publish it to the hot path and persist it to the cold path.

        Returns the accepted tick, or None if the gate rejected it.
        """
        try:
            validated = self.gate.validate(tick, check_staleness=check_staleness)
        except TickRejected as exc:
            logger.warning(
                "tick rejected: reason=%s exchange=%s symbol=%s",
                exc.reason,
                tick.exchange,
                tick.symbol,
            )
            return None

        await hot_path.publish_tick(validated)
        await cold_path.write_ticks([validated])
        return validated
