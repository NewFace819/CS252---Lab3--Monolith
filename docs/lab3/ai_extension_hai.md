# Lab 3 — AI extension review (H1) — Hải (NewFace819)

## 1. Feature

"Help": when a student asks what the assistant can do, it lists its abilities (tuition, offices, handbook rules).

```text
$ python -m assistant_core "what can you do?"
I can: 1) calculate tuition (e.g. 'tuition for 18 credits and 2 retake'), 2) give room and hours for an office
(IT Helpdesk, Library, Student Affairs, Training Office), 3) answer handbook rules (Retaking a course; Thesis
registration; Late thesis registration; Credit load; Exam absence).
```

## 2. Prompt used

> Add a "help" feature to the `assistant_core` service: when a student asks what the assistant can do, answer with
> a list of its abilities. Add tests.

AI assistant: Claude Code. The first draft is what it produced from this prompt; section 3 is my review of it.

## 3. Review of the generated code

The draft touched `models.py`, `router.py` and `service.py` and added no tests. The existing 176 tests still passed,
so every problem below was found by running inputs against the draft, not by the existing checks.

| # | What the AI generated | Problem you found | What you changed | Why |
|---|---|---|---|---|
| 1 | `Intent.HELP` added to `models.py`, returned by the router. | `models.py` is the shared contract. A new enum value changes the `intent` that `/v1/chat` returns to the Lab 4 API and the future UI, so clients that list the known intents would break. | Removed `Intent.HELP`. A help request returns `Intent.GREETING` (it is the same kind of "introduce the assistant" answer); the service tells them apart with `is_help()`. | The feature works without touching the contract, so no other member's code or client changes. |
| 2 | Router branch `if "help" in t or "what can you do" in t`. | Substring match hijacks real questions. Probe: "help me register my thesis with 118 credits" and "can you help? I missed my final exam on 2026-11-06" both returned the help text instead of the thesis rule and the exam-absence deadline. | `HELP_REQUESTS` frozenset matched against the whole normalised message, same style as `GREETINGS`. Tests: `test_real_questions_are_not_help_requests`, `test_questions_containing_help_still_get_real_answers`. | A new feature must not take answers away from existing ones. |
| 3 | `HELP_ANSWER`: a constant listing office names and rule topics by hand. | Goes stale: a new row in `offices.csv` or `handbook.json` is not listed, and the text can name things that no longer exist. | `help_text(office_names, rule_titles)` in `tools.py` (pure, no I/O) builds the answer from `offices.all()` and a new public `Handbook.titles()`. Test checks every loaded office and title appears. | One source of truth: the data files. I added a public `titles()` instead of reading the private `_rules`. |
| 4 | No tests. | Nothing failed when the draft broke rows 1–2 behaviour. | `tests/test_help.py`: recognised phrases, real questions not hijacked, answer follows the data, greeting unchanged, empty data, message not logged. | Tests that fail on the draft's bugs. My first version of the service tests used the shared `service` fixture, which is all fakes, and failed; they now use a real service built with `build_service`. |
| 5 | Normalising text in two places (`strip().lower()` for greeting, a second copy for help). | Duplicated rules drift: the greeting path had just been fixed for trailing `?!.`. | One `_normalise()` in `router.py` used by `route()` and `is_help()`. | "Hello!", "Help!" and "what can you do?" behave the same way. |

## 4. Checklist

- **Interfaces respected?** Yes after review. `models.py` and the `Response` shape are unchanged; the draft changed `Intent`.
- **New dependencies?** None.
- **Secrets?** None used or printed.
- **Logging of user data?** The service still logs only intent, latency, session and degraded; test added.
- **Tests added and meaningful?** 14 new tests in `tests/test_help.py`, including cases that fail on the draft. Full suite: 190 passed; `ruff check .` and `ruff format --check .` clean.

## 5. What I would still change

Only English phrases are recognised; Vietnamese ("giúp tôi", "bạn làm được gì") would need its own entries in `HELP_REQUESTS`. The help text is one long sentence; a list would read better in the UI.
