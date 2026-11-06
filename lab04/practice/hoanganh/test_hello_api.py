from fastapi.testclient import TestClient
from hello_api import app

client = TestClient(app)


def test_p1_home():
    assert client.get("/").json() == {"message": "Hello, CSC10014!"}


def test_p2_hello_path_parameter():
    assert client.get("/hello/Lan").json() == {"message": "Hello, Lan!"}


def test_p3_square_query_parameter():
    assert client.get("/square", params={"n": 7}).json() == {"n": 7, "square": 49}
    assert client.get("/square", params={"n": "abc"}).status_code == 422


def test_p4_add_json_body():
    r = client.post("/add", json={"a": 2, "b": 3})
    assert r.status_code == 200
    assert r.json() == {"sum": 5.0}


def test_p5_unknown_course_404():
    assert client.get("/courses/CSC10014").status_code == 200
    assert client.get("/courses/XYZ").status_code == 404
