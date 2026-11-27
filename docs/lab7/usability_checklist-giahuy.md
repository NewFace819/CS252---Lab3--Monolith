# Lab 7 — Usability checklist (Gia Huy / wiih0521)

Developer checks on 2026-11-27; hallway feedback has been reported by Gia Huy below.

- [x] First screen explains scope and provides examples.
- [x] Empty Enter does not submit; long input is validated with a friendly warning (AppTest).
- [x] “Thinking…” appears while the request is running (observed during API-offline check).
- [x] Document answer displays source ID/title.
- [x] Abstention names the Training Office, room I.101.
- [x] Stopped backend produces a readable error without losing history.
- [x] Answer with request ID has thumbs-up/down; saved ratings show thanks and hide both buttons.
- [x] Sidebar identifies the product as an AI assistant.
- [x] Dark-theme text is readable; feedback controls have explanatory help text.
- [x] Phone-width viewport 390 × 844: text wraps and chat input remains reachable; DOM scroll width equals viewport width (390), no horizontal page overflow.

![Phone-width developer check](img/giahuy-core-mobile.jpg)

## Hallway test — reported feedback

- [ ] A student from another group used the app unassisted for two minutes.
- First name or anonymous participant label: **pending**.
- Feedback reported on: **2026-11-27**; actual session date/duration and other-group eligibility still need confirmation.
- Asked about surprises, Gia Huy relayed: **"cũng không có gì bất ngờ lắm"** (nothing particularly surprising).
- Additional comment: **"giao diện có mỗi nút hỏi thôi mà =))"** (the interface only has a question control).

The participant reported no particular surprise; this is recorded as a valid outcome,
not replaced with an invented surprise or interpreted as proof that every control was understood.
The second quote records their perception of the interface, not an audit of the buttons it contains.

No participant observations are inferred from automated tests or the developer browser check.
