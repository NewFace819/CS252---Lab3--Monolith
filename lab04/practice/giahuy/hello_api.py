"""Warm-up API (P1-P5), Lab 4 Part C. Run: uvicorn hello_api:app --reload"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Hello API")

COURSES = {
    "CS252": "Software Engineering Practice",
    "CSC10014": "Software Engineering Practice",
    "CSC10002": "Programming Techniques",
}


class Numbers(BaseModel):
    a: float
    b: float


@app.get("/")
def home() -> dict:
    """P1: nothing to add, just read it."""
    return {"message": "Hello, CS252!"}


@app.get("/hello/{name}")
def hello(name: str) -> dict:
    """P2: {name} in the path becomes the argument ``name``."""
    return {"message": f"Hello, {name}!"}


@app.get("/square")
def square(n: int) -> dict:
    """P3: ``n`` is not in the path, so it comes from ?n=7; the int hint makes ?n=abc a 422."""
    return {"n": n, "square": n * n}


@app.post("/add")
def add(nums: Numbers) -> dict:
    """P4: the JSON body is checked against ``Numbers`` before this function runs."""
    return {"sum": nums.a + nums.b}


@app.get("/courses/{code}")
def course(code: str) -> dict:
    """P5: an unknown code stops the function and answers 404."""
    if code not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"code": code, "name": COURSES[code]}
