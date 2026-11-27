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

## Lab 4 — REST API

Xem [docs/lab4/README.md](docs/lab4/README.md): hợp đồng API, phân công và checklist nộp bài.

## Lab 5 — Database (SQLite + SQLModel)

Feedback và metadata của mỗi câu hỏi giờ được lưu vào SQLite (`assistant.db`) qua `Repository` trong
`src/assistant_api/db.py`. Không lưu nguyên văn câu hỏi hay thông tin cá nhân; session id được hash SHA-256 với `SESSION_SALT`.

```bash
cp .env.example .env                       # đặt SESSION_SALT và API_ADMIN_KEY của riêng bạn
uvicorn assistant_api.main:create_app --factory --reload   # tự tạo assistant.db (3 bảng) khi khởi động
python scripts/migrate.py assistant.db     # áp dụng sql/migrations theo thứ tự (chạy lại nhiều lần vẫn an toàn)
python scripts/seed.py assistant.db 300    # chỉ dữ liệu giả lập, cho Part F
```

| Thay đổi so với Lab 4 | |
|---|---|
| `POST /v1/chat` | ghi một dòng `interaction` (intent, topic, resolved, degraded, latency) |
| `POST /v1/feedback` | `request_id` phải là của một câu trả lời có thật, nếu không trả **404** |
| `GET /v1/feedback?limit=` | đọc từ DB, mới nhất trước; vẫn cần `X-API-Key` |
| `GET /v1/stats/intents` | mới: số request, latency trung bình, số chưa giải quyết theo intent; cần `X-API-Key` |

Test dùng SQLite in-memory (fixture `in_memory_database` trong `tests/conftest.py`), không đụng tới `assistant.db`.
Không commit file `*.db` hay `.env`.

## Lab 6 — AI services & RAG

Câu hỏi về quy định giờ đi qua: guard (`guard.py`) → tìm đoạn văn bằng BM25 trong `data/kb/*.md` → nếu điểm thấp thì
**abstain** (nói "không biết") → LLM trả JSON, kiểm tra schema + grounding → nếu lỗi thì quote nguyên đoạn văn.
Học phí và phòng ban vẫn do code tính (deterministic). Mặc định chạy offline với `StubLLM`, không cần API key.

```bash
python -m assistant_core "I lost my student card"     # in câu trả lời + source
python eval/compare_paths.py                          # so sánh deterministic / retrieval / llm (chạy ở thư mục gốc)
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 python -m assistant_core "..."   # bonus: model thật (ollama pull llama3.2)
```

`POST /v1/chat` trả thêm `path` (deterministic | retrieval | llm | tool | abstain), `escalate`, `confidence`.
Phân công và checklist nộp bài: [docs/lab6/README.md](docs/lab6/README.md).


## Lab 7 — UI (Streamlit) · MVP v1

Giao diện chat ở `ui/` là một client riêng: chỉ gọi backend qua HTTP (`ui/api_client.py`), **không import
`assistant_core`**. Chạy 2 server, mỗi cái một terminal, từ thư mục gốc repo:

```bash
pip install -r requirements.txt && pip install -e .      # có thêm streamlit
# terminal 1 — API, port 8000
uvicorn assistant_api.main:create_app --factory
# terminal 2 — UI, port 8501 (mở http://localhost:8501)
streamlit run ui/app.py
```

API chạy ở địa chỉ khác thì đặt `ASSISTANT_API_URL=http://<host>:<port>` trước khi `streamlit run`. Nếu API chưa chạy,
trang hiện hộp đỏ "backend is not reachable" thay vì crash.

```bash
pytest -q tests/test_ui.py                                 # api_client + logic của UI, không cần trình duyệt
cd lab07/practice/<tên> && pytest -q test_hello_streamlit.py   # warm-up U1–U4
```

Phân công và checklist nộp bài: [docs/lab7/README.md](docs/lab7/README.md).
