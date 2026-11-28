"""UI logic without Streamlit, so it can be unit-tested."""

from __future__ import annotations

import unicodedata

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I can answer questions about fees, offices and the student handbook. "
    "Try: “Can I register my thesis with 118 credits?”"
)
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retake",
    "Where is the library?",
    "I lost my student card",
]


def validate_input(text: str) -> str | None:
    """Return an error message for bad input, or None if it is fine."""
    t = text.strip()
    if not t:
        return "Please type a question."
    if len(t) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


_THANKS = {
    "thanks", "thank you", "thanks a lot", "thank you so much", "thank u", "thx", "tks", "ty",
    "cảm ơn", "cám ơn", "cảm ơn bạn", "cám ơn bạn", "cảm ơn ạ", "cảm ơn nhiều", "cam on", "cam on ban",
}  # fmt: skip
_BYE = {"bye", "goodbye", "bye bye", "see you", "tạm biệt", "tam biet"}


def small_talk_reply(text: str) -> str | None:
    """A friendly reply for a message that is only 'thanks' or 'bye', or None for a real question.

    The backend has no intent for these, so it would answer with an escalation note
    ("I'm not confident… contact the Training Office"), which reads like an error.
    """
    t = " ".join(unicodedata.normalize("NFC", text).lower().strip(" \t\n.!?,:;)(").split())
    if t in _THANKS:
        return "You're welcome! Ask me another question any time."
    if t in _BYE:
        return "Goodbye! Come back any time you have a question."
    return None


def format_sources(sources: list[dict]) -> str:
    """'Sources: H26#5.3 — 5.3 Thesis registration' or '' if none."""
    if not sources:
        return ""
    return "Sources: " + "; ".join(f"{s['id']} — {s['title']}" for s in sources)


def status_note(result: ChatResult) -> str | None:
    """A short note shown under the answer, explaining special situations."""
    if result.escalate:
        return "I could not find this in the official documents. A staff member can help: Training Office, room I.101."
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None
