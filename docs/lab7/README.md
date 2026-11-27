# Lab 7 — UI & Full-stack: phân công

Đề: *Lab 7 — A User Interface for the Assistant* (Streamlit). Tuần này **Hải và Đức Huy đi vắng**, nên 3 người còn lại
(Thông, Gia Huy, Từ Hoàng Anh) chia phần chung. Phần cá nhân của Hải và Đức Huy để hai bạn tự làm khi về, theo đúng
bảng "Mỗi người làm" bên dưới.

Starter của thầy (`public_materials/lab07`) được ghép vào `main` qua PR setup của **Từ Hoàng Anh** (branch
`feat/lab7-starter`), nên mọi người **không cần giải nén gì thêm**: đợi PR đó merge rồi làm thẳng trên repo này.
Backend của starter Lab 7 chỉ là Lab 6 + lời giải A1/A2, nhóm đã có, nên PR setup chỉ thêm `ui/`, `tests/test_ui.py`,
`lab07/practice/<tên>/`, `lab07/worksheets/` và `streamlit==1.39.0`.

## Setup (1 lần)

```powershell
git switch main; git pull
.venv\Scripts\activate
pip install -r requirements.txt; pip install -e .   # requirements.txt có thêm streamlit
copy .env.example .env
pytest -q                         # trước khi làm L1/L2: chỉ 2 test trong tests/test_ui.py fail — bình thường
```

Chạy 2 server, mỗi cái một terminal, **từ thư mục gốc repo**:

```powershell
# terminal 1 — API (port 8000)
uvicorn assistant_api.main:create_app --factory
# terminal 2 — UI (port 8501)
streamlit run ui/app.py
```

API chạy ở địa chỉ khác thì đặt `ASSISTANT_API_URL=http://<host>:<port>` trước khi `streamlit run`.
UI **không được import `assistant_core`**: chỉ nói chuyện với backend qua `ui/api_client.py`.

## Mỗi người làm (đề chấm điểm từng cá nhân)

`<tên>` = `vbthg`, `giahuy`, `hoanganh` (tuần này) · `hai`, `duchuy` (làm bù khi về).

### PR 1 — nộp cuối buổi học (branch `lab7/<tên>-core`)

| Việc | File | Kiểm tra |
|---|---|---|
| U1–U4 Streamlit warm-up (Part B) | `lab07/practice/<tên>/hello_streamlit.py` | `cd lab07/practice/<tên>; pytest -q test_hello_streamlit.py` → 4 passed |
| L1 `format_sources` (Part D.1) | `ui/logic.py` | `pytest -q tests/test_ui.py` |
| L2 `status_note` (Part D.2) | `ui/logic.py` | `pytest -q tests/test_ui.py` → 7 passed |
| F1 nút 👎 (Part D.3) | `ui/app.py` | bấm thử trên trình duyệt: hiện toast, nút biến mất |
| D.4 thử đủ 6 trạng thái | `docs/lab7/states-<tên>.md`: bảng 6 dòng (Try / thấy gì / đúng chưa) + ảnh chụp | xem bảng dưới |
| Usability checklist (Part E) | `docs/lab7/usability_checklist-<tên>.md` (mẫu: `lab07/worksheets/usability_checklist.md`) | tick hết, mục nào thiếu thì sửa |
| Hallway test 2 phút (Part E.3): nhờ 1 bạn **nhóm khác** dùng trang, không giải thích, ghi 1 điều làm họ bất ngờ | cuối `docs/lab7/usability_checklist-<tên>.md` | 1–2 câu |

Commit warm-up: `feat(practice): streamlit U1-U4`.

**D.4, 6 trạng thái phải thử (cả 2 server đang chạy):**

| Thử | Phải thấy |
|---|---|
| bấm câu ví dụ ở sidebar | câu hỏi + câu trả lời hiện ra |
| "Can I register my thesis with 118 credits?" | câu trả lời + `Sources: H26#5.3 — …` |
| "what is the capital of France" | note escalation (Training Office, room I.101) |
| Enter khi ô trống | không gửi gì |
| bấm 👍 | toast "Thanks", nút biến mất |
| tắt API (Ctrl+C terminal 1) rồi hỏi | "Cannot reach the assistant…", không crash |

**Về L1/L2/F1:** cả nhóm sửa cùng `ui/logic.py` và `ui/app.py`. Từ Hoàng Anh merge **một** bản vào `main`, các PR
còn lại vẫn giữ làm minh chứng (mục *Team Integration* của đề). Khi PR của bạn bị conflict ở `ui/logic.py`/`ui/app.py`
thì giữ bản của `main`: phần `lab07/practice/<tên>/` và `docs/lab7/` của bạn vẫn được merge.

