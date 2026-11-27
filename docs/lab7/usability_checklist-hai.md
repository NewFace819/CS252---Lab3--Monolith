# Lab 7 — Usability checklist (Hải)

Checked against the running app (both servers, see `states-hai.md`).

- [x] The first screen says what the assistant can do, with example questions — welcome message + 4 examples in the sidebar
- [x] Empty or too-long input shows a friendly message (not a crash) — "Please type a question." / "too long (max 2000 characters)"
- [x] While waiting, the user sees "Thinking…" — `st.spinner("Thinking…")` around `client.ask`
- [x] Every answer from documents shows its sources — `Sources: H26#5.3 — 5.3 Thesis registration`
- [x] "I don't know" answers tell the user who can help (escalation) — Training Office, room I.101
- [x] If the backend is down, the page says so clearly — red box at the top + "Cannot reach the assistant. Is the backend running?"
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message — toast; both buttons now have a text tooltip (`help=`) because they are emoji-only
- [x] The page says it is an AI assistant — sidebar caption "This is an AI assistant. Check important decisions with the Training Office."
- [x] Text is readable (size, contrast); buttons have clear labels — default Streamlit theme, example buttons use full sentences
- [x] Works on a phone-width window — 390 px screenshot `img/hai-phone.png`: title, welcome and input fit. The examples are in the sidebar,
      which is collapsed on a phone, so a new user may not notice them.

## Hallway test (E.3)

Tester (another group): said the app works fine ("cũng ok") but the look is not very attractive ("hình ảnh không được
quá đẹp mắt"). What surprised them was the plain default look, not the behaviour: the page is the stock Streamlit theme
with no colours, logo or styling of its own.
