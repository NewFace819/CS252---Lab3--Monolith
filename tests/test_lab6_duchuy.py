"""Edge cases for A1 (abstain) and A2 (grounding) that tests/test_rag.py does not cover."""

import json
from pathlib import Path

import pytest

from assistant_core.errors import ProviderError
from assistant_core.llm import parse_draft
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import Hit

CHUNK = load_folder(Path(__file__).resolve().parents[1] / "data" / "kb")[0]


class FixedIndex:
    """Always returns one hit with the given score."""

    def __init__(self, score: float):
        self.score = score

    def search(self, query, k=3):
        return [Hit(CHUNK, self.score)]


class MustNotCall:
    name = "must-not-call"

    def complete(self, prompt):
        raise AssertionError("the LLM must not be called when abstaining")


def draft(**kw) -> str:
    return json.dumps({"answer": "x", "confidence": 0.5, **kw})


def test_a2_rejects_answer_without_sources():
    with pytest.raises(ProviderError):
        parse_draft(draft(source_ids=[]), {"A"})


def test_a2_allows_abstain_without_sources():
    assert parse_draft(draft(source_ids=[], abstain=True), {"A"}).abstain


def test_a1_low_score_hit_abstains_without_calling_llm():
    r = RagAnswerer(FixedIndex(1.9), MustNotCall(), min_score=2.0).answer("q")
    assert r.path == "abstain" and r.escalate and r.confidence == 0.0


def test_a1_score_equal_to_threshold_is_answered():
    assert RagAnswerer(FixedIndex(2.0), None, min_score=2.0).answer("q").path == "retrieval"