### PR 2 — bài tập về nhà, hạn 23:59 ngày trước Lab 8 (branch `lab7/<tên>-hw`)

| Việc | File |
|---|---|
| H1: test 10 phút với 1 người **ngoài nhóm**, giao đúng task của đề, không giúp, ghi 3 chỗ họ hiểu sai | `docs/lab7/user_test-<tên>.md` (mẫu: `lab07/worksheets/user_test_observations.md`) |
| H1: sửa 1 trong 3 chỗ đó, commit kèm ảnh trước/sau | code trong `ui/` + `docs/lab7/img/<tên>-before.png`, `<tên>-after.png` |
| H2: đọc PAIR Guidebook (Feedback + Control, Errors + Graceful Failure), viết 2 câu: 1 ý đã dùng hôm nay, 1 ý muốn thêm | `docs/lab7/reflection-<tên>.md` |

Task giao cho người test (đề): *"Find out if you can register your thesis with 118 credits, and where to replace a lost
student card."*

Fix H1 đụng vào `ui/app.py` nên dễ conflict: mỗi người **chỉ sửa 1 chỗ nhỏ**, `git pull origin main` trước khi mở PR.
Hai bạn sửa trùng một chỗ thì báo nhau, người sau chọn observation khác.

## Phần chung theo module (thay vai của Hải tuần này)

| Người | Việc |
|---|---|
| Từ Hoàng Anh | **Tech Lead tuần này:** ghép starter (PR setup `feat/lab7-starter`, thêm `streamlit` vào `requirements.txt`), review + merge một bản L1/L2/F1, cập nhật `README.md` mục Lab 7 (cách chạy 2 server), thêm mục UI vào `docs/architecture.md` (browser → UI → API → assistant), tag **`v0.7-mvp`**, nộp link tag |
| Thông | bổ sung test cho `ui/api_client.py` trong `tests/test_api_client.py` bằng `httpx.MockTransport`, các case `tests/test_ui.py` của thầy **chưa có**: timeout, 429, đọc đúng `escalate`/`degraded`/`sources`/`path`, `healthy()` khi backend sập, `send_feedback` trả `False` khi lỗi; thêm `ASSISTANT_API_URL` vào `.env.example` |
| Gia Huy | **Bonus (+1):** hiệu ứng "typing…" (`st.write_stream` với generator chia chữ) **hoặc** hiển thị nguồn đẹp hơn (`st.expander` mỗi nguồn, có id + title). Merge **sau** bản L1/L2/F1 chính. Kèm kiểm tra giao diện ở độ rộng điện thoại (Part E.2), ghi kết quả vào `docs/lab7/usability_checklist-giahuy.md` |

### Thứ tự và phụ thuộc
`Hoàng Anh ghép starter` → (PR 1 của cả 3 người song song) → Hoàng Anh merge 1 bản L1/L2/F1 → Thông test api_client ∥
Gia Huy bonus → README + architecture → tag `v0.7-mvp` (MVP v1 chạy được từ đầu tới cuối: UI → API → data / retrieval /
AI / tools → response).

## Checklist nộp bài

- [ ] U1–U4 (`pytest test_hello_streamlit.py` 4 passed) — mỗi người
- [ ] L1, L2 (`pytest -q tests/test_ui.py` 7 passed), F1 chạy được trên trình duyệt — mỗi người
- [ ] Đủ 6 trạng thái D.4, có ảnh trong `docs/lab7/states-<tên>.md` — mỗi người
- [ ] Usability checklist tick hết — mỗi người
- [ ] PR 1 mở và dán link lên LMS cuối buổi (draft được)
- [ ] `README.md` có lệnh chạy cả 2 server; tag `v0.7-mvp`; Tech Lead nộp link tag trước 23:59 ngày trước Lab 8
- [ ] H1 (3 observations + 1 fix có ảnh trước/sau) và H2 (2 câu) nộp PR link trước 23:59 ngày trước Lab 8
- [ ] Bonus (+1): typing animation hoặc hiển thị nguồn đẹp hơn

## Điểm (theo đề)

U1–U4 2đ · L1, L2 + F1 3đ · đủ trạng thái D.4 2đ · usability checklist 1đ · H1 2đ · bonus +1.

## Lưu ý

- Không commit `.env`, `*.db`, API key.
- Ghi việc dùng AI vào `docs/ai-use-log.md` như các lab trước.
- Lỗi hay gặp: `ModuleNotFoundError: No module named 'ui'` → chạy `streamlit run ui/app.py` từ thư mục gốc;
  `DuplicateWidgetID` → key nút phải khác nhau (`key=f"down{i}"`); đếm luôn ra 1 → dùng `st.session_state`.
- Mọi thông báo lỗi phải là câu dễ hiểu + bước tiếp theo, không chỉ emoji hay màu (Part E.2).
