"""Real-provider adapters must turn any malformed HTTP-200 response into ProviderError (review follow-up on #45).

No network: every request goes to an httpx.MockTransport.
"""

import json
from pathlib import Path

import httpx
import pytest

from assistant_core.errors import ProviderError
from assistant_core.llm import OllamaLLM, OpenAICompatibleLLM
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import make_index

KB = Path(__file__).resolve().parents[1] / "data" / "kb"
GOOD = json.dumps({"answer": "x", "source_ids": ["S26#3"], "confidence": 0.8, "abstain": False})


def transport(status=200, body=None, text=None):
    def handler(request):
        if text is not None:
            return httpx.Response(status, text=text)
        return httpx.Response(status, json=body)

    return httpx.MockTransport(handler)


def ollama(**kw):
    return OllamaLLM(transport=transport(**kw))


def openai(**kw):
    return OpenAICompatibleLLM("test-only-key", "test-model", transport=transport(**kw))


def test_ollama_returns_content():
    assert ollama(body={"message": {"content": GOOD}}).complete("prompt") == GOOD


def test_openai_returns_content():
    assert openai(body={"choices": [{"message": {"content": GOOD}}]}).complete("prompt") == GOOD


@pytest.mark.parametrize(
    "kw",
    [
        {"body": {"message": {"content": None}}},  # null content
        {"body": {"message": None}},  # null message -> TypeError before the fix
        {"body": {"message": {"content": 42}}},  # wrong type
        {"body": {"message": {"content": "   "}}},  # empty text
        {"body": {}},  # missing key
        {"body": ["not", "a", "dict"]},  # wrong shape
        {"text": "<html>proxy error</html>"},  # not JSON
        {"status": 500, "body": {"error": "down"}},  # HTTP error
    ],
)
def test_ollama_malformed_response_is_provider_error(kw):
    with pytest.raises(ProviderError):
        ollama(**kw).complete("prompt")


@pytest.mark.parametrize(
    "kw",
    [
        {"body": {"choices": [{"message": {"content": None}}]}},
        {"body": {"choices": [{"message": None}]}},
        {"body": {"choices": []}},
        {"body": {"choices": None}},
        {"text": "not json"},
        {"status": 429, "body": {"error": "rate limited"}},
    ],
)
def test_openai_malformed_response_is_provider_error(kw):
    with pytest.raises(ProviderError):
        openai(**kw).complete("prompt")


def test_malformed_provider_falls_back_to_retrieval():
    index = make_index("bm25", load_folder(KB))
    r = RagAnswerer(index, ollama(body={"message": None})).answer("I lost my student card")
    assert r.path == "retrieval" and r.degraded and r.sources[0].id == "S26#3"
