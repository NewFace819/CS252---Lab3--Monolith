"""Feedback interactions must reflect the server result across Streamlit reruns."""

from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from ui.api_client import ChatResult
from ui.logic import status_note

APP = Path(__file__).resolve().parents[1] / "ui" / "app.py"


@pytest.mark.parametrize("rating, key", [(1, "up1"), (-1, "down1")])
def test_successful_feedback_hides_both_buttons_after_rerun(rating, key):
    with patch("ui.api_client.AssistantClient") as factory:
        client = factory.return_value
        client.healthy.return_value = True
        client.send_feedback.return_value = True
        at = AppTest.from_file(str(APP))
        at.session_state.messages = [
            {"role": "assistant", "content": "Welcome"},
            {"role": "assistant", "content": "Answer", "request_id": "test-request"},
        ]
        at.run()
        at.button(key=key).click().run()
        assert not at.exception
        client.send_feedback.assert_called_once_with("test-request", rating)
        assert "test-request" in at.session_state.rated
        assert not any(b.key in {"up1", "down1"} for b in at.button)
        assert "Thanks" in at.toast[0].value


def test_failed_feedback_remains_retryable():
    with patch("ui.api_client.AssistantClient") as factory:
        client = factory.return_value
        client.healthy.return_value = True
        client.send_feedback.return_value = False
        at = AppTest.from_file(str(APP))
        at.session_state.messages = [{"role": "assistant", "content": "Answer", "request_id": "test-request"}]
        at.run()
        at.button(key="down0").click().run()
        assert not at.exception
        assert "test-request" not in at.session_state.rated
        assert "try again" in at.warning[0].value
        assert at.button(key="down0") and not at.toast


def test_escalation_takes_priority_over_degraded_notice():
    assert "Training Office" in status_note(ChatResult(ok=True, escalate=True, degraded=True))
    assert "source document" in status_note(ChatResult(ok=True, degraded=True))


def test_long_question_is_not_sent_to_backend():
    with patch("ui.api_client.AssistantClient") as factory:
        factory.return_value.healthy.return_value = True
        at = AppTest.from_file(str(APP)).run()
        at.chat_input[0].set_value("x" * 2001).run()
        assert not at.exception
        assert "too long" in at.warning[0].value
        factory.return_value.ask.assert_not_called()
