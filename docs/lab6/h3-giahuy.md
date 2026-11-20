# Lab 6 H3 — trailing-s experiment (Gia Huy / wiih0521)

Status: draft, review last after everyone's baseline comparisons. Do not merge as an E14 fix.

The assigned change is deliberately small: after lowercasing and stop-word filtering,
remove one trailing `s` when the token is longer than four characters.
The same tokenizer is used for document indexing and queries in BM25, TF-IDF and hybrid retrieval.
Boundary and integration tests cover short words, case/punctuation, and singular/plural query equivalence.
This is a heuristic, not an English stemmer: `class` becomes `clas` and `thesis` becomes `thesi`.

## Actual evaluation on the 25 cases, A1/A2 enabled, offline stub

| Path | Before H3 | After H3 | Abstain before | Abstain after | After p50 / max ms |
|---|---|---|---|---|---|
| deterministic | 9/25 | 9/25 | 7/7 | 7/7 | 0.0 / 0.4 |
| retrieval | 21/25 | 20/25 | 6/7 | 5/7 | 0.0 / 0.1 |
| llm (stub) | 21/25 | 20/25 | 6/7 | 5/7 | 0.2 / 0.5 |

The five added H1 cases still pass. Retrieval and stub fail E13, E14, E15, E19 and now E20.
E20 (`tell me about exams`) matches `exam` after normalization and no longer abstains;
the broader match is not enough evidence to resolve this ambiguous question.
E14 (`can I take 32 credits`) still ranks the wrong section first: BM25 returns H26#7.2,
while TF-IDF and hybrid return F26#2. Removing `s` alone does not express that 32 exceeds
the maximum regular semester load of 30, and `take` also matches the exam-absence passage.

The issue's expectation that this single tokenizer change fixes E14 is not reproduced.
Keep this experiment separate from the passing core/homework PRs. Before merging,
the team should agree on a separate ranking/disambiguation change and rerun E14 and E20;
this PR does not change thresholds, evaluation expectations or special-case either question.
