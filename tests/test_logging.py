import json
import logging

import pytest

from assistant_core.errors import ConfigError
from assistant_core.logging_setup import JsonFormatter, setup_logging


@pytest.fixture(autouse=True)
def restore_application_logger():
    logger = logging.getLogger("assistant_core")
    handlers, level, propagate = list(logger.handlers), logger.level, logger.propagate
    logger.handlers = []
    yield
    for handler in list(logger.handlers):
        handler.close()
    logger.handlers = handlers
    logger.setLevel(level)
    logger.propagate = propagate


def test_formatter_includes_only_operational_fields():
    record = logging.LogRecord("assistant_core.service", logging.INFO, __file__, 1, "handled %s", ("ok",), None)
    record.intent = "fee"
    record.latency_ms = 1.25
    record.session = "local"
    record.degraded = False
    record.api_key = "test-only-secret"
    record.text = "private full message"
    data = json.loads(JsonFormatter().format(record))
    assert data == {
        "level": "INFO",
        "logger": "assistant_core.service",
        "msg": "handled ok",
        "intent": "fee",
        "latency_ms": 1.25,
        "session": "local",
        "degraded": False,
    }


def test_minimal_record_without_optional_extras():
    record = logging.LogRecord("assistant_core", logging.WARNING, __file__, 1, "fallback", (), None)
    assert json.loads(JsonFormatter().format(record)) == {
        "level": "WARNING",
        "logger": "assistant_core",
        "msg": "fallback",
    }


def test_child_logger_writes_json_only_to_stderr(capsys):
    setup_logging("info")
    logging.getLogger("assistant_core.service").info("handled", extra={"intent": "rule", "degraded": True})
    output = capsys.readouterr()
    assert output.out == ""
    assert json.loads(output.err)["degraded"] is True
    assert len(output.err.splitlines()) == 1


def test_repeated_setup_does_not_duplicate_records(capsys):
    setup_logging()
    setup_logging()
    logging.getLogger("assistant_core").info("handled")
    assert len(capsys.readouterr().err.splitlines()) == 1


def test_level_filters_lower_priority_records(capsys):
    setup_logging("WARNING")
    logger = logging.getLogger("assistant_core")
    logger.info("hidden")
    logger.warning("visible")
    output = capsys.readouterr().err
    assert json.loads(output)["msg"] == "visible"


def test_invalid_level_raises_without_reconfiguring():
    setup_logging()
    logger = logging.getLogger("assistant_core")
    handlers = list(logger.handlers)
    with pytest.raises(ConfigError, match="LOG_LEVEL"):
        setup_logging("invalid")
    assert logger.handlers == handlers


def test_quoted_multiline_message_remains_one_json_line(capsys):
    setup_logging()
    logging.getLogger("assistant_core").info('status "ok"\nnext line')
    output = capsys.readouterr().err
    assert len(output.splitlines()) == 1
    assert json.loads(output)["msg"] == 'status "ok"\nnext line'
