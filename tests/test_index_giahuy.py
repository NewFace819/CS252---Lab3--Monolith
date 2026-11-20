"""Lab 6 H3: shared token normalization for indexing and queries."""

from pathlib import Path

import pytest

from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import Chunk, load_folder
from assistant_core.rag.index import make_index, tokenize


def test_trailing_s_rule_preserves_short_words_and_removes_stop_words():
    assert tokenize("The CREDITS, books, bus, this!") == ["credit", "book", "bus", "this"]


def test_normalized_stop_words_do_not_leak_into_index_or_query():
    assert tokenize("whats the retake fee") == ["retake", "fee"]
    assert tokenize("wheres the library") == ["library"]


def test_known_overstemming():
    # Document the assigned heuristic's limitations, not desirable English stemming.
    assert tokenize("class classes address addresses thesis theses") == [
        "clas",
        "classe",
        "addres",
        "addresse",
        "thesi",
        "these",
    ]
    assert tokenize("fees days") == ["fees", "days"]  # Four-letter plurals are intentionally unchanged.


@pytest.mark.parametrize("kind", ["bm25", "tfidf", "hybrid"])
def test_credit_load_retrieved_for_singular_and_plural_terms(kind):
    chunks = load_folder(Path(__file__).resolve().parents[1] / "data" / "kb")
    index = make_index(kind, chunks)
    singular = index.search("regular semester credit load")
    plural = index.search("regular semester credits loads")
    assert singular == plural
    assert plural[0].chunk.id == "H26#6.1"


@pytest.mark.parametrize("question", ["can I take 32 credits", "may I take 31 credits", "Can I register 35 credits?"])
def test_numeric_credit_questions_find_load_rule(question):
    chunks = load_folder(Path(__file__).resolve().parents[1] / "data" / "kb")
    response = RagAnswerer(make_index("bm25", chunks), None).answer(question)
    assert response.path == "retrieval" and response.sources[0].id == "H26#6.1"


def test_numeric_range_preference_is_not_specific_to_credit_documents():
    chunks = [
        Chunk("A", "doc", "Time", "The exam takes between 10 and 20 minutes.", "1", "office"),
        Chunk("B", "doc", "Credit load", "A semester is between 14 and 30 credits.", "1", "office"),
    ]
    index = make_index("bm25", chunks)
    assert index.search("can I take 35 credits")[0].chunk.id == "B"
    assert index.search("can I take 25 minutes")[0].chunk.id == "A"


@pytest.mark.parametrize("question", ["tell me about exams", "Please describe exams", "Explain refunds"])
def test_broad_one_topic_requests_abstain_without_model_call(question):
    class UnusedIndex:
        def search(self, query, k=3):
            pytest.fail("Broad ambiguous requests should abstain before retrieval/model calls")

    response = RagAnswerer(UnusedIndex(), None).answer(question)
    assert response.path == "abstain" and response.escalate


@pytest.mark.parametrize("question", ["tell me about exam absence", "reset my password"])
def test_specific_requests_are_still_answered(question):
    chunks = load_folder(Path(__file__).resolve().parents[1] / "data" / "kb")
    response = RagAnswerer(make_index("bm25", chunks), None).answer(question)
    assert response.path == "retrieval" and response.sources
