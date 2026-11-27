# Lab 7 — 10-minute user test (Gia Huy / wiih0521)

Status: **three participant feedback items reported by Gia Huy; study incomplete**.
Participant eligibility and session details still need confirmation; the H1 fix remains pending.
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
| 3 | Gia Huy relayed: "add nhiều câu không liên quan trực tiếp tới nhau thì nó chỉ trả lời 1 cái =))" (multiple unrelated questions in one message get only one answer). Supplied screenshot confirms the exact prompt/response below. | Inferred: an answer to each question in the message, rather than only one topic. | Analysis: `tuition` routes the message to the fee calculator, which rejects 118 as a semester credit load and returns without answering the card-replacement part. The UI does not explain that independent questions should be sent separately or distinguish accumulated credits from credits used for tuition calculation. | Add visible one-question-per-message guidance and distinguish thesis eligibility from semester tuition with appropriate examples; multi-intent decomposition is a separate backend enhancement, not required for this UI fix. |

## Evidence and missing details

All three observations were added on 2026-11-27 from Gia Huy's reports in chat, not from
an automated test or an invented transcript. The actual test date/duration, whether
the participant is outside the group, the exact prompt/response for observation 2 and
completion of the assigned task remain unconfirmed. Proposed causes/fixes are developer
analysis; they are not additional participant quotes.

### Observation 3 — supplied screenshot

- User message: `tuition for 118 credits and where to replace a lost student card`
- Assistant answer: `Credits must be between 1 and 30.`
- The visible response does not answer where to replace the card. It also shows a
  mismatch between the assigned thesis-eligibility task (118 accumulated credits)
  and the tester's tuition wording (semester credits); this is not evidence that
  the backend's 30-credit tuition validation should be removed.
- Screenshot supplied by Gia Huy on 2026-11-27, preserved without editing:

![Observation 3: tuition validation and omitted card question](img/giahuy-observation3-evidence.png)

Selected observation and reason: **pending selection**.
One resulting code change and commit: **pending implementation**.
Before/after screenshots (`img/giahuy-before.png`, `img/giahuy-after.png`): **pending**.

The source-expander bonus was implemented independently of participant research;
its screenshots must not be presented as a participant-driven H1 fix.
