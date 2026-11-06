# H2 — Reflection (Đức Huy, npdwuy)

1. In Lab 3, `service.handle(Message)` is a function call inside one Python process: the caller must import `assistant_core`, and an error is a Python exception.
2. In Lab 4, `POST /v1/chat` receives JSON over HTTP, FastAPI validates it (empty message → 422 `invalid_request`), then calls the same `service.handle()`; my `tools.py` and `router.py` run unchanged behind it, and the answer comes back as JSON with a `request_id`.
3. A team may prefer the HTTP version because any client (browser, mobile app, a script in another language, curl, Postman) can use one assistant through one documented contract without installing our package.
4. It also gives one place for cross-cutting rules (one error shape, API key on `/v1/feedback`, rate limit on `/v1/chat`), and the API can be tested end to end with `TestClient` and checked on every PR by CI.
5. The cost is new failure modes the function call never had: network errors, slow or down services such as the weather site, and a contract that clients depend on, so we need timeouts, a retry, a cached fallback and a `/v2` when the contract has to break.
