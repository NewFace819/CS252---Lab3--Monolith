"""Shared fixtures.

The service is tested with fakes for every collaborator, so test_service.py does not
depend on knowledge / responder / router / tools being finished.
"""

from types import SimpleNamespace

import pytest

from assistant_core import service as service_module
from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.models import Intent, Office, Rule
from assistant_core.service import AssistantService

THESIS_RULE = Rule(id="H26-5.3", title="Thesis registration", text="Students may register a thesis ...")
LIBRARY = Office(name="Library", room="B.201", hours="Mon-Sat 07:00-20:00")


class FakeOffices:
    names = {"library"}

    def find(self, text):
        return LIBRARY if "library" in text.lower() else None


class FakeHandbook:
    def search(self, query):
        return THESIS_RULE if "thesis" in query.lower() else None


class FakeResponder:
    def __init__(self, fail=False):
        self.fail = fail

    def explain(self, question, rule):
        if self.fail:
            raise ProviderError("fake provider down")
        return f"LLM: {rule.text}"


class FakeTemplate:
    def explain(self, question, rule):
        return f"{rule.title}: {rule.text}"


def fake_route(text, office_names):
    t = text.lower().strip()
    if t in {"hi", "hello"}:
        return Intent.GREETING
    if "fee" in t or "tuition" in t:
        return Intent.FEE
    if any(name in t for name in office_names):
        return Intent.OFFICE
    return Intent.RULE


def fake_parse_credits(text):
    if "credits" not in text:
        raise InvalidRequest("How many credits?")
    return 18, 2


def fake_tuition(credits, retake, rate, retake_multiplier, max_credits):
    return int(credits * rate + retake * rate * retake_multiplier)


@pytest.fixture
def settings():
    return SimpleNamespace(credit_rate_vnd=450_000, retake_multiplier=1.5, max_credits=30)


@pytest.fixture
def service(monkeypatch, settings):
    monkeypatch.setattr(service_module, "route", fake_route)
    monkeypatch.setattr(service_module, "parse_credits", fake_parse_credits)
    monkeypatch.setattr(service_module, "tuition", fake_tuition)
    return AssistantService(settings, FakeOffices(), FakeHandbook(), FakeResponder(), fallback=FakeTemplate())
