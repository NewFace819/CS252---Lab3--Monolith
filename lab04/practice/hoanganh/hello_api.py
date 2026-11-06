"""Warm-up API (P1-P5), Lab 4 Part C. Run: uvicorn hello_api:app --reload"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Hello API")

COURSES = {"CSC10014": "Intro to Backend", "CSC10002": "Programming Techniques"}


class Numbers(BaseModel):
    a: float
    b: float


@app.get("/")
def home() -> dict:
    """P1: nothing to add. The returned dict is sent to the client as JSON."""
    return {"message": "Hello, CSC10014!"}


@app.get("/hello/{name}")
def hello(name: str) -> dict:
    """P2: path parameter. The {name} part of the path becomes the argument ``name``."""
    return {"message": f"Hello, {name}!"}


@app.get("/square")
def square(n: int) -> dict:
    """P3: query parameter. ``n`` is not in the path, so FastAPI reads it from ?n=7.

    The ``int`` type hint converts "7" to 7; /square?n=abc is rejected with 422 automatically.
    """
    return {"n": n, "square": n * n}


@app.post("/add")
def add(nums: Numbers) -> dict:
    """P4: request body. FastAPI checks the JSON against ``Numbers`` before this function runs.

    A missing or non-numeric field is rejected with 422.
    """
    return {"sum": nums.a + nums.b}


@app.get("/courses/{code}")
def course(code: str) -> dict:
    """P5: error response. An unknown course code stops the function and answers 404."""
    if code not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"code": code, "name": COURSES[code]}
