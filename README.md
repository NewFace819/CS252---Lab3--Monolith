# CS252 Lab 3 — assistant_core

Refactor `monolith/assistant_monolith.py` into a maintainable package, `assistant_core`.
Behaviour stays the same; structure changes. Tests prove it.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
pytest -q
ruff check .
```

## Layout

```
monolith/            original script + data (reference only, do not edit)
worksheets/          before/after + AI-extension templates
data/                offices.csv, handbook.json
src/assistant_core/  the package
tests/               pytest
docs/                architecture.md, lab3/ worksheets
```

## Module ownership

`errors.py` and `models.py` are the shared contract and are already on `main`.
Every other module already has a stub with its final signature: **replace only the stub in your own file**.
Leaf modules import only `errors` and `models`, never each other, so all work runs in parallel.

| Member | Owns | Tests |
|---|---|---|
| Hải (Tech Lead) | `errors.py`, `models.py`, `service.py`, `__main__.py`, tag `v0.3-core` | `conftest.py`, `test_models.py`, `test_service.py` |
| Thông | `config.py`, `logging_setup.py`, `.env.example` | `test_config.py`, `test_logging.py` |
| Gia Huy | `knowledge.py` | `test_knowledge.py` |
| Đức Huy | `tools.py`, `router.py`, CI (pytest + Ruff) | `test_tools.py`, `test_router.py` |
| THA | `responder.py`, `docs/architecture.md` | `test_responder.py` |

If you need to change the contract (`models.py`, `errors.py`, or a signature), open an issue first — don't change it in your PR.

## Workflow

1. `git switch -c feat/<module>` from `main`.
2. Implement + tests. `pytest -q` and `ruff check .` must pass.
3. Open a PR that closes your issue; one teammate reviews.

Individual work (everyone): `docs/lab3/before_after_<name>.md` and the H1 AI-extension review.
