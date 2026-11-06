"""H1 (Lab 3): exam-absence answers give the exact deadline from the handbook rule."""

import json
import logging
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService
from assistant_core.tools import add_working_days, parse_date, working_days_limit

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture
def real_service():
    settings = SimpleNamespace(credit_rate_vnd=450_000, retake_multiplier=1.5, max_credits=30)
    return AssistantService(
        settings,
        OfficeDirectory.from_csv(DATA / "offices.csv"),
        Handbook.from_json(DATA / "handbook.json"),
        StubLLMResponder(),
        fallback=TemplateResponder(),
    )


def test_parse_date_finds_iso_date():
    assert parse_date("I missed the final exam on 2026-11-06, what now?") == date(2026, 11, 6)


@pytest.mark.parametrize("text", ["I missed the final exam yesterday", "missed the exam on 2026-02-30"])
def test_parse_date_returns_none_without_a_valid_date(text):
    assert parse_date(text) is None


def test_working_days_limit_reads_the_rule():
    assert working_days_limit("submit evidence to the Training Office within 3 working days.") == 3
    assert working_days_limit("Late thesis registration requires approval.") is None


@pytest.mark.parametrize(
    ("start", "expected"),
    [
        (date(2026, 11, 2), date(2026, 11, 5)),  # Monday -> Thursday
        (date(2026, 11, 6), date(2026, 11, 11)),  # Friday -> Wednesday, weekend skipped
        (date(2026, 11, 7), date(2026, 11, 11)),  # Saturday -> Wednesday
    ],
)
def test_add_working_days_skips_weekends(start, expected):
    assert add_working_days(start, 3) == expected


def test_add_working_days_rejects_negative():
    with pytest.raises(InvalidRequest):
        add_working_days(date(2026, 11, 6), -1)


def test_exam_absence_with_date_gives_exact_deadline(real_service):
    r = real_service.handle(Message(text="I was absent from my final exam on 2026-11-06 for medical reasons"))
    assert r.intent is Intent.RULE
    assert [s.id for s in r.sources] == ["H26-7.2"]
    assert r.answer.endswith("Deadline: Wednesday 2026-11-11 (3 working days after 2026-11-06).")


def test_exam_absence_without_date_keeps_the_rule_answer(real_service):
    r = real_service.handle(Message(text="I was absent from my final exam, what should I do?"))
    assert [s.id for s in r.sources] == ["H26-7.2"]
    assert "Deadline:" not in r.answer and "3 working days" in r.answer


def test_deadline_is_kept_when_provider_fails(real_service):
    real_service.responder = StubLLMResponder(fail=True)
    r = real_service.handle(Message(text="absent from final exam on 2026-11-06"))
    assert r.degraded
    assert r.answer.startswith("Exam absence:") and "Wednesday 2026-11-11" in r.answer


def test_rule_without_working_days_is_unchanged(real_service):
    r = real_service.handle(Message(text="thesis registration credits on 2026-11-06"))
    assert [s.id for s in r.sources] == ["H26-5.3"]
    assert "Deadline:" not in r.answer


def test_question_text_is_not_logged(real_service, caplog):
    with caplog.at_level(logging.DEBUG, logger="assistant_core"):
        real_service.handle(Message(text="absent from final exam on 2026-11-06 private-note"))
    assert all("private-note" not in json.dumps(rec.__dict__, default=str) for rec in caplog.records)
