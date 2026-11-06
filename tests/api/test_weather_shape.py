"""Upstream answers with 200 but an unusable shape: 503 without cache, stale data with cache."""

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.weather import WeatherClient

GOOD = {"current": {"temperature_2m": 28.0, "wind_speed_10m": 5.0, "weather_code": 0, "time": "2026-11-06T13:45"}}
BAD_SHAPES = [{"current": None}, {"current": []}, {"current": 5}, {}]


def make(handler):
    return WeatherClient("https://example.test/forecast", 0, 0, transport=httpx.MockTransport(handler), retries=0)


@pytest.mark.parametrize("payload", BAD_SHAPES)
def test_bad_shape_without_cache_is_503_with_error_json(settings, service, payload):
    app = create_app(settings, service, make(lambda req: httpx.Response(200, json=payload)))
    r = TestClient(app).get("/v1/weather")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "weather_service_unavailable"


@pytest.mark.parametrize("payload", BAD_SHAPES)
def test_bad_shape_with_cache_returns_stale(payload):
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        return httpx.Response(200, json=GOOD if calls["n"] == 1 else payload)

    w = make(handler)
    w.cache_ttl_s = 0
    assert not w.current().stale
    assert w.current().stale
