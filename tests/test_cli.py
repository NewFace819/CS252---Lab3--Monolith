"""End-to-end: real config, knowledge, router, tools and responder behind the CLI.

Expected answers are characterisation values from running the monolith.
"""

import logging
from pathlib import Path

import pytest

from assistant_core.__main__ import main

REPO_DATA = str(Path(__file__).resolve().parents[1] / "data")


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("ASSISTANT_DATA_DIR", REPO_DATA)
    monkeypatch.setenv("LLM_PROVIDER", "stub")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    # main() calls setup_logging(); undo it so other tests see the default logger.
    logger = logging.getLogger("assistant_core")
    handlers, level, propagate = list(logger.handlers), logger.level, logger.propagate
    yield
    logger.handlers, logger.propagate = handlers, propagate
    logger.setLevel(level)


@pytest.mark.parametrize(
    "question, expected",
    [
        ("hi", "Hello! I can help with offices, fees and rules."),
        ("tuition for 18 credits and 2 retake", "Your tuition is 9,450,000 VND."),
        ("where is the library", "Library: room B.201, open Mon-Sat 07:00-20:00."),
        ("tuition 40 credits", "Credits must be between 1 and 30."),
    ],
)
def test_cli_answers(capsys, question, expected):
    assert main(question.split()) == 0
    assert capsys.readouterr().out.strip() == expected


def test_cli_rule_answer_comes_from_handbook(capsys):
    main("can I register my thesis with 118 credits".split())
    assert "Thesis registration" in capsys.readouterr().out


def test_cli_logs_go_to_stderr_not_stdout(capsys):
    main(["hi"])
    out, err = capsys.readouterr()
    assert '"intent": "greeting"' in err
    assert "intent" not in out


def test_cli_missing_data_fails_at_startup(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("ASSISTANT_DATA_DIR", str(tmp_path))
    assert main(["hi"]) == 2
    assert "startup failed" in capsys.readouterr().err


def test_cli_unknown_provider_fails_at_startup(monkeypatch, capsys):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "test-only-key")
    assert main(["hi"]) == 2
    err = capsys.readouterr().err
    assert "not supported" in err and "test-only-key" not in err
