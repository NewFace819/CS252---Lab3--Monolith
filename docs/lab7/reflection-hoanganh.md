# Lab 7 H2 — PAIR Guidebook (Feedback + Control, Errors + Graceful Failure)

> Draft written with Claude Code — read the two PAIR chapters and rewrite in your own words before submitting.

**An idea I used today:** PAIR says an error should give the user a path forward, not a dead end, so when our
assistant abstains it does not just say "I don't know" but names a human who can help (Training Office, room I.101),
and when the backend is down the page says so in a sentence instead of crashing.

**An idea I would add:** PAIR suggests letting users explain *why* feedback is negative, so after 👎 I would show a short
optional comment box (wrong answer / outdated / not what I asked) and send it as the `comment` field of
`POST /v1/feedback`, which the API already accepts but the UI never fills.
