# Lab 7 — Usability checklist (Từ Hoàng Anh)

- [x] The first screen says what the assistant can do, with example questions — welcome message + 4 examples in the sidebar
- [x] Empty or too-long input shows a friendly message (not a crash) — "Please type a question." / "Your question is too long (max 2000 characters)."
- [x] While waiting, the user sees "Thinking…" — `st.spinner("Thinking…")` around `client.ask`
- [x] Every answer from documents shows its sources — `Sources: H26#5.3 — 5.3 Thesis registration` (L1)
- [x] "I don't know" answers tell the user who can help (escalation) — Training Office, room I.101 (L2)
- [x] If the backend is down, the page says so clearly — red box at the top + "Cannot reach the assistant…"
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message — both toasts are real text, buttons disappear after one vote
- [x] The page says it is an AI assistant — sidebar caption "This is an AI assistant. Check important decisions with the Training Office."
- [x] Text is readable (size, contrast); buttons have clear labels — default Streamlit theme, dark text on white; 👍/👎 now also have a text tooltip (`help=`), and both toasts are full sentences
- [x] Works on a phone-width window — at 390 px no horizontal scroll (`scrollWidth` = 390), answer, sources and buttons stack cleanly (`img/hoanganh-phone.png`). Note: on a phone the example questions sit in the collapsed sidebar (behind `>`), so a new user may not see them

## Hallway test (E.3)

Tester (other team, first name only): ____
One thing that surprised them: ____
