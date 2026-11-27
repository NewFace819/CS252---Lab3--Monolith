# Lab 7 — Six UI states (Gia Huy / wiih0521)

Checked on 2026-11-27 with local API `127.0.0.1:8768`, Streamlit `127.0.0.1:8571`
and offline stub. Each row links to an actual screenshot.

| Try | Observed | Result | Evidence |
|---|---|---|---|
| Click thesis example in sidebar | Question and answer appear | Pass | [Sidebar example](img/giahuy-core-sidebar.jpg) |
| Ask “Can I register my thesis with 118 credits?” | Answer includes `H26#5.3 — 5.3 Thesis registration` | Pass | [Sources](img/giahuy-core-sources.jpg) |
| Ask “what is the capital of France” | Abstention points to Training Office, room I.101 | Pass | [Escalation](img/giahuy-core-escalation.jpg) |
| Press Enter with empty input | No question/message is sent | Pass | [Empty Enter](img/giahuy-core-empty.jpg) |
| Click thumbs-up | API 201, thanks toast and rating controls disappear | Pass | [Saved feedback](img/giahuy-core-feedback.jpg) |
| Stop API and ask a question | Readable connection error; history remains, no crash | Pass | [Backend offline](img/giahuy-core-offline.jpg) |

Also checked thumbs-down: API 201, thanks toast and both controls disappear
([screenshot](img/giahuy-core-down.jpg)). Failed feedback remains retryable in AppTest.
After integrating main's shared implementation, the controls have text labels and
show “✓ Feedback recorded — thanks!” after saving; the earlier screenshots retain
that first verification, while sidebar/empty captures show the integrated UI.
