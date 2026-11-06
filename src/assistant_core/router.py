"""Choose an Intent with simple rules.

Owner: Đức Huy (see issue). Contract below is fixed; replace the stub body.
"""

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})
HELP_REQUESTS = frozenset({"help", "what can you do", "what can you help with", "what do you do", "commands"})
FEE_WORDS = ("fee", "tuition")


def _normalise(text: str) -> str:
    return text.lower().strip().rstrip("?!.").strip()


def is_help(text: str) -> bool:
    """True only when the whole message asks what the assistant can do ("help me with my thesis" is not)."""
    return _normalise(text) in HELP_REQUESTS


def route(text: str, office_names: set[str]) -> Intent:
    """GREETING / FEE / OFFICE, otherwise RULE (the service turns a miss into UNKNOWN)."""
    t = _normalise(text)
    if t in GREETINGS or t in HELP_REQUESTS:
        return Intent.GREETING
    if any(word in t for word in FEE_WORDS):
        return Intent.FEE
    if any(name.lower() in t for name in office_names):
        return Intent.OFFICE
    return Intent.RULE
