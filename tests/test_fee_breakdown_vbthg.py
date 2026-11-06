import logging
from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.models import Intent, Message
from assistant_core.service import build_service

DATA = Path(__file__).resolve().parents[1] / "data"


def make_service(**changes):
    return build_service(Settings(data_dir=DATA, **changes))


def test_breakdown_default_rates():
    response = make_service().handle(Message(text="tuition breakdown for 18 credits and 2 retake"))
    assert response.intent is Intent.FEE
    assert response.answer == "Your tuition is 9,450,000 VND. Regular: 8,100,000 VND; retake: 1,350,000 VND."
    assert response.sources == [] and not response.degraded


def test_breakdown_uses_configured_rates_and_existing_rounding():
    service = make_service(credit_rate_vnd=101, retake_multiplier=1.5)
    response = service.handle(Message(text="fee BREAKDOWN for 2 credits and 1 retake"))
    assert response.answer == "Your tuition is 353 VND. Regular: 202 VND; retake: 151 VND."


def test_breakdown_without_retake():
    response = make_service().handle(Message(text="fee breakdown for 1 credit"))
    assert response.answer == "Your tuition is 450,000 VND. Regular: 450,000 VND; retake: 0 VND."


@pytest.mark.parametrize(
    ("text", "answer"),
    [
        ("fee breakdown please", "How many credits?"),
        ("fee breakdown for 0 credits", "Credits must be between 1 and 30."),
        ("fee breakdown for 31 credits", "Credits must be between 1 and 30."),
    ],
)
def test_invalid_input_keeps_existing_error_answer(text, answer):
    assert make_service().handle(Message(text=text)).answer == answer


def test_ordinary_fee_answer_is_unchanged():
    response = make_service().handle(Message(text="tuition for 18 credits and 2 retake"))
    assert response.answer == "Your tuition is 9,450,000 VND."


def test_breakdown_does_not_log_user_message(caplog):
    text = "fee breakdown for 2 credits private-student-note"
    with caplog.at_level(logging.INFO, logger="assistant_core"):
        make_service().handle(Message(text=text))
    assert caplog.records
    assert all(text not in str(record.__dict__) for record in caplog.records)
