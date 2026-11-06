# Lab 4 — Thông (vbthg)

## Integration with the current team API

PR #19 supplies the shared T2/T3 implementation in `src/assistant_api/main.py` and configuration in `assistant_core/config.py`. This branch uses that implementation directly; it does not register a second feedback router or change the shared schemas.

- `create_app(settings, service, weather)` accepts the same dependencies as the official starter.
- `POST /v1/feedback` returns 201 with an increasing id and UTC timestamp. `request_id` is 1–64 characters; `rating` is -1, 0 or 1; `comment` is optional/null with a 500-character maximum.
- `GET /v1/feedback` requires a configured `API_ADMIN_KEY` and matching `X-API-Key`; 401 uses `missing_or_invalid_api_key`. The admin key defaults to `None`, disabling access until configured. The commented `change-me` example is only a development placeholder.
- Feedback is kept per application and discarded on restart, as specified for Lab 4.

## Additional checks and individual work

- `tests/api/test_feedback_vbthg.py`: all three ratings and UTC timestamps, omitted/null comments, boundary lengths, invalid input not saved, secret-free auth errors, disabled keys and per-app data isolation. External weather is mocked.
- `tests/api/test_config_vbthg.py`: API defaults/environment fields, dotenv precedence, blank keys, secret-free repr and invalid numeric input. The original Week 3 tests stay unchanged.
- `lab04/practice/vbthg/`: P1–P5 with the five official practice checks. Run explicitly because the team's default pytest collection is limited to `tests/`.
- `reflection-vbthg.md`: H2 draft awaiting Thông's review/revision before submission.

## Verify

```bash
python -m pytest -q
python -m pytest lab04/practice/vbthg -q
python -m ruff check .
python -m ruff format --check .
git diff --check
```

For manual integration checks, configure a local `API_ADMIN_KEY`, start uvicorn and run the team's `api-tests/curl_tests.sh` in Git Bash. No real key is committed. Final release tagging and LMS submission remain team tasks.
