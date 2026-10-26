"""Command-line interface: ``python -m assistant_core "your question"``.

Owner: Hải (issue #1). Answers go to stdout, JSON logs to stderr.
"""

import sys

from pydantic import ValidationError

from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError, DataError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService

RESPONDERS: dict[str, type[Responder]] = {"stub": StubLLMResponder, "template": TemplateResponder}


def build_service(settings: Settings) -> AssistantService:
    """Wire every module together. Raises ConfigError / DataError at startup."""
    responder_cls = RESPONDERS.get(settings.llm_provider)
    if responder_cls is None:
        raise ConfigError(f"LLM_PROVIDER={settings.llm_provider!r} is not supported yet (Week 4).")
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    return AssistantService(settings, offices, handbook, responder_cls())


def ask(service: AssistantService, text: str) -> str:
    try:
        return service.handle(Message(text=text)).answer
    except ValidationError:
        return "Please type a question (1-2000 characters)."


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        settings = load_settings()
        setup_logging(settings.log_level)
        service = build_service(settings)
    except (ConfigError, DataError) as exc:
        print(f"startup failed: {exc}", file=sys.stderr)
        return 2

    if argv:
        print(ask(service, " ".join(argv)))
        return 0

    print("assistant ready (type 'quit' to exit)")
    while True:
        try:
            text = input("> ")
        except (EOFError, KeyboardInterrupt):
            break
        if text.strip() == "quit":
            break
        print(ask(service, text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
