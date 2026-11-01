# H2 — Reflection (Võ Thanh Hải)

1. In Lab 3, `service.handle()` is a normal Python call inside one process: the caller must be Python code that has installed `assistant_core`.
2. In Lab 4, `POST /v1/chat` receives JSON over the network, FastAPI validates it (an empty message gives 422), and then the same `service.handle()` runs; the result comes back as JSON plus a `request_id`.
3. A team may prefer the HTTP version because a browser, a phone app or a program in another language can all use one assistant through one contract, without knowing Python.
4. The UI, the tests and other services can be built and deployed separately, and the API can add access control (API key) and limits (rate limit) in one place.
5. The price is new failure modes — timeouts, a down service, bad input — which is why every error has the same shape and why outside services need a timeout, a retry and a backup plan.
