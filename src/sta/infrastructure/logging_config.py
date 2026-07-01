"""Structured JSON logging, configured once at process startup.

See CLAUDE.md rule 7: no print() anywhere; every module uses
`logging.getLogger(__name__)`.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from sta.config.settings import get_settings

# CONFIG: structured JSON logging — log level read from app settings.
# NOTE: _configured guard makes configure_logging() idempotent — safe to call
# NOTE: from tests, lifespan hooks, and scripts without double-registering handlers.
_configured = False


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> None:
    """Configure the root logger with a JSON formatter. Idempotent."""
    global _configured
    if _configured:
        return

    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level)

    _configured = True
