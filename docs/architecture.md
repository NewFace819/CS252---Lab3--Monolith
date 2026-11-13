# assistant_core — Architecture

`assistant_core` is a small Python package refactored from `monolith/assistant_monolith.py`.
Behaviour is unchanged; structure is not. Every client (CLI today, FastAPI in Lab 4, UI in Lab 7)
calls one method: `AssistantService.handle(Message) -> Response`.

## 1. Modules and owners

| Module | Responsibility | Owner |
|---|---|---|
| `config.py` | Read settings from the environment / `.env`; validate | Thông |
| `errors.py` | Named exceptions (`AssistantError` and subclasses) | Hải |
| `models.py` | Public contract: `Message`, `Response`, `Intent`, `Source` (plus `Office`, `Rule`) | Hải |
| `router.py` | Choose an `Intent` with simple rules | Đức Huy |
| `knowledge.py` | Office directory (CSV) and handbook (JSON) with search | Gia Huy |
| `tools.py` | Deterministic tuition calculation | Đức Huy |
| `responder.py` | Response generation behind one `Responder` interface (template, stub LLM) | THA |
| `service.py` | `AssistantService.handle(Message) -> Response`, the only entry point | Hải |
| `logging_setup.py` | Structured JSON logs (stderr) | Thông |
| `__main__.py` | Command-line interface | Hải |

Dependency rule: leaf modules (`config`, `knowledge`, `tools`, `router`, `responder`) import only
`errors` and `models`, never each other. Only `service.py` wires them together, which avoids circular
imports and lets each member work in parallel.

```mermaid
flowchart LR
    CLI["__main__ / API / UI"] --> S[service]
    S --> R[router]
    S --> K[knowledge]
    S --> T[tools]
    S --> P[responder]
    S --> C[config]
    R & K & T & P & C --> M["models + errors"]
```

## 2. Service interface

```python
AssistantService.handle(msg: Message) -> Response
```

- **Message**: `text` (1–2000 chars), `session_id` (default `"local"`).
- **Response**: `answer`, `intent`, `sources[]` (`Source(id, title)`), `degraded`
  (`True` if a fallback answered).
- **Errors**
  - Invalid input -> `ValidationError` (Pydantic, at the `Message` boundary) / `InvalidRequest`
    (e.g. credits out of range).
  - Startup -> `ConfigError` (bad or missing settings) / `DataError` (knowledge file missing or malformed).
  - Provider failures **never reach the caller**: the service catches `ProviderError`, answers with
    `TemplateResponder` and sets `degraded=True`.
- **Dependency injection**: `AssistantService(settings, offices, handbook, responder)`, so tests can
  inject a failing `StubLLMResponder(fail=True)`.
- **Logging**: intent, latency, session and degraded flag only; never the API key or the full user message.

### Responder interface

```python
class Responder(Protocol):
    def explain(self, question: str, rule: Rule) -> str: ...
```

| Implementation | Behaviour |
|---|---|
| `TemplateResponder` | `"<title>: <text>"`, no AI. Also the service's fallback. |
| `StubLLMResponder(fail=False)` | `"Based on '<title>': <text>"`; with `fail=True` raises `ProviderError`. Deterministic, no key, no sleep. |

A real provider class is added in Week 4 without changing `service.py`.

## 3. Design decisions

1. **Fees are computed in `tools.py`, never by an LLM.** Tuition is exact arithmetic: pure functions
   give the same output for the same input, are trivially unit-tested, and cannot hallucinate. A
   characterisation test (`18` credits + `2` retake = `9_450_000`) locks in the monolith's result.
2. **The LLM sits behind `Responder`; the stub needs no key.** Adapter pattern: the service depends
   on a Protocol, not a vendor. Tests and CI run offline and deterministically, failures are simulated
   with `fail=True`, and providers can be swapped without editing the service.
3. **Configuration comes from the environment; `.env.example` documents every variable.**
   (Twelve-Factor III.) Rates, limits and keys are not in code, so changing a fee means editing one
   variable. `llm_api_key` uses `repr=False` and `.env` is git-ignored, so secrets never reach Git or logs.

## 4. Storage layer (Lab 5)

Feedback and interaction metadata are persisted in SQLite through SQLModel. The API never writes SQL:
every database operation goes through one class.

| Piece | Where | Role |
|---|---|---|
| Models | `src/assistant_api/db.py` | `ChatSession`, `Interaction`, `Feedback`: one class = one table |
| `Repository` | `src/assistant_api/db.py` | `record_interaction`, `add_feedback`, `list_feedback`, `intent_stats`. Each call opens a `Session`, adds or queries, then commits (one transaction) |
| Schema SQL | `sql/migrations/001_init.sql` | Equivalent hand-written SQL; `scripts/migrate.py` applies numbered files once |
| Seed data | `scripts/seed.py` | Invented interactions for practising queries |
| Wiring | `src/assistant_api/main.py` | Creates the engine and `Repository(engine, settings.session_salt)` |

```mermaid
flowchart LR
    API["main.py (FastAPI)"] --> REPO[Repository]
    REPO --> DB[("assistant.db (SQLite)")]
    API --> S[AssistantService]
```

### Tables

```mermaid
erDiagram
    chat_session ||--o{ interaction : has
    interaction ||--o{ feedback : receives
```

- `chat_session(id PK, channel, created_at)`: `id` is the hashed session id.
- `interaction(id PK, request_id UNIQUE, session_id FK, intent, topic, resolved, degraded, latency_ms, created_at)`.
- `feedback(id PK, request_id FK, rating, comment, created_at)`: `rating` is -1, 0 or 1; `comment` is optional (max 500 chars).

Full reasoning and the ER diagram are in `lab05/worksheets/data_model.md`.

### Privacy by design

- The raw user message is **never stored**; only metadata (intent, topic, resolved, degraded, latency).
- The session id is stored as `sha256(SESSION_SALT + raw_id)[:16]`: the same session always maps to the same
  code, but the id cannot be recovered. `SESSION_SALT` comes from `.env` (default `dev-salt` for local use only).
- No name, phone number or other personal field exists in the schema.

### Endpoints that use the database

| Endpoint | Behaviour |
|---|---|
| `POST /v1/chat` | Answers, then records one `interaction` (metadata only) and returns its `request_id` |
| `POST /v1/feedback` | Saves a `feedback` row (201). Unknown `request_id` -> 404 |
| `GET /v1/feedback` | Admin (`X-API-Key`): newest first, up to 100 |
| `GET /v1/stats/intents` | Admin: per intent `requests`, `avg_latency_ms`, `unresolved`, most requests first |

Feedback now survives a server restart (it used to be an in-memory list).
