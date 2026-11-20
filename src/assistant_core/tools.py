"""Deterministic tuition calculation. Pure functions: no I/O, no globals.

Owner: Đức Huy (see issue). Contract below is fixed; replace the stub bodies.
"""

import json
import re
from datetime import date, timedelta

from pydantic import BaseModel, Field, ValidationError

from assistant_core.errors import InvalidRequest

_PUNCTUATION = str.maketrans({c: " " for c in "?!,;:"})
_ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_WORKING_DAYS = re.compile(r"within (\d+) working days?", re.IGNORECASE)


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


def parse_date(text: str) -> date | None:
    """The one valid YYYY-MM-DD date in ``text``, or None.

    None if there is no valid date (2026-02-30 does not count) or several different ones, because then we cannot
    tell which is the exam date ("Today is 2026-11-06. I missed my exam on 2026-11-02.").
    """
    found: set[date] = set()
    for match in _ISO_DATE.finditer(text):
        try:
            found.add(date(*(int(part) for part in match.groups())))
        except ValueError:
            continue
    return found.pop() if len(found) == 1 else None


def working_days_limit(rule_text: str) -> int | None:
    """N from 'within N working days' in a handbook rule, or None if the rule has no such limit."""
    match = _WORKING_DAYS.search(rule_text)
    return int(match.group(1)) if match else None


def add_working_days(start: date, days: int) -> date:
    """The date ``days`` working days (Mon-Fri) after ``start``. Public holidays are not counted."""
    if days < 0:
        raise InvalidRequest("Working days cannot be negative.")
    current = start
    while days > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            days -= 1
    return current


# ---------------------------------------------------------------- Lab 6: tool calling (from the starter)
# An LLM may ask for a tool with JSON like {"tool": "calc_fee", "args": {"credits": 18, "retake": 2}}.
# We never trust the arguments: they are validated with a schema, then a deterministic function runs.


class FeeArgs(BaseModel):
    credits: int = Field(ge=1, le=30)
    retake: int = Field(default=0, ge=0, le=30)


TOOL_SPECS = {
    "calc_fee": {
        "description": "Compute tuition in VND for a number of credits and retake credits.",
        "parameters": FeeArgs.model_json_schema(),
    },
}


def run_tool_call(raw: str, rate: int, retake_multiplier: float, max_credits: int) -> str | None:
    """Return the tool result as text, or None if `raw` is not a tool call. Raises InvalidRequest on bad args."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or "tool" not in data:
        return None
    if data["tool"] != "calc_fee":
        raise InvalidRequest(f"unknown tool {data['tool']!r}")
    try:
        args = FeeArgs.model_validate(data.get("args", {}))
    except ValidationError as exc:
        raise InvalidRequest("invalid tool arguments") from exc
    total = tuition(args.credits, args.retake, rate, retake_multiplier, max_credits)
    return f"Your tuition is {total:,} VND."
