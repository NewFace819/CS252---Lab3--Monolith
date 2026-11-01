"""FastAPI app factory: ``uvicorn assistant_api.main:create_app --factory``.

Owner: Hải. Other members add their router with one ``include_router`` line below.
"""

import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from assistant_api.offices import router as offices_router
from assistant_api.ratelimit import RateLimiter
from assistant_api.schemas import ChatRequest, ChatResponse
from assistant_core.__main__ import build_service
from assistant_core.config import load_settings
from assistant_core.models import Message

API_VERSION = "1.0.0"

ERROR_CODES = {
    401: "unauthorized",
    404: "not_found",
    422: "invalid_request",
    429: "too_many_requests",
    503: "service_unavailable",
}


def error(status_code: int, code: str, message: str) -> JSONResponse:
    """Every error looks the same: {"error": {"code": ..., "message": ...}}."""
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


def create_app(settings=None, service=None, weather_client=None, rate_limiter=None) -> FastAPI:
    """Build the app. Tests pass fakes; uvicorn --factory passes nothing and gets the real parts."""
    if settings is None:
        settings = load_settings()
    if service is None:
        service = build_service(settings)
    if rate_limiter is None:
        rate_limiter = RateLimiter()

    app = FastAPI(title="Study Assistant API", version=API_VERSION)
    app.state.settings = settings
    app.state.service = service
    app.state.weather_client = weather_client
    app.state.rate_limiter = rate_limiter

    # Starlette's class also covers the router's own 404 / 405, not only our raised HTTPException.
    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = ERROR_CODES.get(exc.status_code, "http_error")
        return error(exc.status_code, code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]
        field = ".".join(str(part) for part in first["loc"] if part != "body")
        return error(422, "invalid_request", f"{field}: {first['msg']}")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "version": API_VERSION}

    @app.post("/v1/chat")
    def chat(req: ChatRequest, request: Request) -> ChatResponse:
        client_id = request.client.host if request.client else "unknown"
        limiter = getattr(request.app.state, "rate_limiter", None)
        if limiter is not None and not limiter.allow(client_id):
            raise StarletteHTTPException(429, "Rate limit exceeded")
        resp = request.app.state.service.handle(Message(text=req.message, session_id=req.session_id))
        return ChatResponse(**resp.model_dump(), request_id=uuid.uuid4().hex[:12])

    # app.include_router(feedback_router)   # Thông  — T2/T3
    # app.include_router(weather_router)    # Đức Huy — T4
    app.include_router(offices_router)
    return app
