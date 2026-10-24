"""Choose an Intent with simple rules.

Owner: Đức Huy (see issue). Contract below is fixed; replace the stub body.
"""

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})


def route(text: str, office_names: set[str]) -> Intent:
    """GREETING / FEE / OFFICE, otherwise RULE (the service turns a miss into UNKNOWN)."""
    raise NotImplementedError("router.route — owned by Đức Huy")
