"""Tests for rate limiting (Bonus +1).

Owner: Gia Huy.
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.ratelimit import RateLimiter
from assistant_core.models import Intent, Response


class FakeService:
    def handle(self, msg):
        return Response(answer="ok", intent=Intent.GREETING)


def test_rate_limiter_unit():
    limiter = RateLimiter(max_requests=3, window_seconds=10.0)
    assert limiter.allow("client1") is True
    assert limiter.allow("client1") is True
    assert limiter.allow("client1") is True
    assert limiter.allow("client1") is False

    # Another client is unaffected
    assert limiter.allow("client2") is True


def test_rate_limit_exceeded_returns_429():
    limiter = RateLimiter(max_requests=2, window_seconds=60.0)
    app = create_app(settings=SimpleNamespace(), service=FakeService(), rate_limiter=limiter)
    client = TestClient(app)

    r1 = client.post("/v1/chat", json={"message": "msg 1"})
    assert r1.status_code == 200

    r2 = client.post("/v1/chat", json={"message": "msg 2"})
    assert r2.status_code == 200

    r3 = client.post("/v1/chat", json={"message": "msg 3"})
    assert r3.status_code == 429
    err = r3.json()["error"]
    assert err["code"] == "too_many_requests"
    assert "Rate limit exceeded" in err["message"]
