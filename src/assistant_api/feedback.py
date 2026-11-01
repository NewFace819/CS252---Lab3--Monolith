"""Feedback endpoints (T2/T3), owned by Thông (vbthg).

The store belongs to each app instance and is intentionally lost on restart.
"""

from datetime import datetime, timezone
from secrets import compare_digest

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from assistant_api.schemas import FeedbackIn, FeedbackOut

router = APIRouter()


def require_admin(request: Request, x_api_key: str | None = Header(default=None)) -> None:
    expected = getattr(request.app.state.settings, "api_admin_key", "")
    # An empty configured key never enables access; errors never echo either key.
    if not expected or x_api_key is None or not compare_digest(x_api_key.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")


@router.post("/v1/feedback", response_model=FeedbackOut, status_code=201, tags=["feedback"])
async def add_feedback(fb: FeedbackIn, request: Request) -> FeedbackOut:
    store = request.app.state.feedback_store
    item = FeedbackOut(**fb.model_dump(), id=len(store) + 1, created_at=datetime.now(timezone.utc))
    store.append(item)
    return item


@router.get("/v1/feedback", response_model=list[FeedbackOut], tags=["feedback"], dependencies=[Depends(require_admin)])
async def list_feedback(request: Request) -> list[FeedbackOut]:
    return request.app.state.feedback_store
