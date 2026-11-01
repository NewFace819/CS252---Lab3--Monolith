"""Tests for GET /v1/offices endpoint (H1).

Owner: Gia Huy.
"""

import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_get_offices_status_and_sorted(client):
    response = client.get("/v1/offices")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 4
    names = [item["name"] for item in items]
    assert names == ["IT Helpdesk", "Library", "Student Affairs", "Training Office"]
    assert names == sorted(names)


def test_get_offices_contains_library(client):
    response = client.get("/v1/offices")
    assert response.status_code == 200
    items = response.json()
    library = next((item for item in items if item["name"] == "Library"), None)
    assert library is not None
    assert library["room"] == "B.201"
    assert library["hours"] == "Mon-Sat 07:00-20:00"
