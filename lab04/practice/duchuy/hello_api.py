"""Warm-up API (P1-P5), Lab 4 Part C. Run: uvicorn hello_api:app --reload"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Hello API")

COURSES = {
    "CSC10014": "Software Engineering Practice",
    "CSC10002": "Programming Techniques",
}


class Numbers(BaseModel):
    a: float
    b: float


@app.get("/")
def home() -> dict:
    """P1: a fixed JSON answer."""
    return {"message": "Hello, CSC10014!"}


@app.get("/hello/{name}")
def hello(name: str) -> dict:
    """P2: {name} in the path becomes the argument ``name``."""
    return {"message": f"Hello, {name}!"}


@app.get("/square")
def square(n: int) -> dict:
    """P3: ``n`` comes from the query string (?n=7); the int hint turns ?n=abc into a 422."""
    return {"n": n, "square": n * n}


@app.post("/add")
def add(nums: Numbers) -> dict:
    """P4: the JSON body is validated against ``Numbers`` before this function runs."""
    return {"sum": nums.a + nums.b}


@app.get("/courses/{code}")
def course(code: str) -> dict:
    """P5: an unknown code answers 404 instead of a 200 with empty data."""
    if code not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"code": code, "name": COURSES[code]}
