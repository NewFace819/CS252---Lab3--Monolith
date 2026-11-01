"""Offices router (H1).

Owner: Gia Huy.
"""

from fastapi import APIRouter, Request

router = APIRouter()
offices_router = router


@router.get("/v1/offices")
def get_offices(request: Request) -> list[dict]:
    service = getattr(request.app.state, "service", None)
    offices = getattr(service, "offices", None)
    if offices is None:
        return []
    return [o.__dict__ for o in offices.all()]
