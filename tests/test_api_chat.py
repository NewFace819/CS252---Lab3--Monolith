"""Skeleton + T1 tests: /health, /v1/chat and the shared error shape."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_core.models import Intent, Response, Source


class FakeService:
    def handle(self, msg):
        return Response(
            answer=f"echo: {msg.text}",
            intent=Intent.RULE,
            sources=[Source(id="H26-5.3", title="Thesis registration")],
        )


@pytest.fixture
def client():
    return TestClient(create_app(SimpleNamespace(), FakeService(), None))


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": "1.0.0"}


def test_chat_returns_response_and_request_id(client):
    r = client.post("/v1/chat", json={"message": "thesis", "session_id": "s1"})
    body = r.json()
    assert r.status_code == 200
    assert body["answer"] == "echo: thesis"
    assert body["intent"] == "rule"
    assert body["sources"] == [{"id": "H26-5.3", "title": "Thesis registration"}]
    assert body["degraded"] is False
    assert len(body["request_id"]) == 12


def test_chat_request_ids_are_unique(client):
    ids = {client.post("/v1/chat", json={"message": "hi"}).json()["request_id"] for _ in range(3)}
    assert len(ids) == 3


def test_chat_empty_message_is_422_with_error_shape(client):
    r = client.post("/v1/chat", json={"message": ""})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "invalid_request"
    assert "message" in r.json()["error"]["message"]


def test_unknown_path_uses_error_shape(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"
