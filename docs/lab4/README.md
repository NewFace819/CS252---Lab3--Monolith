# Lab 4 — Your First Web API (Group 01)

Mục tiêu: đưa trợ lý `assistant_core` (Lab 3) ra HTTP bằng FastAPI. Đề: `CSC10014_2026_Lab04_REST_API_Backend_Tutorial.pdf`.
Code API nằm ở `src/assistant_api/`, cạnh `assistant_core`, và gọi `AssistantService.handle()` cùng `OfficeDirectory`. Phân công bên dưới đã được cập nhật theo cấu trúc starter chính thức sau tích hợp.

## Setup (mỗi người làm một lần)

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate          # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
pytest -q                       # Chạy toàn bộ test Lab 3 + Lab 4
```

Trong `.env` vừa copy, bỏ comment `API_ADMIN_KEY` và thay placeholder bằng khóa dùng
riêng tại máy bạn. Nếu không đặt khóa, GET `/v1/feedback` luôn trả 401; đây là mặc định
chủ động khóa quyền admin. Không commit `.env` hoặc khóa thật.

Chạy server từ thư mục gốc repo (để đọc đúng `.env` và `data/`):

```bash
uvicorn assistant_api.main:create_app --factory --reload
```

Mở http://127.0.0.1:8000/docs để thử endpoint. Chạy curl bằng Git Bash, không dùng PowerShell.
Trong terminal Git Bash thứ hai, dùng **cùng khóa đã đặt cho server**:

```bash
read -rsp 'API_ADMIN_KEY (same as server): ' API_ADMIN_KEY; echo
export API_ADMIN_KEY
bash api-tests/curl_tests.sh
unset API_ADMIN_KEY
```

Nếu sửa khóa trong `.env`, khởi động lại server trước khi thử. Biến môi trường đã có
ưu tiên hơn `.env`, nên kiểm tra terminal chạy server không giữ một khóa cũ.

## Hợp đồng API

| Method | Path | Gửi | Nhận |
| --- | --- | --- | --- |
| GET | `/health` | không | `{"status":"ok","version":"1.0.0"}` |
| POST | `/v1/chat` | `{"message","session_id"}` | `{"answer","intent","sources","degraded","request_id"}`; message rỗng → 422 |
| POST | `/v1/feedback` | `{"request_id","rating"(-1/0/1),"comment"}` | 201 + feedback đã lưu |
| GET | `/v1/feedback` | header `X-API-Key` | danh sách feedback; sai key → 401 |
| GET | `/v1/weather` | không | thời tiết campus; site ngoài lỗi → 503 |
| GET | `/v1/offices` (H1) | không | `[{"name","room","hours"}]` sắp theo tên |

Lỗi luôn có dạng `{"error": {"code": "...", "message": "..."}}` (422 → `invalid_request`; còn lại `code` = `message` viết thường, thay dấu cách bằng `_`, ví dụ 401 → `missing_or_invalid_api_key`, 503 → `weather_service_unavailable`, 429 → `too_many_requests`, 404 → `not_found`).
`ChatResponse` = `Response` của Lab 3 (`model_dump()`) + `request_id = uuid4().hex[:12]`. `/v1/chat` nhận `message` rồi đổi thành `Message(text=message, session_id=session_id)`.

## Phân công

Quy ước chung:
- Mỗi người một branch tách từ `main`, một PR, tên branch ghi bên dưới. Chỉ sửa file của mình; cần đổi hợp đồng thì báo Hải. Reviewer của PR Thông là **Hải (`NewFace819`)**; PR sửa file chung ghi rõ phạm vi để Hải review trước khi merge.
- Commit dạng `feat(api): ...`, `test(api): ...`. `ruff check .` và `pytest -q` phải xanh trước khi mở PR.
- **Cá nhân (cả 5 người):** P1–P5 trong `lab04/practice/<tên>/hello_api.py` + `test_hello_api.py` (5 passed), commit `feat(practice): hello API P1-P5`; và H2 reflection 5 dòng trong `docs/lab4/reflection-<tên>.md`.

### Hải — khung API + T1 + tích hợp (branch `feat/api-skeleton`)
Làm **đầu tiên**, merge sớm để các bạn khác tách branch từ đó.
1. `src/assistant_api/__init__.py`, `schemas.py`: `ChatRequest` (`message` min_length=1, `session_id`), `ChatResponse`, `FeedbackIn` (`request_id`, `rating` -1/0/1, `comment`), `FeedbackOut` (+`id`, `created_at`), `Weather`.
2. `main.py`: `create_app(settings=None, service=None, weather=None)` dùng với `--factory`; mặc định `load_settings()` + `build_service()` từ `assistant_core.service`; `GET /health`; hàm `error(code, key, message)` + handler cho `HTTPException` và lỗi validate (422 → `invalid_request`). Feedback và weather hiện được tích hợp trực tiếp trong app factory; offices dùng `include_router`.
3. **T1** `POST /v1/chat`: `service.handle(Message(...))`, thêm `request_id`.
4. Cuối buổi: review PR của mọi người, merge, tag `v0.4-api`, nộp link tag.
Xong khi: `/health` 200; `/v1/chat` trả đủ 5 trường; message rỗng 422.

### Thông — config + T2 + T3 (branch `feat/api-feedback`)
1. `config.py`: `api_admin_key: str | None = None` trong `Settings` và đọc `API_ADMIN_KEY`; thiếu hoặc rỗng thì khóa quyền admin. Test trong `tests/api/test_config_vbthg.py`.
2. `src/assistant_api/main.py`: sau tích hợp starter, `feedback_store` (list) nằm trong app factory, `require_admin` đọc header `X-API-Key`, sai/thiếu → 401. Test T2/T3 trong `tests/api/test_feedback_vbthg.py`.
3. **T2** `POST /v1/feedback`: status 201, `id=len(store)+1`, `created_at` UTC; rating ngoài -1/0/1 → 422.
4. **T3** `GET /v1/feedback`: có `require_admin`, trả toàn bộ store.
Xong khi: POST hợp lệ 201; rating 5 → 422; GET không key → 401; có key → danh sách.

### Đức Huy — T4 + CI (branch `feat/api-weather`)
1. `src/assistant_api/weather.py`: `ExternalServiceError`; `WeatherClient` gọi Open-Meteo (Nguyen Van Cu campus), `httpx.Client(timeout=3)`, thử lại 1 lần, lỗi thì trả bản cache cuối với `stale=True`, chưa có cache thì raise `ExternalServiceError`. Nhận `transport` tùy chọn để test dùng `httpx.MockTransport`.
2. **T4** `GET /v1/weather`: bắt `ExternalServiceError` → `HTTPException(503, "Weather service unavailable") from None`.
3. Kiểm tra `.github/workflows/ci.yml` vẫn cài đủ dependency mới (đã nằm trong `requirements.txt`) và chạy `ruff` + `pytest`.
Xong khi: fake site trả 200; fake site sập trả 503; CI xanh.

### Tô Hoàng Anh — test + công cụ gọi thử (branch `test/api-suite`)
Viết theo hợp đồng ngay từ đầu; test sẽ fail cho tới khi module của người khác merge, đó là bình thường.
1. `tests/conftest.py`: thêm fixture `client = TestClient(create_app(settings, service, weather))` với service giả, helper `weather_with(handler)` dùng `httpx.MockTransport` (không đổi fixture Lab 3 cũ).
2. `tests/api/test_api.py`: health, chat OK, chat rỗng 422 (`invalid_request`), feedback tạo 201, rating sai 422, list feedback không key 401 / có key 200, weather OK, `test_weather_down_returns_503` (fake site lỗi), `test_rate_limit` (bonus đã bật, không skip).
3. `api-tests/curl_tests.sh` (Git Bash, in status code từng request theo bảng hợp đồng) và `api-tests/study-assistant.postman_collection.json`.
Xong khi: sau khi mọi PR merge, `pytest -q` xanh; `bash api-tests/curl_tests.sh` in đúng status mong đợi khi server và script dùng cùng khóa admin.

### Gia Huy — H1 + bonus + ảnh nộp (branch `feat/api-offices`)
1. `knowledge.py`: thêm `OfficeDirectory.all()` trả `list[Office]` sắp theo `name`; test trong `tests/test_knowledge.py`.
2. **H1** `src/assistant_api/offices.py`: `GET /v1/offices` trả `[o.__dict__ for o in service.offices.all()]`; 2 test trong `tests/test_offices_api.py`: status 200 và có item tên "Library".
3. **Bonus (+1)** `ratelimit.py` có `RateLimiter.allow(client)`; thêm vào đầu `/v1/chat` trả 429; bỏ skip của `test_rate_limit`. Làm sau khi T1 merge.
4. Chụp ảnh `/docs` với một lần `/v1/chat` thành công, lưu `docs/lab4/docs-chat.png`, dán vào PR.
Xong khi: `/v1/offices` 200, sắp theo tên; 2 test xanh; vượt hạn mức → 429.

### Thứ tự và phụ thuộc
`Hải khung` → (Thông ∥ Đức Huy ∥ Gia Huy) song song, `Tô Hoàng Anh` viết test từ đầu → Hải T1 + tích hợp → ảnh `/docs`, curl, tag.

## Checklist nộp bài

- [ ] P1–P5 (`pytest test_hello_api.py` 5 passed) — mỗi người
- [ ] T1–T4 xong, `pytest -q` xanh
- [ ] Ảnh `/docs` với một lần `/v1/chat` thành công (đính trong PR)
- [ ] Đã chạy `bash api-tests/curl_tests.sh`
- [ ] PR mở và dán link lên LMS cuối buổi (draft được)
- [ ] Nhóm chọn một PR rõ nhất để merge, các bạn khác review; Hải tag `v0.4-api`, nộp link tag trước 23:59 ngày trước Lab 5
- [ ] H1 (`/v1/offices` + 2 test) và H2 (reflection, mỗi người) nộp PR link trước 23:59 ngày trước Lab 5
- [ ] Bonus (+1): rate limit hoặc một API ngoài thứ hai (`worksheets/external_api_failure.md`)

## Điểm (10 + 1)

P1–P5: 2 · T1–T4: 4 · ảnh `/docs` + curl: 1 · H1: 2 · H2: 1 · Bonus: +1

## Lưu ý

- Không commit `.env` hay key thật; chỉ commit `.env.example`.
- Code API đã được căn theo starter chính thức (`public_materials/lab04/starter`): chữ ký `create_app(settings, service, weather)`, schemas, `WeatherClient`, các trường `Settings` mới và `build_service` trong `assistant_core.service`. Test chính thức nằm ở `tests/api/` (đã bỏ skip của `test_rate_limit`); `api-tests/` và `worksheets/` lấy từ starter. Test Week 3 không bị sửa.
- Chạy test API: `pytest tests/api -q`; chạy tất cả: `pytest -q`.
