"""AssistantService.handle(Message) -> Response — the only entry point.

Owner: Hải (see issue).
"""

import logging
import time

from assistant_core.config import Settings
from assistant_core.errors import ConfigError, InvalidRequest, ProviderError
from assistant_core.guard import PRIVATE_REPLY, is_private_request
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.llm import make_llm
from assistant_core.models import Intent, Message, Response, Rule, Source
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import make_index
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder
from assistant_core.router import route
from assistant_core.tools import (
    add_working_days,
    parse_credits,
    parse_date,
    run_tool_call,
    tuition,
    working_days_limit,
)

log = logging.getLogger("assistant_core")

GREETING_ANSWER = "Hello! I can help with offices, fees and rules."
UNKNOWN_ANSWER = "Sorry, I don't know that yet."

RESPONDERS: dict[str, type[Responder]] = {"stub": StubLLMResponder, "template": TemplateResponder}
# Lab 6: real models answer through the RAG path; the old handbook path then uses the template.
LLM_PROVIDERS = {"stub", "template", "ollama", "openai"}


class AssistantService:
    def __init__(self, settings, offices, handbook, responder, rag: RagAnswerer | None = None, fallback=None):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.rag = rag  # Lab 6: retrieval + LLM for rule questions (None = Lab 5 handbook path)
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
        answer = f"Your tuition is {total:,} VND."
        if "breakdown" in text.lower().split():
            regular = credits * s.credit_rate_vnd
            # Derive the retake portion from the validated total: same rounding as tuition().
            answer += f" Regular: {regular:,} VND; retake: {total - regular:,} VND."
        return Response(answer=answer, intent=Intent.FEE)

    def _rule(self, text: str) -> Response:
        if self.rag is not None:  # Lab 6: guard first, then retrieval + LLM with abstain
            if is_private_request(text):
                return Response(answer=PRIVATE_REPLY, intent=Intent.UNKNOWN, path="abstain", escalate=False)
            resp = self.rag.answer(text)
            if resp.path in ("llm", "retrieval"):
                resp.answer = _with_deadline_text(resp.answer, text, resp.answer)
            return resp
        rule = self.handbook.search(text)
        if rule is None:
            return Response(answer=UNKNOWN_ANSWER, intent=Intent.UNKNOWN)
        sources = [Source(id=rule.id, title=rule.title)]
        try:
            answer = self.responder.explain(text, rule)
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = _with_deadline(self.fallback.explain(text, rule), text, rule)
            return Response(answer=answer, intent=Intent.RULE, sources=sources, degraded=True)
        return Response(answer=_with_deadline(answer, text, rule), intent=Intent.RULE, sources=sources)


def _with_deadline(answer: str, text: str, rule: Rule) -> str:
    """If the rule sets 'within N working days' and the question gives a date, add the exact deadline."""
    return _with_deadline_text(answer, text, rule.text)


def _with_deadline_text(answer: str, text: str, rule_text: str) -> str:
    days = working_days_limit(rule_text)
    start = parse_date(text)
    if days is None or start is None:
        return answer
    deadline = add_working_days(start, days)
    return f"{answer} Deadline: {deadline:%A %Y-%m-%d} ({days} working days after {start:%Y-%m-%d})."


def build_service(settings: Settings) -> AssistantService:
    """Wire every module together. Raises ConfigError / DataError at startup."""
    if settings.llm_provider not in LLM_PROVIDERS:
        raise ConfigError(f"LLM_PROVIDER={settings.llm_provider!r} is not supported.")
    responder_cls = RESPONDERS.get(settings.llm_provider, TemplateResponder)
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    return AssistantService(settings, offices, handbook, responder_cls(), _build_rag(settings))


def _build_rag(settings: Settings) -> RagAnswerer | None:
    """Lab 6: index data/kb and pick the LLM. No knowledge base folder -> keep the Lab 5 handbook path."""
    if not settings.kb_dir.exists():
        return None
    s = settings
    index = make_index(s.retrieval_kind, load_folder(s.kb_dir))
    llm = (
        None
        if s.llm_provider == "template"
        else make_llm(s.llm_provider, s.llm_model, s.llm_base_url, s.llm_api_key, s.llm_timeout_s)
    )

    def tool_runner(raw: str) -> str | None:
        return run_tool_call(raw, s.credit_rate_vnd, s.retake_multiplier, s.max_credits)

    return RagAnswerer(index, llm, s.retrieval_min_score, prompt_version=s.prompt_version, tool_runner=tool_runner)
