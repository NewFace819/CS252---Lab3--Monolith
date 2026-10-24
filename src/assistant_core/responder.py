"""Response generation behind one interface (adapter pattern).

Owner: THA (see issue). The Protocol is fixed; replace the stub bodies.
"""

from typing import Protocol

from assistant_core.models import Rule


class Responder(Protocol):
    def explain(self, question: str, rule: Rule) -> str: ...


class TemplateResponder:
    """No AI: answer straight from the rule. Also the service's fallback."""

    def explain(self, question: str, rule: Rule) -> str:
        raise NotImplementedError("responder.TemplateResponder — owned by THA")


class StubLLMResponder:
    """Fake LLM for tests and offline runs. ``fail=True`` raises ProviderError."""

    def __init__(self, fail: bool = False):
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        raise NotImplementedError("responder.StubLLMResponder — owned by THA")
