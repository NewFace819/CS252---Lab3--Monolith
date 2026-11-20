# Lab 6 — Three assistant paths (Hải)

Run from the repository root with `python eval/compare_paths.py`, using `LLM_PROVIDER=stub`, `RETRIEVAL_KIND=bm25`,
`RETRIEVAL_MIN_SCORE=2.0` and the 20 cases E01–E20.

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.7   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.1     0.1   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.2     0.5   fails: E13 E14 E15 E19
```

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7 | 5 | 0.0 ms | 5 | only answers fees and offices; every policy question goes unanswered |
| retrieval | 16 | 4 | 0.1 ms | 4 | exact word matching: "due" ≠ "deadline" (E13), "credits" ≠ "credit" (E14); E19 finds a related paragraph with a high score, so it does not abstain |
| llm (provider: stub) | 16 | 4 | 0.2 ms | 3 | fails on exactly the same cases as retrieval, because the stub only rephrases the first retrieved paragraph; a real model would be slower and could invent rules without the grounding check |

E15 ("how long can I keep a library book") fails on all three paths: the router sees the word "library" and returns the
library's room before retrieval is ever tried.

**Which path would you ship for policy questions, and why?**
For handbook questions I would ship the **retrieval** path: it gets 16/20, the same as the LLM path, it is faster, and it
always quotes the official paragraph with its source, so it cannot invent a rule. I would only switch on the LLM path
with a real model that phrases answers better, and only behind the grounding check (A2) and the abstain step (A1). The
first failure I would fix is **E14**: removing a final "s" in `tokenize` makes "credits" match "credit", a very cheap fix
that helps both retrieval and the LLM path.

## H1 — five more test questions (E21–E25)

| ID | Question | Expected | Category |
|---|---|---|---|
| E21 | how do I change my IT account password | `S26#2` | normal |
| E22 | how much is the student card replacement fee | `S26#3` | normal |
| E23 | can I get a refund after week 4 | `F26#4` | normal |
| E24 | who will win the football match | abstain | out-of-scope |
| E25 | what is the phone number of 22127001 | abstain | privacy |

New table (25 cases):

```
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.7   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23
retrieval             20/25       6/7     0.1     0.1   fails: E13 E14 E15 E19 E22
llm (stub)            20/25       6/7     0.2     0.4   fails: E13 E14 E15 E19 E22
```

**Did any of my questions fail?** Yes, E22 fails on all three paths: the router sees the word "fee" and sends the
question to the tuition calculator, which replies "How many credits?", even though BM25 ranks the right paragraph
`S26#3` first (score 12.57) — the same kind of failure as E15, so the fix belongs in the router, not in retrieval.

## Bonus — fixing one failed question (E22)

**Problem.** E22 ("how much is the student card replacement fee") failed on every path. The router sends any question
containing "fee" to the tuition calculator, which answered "How many credits?", although BM25 ranks the right paragraph
`S26#3` first.

**Fix** (`src/assistant_core/router.py`). A fee question about a campus service that the knowledge base documents
("replacement", "student card") goes to retrieval, as long as it has no "tuition" word and no credit count. Every other
fee question still goes to the calculator, so "tuition for 18 credits and 2 retake", "What is the FEE?" and
"fee at the library" behave exactly as before. New tests in `tests/test_router.py` cover both directions; three of them
fail without the fix.

**Re-run (25 cases):**

```
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.7   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23
retrieval             21/25       6/7     0.1     0.1   fails: E13 E14 E15 E19
llm (stub)            21/25       6/7     0.2     0.7   fails: E13 E14 E15 E19
```

E22 now passes on retrieval and llm (20/25 → 21/25) and nothing else changed. The deterministic path still fails it, as
it should: that path never reads the documents. The retrieval answer now quotes the real price ("The replacement fee is
50,000 VND"); the stub only repeats the first sentence of the paragraph, so its answer cites the right source but does not
state the price — a real model would be needed for that. The word list is deliberately small; a later fee question about
another service would need its own entry or a smarter intent classifier.
