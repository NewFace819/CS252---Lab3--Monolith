"""H1 (AI extension): 'help' lists what the assistant can do, built from the loaded data."""

import logging
from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.models import Intent, Message
from assistant_core.router import is_help, route
from assistant_core.service import build_service
from assistant_core.tools import help_text

OFFICES = {"library"}
DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture
def real_service():
    """Real data and the stub responder (the shared `service` fixture is all fakes)."""
    return build_service(Settings(data_dir=DATA))


@pytest.mark.parametrize("text", ["help", "Help!", "  what can you do?  ", "What can you help with", "commands"])
def test_help_requests_are_recognised(text):
    assert is_help(text)
    assert route(text, OFFICES) is Intent.GREETING


@pytest.mark.parametrize(
    "text",
    ["help me register my thesis with 118 credits", "can you help? I missed my final exam", "helpdesk", "hi"],
)
def test_real_questions_are_not_help_requests(text):
    assert not is_help(text)


def test_help_answer_lists_data_driven_capabilities(real_service):
    r = real_service.handle(Message(text="help"))
    assert r.intent is Intent.GREETING
    assert r.sources == [] and not r.degraded
    for office in real_service.offices.all():
        assert office.name in r.answer
    for title in real_service.handbook.titles():
        assert title in r.answer
    assert "tuition" in r.answer


def test_greeting_keeps_its_old_answer(real_service):
    assert real_service.handle(Message(text="hi")).answer == "Hello! I can help with offices, fees and rules."


def test_questions_containing_help_still_get_real_answers(real_service):
    r = real_service.handle(Message(text="help me register my thesis with 118 credits"))
    assert r.intent is Intent.RULE
    assert "Thesis registration" in r.answer


def test_help_text_handles_empty_data():
    assert "none loaded" in help_text([], [])


def test_help_does_not_log_the_message(real_service, caplog):
    with caplog.at_level(logging.INFO, logger="assistant_core"):
        real_service.handle(Message(text="help"))
    assert "help" not in " ".join(r.getMessage() for r in caplog.records)
