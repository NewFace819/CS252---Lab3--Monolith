"""Extra API tests: error shape and admin-key edge cases not covered by test_api.py."""

import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app

ADMIN = {"X-API-Key": "secret-admin"}


@pytest.fixture
def client(settings, service):
    settings = settings.model_copy(update={"api_admin_key": "secret-admin"})
    return TestClient(create_app(settings, service, None))


def test_health_reports_version(client):
    assert client.get("/health").json() == {"status": "ok", "version": "1.0.0"}


def test_chat_response_has_contract_fields(client):
    body = client.post("/v1/chat", json={"message": "tuition for 18 credits and 2 retake"}).json()
    assert set(body) == {"answer", "intent", "sources", "degraded", "request_id"}
    assert len(body["request_id"]) == 12


def test_chat_empty_message_uses_error_shape(client):
    r = client.post("/v1/chat", json={"message": ""})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "invalid_request"


def test_feedback_list_without_key_uses_error_shape(client):
    r = client.get("/v1/feedback")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "missing_or_invalid_api_key"


def test_feedback_list_wrong_key_is_401(client):
    assert client.get("/v1/feedback", headers={"X-API-Key": "wrong"}).status_code == 401


def test_feedback_ids_increase_and_are_listed(client):
    first = client.post("/v1/feedback", json={"request_id": "r1", "rating": 1}).json()
    second = client.post("/v1/feedback", json={"request_id": "r2", "rating": -1}).json()
    assert second["id"] == first["id"] + 1
    ids = [item["request_id"] for item in client.get("/v1/feedback", headers=ADMIN).json()]
    assert "r1" in ids and "r2" in ids


def test_unknown_route_uses_error_shape(client):
    r = client.get("/v1/nope")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"
