"""Structured JSON logs to stderr. Never log the API key or the full user message.

Owner: Thông (see issue). Contract below is fixed; replace the stub body.
"""

import logging


class JsonFormatter(logging.Formatter):
    """One JSON object per line: level, logger, msg + extras (intent, latency_ms, session, degraded)."""

    def format(self, record: logging.LogRecord) -> str:
        raise NotImplementedError("logging_setup.JsonFormatter — owned by Thông")


def setup_logging(level: str = "INFO") -> None:
    """Attach a JsonFormatter handler on stderr to the ``assistant_core`` logger."""
    raise NotImplementedError("logging_setup.setup_logging — owned by Thông")
