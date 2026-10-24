"""Deterministic tuition calculation. Pure functions: no I/O, no globals.

Owner: Đức Huy (see issue). Contract below is fixed; replace the stub bodies.
"""

from assistant_core.errors import InvalidRequest

_PUNCTUATION = str.maketrans({c: " " for c in "?!,;:"})


def parse_credits(text: str) -> tuple[int, int]:
    """Extract (credits, retake_credits) from e.g. 'fee for 18 credits and 2 retake'.

    Raises InvalidRequest("How many credits?") if no credit count is found.
    """
    words = text.lower().translate(_PUNCTUATION).split()
    credits: int | None = None
    retake = 0
    for i, word in enumerate(words):
        if not word.isdigit():
            continue
        next_word = words[i + 1] if i + 1 < len(words) else ""
        if next_word.startswith("retake"):
            retake = int(word)
        elif credits is None:
            credits = int(word)
    if credits is None:
        raise InvalidRequest("How many credits?")
    return credits, retake


def tuition(credits: int, retake: int, rate: int, retake_multiplier: float, max_credits: int) -> int:
    """credits * rate + retake * rate * retake_multiplier.

    Raises InvalidRequest if credits is not in 1..max_credits.
    """
    if not 1 <= credits <= max_credits:
        raise InvalidRequest(f"Credits must be between 1 and {max_credits}.")
    if retake < 0:
        raise InvalidRequest("Retake credits cannot be negative.")
    return int(credits * rate + retake * rate * retake_multiplier)
