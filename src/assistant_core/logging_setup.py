"""Structured JSON logs to stderr. Never log the API key or the full user message.

Owner: Thông (issue #2). Callers must use operational messages, not user text or keys.
"""

import json
import logging

from assistant_core.errors import ConfigError


class JsonFormatter(logging.Formatter):
    """One JSON object per line: level, logger, msg + extras (intent, latency_ms, session, degraded)."""

    def format(self, record: logging.LogRecord) -> str:
        data = {"level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        # Only known operational fields cross the logging boundary. Do not dump
        # record.__dict__, settings, arbitrary extras or exception details.
        for key in ("intent", "latency_ms", "session", "degraded"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Attach a JsonFormatter handler on stderr to the ``assistant_core`` logger."""
    levels = {
        "NOTSET": logging.NOTSET,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.CRITICAL,
    }
    numeric_level = levels.get(level.strip().upper())
    if numeric_level is None:
        raise ConfigError("LOG_LEVEL must name a standard Python logging level.")
    logger = logging.getLogger("assistant_core")
    for old_handler in list(logger.handlers):
        if old_handler.name == "assistant_core_json":
            logger.removeHandler(old_handler)
            old_handler.close()
    handler = logging.StreamHandler()  # StreamHandler defaults to stderr.
    handler.set_name("assistant_core_json")
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(numeric_level)
    logger.propagate = False
