"""Deterministic tuition calculation. Pure functions: no I/O, no globals.

Owner: Đức Huy (see issue). Contract below is fixed; replace the stub bodies.
"""


def parse_credits(text: str) -> tuple[int, int]:
    """Extract (credits, retake_credits) from e.g. 'fee for 18 credits and 2 retake'.

    Raises InvalidRequest("How many credits?") if no credit count is found.
    """
    raise NotImplementedError("tools.parse_credits — owned by Đức Huy")


def tuition(credits: int, retake: int, rate: int, retake_multiplier: float, max_credits: int) -> int:
    """credits * rate + retake * rate * retake_multiplier.

    Raises InvalidRequest if credits is not in 1..max_credits.
    """
    raise NotImplementedError("tools.tuition — owned by Đức Huy")
