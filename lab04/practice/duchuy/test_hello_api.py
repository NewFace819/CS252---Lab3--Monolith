from fastapi.testclient import TestClient

from .hello_api import app

client = TestClient(app)


def test_p1_home():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello, CSC10014!"}


def test_p2_hello_uses_name_from_path():
    assert client.get("/hello/Huy").json() == {"message": "Hello, Huy!"}


def test_p3_square_uses_query_and_rejects_text():
    assert client.get("/square?n=7").json() == {"n": 7, "square": 49}
    assert client.get("/square?n=-3").json() == {"n": -3, "square": 9}
    assert client.get("/square?n=abc").status_code == 422
    assert client.get("/square").status_code == 422


def test_p4_add_reads_json_body():
    r = client.post("/add", json={"a": 2, "b": 3.5})
    assert r.status_code == 200
    assert r.json() == {"sum": 5.5}
    assert client.post("/add", json={"a": 2}).status_code == 422
    assert client.post("/add", json={"a": "two", "b": 3}).status_code == 422


def test_p5_unknown_course_is_404():
    r = client.get("/courses/CSC10014")
    assert r.status_code == 200
    assert r.json() == {"code": "CSC10014", "name": "Software Engineering Practice"}
    r = client.get("/courses/XYZ")
    assert r.status_code == 404
    assert r.json() == {"detail": "Course not found"}
