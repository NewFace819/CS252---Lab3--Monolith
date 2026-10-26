import pytest

from assistant_core.errors import AssistantError, ProviderError
from assistant_core.models import Rule
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder


@pytest.fixture
def rule() -> Rule:
    return Rule(id="H26-5.3", title="Thesis registration", text="Students need 100 credits to register a thesis.")


def test_template_answers_from_rule(rule):
    assert TemplateResponder().explain("thesis?", rule) == f"{rule.title}: {rule.text}"


def test_template_ignores_question(rule):
    r = TemplateResponder()
    assert r.explain("a", rule) == r.explain("b", rule)


def test_stub_answers_from_rule(rule):
    assert StubLLMResponder().explain("thesis?", rule) == f"Based on '{rule.title}': {rule.text}"


def test_stub_is_deterministic(rule):
    r = StubLLMResponder()
    assert len({r.explain("thesis?", rule) for _ in range(20)}) == 1


def test_stub_fail_raises_provider_error(rule):
    with pytest.raises(ProviderError, match="unavailable"):
        StubLLMResponder(fail=True).explain("thesis?", rule)


def test_provider_error_is_assistant_error(rule):
    with pytest.raises(AssistantError):
        StubLLMResponder(fail=True).explain("thesis?", rule)


def test_stub_fail_can_be_toggled(rule):
    r = StubLLMResponder()
    r.fail = True
    with pytest.raises(ProviderError):
        r.explain("q", rule)
    r.fail = False
    assert r.explain("q", rule)


@pytest.mark.parametrize("impl", [TemplateResponder(), StubLLMResponder()])
def test_implementations_satisfy_protocol(impl, rule):
    responder: Responder = impl
    assert isinstance(responder.explain("q", rule), str)
