"""AssistantService.handle(Message) -> Response — the only entry point.

Owner: Hải (see issue).
"""

import logging
import time

from assistant_core.config import Settings
from assistant_core.errors import ConfigError, InvalidRequest, ProviderError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

log = logging.getLogger("assistant_core")

GREETING_ANSWER = "Hello! I can help with offices, fees and rules."
UNKNOWN_ANSWER = "Sorry, I don't know that yet."

RESPONDERS: dict[str, type[Responder]] = {"stub": StubLLMResponder, "template": TemplateResponder}


class AssistantService:
    def __init__(self, settings, offices, handbook, responder, fallback=None):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = fallback or TemplateResponder()

    def handle(self, msg: Message) -> Response:
        start = time.perf_counter()
        response = self._dispatch(msg.text)
        log.info(
            "handled",
            extra={
                "intent": response.intent.value,
                "latency_ms": round((time.perf_counter() - start) * 1000, 1),
                "session": msg.session_id,
                "degraded": response.degraded,
            },
        )
        return response

    def _dispatch(self, text: str) -> Response:
        intent = route(text, self.offices.names)
        if intent is Intent.GREETING:
            return Response(answer=GREETING_ANSWER, intent=intent)
        if intent is Intent.FEE:
            return self._fee(text)
        if intent is Intent.OFFICE:
            office = self.offices.find(text)
            if office is not None:
                return Response(answer=f"{office.name}: room {office.room}, open {office.hours}.", intent=intent)
        return self._rule(text)

    def _fee(self, text: str) -> Response:
        s = self.settings
        try:
            credits, retake = parse_credits(text)
            total = tuition(credits, retake, s.credit_rate_vnd, s.retake_multiplier, s.max_credits)
        except InvalidRequest as exc:
            return Response(answer=str(exc), intent=Intent.FEE)
        return Response(answer=f"Your tuition is {total:,} VND.", intent=Intent.FEE)

    def _rule(self, text: str) -> Response:
        rule = self.handbook.search(text)
        if rule is None:
            return Response(answer=UNKNOWN_ANSWER, intent=Intent.UNKNOWN)
        sources = [Source(id=rule.id, title=rule.title)]
        try:
            answer = self.responder.explain(text, rule)
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = self.fallback.explain(text, rule)
            return Response(answer=answer, intent=Intent.RULE, sources=sources, degraded=True)
        return Response(answer=answer, intent=Intent.RULE, sources=sources)


def build_service(settings: Settings) -> AssistantService:
    """Wire every module together. Raises ConfigError / DataError at startup."""
    responder_cls = RESPONDERS.get(settings.llm_provider)
    if responder_cls is None:
        raise ConfigError(f"LLM_PROVIDER={settings.llm_provider!r} is not supported yet (Week 4).")
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    return AssistantService(settings, offices, handbook, responder_cls())
