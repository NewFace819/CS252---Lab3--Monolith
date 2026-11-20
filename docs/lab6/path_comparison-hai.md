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
