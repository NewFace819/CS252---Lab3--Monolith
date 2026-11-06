"""T2/T3 tests use isolated apps and no real secrets or external services."""

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.weather import WeatherClient
from assistant_core.config import Settings

ADMIN_KEY = "test-only-admin"


def make_client(key=ADMIN_KEY):
    weather = WeatherClient(
        "https://example.test/forecast", 0, 0, transport=httpx.MockTransport(lambda request: httpx.Response(500))
    )
    return TestClient(create_app(Settings(api_admin_key=key), object(), weather))


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
    assert response.json()["comment"] is None


def test_feedback_accepts_null_comment_and_schema_boundaries(client):
    for comment in (None, "a" * 500):
        payload = {"request_id": "r" * 64, "rating": 1, "comment": comment}
        response = client.post("/v1/feedback", json=payload)
        assert response.status_code == 201
        assert response.json()["comment"] == comment
        assert response.json()["request_id"] == payload["request_id"]


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
        {"request_id": "r" * 65, "rating": 1},
        {"request_id": "r", "rating": 1, "comment": "a" * 501},
    ],
)
def test_invalid_feedback_is_422_and_not_saved(client, payload):
    response = client.post("/v1/feedback", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert client.get("/v1/feedback", headers={"X-API-Key": ADMIN_KEY}).json() == []


@pytest.mark.parametrize("key", [None, "", "wrong-test-key"])
def test_admin_missing_or_wrong_key_is_401_without_leaks(client, key):
    headers = {} if key is None else {"X-API-Key": key}
    response = client.get("/v1/feedback", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "missing_or_invalid_api_key", "message": "Missing or invalid API key"}}
    assert ADMIN_KEY not in response.text
    if key:
        assert key not in response.text


@pytest.mark.parametrize("configured_key", [None, ""])
def test_disabled_admin_key_never_authorizes(configured_key):
    with make_client(configured_key) as client:
        for supplied_key in ("", "change-me", ADMIN_KEY):
            response = client.get("/v1/feedback", headers={"X-API-Key": supplied_key})
            assert response.status_code == 401


def test_feedback_is_isolated_between_app_instances(client):
    assert client.post("/v1/feedback", json={"request_id": "r", "rating": 1}).status_code == 201
    with make_client() as other:
        assert other.get("/v1/feedback", headers={"X-API-Key": ADMIN_KEY}).json() == []
