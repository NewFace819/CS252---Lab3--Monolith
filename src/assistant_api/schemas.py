"""Request / response models: the HTTP contract (see docs/lab4/README.md)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from assistant_core.models import Response


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str = "local"


class ChatResponse(Response):
    """The Lab 3 ``Response`` plus an id the user can later rate."""

    request_id: str


class FeedbackIn(BaseModel):
    request_id: str = Field(min_length=1)
    rating: Literal[-1, 0, 1]
    comment: str = ""


class FeedbackOut(FeedbackIn):
    id: int
    created_at: datetime


class Weather(BaseModel):
    location: str
    temperature_c: float
    description: str
    stale: bool = False
