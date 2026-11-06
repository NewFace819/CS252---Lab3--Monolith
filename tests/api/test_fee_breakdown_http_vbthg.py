from fastapi.testclient import TestClient

from assistant_api.main import create_app


def test_chat_exposes_breakdown_without_changing_contract(settings, service):
    with TestClient(create_app(settings, service)) as client:
        response = client.post("/v1/chat", json={"message": "tuition breakdown for 18 credits and 2 retake"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "fee"
    assert body["answer"] == "Your tuition is 9,450,000 VND. Regular: 8,100,000 VND; retake: 1,350,000 VND."
    assert set(body) == {"answer", "intent", "sources", "degraded", "request_id"}
    assert len(body["request_id"]) == 12
