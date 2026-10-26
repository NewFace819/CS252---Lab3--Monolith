# Lab 3 before/after comparison — vbthg

Scope: issue #2 (configuration and logging), with the team's parallel module split.
The comparison below distinguishes implemented behaviour from integration still
owned by other members. The monolith is retained unchanged as a reference.

| Question | Before: monolith | After: current configuration/logging branch |
|---|---|---|
| Where would you change the credit rate? How many places? | Change the RATE constant in Python source. | Set CREDIT_RATE_VND in the environment or local .env; no source edit. Existing process variables take precedence. |
| Can you run tests without internet or an API key? | The fake LLM sleeps and fails randomly; its handwritten test prints output. | Yes: 29 automated tests pass locally, using the stub and fake test values; dependencies must be installed first. Full service integration is still pending. |
| What happens if handbook.json is missing? | load() catches the error with bare except, prints and continues. | Not implemented by this branch: knowledge.py is another member's task and must raise DataError at startup. |
| Is any secret printed or logged? | llm() prints the hard-coded key and part of the prompt. | Settings repr/print omit the key; config errors suppress raw input values. JSON formatting excludes arbitrary extras and exception details. Callers must still avoid placing secrets or full user text in the message or allowed session field; model_dump() is not a secret-safe logging API. |
| How does a teammate find fee logic? | Read handle(), which mixes routing, parsing and calculation. | The agreed location is tools.py, owned by another member; it remains a stub on this branch. No subjective timing is claimed. |
| Number of global variables | 9 module assignments, including 3 mutable collections (history, offices, handbook). | 0 module-level state assignments in config.py and logging_setup.py; settings are returned explicitly. Python's standard logging registry is intentionally configured by setup_logging. |
| Number of bare except blocks | 3. | 0 in the implemented owned modules. The reference monolith is unchanged and excluded from lint. |
| Lines in the longest function | handle(): 56 lines including declaration and whitespace, measured with AST end_lineno. | load_settings(): 31 lines by the same measure. This is an owned-module measurement, not a completed-team metric. |
| Ruff issues | Reference code contains mixed imports, broad exception handling and other smells; it is excluded by the repo's lint configuration. | ruff check . and ruff format --check . pass with pinned Ruff 0.6.9. |
| Swap the LLM without touching the service? | The provider call is inside the monolith. | The team contract defines a Responder interface. This branch supplies provider/key configuration; responder/service integration remains the respective owners' work. |

Configuration is now separate from business logic, and named errors plus JSON
logs make startup and operational behaviour easier to test. Environment loading
and logger setup introduce extra concepts, including precedence and avoiding
duplicate handlers. After the other modules land, I would verify service startup,
fallback logging and CLI stdout/stderr end to end before claiming the whole lab
is complete.

## Verification and AI disclosure

- Pinned dependencies: Pydantic 2.9.2, python-dotenv 1.0.1, pytest 8.3.3, Ruff 0.6.9.
- 26 added tests plus 3 existing model tests pass; no real key or provider is used.
- The member defined the requested scope and directed work against the team's
  contract. OpenAI Codex assisted with implementation, tests, documentation and
  automated checks; generated code was retained as recorded in docs/ai-use-log.md.
  The member is responsible for reviewing, understanding and explaining the work.
- H1 (AI feature extension with three personally reviewed improvements) is a
  separate homework task and is not claimed complete by this configuration PR.
