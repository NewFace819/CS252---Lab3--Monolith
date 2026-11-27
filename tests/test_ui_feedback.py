"""👍/👎 must only count a vote the API actually saved."""

from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "ui" / "app.py")
ANSWER = {"role": "assistant", "content": "Answer", "request_id": "r1"}


def run_app(saved: bool):
    patcher = patch("ui.api_client.AssistantClient")
    factory = patcher.start()
    client = factory.return_value
    client.healthy.return_value = True
    client.send_feedback.return_value = saved
    at = AppTest.from_file(APP)
    at.session_state.messages = [ANSWER]
    at.run()
    return at, client, patcher


@pytest.mark.parametrize("key, rating", [("up0", 1), ("down0", -1)])
def test_saved_vote_thanks_and_hides_buttons(key, rating):
    at, client, patcher = run_app(saved=True)
    try:
        at.button(key=key).click().run()
        client.send_feedback.assert_called_once_with("r1", rating)
        assert "r1" in at.session_state.rated
        assert "Thanks" in at.toast[0].value
        assert not any(b.key in {"up0", "down0"} for b in at.button)
    finally:
        patcher.stop()


@pytest.mark.parametrize("key", ["up0", "down0"])
def test_failed_vote_warns_and_keeps_buttons(key):
    at, client, patcher = run_app(saved=False)
    try:
        at.button(key=key).click().run()
        assert "r1" not in at.session_state.rated
        assert not at.toast
        assert "could not be saved" in at.warning[0].value
        assert {"up0", "down0"} <= {b.key for b in at.button}
    finally:
        patcher.stop()
