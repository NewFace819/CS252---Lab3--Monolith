"""Greeting detection ignores trailing punctuation (Lab 3 guide p.13), without changing the Week 3 tests."""

import pytest

from assistant_core.models import Intent
from assistant_core.router import route

OFFICES = {"Library"}


@pytest.mark.parametrize("text", ["Hello!", "hi.", "hey?!", "  Xin chao!  "])
def test_greeting_with_trailing_punctuation(text):
    assert route(text, OFFICES) is Intent.GREETING


def test_punctuation_does_not_turn_questions_into_greetings():
    assert route("hi, where is the library?", OFFICES) is Intent.OFFICE
