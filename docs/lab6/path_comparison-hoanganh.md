# Lab 6 — Three assistant paths (Từ Hoàng Anh)

I ran `python eval/compare_paths.py` from the repository root with `LLM_PROVIDER=stub`, `RETRIEVAL_KIND=bm25`,
`RETRIEVAL_MIN_SCORE=2.0` on the 20 cases E01–E20, after finishing A1 and A2.

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.8   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.1     0.2   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.3     0.9   fails: E13 E14 E15 E19
```

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7 | 5 | 0.0 ms | 5 | only covers fees and offices, so handbook and service questions get no answer |
| retrieval | 16 | 4 | 0.1 ms | 4 | plain word matching misses synonyms and plurals ("due" vs "paid by", "credits" vs "credit"), and E19 gets a high score from a related paragraph, so it answers when it should abstain |
| llm (provider: stub) | 16 | 4 | 0.3 ms | 3 | fails on the same four cases as retrieval, because the stub only rewrites the top paragraph. A real model would also be slower and less predictable. |

The fees case E03 is correct on every path because the router sends it to the Lab 3 fee calculator before search.
Money is never computed by the model.

**Which path would you ship for handbook questions, and why?**
For handbook questions I would ship the **retrieval** path. It scores 16/20, the same as the LLM path, and it is
the fastest of the two. It also always quotes an official paragraph with its source id, so it cannot make up a rule or a
number. The first failure I would fix is **E15** ("how long can I keep a library book"). It fails on all three paths
because the router sees the word "library" and returns the library's room before retrieval runs. Only sending
location-style questions ("where is…", "which room…") to the office lookup would fix it without touching search.

## H1 — Five more test questions (E41–E45)

| ID | Question | Expected | Category |
|---|---|---|---|
| E41 | what GPA do I need to register a thesis | `H26#5.3` | normal |
| E42 | how many days until my new student card is ready | `S26#3` | normal |
| E43 | can I renew a borrowed book online | `S26#1` | normal |
| E44 | how do I apply for a dormitory room | abstain | out-of-scope (not in the documents) |
| E45 | what is the phone number of my classmate | abstain | privacy |

New table after adding them (25 cases):

```
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.4   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E41 E42 E43
retrieval             20/25       6/7     0.0     0.1   fails: E13 E14 E15 E19 E43
llm (stub)            20/25       6/7     0.2     0.4   fails: E13 E14 E15 E19 E43
```

E43 fails on retrieval and the LLM path. The question says "borrowed book" but the document says "borrow up to 5
books", so only "renew" and "online" match. S26#1 then scores 1.79 and the IT password chunk (S26#2, which also contains
"online") scores 1.91. Both are below `RETRIEVAL_MIN_SCORE=2.0`, so the assistant abstains instead of quoting the
library rule.
