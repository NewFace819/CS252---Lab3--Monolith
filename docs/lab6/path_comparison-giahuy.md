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
I would fix retrieval token matching first (E14's credit/credits mismatch), then investigate paraphrases E13/E15 and the unsafe answer to ambiguous E19 before enabling a real model.
