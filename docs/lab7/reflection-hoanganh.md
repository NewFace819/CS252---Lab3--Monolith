# Lab 7 H2 — PAIR Guidebook (Feedback + Control, Errors + Graceful Failure)

**An idea I used today:** From *Errors + Graceful Failure* and *Feedback + Control*, users should always see a clear next step and know their input was received, so our UI points to the Training Office (room I.101) when the assistant abstains, shows a plain message if the backend is unreachable, and keeps a visible `✓ Feedback recorded — thanks!` confirmation after clicking `👍 Helpful` / `👎 Not helpful`.

**An idea I would add:** From *Feedback + Control*, explicit feedback is much more useful when users can say *what* went wrong, so clicking `👎 Not helpful` should open a short optional reason picker (wrong rule / outdated info / missed part of my question) and send it in the `comment` field of `POST /v1/feedback`.
