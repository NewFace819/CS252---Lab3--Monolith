"""AssistantService.handle(Message) -> Response — the only entry point.

Owner: Hải (see issue).
"""

from assistant_core.models import Message, Response


class AssistantService:
    def __init__(self, settings, offices, handbook, responder):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder

    def handle(self, msg: Message) -> Response:
        raise NotImplementedError("service.AssistantService.handle — owned by Hải")
