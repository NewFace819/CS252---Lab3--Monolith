# Lab 6 H3 — trailing-s experiment (Gia Huy / wiih0521)

Status: E14/E20 follow-up implemented and tested. Review last after everyone's baseline comparisons.

The assigned change is deliberately small: lowercase, remove one trailing `s` when
the token is longer than four characters, then filter stop words on normalized tokens.
This order also removes `whats -> what` and `wheres -> where` rather than leaking stop words.
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
H26#6.1 already contains `credits` in its body: the baseline failure was ranking caused
by the incidental `take` match, not the absence of a plural match in the credit-load passage.

The issue's expectation that the tokenizer change alone fixes E14 was not reproduced.
The table above records that first experiment, not the final result.

## Follow-up: numeric ranges and broad topic requests

For BM25, when a question contains a number and a unit, give additional relevance weight
to a passage defining a range in that unit (`between N and M <unit>`).
The bonus is twice the unit's existing IDF. It is independent of chunk IDs, specific numbers
and exact questions. E14 now ranks the credit-load range above the incidental verb `take`.
TF-IDF cosine scores are unchanged; this ranking extension applies to BM25 (and its hybrid contribution).

Before retrieval/model calls, requests starting with `tell me about`, `explain`, `describe`
or `give me an overview of` abstain if only one distinct non-stop-word topic remains.
Thus `tell me about exams` abstains, while `tell me about exam absence` can retrieve a specific rule.
The original escalation response is reused. No eval expectations or thresholds were changed.

Final 25-case run, same defaults and offline stub:

| Path | Correct | Abstain correct | p50 / max ms | Failed cases |
|---|---|---|---|---|
| deterministic | 9/25 | 7/7 | 0.0 / 0.5 | All document questions |
| retrieval | 22/25 | 6/7 | 0.0 / 0.1 | E13 E15 E19 |
| llm (stub) | 22/25 | 6/7 | 0.2 / 1.1 | E13 E15 E19 |

Also evaluated the temporary union of `origin/main` and Gia Huy's cases (30 unique IDs),
without committing other members' cases: deterministic 11/30; retrieval/stub 26/30;
abstention 9/9 and 8/9 respectively. Remaining retrieval/stub failures: E13, E15, E19, E22.
Full pytest: 252 passed; targeted RAG/index tests: 34 passed; Ruff check/format passed.

## Ambiguities and limits to review

- The assignment suggests stripping `s` fixes E14, but the baseline passage already contains
  `credits`. Extra ranking and ambiguity handling go beyond that one-line assignment;
  they are explicitly included here under the requested follow-up, not attributed to stemming alone.
- A numeric range match is a relevance heuristic, not a calculation or eligibility decision.
  It only recognizes the English `between N and M <unit>` form; alternatives such as
  `at most` and multiple ranges require separate evaluation. The weight 2 is not calibrated
  on an independent dataset and may prefer a range passage over another valid numeric policy.
- A one-topic overview can be a valid user request, so the conservative broad-request rule
  may abstain unnecessarily (e.g. `explain refunds`). It does not recognize every paraphrase
  or language, and multiword ambiguity remains: E19 still fails. It is not a semantic classifier.
- Stripping trailing `s` still changes `class`/`thesis` to `clas`/`thesi`; shared normalization
  is not linguistically correct stemming. In particular, `class/classes` becomes
  `clas/classe`, `address/addresses` becomes `addres/addresse` and `thesis/theses` becomes
  `thesi/these`, so these singular/plural pairs still do not match. Four-letter plurals
  `fees` and `days` are unchanged and do not match `fee` and `day`. A separate
  `test_known_overstemming` documents these limits rather than treating them as desirable behavior.
- Results use the offline stub and a small dataset. They do not establish real-model answer
  correctness or a general solution to ambiguity. Keep the original Part F/H1 tables unchanged
  as before-H3 evidence and review this bonus after the other members' submissions.

## Peer-review follow-up — all available H1 cases

Re-ran with a temporary union of E01–E45 from `origin/main`, the four teammates' homework
branches, and Gia Huy's local cases (45 unique IDs, no conflicting definitions).
This tests the current H3 code against everyone's available cases before all H1 PRs merge;
it does not claim that their other branch changes are integrated. The committed eval file
is restored afterward and still contains only the original cases plus Gia Huy's assigned IDs.

| Path | Correct /45 | Abstain correct /15 | p50 / max ms | Failed cases |
|---|---|---|---|---|
| deterministic | 16/45 | 14/15 | 0.0 / 0.5 | Document questions and E30 |
| retrieval | 39/45 | 12/15 | 0.0 / 0.1 | E13 E15 E19 E22 E30 E39 |
| llm (stub) | 39/45 | 12/15 | 0.2 / 0.5 | E13 E15 E19 E22 E30 E39 |

E14 selects H26#6.1, E20 abstains, and E43 now retrieves S26#1. The original review
5994177615 referred to the earlier trailing-s-only commit, so its E14/E20 verdict is
superseded by the follow-up results above. Latest checks: 254 full tests passed,
36 targeted RAG/index tests passed, Ruff check/format passed.
Re-run on the merged main code and full eval set again before final integration.

The review also identified a pre-existing hybrid score-scale issue: RRF determines
ranking, but returned scores come from component indexes. It is not corrected by
this tokenizer PR; the results here use default BM25, not hybrid calibration.

## Integration readiness

Merged `origin/main` at df84c0d and resolved conflicts in `llm.py`, `answerer.py`,
`ai-use-log.md` and `cases.jsonl`. Preserved main's provider validation/deadline fixes,
the equivalent A1/A2 checks, both members' log entries and all unique evaluation cases.
The merged branch has 30 cases: deterministic 11/30, retrieval/stub 26/30;
E14 and E20 pass, remaining retrieval/stub failures are E13, E15, E19, E22.
Full tests: 278 passed; Ruff check/format and diff check passed.

The author explicitly accepts the documented ranking/abstention trade-offs for review:
numeric credit questions can prefer the credit-load rule even for other credit policies,
and a valid single-topic overview such as `explain refunds` may abstain unnecessarily.
This accepts answer-quality limitations, not merely slower execution. The heuristics
remain unchanged. The PR is ready for review, with team merge ordering still applicable.
