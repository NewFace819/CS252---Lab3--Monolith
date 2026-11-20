"""Boundary checks for Gia Huy's Lab 6 A1/A2 safety requirements."""

import json

import pytest

from assistant_core.errors import ProviderError
from assistant_core.llm import parse_draft
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import Chunk
from assistant_core.rag.index import Hit


@pytest.mark.parametrize("ids", [[], ["allowed", "invented"]])
def test_non_abstaining_answer_requires_only_retrieved_citations(ids):
    raw = json.dumps({"answer": "answer", "source_ids": ids, "confidence": 0.7})
    with pytest.raises(ProviderError, match="not retrieved"):
        parse_draft(raw, {"allowed"})


def test_abstaining_answer_needs_no_citation():
    draft = parse_draft('{"answer":"", "confidence":0, "abstain":true}', set())
    assert draft.abstain and draft.source_ids == []


@pytest.mark.parametrize("score", [None, 1.999, 2.0])
def test_retrieval_threshold_and_no_model_call_below_it(score):
    chunk = Chunk("test#1", "test", "Title", "Official passage.", "1", "Office")

    class FixedIndex:
        def search(self, query, k=3):
            return [] if score is None else [Hit(chunk, score)]

    class RecordingLLM:
        calls = 0

        def complete(self, prompt):
            self.calls += 1
            return '{"answer":"Official passage.","source_ids":["test#1"],"confidence":0.7}'

    llm = RecordingLLM()
    response = RagAnswerer(FixedIndex(), llm, min_score=2.0).answer("question")
    if score is None or score < 2.0:
        assert response.path == "abstain" and response.escalate
        assert response.confidence == 0.0 and response.sources == []
        assert llm.calls == 0
    else:
        assert response.path == "llm" and llm.calls == 1
