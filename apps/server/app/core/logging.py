"""Logging setup. Readable console in dev, structured JSON with request ids in prod."""

from __future__ import annotations

import json
import logging
import sys

from app.core.context import get_request_id
from app.core.redaction import redact


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": redact(record.getMessage()),
            "requestId": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["error"] = redact(self.formatException(record.exc_info))
        return json.dumps(payload)


class RedactingFormatter(logging.Formatter):
    """Plain-text formatter that masks secrets in the rendered message (dev console)."""

    def format(self, record: logging.LogRecord) -> str:
        return redact(super().format(record))


def configure_logging(app_env: str, log_level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())

    if app_env == "prod":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            RedactingFormatter("%(levelname)s [%(request_id)s] %(name)s: %(message)s")
        )

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(log_level.upper())
