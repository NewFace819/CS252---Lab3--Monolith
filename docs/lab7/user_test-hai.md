# Lab 7 homework — 10-minute usability test (Hải)

Tester (not in my team, first name only): TODO  Date: TODO
Task I gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Said the app is OK ("cũng ok") and solves the main problem, but looks too generic, "like an AI app", and monotonous | A page with its own look, something that feels like a university tool | Stock Streamlit theme: grey sidebar, default red/orange chat avatars, no brand colour | Custom theme (`.streamlit/config.toml`) and graduation-cap avatars. **This is the fix below.** |
| 2 | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO |

Rows 2 and 3 are still empty: only row 1 comes from a real tester so far.

The one change we made: observation 1 — `.streamlit/config.toml` (green/cream theme) and `AVATARS` in `ui/app.py`
(🎓 for the assistant, 🧑‍🎓 for the user). The behaviour is unchanged.

Before / after screenshot (same two questions, 1280×900):

| Before | After |
|---|---|
| ![before](img/hai-before.png) | ![after](img/hai-after.png) |
