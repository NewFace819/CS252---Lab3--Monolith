import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure local import works when running pytest from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hello_api import app

client = TestClient(app)


def test_p1_home():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello, CS252!"}


def test_p2_hello_uses_name_from_path():
    assert client.get("/hello/Lan").json() == {"message": "Hello, Lan!"}


def test_p3_square_uses_query_and_rejects_text():
    assert client.get("/square?n=7").json() == {"n": 7, "square": 49}
    assert client.get("/square?n=abc").status_code == 422


def test_p4_add_reads_json_body():
    r = client.post("/add", json={"a": 2, "b": 3})
    assert r.status_code == 200
    assert r.json() == {"sum": 5.0}
    assert client.post("/add", json={"a": 2}).status_code == 422


def test_p5_unknown_course_is_404():
    assert client.get("/courses/CS252").status_code == 200
    r = client.get("/courses/XYZ")
    assert r.status_code == 404
    assert r.json() == {"detail": "Course not found"}
