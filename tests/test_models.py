import pytest
from pydantic import ValidationError

from assistant_core.models import Intent, Message, Response


def test_empty_message_is_rejected():
    with pytest.raises(ValidationError):
        Message(text="")


def test_too_long_message_is_rejected():
    with pytest.raises(ValidationError):
        Message(text="x" * 2001)


def test_response_defaults():
    r = Response(answer="ok", intent=Intent.GREETING)
    assert r.sources == [] and r.degraded is False
