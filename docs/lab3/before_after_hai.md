# Lab 3 before/after comparison — Hải (NewFace819)

Scope: the integrated `assistant_core` package (all five modules merged), compared with
`monolith/assistant_monolith.py`. Numbers were measured on the integrated branch.

| Question | Before: monolith | After: assistant_core |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant (`RATE`) in Python source. | 1 variable, `CREDIT_RATE_VND`, in the environment / `.env`. No code edit. |
| Can you run the tests without internet or an API key? | No real tests; `test()` prints output, and `llm()` sleeps and fails randomly 10% of the time. | Yes. 92 pytest tests, deterministic, offline, stub responder, no key. |
| What happens if `handbook.json` is missing? | Bare `except:` prints "could not load handbook" and the bot keeps running with an empty handbook. | `DataError` at startup; the CLI prints "startup failed" to stderr and exits with code 2. |
| Is any secret printed or logged? | Yes. The `[debug]` line prints the API key and the prompt. | No. `llm_api_key` uses `repr=False`; logs hold only intent, latency, session and degraded. |
| How long does it take a new teammate to find the fee logic? | Has to read the 56-line `handle()`, where fee parsing sits between routing and office lookup. | Open `tools.py` (two pure functions); the module table in `docs/architecture.md` points there. |
| Number of global variables | 9 (3 mutable: `history`, `offices`, `handbook`). | 0 mutable globals; only constants such as `GREETINGS`. |
| Number of bare `except:` blocks | 3 (plus 1 blind `except Exception`). | 0. Every handler catches a named exception. |
| Lines in the longest function | 56 (`handle`). | 31 (`config.load_settings`); `service.handle` is 14. |
| `ruff check` issues | 8 with the project rules (3× E722 bare-except, BLE001, E401, I001, E501, E711). | 0; `ruff format --check` also clean. |
| Can you swap the LLM without touching the service? | No; `llm()` is called inside `handle()`. | Yes. The service receives any `Responder`; Week 4 adds one class and one entry in `RESPONDERS`. |

**Three sentences.** What improved most is testability: every module has a single job and the service
takes its collaborators as arguments, so 92 tests run offline in under a second and the provider
fallback is tested on purpose instead of by luck. What got more complex is the number of files and
concepts (Pydantic models, a Protocol, dependency injection, a logging setup), which a newcomer has to
learn before making a first change. What I would still change is the handbook search, which is still
plain keyword overlap and picks the first rule on ties, and the history/stats/save commands, which the
refactor dropped and should come back as a proper feature if the team still needs them.
