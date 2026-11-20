"""Choose an Intent with simple rules.

Owner: Đức Huy (see issue). Contract below is fixed; replace the stub body.
"""

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})
FEE_WORDS = ("fee", "tuition")
# Lab 6 bonus (E22): campus-service fees that the knowledge base documents. They are not tuition, so the
# question must reach retrieval instead of the tuition calculator ("how much is the student card replacement fee").
SERVICE_FEE_WORDS = ("replacement", "student card")


def _is_service_fee(t: str) -> bool:
    """A fee question about a documented service, with no tuition word and no credit count to calculate with."""
    return "tuition" not in t and not any(ch.isdigit() for ch in t) and any(word in t for word in SERVICE_FEE_WORDS)


def route(text: str, office_names: set[str]) -> Intent:
    """GREETING / FEE / OFFICE, otherwise RULE (the service turns a miss into UNKNOWN)."""
    t = text.lower().strip().rstrip("?!.")
    if t in GREETINGS:
        return Intent.GREETING
    if any(word in t for word in FEE_WORDS) and not _is_service_fee(t):
        return Intent.FEE
    if any(name.lower() in t for name in office_names):
        return Intent.OFFICE
    return Intent.RULE
