# Lab 7 — 10-minute user test (Gia Huy / wiih0521)

Status: **two participant feedback items reported by Gia Huy; study incomplete**.
The third observation, participant eligibility and session details still need confirmation.
Developer/browser/AppTest checks are documented separately.

Participant (first name or anonymous label only): **pending**.
Date and duration (10 minutes): **pending**.

Task, exactly as assigned: “Find out if you can register your thesis with 118 credits,
and where to replace a lost student card.”

Do not coach the participant. Record their actual actions and words; do not infer observations
from test results. No student ID, contact details or personal records are needed.

| # | What they did or said | What they expected | UI/system cause | Proposed fix |
|---|---|---|---|---|
| 1 | Gia Huy relayed that the tester asked whether Vietnamese was available ("không có tiếng việt à"). | Inferred: Vietnamese interaction or a visible language option; not yet directly confirmed with the tester. | Analysis: UI and examples are in English; supported language is not explicitly stated. | Clearly state that the current demo supports English questions, with English examples; full Vietnamese support is outside the required H1 fix. |
| 2 | Gia Huy reported the tester's feedback: "phạm vi trả lời cũng không rộng" (the answer coverage is limited). | Inferred: answers on a wider range of topics; exact question/topic still needs recording. | Analysis: the demo only contains sample fees, offices and selected handbook policies; the opening copy does not clearly explain these limits. | Clarify the supported topics and that the knowledge base is limited/sample data; expanding the backend knowledge base is not required for this UI fix. |
| 3 | Pending | Pending | Pending | Pending |

## Evidence and missing details

Both observations were added on 2026-11-27 from Gia Huy's reports in chat, not from
an automated test or an invented transcript. The actual test date/duration, whether
the participant is outside the group, the exact question for observation 2 and
completion of the assigned task remain unconfirmed. Proposed causes/fixes are developer
analysis; they are not additional participant quotes.

Selected observation and reason: **pending selection**.
One resulting code change and commit: **pending implementation**.
Before/after screenshots (`img/giahuy-before.png`, `img/giahuy-after.png`): **pending**.

The source-expander bonus was implemented independently of participant research;
its screenshots must not be presented as a participant-driven H1 fix.
