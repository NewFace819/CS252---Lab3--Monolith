# H2 — Reflection (Từ Hoàng Anh)

1. In Lab 3, `service.handle()` is a plain Python function call inside one process: only our own code can use it, and the caller must install the whole package.
2. In Lab 4, `POST /v1/chat` receives a request over the network, validates it with Pydantic, then calls the very same `service.handle()`; failures come back as status codes (422, 401, 503).
3. A team may prefer the HTTP version because a browser, a phone app or a program in another language (Java, JS) can all use one assistant without knowing Python.
4. It also lets the frontend and backend be built and deployed separately, adds access control (API key, rate limit), and can be tested with TestClient or curl.
5. The price is extra work for network failures, timeouts and security, which is why we need habits like timeout, retry and a backup plan.
