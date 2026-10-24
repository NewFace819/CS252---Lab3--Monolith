import pytest

from assistant_core.models import Intent
from assistant_core.router import route

OFFICES = {"training office", "library", "it helpdesk"}


@pytest.mark.parametrize("text", ["hi", "Hello", "  hey  ", "xin chao"])
def test_greeting(text):
    assert route(text, OFFICES) is Intent.GREETING


def test_greeting_must_be_whole_message():
    assert route("hi, where is the library", OFFICES) is Intent.OFFICE


@pytest.mark.parametrize("text", ["tuition for 18 credits and 2 retake", "What is the FEE?"])
def test_fee(text):
    assert route(text, OFFICES) is Intent.FEE


def test_fee_wins_over_office():
    assert route("fee at the library", OFFICES) is Intent.FEE


def test_office():
    assert route("Where is the Library?", OFFICES) is Intent.OFFICE


def test_rule_is_the_default():
    assert route("can I register my thesis with 118 credits", OFFICES) is Intent.RULE


def test_no_offices_falls_through_to_rule():
    assert route("where is the library", set()) is Intent.RULE
