# T2/T3 — Thông (vbthg)

## Behaviour

- `POST /v1/feedback` accepts the team's `FeedbackIn`, saves the feedback and returns 201 with an increasing integer id and a UTC timestamp.
- `GET /v1/feedback` requires `X-API-Key` matching `API_ADMIN_KEY`. Missing, wrong or blank configured keys return 401 with the team's `unauthorized` error code; neither key is echoed.
- Each app has its own in-memory store. Restarting the app discards the data, as specified for Lab 4.
- `API_ADMIN_KEY` defaults to the tutorial's development placeholder `change-me`, loads from `.env` without overriding process variables, and is excluded from Settings repr/print. No real key is committed.

## Shared contract: explicitly retained

At Thông's direction, this PR leaves Hải's `schemas.py` unchanged. Compared with the official starter:

| Field | Current team schema | Official starter |
|---|---|---|
| `FeedbackIn.request_id` | nonempty, no upper limit | 1–64 characters |
| `FeedbackIn.comment` | string, default empty string, no upper limit | optional string / null, default null, maximum 500 characters |

Consequently, oversized request ids/comments remain accepted and an explicit `comment: null` is rejected with 422. This is a documented difference, not a claim of exact starter compatibility. Any later shared-contract change belongs in a coordinated change with Hải.

## Individual work

- P1–P5: `lab04/practice/vbthg/`, using the five official checks. The relative import and package marker allow teammates to keep identically named practice files without test collection collisions.
- H2: `reflection-vbthg.md` is an AI-assisted draft awaiting Thông's own review/revision. It is not represented as a completed personal submission.

## Validation

- Python 3.12 locally, using the exact versions in `requirements.txt`; CI uses Python 3.11.
- `python -m pytest -q`: 126 passed (including the five practice tests, after integrating main's offices and rate limiter).
- `python -m ruff check .`, `python -m ruff format --check .`, `git diff --check`: passed.
- HTTP smoke check against a running uvicorn app: see PR validation details.

Full-team curl checks, the final `/docs` screenshot and `v0.4-api` tag remain team integration tasks. This PR does not implement teammates' weather, offices or bonus tasks.
