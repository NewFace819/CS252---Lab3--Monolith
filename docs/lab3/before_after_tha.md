# Lab 3 â€” Before / after maintainability comparison â€” THA

Scope: `responder.py` (`Responder` Protocol, `TemplateResponder`, `StubLLMResponder`), `tests/test_responder.py`
and `docs/architecture.md`. "After" is the refactored package, with emphasis on my module.

| Question | Before: monolith | After: `assistant_core` |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant (`RATE`) in `assistant_monolith.py`: a code edit. | 1 variable (`CREDIT_RATE_VND`) in `.env`; no code edit. |
| Can you run the tests without internet or an API key? | No. `llm()` fails randomly (`random.random()`), and the hand-made `test()` only prints. | Yes. `StubLLMResponder` needs no key and is deterministic; `test_responder.py` runs offline in well under a second. |
| What happens if `handbook.json` is missing? | A bare `except:` prints and continues with an empty handbook. | `DataError` at startup (`Handbook.from_json`). |
| Is any secret printed or logged? | Yes. `API_KEY` is hard-coded and `llm()` prints it in a debug line. | No. The key comes from the environment, `repr=False` hides it, and the responders never see or log it. |
| How long does it take a new teammate to find the fee logic? | Minutes: it is inside the ~65-line `handle()` next to routing and search. | Seconds: `tools.py`. |
| Number of global variables | 9 (`API_KEY`, `MODEL`, `RATE`, `RETAKE_RATE`, `DEBUG`, `history`, `offices`, `handbook`, `BASE`); 3 mutable. | 0 in `responder.py`; state lives in instances (`StubLLMResponder.fail`). |
| Number of bare `except:` blocks | 3 | 0 (`responder.py` only raises `ProviderError`). |
| Lines in the longest function | ~65 (`handle`) | 4 in `responder.py` (`StubLLMResponder.explain`). |
| `ruff check` issues | 8 with the lab rule set (3 Ã— E722, BLE001, E501, E401, E711, I001). | 0 (`ruff check .` passes). |
| Can you swap the LLM without touching the service? | No. `llm()` is called directly from `handle()`. | Yes. The service depends on the `Responder` Protocol, so a real provider class is added in Week 4 without editing `service.py`. |

**Three sentences:** The biggest improvement is that the AI part is now replaceable and testable: the stub removes
randomness, the key and the network, and `fail=True` lets us test the fallback path on demand. What got more complex
is the number of files and concepts (Protocol, dependency injection, named errors), which only pays off because
several people maintain and extend this code. I would still add a real provider class with timeouts in Week 4 and
test the service-level fallback (`degraded=True`) end to end once `service.py` is merged.
