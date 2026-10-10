"""Structured application logging: JSON lines to stdout, one object per record."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from starterapp.config import get_settings

_UVICORN_AND_GUNICORN_LOGGERS = (
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "gunicorn.error",
    "gunicorn.access",
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra_fields = getattr(record, "extra_fields", None)
        if isinstance(extra_fields, dict):
            payload.update(extra_fields)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Idempotent: safe to call at import time and again per gunicorn worker."""
    settings = get_settings()
    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

    # Route uvicorn/gunicorn records through the same JSON handler so every
    # line on stdout has one format.
    for name in _UVICORN_AND_GUNICORN_LOGGERS:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
