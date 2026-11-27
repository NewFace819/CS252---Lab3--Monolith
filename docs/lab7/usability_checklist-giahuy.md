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

- [x] A participant outside the group tried the app for approximately two minutes.
- Participant: **anonymous**; no real name collected.
- Session date: **2026-11-27**; duration: **approximately 2 minutes**, confirmed by Gia Huy.
- Eligibility: **student at another school, outside the project group**, confirmed by Gia Huy.
- Whether any moderator assistance was provided was not recorded.
- Asked about surprises, Gia Huy relayed: **"cũng không có gì bất ngờ lắm"** (nothing particularly surprising).
- Additional comment: **"giao diện có mỗi nút hỏi thôi mà =))"** (the interface only has a question control).

Summary: the participant found the interface unsurprising and perceived it as a simple
question control. Whether they noticed the examples or feedback buttons was not established.


## Bonus — source expanders

Each newly received source has its own `Source: <id>` expander; expanding it reveals
the title as plain text. Existing session messages that only contain the formatted
source caption still display correctly. This UI change does not import backend code
or alter answers, grounding or HTTP requests.

Verified on desktop and at 390 × 844: source ID/title and answer wrap without horizontal
page overflow (`scrollWidth == innerWidth == 390`); a saved rating during the phone
check produced the thanks toast and removed both controls. This is a developer check,
not the participant-driven H1 observation/fix.

Before bonus: [caption screenshot](img/giahuy-core-sources.jpg).
![Bonus: expanded source](img/giahuy-bonus-sources.jpg)
![Bonus: phone-width check](img/giahuy-bonus-mobile.jpg)

Merge the bonus/homework branch only after the L1/L2/F1 core branch; when shared-file
conflicts arise, preserve the team's merged core behavior and reapply only the source view.
