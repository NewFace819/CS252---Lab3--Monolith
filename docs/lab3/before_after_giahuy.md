# Lab 3 before/after comparison — Gia Huy

Scope: Issue ownership for `knowledge.py` (`OfficeDirectory`, `Handbook`, searching CSV & JSON) and its test suite `test_knowledge.py`.
The comparison below contrasts the original monolithic script with the refactored `knowledge` module and the team's modular package architecture.

| Question | Before: monolith | After: refactored package (`knowledge.py`) |
|---|---|---|
| Where would you change the credit rate? How many places? | Inside `monolith/assistant_monolith.py` via `RATE = 450000` hardcoded in source. | In environment variables (`CREDIT_RATE_VND`) or `.env`; isolated to `config.py` and injected into `tools.py`. `knowledge.py` has no coupling to rates. |
| Can you run the tests without internet or an API key? | No automated unit tests existed; manual `test()` slept and randomly threw `Exception("LLM timeout")`. | Yes: 17 automated tests run fully offline in ~0.2s without external dependencies, network access, or API keys. |
| What happens if `handbook.json` is missing? | `load()` caught errors with a bare `except:`, printed to stdout, and left `handbook = []` (silent partial failure). | `Handbook.from_json` immediately raises typed `DataError`, failing fast before invalid state propagates. |
| Is any secret printed or logged? | Hardcoded `API_KEY` was printed directly to stdout during `llm()` debug calls. | No secrets are handled or printed by `knowledge.py`. The team's `Settings` model marks keys with `repr=False`. |
| How long does it take a new teammate to find the fee logic? | Requires reading through the 164-line monolith where parsing, routing, fee math, and rule retrieval are intermingled. | Seconds: modular layout isolates fee math to `tools.py`, data persistence to `knowledge.py`, and routing to `router.py`. |
| Number of global variables | 8 globals in `assistant_monolith.py` (`API_KEY`, `MODEL`, `RATE`, `RETAKE_RATE`, `DEBUG`, `history`, `offices`, `handbook`). | 0 in `knowledge.py`. State is cleanly encapsulated in instance attributes (`_offices`, `_rules`) within `OfficeDirectory` and `Handbook`. |
| Number of bare `except:` blocks | 3 bare `except:` blocks in the monolith. | 0 in `knowledge.py`. Catches only specific I/O and format errors (`OSError`, `csv.Error`, `json.JSONDecodeError`) and wraps them in `DataError`. |
| Lines in the longest function | `handle()` in monolith was ~56 lines. | In `knowledge.py`, the longest method is `OfficeDirectory.from_csv` at 17 lines. |
| `ruff check` issues | Multiple lint violations (bare excepts, unused imports, wildcard imports, unformatted code). | 0 issues; `ruff check .` passes cleanly. |
| Can you swap the LLM without touching the service? | No: mock LLM logic was hardcoded in `handle()`. | Yes: decoupled via the `Responder` Protocol; `knowledge.py` produces pure domain `Rule` objects without knowing how answers are synthesized. |

### Three sentences on maintainability
1. **What improved most:** Knowledge retrieval and persistence are now strictly validated, typed into frozen dataclasses (`Office`, `Rule`), and fail fast with `DataError` rather than silently continuing with corrupted state.
2. **What got more complex:** Error handling and schema validation for CSV and JSON inputs required defensive checks for missing columns and dictionary keys instead of naive indexing.
3. **What I would still change:** For larger knowledge corpora, I would replace the O(N) linear keyword search in `Handbook.search` with an inverted index or SQLite full-text search (FTS5) to maintain sub-millisecond retrieval latency.

## Verification and AI disclosure
- Verified with Python 3.12, pytest 8.3.3, and Ruff 0.6.9.
- 17 unit tests pass (14 in `test_knowledge.py`, 3 in `test_models.py`).
- AI assistance was used for generating module boilerplate, edge-case unit tests, and drafting comparison metrics against team requirements. Code was manually reviewed and verified with automated checks.
