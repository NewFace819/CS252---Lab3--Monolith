# Lab 3 — AI extension review (H1) — Đức Huy (npdwuy)

## 1. Feature

Exam absence: when a student says they missed a final exam and gives the date, the assistant answers with the
handbook rule (H26-7.2) **and** the exact deadline for submitting evidence, counted in working days.

```text
$ python -m assistant_core "I missed my final exam on 2026-11-06 because I was sick"
Based on 'Exam absence': Students absent from a final exam for medical reasons must submit evidence to the
Training Office within 3 working days. Deadline: Wednesday 2026-11-11 (3 working days after 2026-11-06).
```

## 2. Prompt used

> Add an "exam absence" answer to the `assistant_core` service: when a student says they missed a final exam,
> tell them the deadline for submitting evidence, using the handbook rule. If they give the exam date, compute
> the actual deadline date. Add tests.

## 3. Review of the generated code

The AI draft touched `models.py`, `router.py`, `tools.py`, `service.py` and added 3 tests. `pytest` and
`ruff check` both passed on the draft, so every problem below was found by reading the code and trying inputs,
not by the existing checks.

| # | What the AI generated | Problem you found | What you changed | Why |
|---|---|---|---|---|
| 1 | A new `Intent.EXAM_ABSENCE` in `models.py` and an "exam" + "absent/missed" keyword branch in `router.py`. | `models.py` is the shared contract owned by the Tech Lead; changing it needs an issue first. A new intent value also changes what `/v1/chat` returns to the Lab 4 API and the future UI. | Removed the new intent and the router branch. The question still routes to `RULE`, the handbook search finds H26-7.2, and the service adds the deadline to the rule answer. | Same feature without changing the contract, so no other member's code or client has to change. |
| 2 | `exam_absence_deadline(exam_date, days=3)` returning `exam_date + timedelta(days=3)`. | Counts calendar days, not working days: an exam on Friday 2026-11-06 gave Monday 2026-11-09 instead of Wednesday 2026-11-11. The `3` was hard-coded instead of read from the handbook. | `working_days_limit(rule.text)` reads N from "within N working days"; `add_working_days(start, n)` skips Saturday and Sunday. | A wrong deadline is worse than no deadline: a student could miss the real one. If the handbook changes, the code follows it. |
| 3 | `parse_date(text)` that fell back to `date.today()` when no date was found and called `date.fromisoformat` on the match. | `tools.py` must be pure (no clock, no I/O), and "today" is a guess: the exam may have been days ago. An impossible date such as `2026-02-30` raised `ValueError`, so the request crashed (500 through the API). | `parse_date` returns `None` when there is no valid date; the service then answers with the rule only, which already says "within 3 working days". | Deterministic, testable functions, and bad input gives a normal answer instead of a crash. |
| 4 | `log.info("exam absence question: %s", text)` in the new service method. | Logs the full user message, which may contain health details ("medical reasons"). The team rule is to log intent, latency, session and degraded only. | Removed the log line; added `test_question_text_is_not_logged`. | Privacy, and consistency with `logging_setup.py` and `test_service.py`. |
| 5 | `rule = self.handbook.search("exam absence")` then `rule.text` directly, outside the responder. | Crashes with `AttributeError` if the rule is missing from `handbook.json`; it also skipped the responder, so the provider fallback (`degraded=True`) never applied. | The deadline is added inside the existing `_rule()` path, after the responder or its template fallback, through `_with_deadline()`. | Missing rules give the normal "unknown" answer, and the fallback still works. Any rule that says "within N working days" gets the same feature. |
| 6 | 3 tests: router, `parse_date` with a date, deadline from Monday 2026-11-02. | Monday + 3 is the same in calendar and working days, so the test passed with the wrong logic. No test for weekends, missing dates, bad dates or the service. | 16 tests in `tests/test_exam_absence.py`: Friday and Saturday starts, negative days, no date, impossible date, rule without a limit, provider failure, and no user text in logs. | The tests now fail on the bugs found in rows 2–5. |

## 4. Checklist

- **Interfaces respected?** Yes after the review. The draft changed `Intent`; the final version keeps `models.py`,
  the router and the `Response` shape unchanged.
- **New dependencies?** None (`re` and `datetime` from the standard library).
- **Secrets?** None used or printed.
- **Logging of user data?** The draft logged the full question; removed, with a test.
- **Tests added and meaningful?** 16 tests, including cases that fail on the draft (Friday start, impossible
  date, logged user text). Full suite: 163 passed; `ruff check .`
  and `ruff format --check .` clean.

## 5. What I would still change

Public holidays (Tết, 30/4, 2/9) are not skipped, so the deadline can be too early around them. A holiday list in
`data/` would fix this. Dates are only recognised in `YYYY-MM-DD`; Vietnamese students usually write `06/11/2026`.

## 6. Peer review (PR #24)

Thông found that a question with several dates took the first one as the exam date:
"Today is 2026-11-06. I missed my final exam on 2026-11-02." gave 2026-11-11 instead of 2026-11-05, a later
deadline than the rule allows. `parse_date` now returns a date only when the question has exactly one; with
several different dates the answer gives the rule ("within 3 working days") without an exact date. Regression
tests: `test_parse_date_returns_none_when_several_dates`, `test_no_exact_deadline_when_the_exam_date_is_ambiguous`.
