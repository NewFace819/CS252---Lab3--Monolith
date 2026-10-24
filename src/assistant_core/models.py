"""Shared types — the contract every module codes against.

Leaf modules (config, knowledge, tools, router, responder) import only from
``errors`` and ``models``, never from each other. That is what lets each
member own one module and work in parallel.
"""

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


class Intent(str, Enum):
    GREETING = "greeting"
    FEE = "fee"
    OFFICE = "office"
    RULE = "rule"
    UNKNOWN = "unknown"


# --- Public API: what the CLI, the Lab 4 backend and the Lab 7 UI see ---


class Message(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    session_id: str = "local"


class Source(BaseModel):
    id: str
    title: str


class Response(BaseModel):
    answer: str
    intent: Intent
    sources: list[Source] = []
    degraded: bool = False


# --- Domain records: produced by knowledge.py, consumed by responder.py / service.py ---


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str
