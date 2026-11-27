# Lab 7 D.4 — every state (Từ Hoàng Anh)

Both servers running from the repo root: `uvicorn assistant_api.main:create_app --factory` (port 8000) and
`streamlit run ui/app.py` (port 8501). Default `.env` (`LLM_PROVIDER=stub`).

| # | Try | Expected on screen | What I saw | OK? |
|---|---|---|---|---|
| 1 | click "I lost my student card" in the sidebar | question and answer appear | answer "A lost student card can be replaced at Student Affairs (room I.102)" + `Sources: S26#3 — 3 Student card replacement` | ✅ |
| 2 | "Can I register my thesis with 118 credits?" | answer + "Sources: H26#5.3 — …" | "…register a thesis when they have at least 120 accumulated credits and a cumulative GPA of at least 2.0" + `Sources: H26#5.3 — 5.3 Thesis registration` | ✅ |
| 3 | "what is the capital of France" | the escalation note (Training Office) | "I'm not confident I can answer that…" + blue box "I could not find this in the official documents. A staff member can help: Training Office, room I.101." | ✅ |
| 4 | press Enter on an empty box | nothing is sent | empty box: Streamlit sends nothing. Only spaces: yellow "Please type a question.", no message added, no API call | ✅ |
| 5 | click 👍 | "Thanks" toast; the buttons disappear | toast "Thanks for your feedback!", both buttons disappear at once, API logs `POST /v1/feedback 201`. 👎 on another answer: toast "Thanks — we will look at this answer.", also 201 | ✅ (after fix below) |
| 6 | stop the API (Ctrl+C), ask again | "Cannot reach the assistant…" instead of a crash | red box at the top "The assistant backend is not reachable…" and the answer "⚠️ Cannot reach the assistant. Is the backend running?", no exception | ✅ |

Screenshots: `img/hoanganh-state-1.png` … `img/hoanganh-state-6.png`.

## Fix found while testing state 5

In the starter, after a vote the buttons stayed on screen until the next interaction, because the click is handled
in the same run that drew them. Clicking 👎 right after 👍 then did nothing (no toast, no request): the vote was lost
without telling the user. The buttons are now drawn in an `st.empty()` slot that is cleared as soon as the answer is
rated, so they disappear in the same run (`ui/app.py`).

Checked with `streamlit.testing.v1.AppTest` against the live API: after `up2` the remaining keys are `up4, down4`; after
`down4` none are left; both votes return 201.
