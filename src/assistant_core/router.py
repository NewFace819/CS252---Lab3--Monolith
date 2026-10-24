"""Choose an Intent with simple rules.

Owner: Đức Huy (see issue). Contract below is fixed; replace the stub body.
"""

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})
FEE_WORDS = ("fee", "tuition")


def route(text: str, office_names: set[str]) -> Intent:
    """GREETING / FEE / OFFICE, otherwise RULE (the service turns a miss into UNKNOWN)."""
    t = text.lower().strip()
    if t in GREETINGS:
        return Intent.GREETING
    if any(word in t for word in FEE_WORDS):
        return Intent.FEE
    if any(name.lower() in t for name in office_names):
        return Intent.OFFICE
    return Intent.RULE
