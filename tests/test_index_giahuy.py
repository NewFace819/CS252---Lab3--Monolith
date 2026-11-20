"""Lab 6 H3: shared token normalization for indexing and queries."""

from pathlib import Path

import pytest

from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import make_index, tokenize


def test_trailing_s_rule_preserves_short_words_and_removes_stop_words():
    assert tokenize("The CREDITS, books, bus, this, class, thesis!") == [
        "credit",
        "book",
        "bus",
        "this",
        "clas",
        "thesi",
    ]


@pytest.mark.parametrize("kind", ["bm25", "tfidf", "hybrid"])
def test_credit_load_retrieved_for_singular_and_plural_terms(kind):
    chunks = load_folder(Path(__file__).resolve().parents[1] / "data" / "kb")
    index = make_index(kind, chunks)
    singular = index.search("regular semester credit load")
    plural = index.search("regular semester credits loads")
    assert singular == plural
    assert plural[0].chunk.id == "H26#6.1"
