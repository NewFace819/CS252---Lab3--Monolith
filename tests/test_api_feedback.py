"""T2/T3 tests use isolated apps and no real secrets or external services."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_core.config import Settings

ADMIN_KEY = "test-only-admin"


def make_client(key=ADMIN_KEY):
    return TestClient(create_app(settings=Settings(api_admin_key=key), service=object()))


@pytest.fixture
def client():
    with make_client() as client:
        yield client


def test_feedback_roundtrip_ids_and_utc_time(client):
    before = datetime.now(timezone.utc)
    for expected_id, rating in enumerate((-1, 0, 1), start=1):
        payload = {"request_id": f"request-{expected_id}", "rating": rating, "comment": "Rõ ràng"}
        response = client.post("/v1/feedback", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert {key: body[key] for key in payload} == payload
        assert body["id"] == expected_id
        created = datetime.fromisoformat(body["created_at"].replace("Z", "+00:00"))
        assert created.utcoffset() == timedelta(0)
        assert before <= created <= datetime.now(timezone.utc)
    listed = client.get("/v1/feedback", headers={"X-API-Key": ADMIN_KEY})
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [1, 2, 3]


def test_feedback_comment_can_be_omitted(client):
    response = client.post("/v1/feedback", json={"request_id": "r", "rating": 0})
    assert response.status_code == 201
    assert response.json()["request_id"] == "r"


@pytest.mark.parametrize(
    "payload",
    [
        {"request_id": "r", "rating": 5},
        {"request_id": "r", "rating": -2},
        {"request_id": "", "rating": 1},
        {"rating": 1},
        {"request_id": "r"},
        {"request_id": None, "rating": 1},
        {"request_id": "r", "rating": None},
    ],
)
def test_invalid_feedback_is_422_and_not_saved(client, payload):
    response = client.post("/v1/feedback", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert client.get("/v1/feedback", headers={"X-API-Key": ADMIN_KEY}).json() == []


@pytest.mark.parametrize("key", [None, "", "wrong-test-key", "test-κλειδί"])
def test_admin_missing_or_wrong_key_is_401_without_leaks(client, key):
    headers = {} if key is None else {"X-API-Key": key.encode("utf-8")}
    response = client.get("/v1/feedback", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "unauthorized", "message": "Missing or invalid API key"}}
    assert ADMIN_KEY not in response.text
    if key:
        assert key not in response.text


def test_empty_configured_key_never_authorizes():
    with make_client("") as client:
        assert client.get("/v1/feedback", headers={"X-API-Key": ""}).status_code == 401


def test_feedback_is_isolated_between_app_instances(client):
    assert client.post("/v1/feedback", json={"request_id": "r", "rating": 1}).status_code == 201
    with make_client() as other:
        assert other.get("/v1/feedback", headers={"X-API-Key": ADMIN_KEY}).json() == []
