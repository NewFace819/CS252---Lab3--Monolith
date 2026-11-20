# Lab 6 — Path comparison (Gia Huy / wiih0521)

## Part F — original 20 cases, before bonus H3

Run from the repository root: `python eval/compare_paths.py`.
Provider: offline `stub`; default BM25, retrieval minimum score 2.0; A1/A2 completed.
Latency is one local run, rounded by the evaluation script, not a production benchmark.

| Path | Correct /20 | Abstain correct /5 | p50 ms | Max ms | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|---|
| deterministic | 7/20 | 5/5 | 0.0 | 1.1 | 5 | No document answers; all 13 source questions fail |
| retrieval | 16/20 | 4/5 | 0.0 | 0.1 | 4 | E13, E14, E15, E19 |
| llm (stub) | 16/20 | 4/5 | 0.2 | 0.4 | 3 | Same retrieval errors; stub cannot repair missing evidence |

Controllability scores are my qualitative assessment: fixed rules are easiest to predict,
retrieval depends on ranking, and a real model would introduce additional output variation.
Here the stub is deterministic and only exercises the LLM interface, not a real model's quality.

### Three-sentence decision

I would ship retrieval-only for handbook questions initially, because it quotes the official source and achieves the same 16/20 as the stub without a model call.
RAG works like an open-book exam: retrieve relevant passages first, then let the model phrase an answer while code checks citations and abstains when evidence is weak.
I would investigate retrieval ranking first (including E14's credit/credits mismatch), then paraphrases E13/E15 and the unsafe answer to ambiguous E19 before enabling a real model.

## H1 — Gia Huy's five added cases (E31–E35), before H3

E31 asks about the maximum leave of absence (H26#8.1), E32 about the medical-certificate
deadline (H26#7.2), and E33 about approval for late thesis registration (H26#5.4).
E34 is outside the campus documents and E35 asks for another student's phone number;
both require abstention. The IDs are unique and use Gia Huy's assigned range only.

| Path | Correct /25 | Abstain correct /7 | p50 ms | Max ms | Failed cases |
|---|---|---|---|---|---|
| deterministic | 9/25 | 7/7 | 0.0 | 0.4 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E31 E32 E33 |
| retrieval | 21/25 | 6/7 | 0.0 | 0.1 | E13 E14 E15 E19 |
| llm (stub) | 21/25 | 6/7 | 0.2 | 0.4 | E13 E14 E15 E19 |

All five new cases pass for retrieval and the stub; E14 still fails because the top-ranked source
is not the credit-load section, and the credit/credits mismatch is one candidate cause to investigate in H3.
