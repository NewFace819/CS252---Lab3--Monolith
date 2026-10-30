# Lab 3 before/after comparison — Đức Huy (npdwuy)

Scope: issue #4, `tools.py` (`parse_credits`, `tuition`), `router.py` (`route`), their tests
(`test_tools.py`, `test_router.py`) and the GitHub Actions CI. "After" is the integrated package on `main`,
with emphasis on my modules.

| Question | Before: monolith | After: assistant_core |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant (`RATE`) in Python source; the 30-credit limit is a second literal inside `handle()`. | 1 variable, `CREDIT_RATE_VND` (and `MAX_CREDITS`), in the environment / `.env`. `tuition()` takes rate, multiplier and limit as arguments, so no code edit. |
| Can you run the tests without internet or an API key? | No real tests; `test()` only prints, and `llm()` sleeps and fails randomly. | Yes. `tools` and `router` are pure functions: 24 tests in `test_tools.py` + `test_router.py` (92 in the whole suite) run offline in under a second. CI runs them on every push and PR. |
| What happens if `handbook.json` is missing? | Bare `except:` prints "could not load handbook" and the bot keeps running with an empty handbook. | `tools` and `router` do no I/O. The package raises `DataError` at startup; the CLI prints "startup failed" and exits with code 2. |
| Is any secret printed or logged? | Yes. The `[debug]` line in `llm()` prints the API key and the prompt. | No. My modules never see the key; settings hide it with `repr=False`. |
| How long does it take a new teammate to find the fee logic? | Has to read the 56-line `handle()`, where fee parsing sits between greeting, history and office lookup. | Open `tools.py`: two pure functions, about 40 lines in total. |
| Number of global variables | 9 module-level names (3 mutable: `history`, `offices`, `handbook`). | 0 mutable globals. Only immutable constants: `_PUNCTUATION` in `tools.py`, `GREETINGS` and `FEE_WORDS` in `router.py`. |
| Number of bare `except:` blocks | 3 (plus 1 blind `except Exception`). | 0. Invalid input raises `InvalidRequest` ("How many credits?", credits outside 1..30, negative retake). |
| Lines in the longest function | 56 (`handle`). | 19 (`parse_credits`); `route` and `tuition` are 10 each. |
| `ruff check` issues | 8 with the project rules (3× E722, BLE001, E401, I001, E501, E711). | 0; `ruff format --check` also clean, both enforced in CI. |
| Can you swap the LLM without touching the service? | No; `llm()` is called inside `handle()`. | Yes, through the `Responder` interface. Fees never go through the LLM: `tuition()` computes them deterministically. |

Behaviour check (CLI vs monolith): "tuition for 18 credits and 2 retake" gives 9,450,000 VND in both;
"how much is the tuition?" asks "How many credits?" in both; "tuition 40 credits" is rejected in both, now with
a clearer message ("Credits must be between 1 and 30.").

**Three sentences.** What improved most is that fee calculation and intent routing are now small pure
functions with characterisation tests, so a change to the rate or the parsing is checked in CI instead of by
running the script by hand. What got more complex is that one `handle()` became several modules plus a
contract (`Intent`, `InvalidRequest`), and the router now only returns an intent while the service decides
the answer, which a newcomer has to trace across files. What I would still change is the substring matching
in `route()` ("fee" also matches words like "feedback") and the parsing in `parse_credits()`, which only
understands digits, not "eighteen credits" or Vietnamese phrasing.
