"""Issue #33: exercise real file persistence, stats and privacy through the API.

PR #38's feedback changes were reviewed and approved by vbthg before merge.
These tests complement the in-memory feedback tests without changing their fixtures.
"""

import sqlite3

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from assistant_api import main as main_module
from assistant_api.db import ChatSession, Feedback, Interaction, make_engine

ADMIN_KEY = "test-only-persistence-admin"
ADMIN = {"X-API-Key": ADMIN_KEY}


@pytest.fixture
def file_app_factory(tmp_path, monkeypatch, settings, service):
    # The root autouse fixture forces in-memory engines. Restore only this test's
    # app factory so database_url really selects a temporary file and can be reopened.
    monkeypatch.setattr(main_module, "make_engine", make_engine)
    engines = []
    file_settings = settings.model_copy(
        update={
            "database_url": f"sqlite:///{(tmp_path / 'assistant.db').as_posix()}",
            "api_admin_key": ADMIN_KEY,
            "session_salt": "test-only-persistence-salt",
        }
    )

    def factory(**changes):
        app = main_module.create_app(file_settings.model_copy(update=changes), service, weather=object())
        engines.append(app.state.repo.engine)
        return app

    yield factory
    for engine in engines:
        engine.dispose()


def test_feedback_survives_app_restart_on_same_file(file_app_factory):
    first = file_app_factory()
    with TestClient(first) as client:
        chat = client.post("/v1/chat", json={"message": "hi", "session_id": "restart-session"})
        assert chat.status_code == 200
        saved = client.post("/v1/feedback", json={"request_id": chat.json()["request_id"], "rating": 1})
        assert saved.status_code == 201
    first.state.repo.engine.dispose()

    restarted = file_app_factory()
    assert restarted.state.repo.engine is not first.state.repo.engine
    with TestClient(restarted) as client:
        assert client.get("/v1/feedback").status_code == 401
        listed = client.get("/v1/feedback", headers=ADMIN)
        assert listed.status_code == 200
        assert listed.json() == [saved.json()]
        stats = client.get("/v1/stats/intents", headers=ADMIN)
        assert stats.status_code == 200
        assert stats.json()[0]["intent"] == "greeting"
        assert stats.json()[0]["requests"] == 1


def test_unknown_feedback_id_is_404_and_does_not_write(file_app_factory):
    app = file_app_factory()
    with TestClient(app) as client:
        response = client.post("/v1/feedback", json={"request_id": "nope", "rating": 1})
        assert response.status_code == 404
        assert response.json() == {"error": {"code": "unknown_request_id", "message": "Unknown request id"}}
        assert client.get("/v1/feedback", headers=ADMIN).json() == []
    with Session(app.state.repo.engine) as db:
        assert db.exec(select(Feedback)).all() == []
        assert db.exec(select(Interaction)).all() == []


@pytest.mark.parametrize("key", [None, "", "wrong-test-key"])
def test_stats_require_valid_admin_key(file_app_factory, key):
    with TestClient(file_app_factory()) as client:
        headers = {} if key is None else {"X-API-Key": key}
        response = client.get("/v1/stats/intents", headers=headers)
        assert response.status_code == 401
        assert response.json() == {
            "error": {"code": "missing_or_invalid_api_key", "message": "Missing or invalid API key"}
        }
        assert ADMIN_KEY not in response.text


@pytest.mark.parametrize("configured_key", [None, ""])
def test_stats_disabled_admin_never_authorizes(file_app_factory, configured_key):
    with TestClient(file_app_factory(api_admin_key=configured_key)) as client:
        assert client.get("/v1/stats/intents", headers=ADMIN).status_code == 401


def test_stats_empty_database_is_empty_list(file_app_factory):
    with TestClient(file_app_factory()) as client:
        response = client.get("/v1/stats/intents", headers=ADMIN)
        assert response.status_code == 200
        assert response.json() == []


def test_stats_aggregate_counts_latency_and_unresolved(file_app_factory):
    app = file_app_factory()
    repo = app.state.repo
    # Fixed latencies make averaging deterministic; HTTP chat persistence is covered
    # separately above. A degraded but resolved response must not count as unresolved.
    for request_id, intent, resolved, degraded, latency in [
        ("r1", "rule", True, False, 10.0),
        ("r2", "rule", True, True, 20.1),
        ("u1", "unknown", False, False, 3.0),
    ]:
        repo.record_interaction("stats-session", request_id, intent, None, resolved, degraded, latency)
    with TestClient(app) as client:
        response = client.get("/v1/stats/intents", headers=ADMIN)
        assert response.status_code == 200
        assert response.json() == [
            {"intent": "rule", "requests": 2, "avg_latency_ms": 15.1, "unresolved": 0},
            {"intent": "unknown", "requests": 1, "avg_latency_ms": 3.0, "unresolved": 1},
        ]


def test_chat_stores_salted_session_hash_and_no_raw_message(file_app_factory):
    raw_session = "private-session-42"
    raw_message = "private-question-do-not-persist"
    app = file_app_factory()
    with TestClient(app) as client:
        for _ in range(2):
            response = client.post("/v1/chat", json={"message": raw_message, "session_id": raw_session})
            assert response.status_code == 200
    with Session(app.state.repo.engine) as db:
        sessions = db.exec(select(ChatSession)).all()
        interactions = db.exec(select(Interaction)).all()
        assert len(sessions) == 1 and len(interactions) == 2
        first_hash = sessions[0].id
        assert len(first_hash) == 16 and set(first_hash) <= set("0123456789abcdef")
        assert first_hash != raw_session
        assert {row.session_id for row in interactions} == {first_hash}

    changed_salt = file_app_factory(session_salt="another-test-salt")
    with TestClient(changed_salt) as client:
        assert client.post("/v1/chat", json={"message": raw_message, "session_id": raw_session}).status_code == 200
    with Session(changed_salt.state.repo.engine) as db:
        hashes = {row.id for row in db.exec(select(ChatSession)).all()}
        assert len(hashes) == 2 and first_hash in hashes and raw_session not in hashes

    with sqlite3.connect(app.state.repo.engine.url.database) as connection:
        persisted = "\n".join(connection.iterdump())
    assert raw_session not in persisted
    assert raw_message not in persisted
