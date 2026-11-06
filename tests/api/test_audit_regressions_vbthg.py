import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.weather import WeatherClient

CURRENT = {"time": "2026-11-06T09:00", "temperature_2m": 31.2, "weather_code": 3, "wind_speed_10m": 8.5}
INVALID_PAYLOADS = [
    None,
    [],
    {},
    {"current": None},
    {"current": []},
    {"current": {**CURRENT, "weather_code": {}}},
    {"current": {**CURRENT, "temperature_2m": "NaN"}},
    {"current": {**CURRENT, "wind_speed_10m": "Infinity"}},
]


@pytest.mark.parametrize("payload", INVALID_PAYLOADS)
@pytest.mark.parametrize("cached", [False, True])
def test_malformed_weather_uses_retry_and_graceful_fallback(settings, service, monkeypatch, payload, cached):
    calls = []
    monkeypatch.setattr("assistant_api.weather.time.sleep", lambda _: None)

    def upstream(request):
        calls.append(request)
        if cached and len(calls) == 1:
            return httpx.Response(200, json={"current": CURRENT})
        return httpx.Response(200, json=payload)

    weather = WeatherClient(
        "https://example.test/forecast",
        10.76,
        106.68,
        retries=1,
        cache_ttl_s=0,
        transport=httpx.MockTransport(upstream),
    )
    try:
        if cached:
            assert not weather.current().stale
        with TestClient(create_app(settings, service, weather), raise_server_exceptions=False) as client:
            response = client.get("/v1/weather")
        if cached:
            assert response.status_code == 200
            assert response.json()["stale"] is True
            assert response.json()["temperature_c"] == 31.2
        else:
            assert response.status_code == 503
            assert response.json() == {
                "error": {"code": "weather_service_unavailable", "message": "Weather service unavailable"}
            }
        assert len(calls) == 2 + int(cached)
    finally:
        weather._client.close()


def test_punctuated_greeting_through_http(settings, service):
    with TestClient(create_app(settings, service)) as client:
        response = client.post("/v1/chat", json={"message": "Hello!"})
    assert response.status_code == 200
    assert response.json()["intent"] == "greeting"
