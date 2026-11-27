# Lab 7 D.4 — Thử đủ 6 trạng thái (Đức Huy, npdwuy)

Chạy 2 server từ thư mục gốc repo: `uvicorn assistant_api.main:create_app --factory` (port 8000, `LLM_PROVIDER=stub`)
và `streamlit run ui/app.py` (port 8501), mở trang trong Chromium (cửa sổ 1280×900). Code: branch `lab7/duchuy-core`
(L1, L2, F1 đã làm; `pytest -q tests/test_ui.py` 7 passed).

| # | Thử | Thấy gì | Đúng chưa | Ảnh |
|---|---|---|---|---|
| 1 | Bấm câu ví dụ "Where is the library?" ở sidebar | Câu hỏi hiện bên user, trả lời "Library: room B.201, open Mon-Sat 07:00-20:00." kèm 👍 👎 | Đúng | ![1](img/duchuy-d4-1-sidebar-example.png) |
| 2 | "Can I register my thesis with 118 credits?" | Trả lời "...at least 120 accumulated credits and a cumulative GPA of at least 2.0." và dòng `Sources: H26#5.3 — 5.3 Thesis registration` | Đúng | ![2](img/duchuy-d4-2-thesis-sources.png) |
| 3 | "what is the capital of France" | Trả lời "I'm not confident…" và ô note xanh "I could not find this in the official documents. A staff member can help: Training Office, room I.101." | Đúng | ![3](img/duchuy-d4-3-escalation.png) |
| 4 | Enter khi ô trống | Không có tin nhắn mới (số tin nhắn 7 → 7). Ảnh giống hệt dòng 3 vì trang không thay đổi; chỉ có khoảng trắng thì hiện cảnh báo "Please type a question." | Đúng | ![4](img/duchuy-d4-4-empty-enter.png) |
| 5 | Bấm 👍 ở câu trả lời cuối | Toast "Thanks for your feedback!". Nút 👍 👎 của câu đó **chưa biến mất ngay**, chỉ biến mất ở lần tương tác tiếp theo (rerun sau) | Toast đúng; nút biến mất trễ 1 lần rerun (xem ghi chú) | ![5](img/duchuy-d4-5-thumbs-up.png) |
| 6 | Tắt API (Ctrl+C terminal 1) rồi hỏi "Where is the library?" | Câu trả lời "⚠️ Cannot reach the assistant. Is the backend running?", trang không crash | Đúng | ![6](img/duchuy-d4-6-api-down.png) |

Thêm F1: bấm 👎 ở câu trả lời đầu tiên → toast "Thanks — we will look at this answer.", feedback `-1` được gửi (backend ghi 1 dòng rating -1 vào bảng `feedback`).
Nút biến mất trễ giống 👍.

![F1](img/duchuy-d4-f1-thumbs-down.png)

**Ghi chú dòng 5.** Code của starter không gọi `st.rerun()` sau khi bấm: lần chạy xử lý cú bấm đã vẽ nút xong rồi mới
thêm `rid` vào `st.session_state.rated`, nên nút chỉ ẩn ở lần rerun sau (đếm nút 👍: 3 → 3 ngay sau khi bấm, → 2 sau
lần tương tác kế tiếp). Feedback vẫn chỉ gửi 1 lần vì lần sau `rid` đã nằm trong `rated`. Cách sửa nếu muốn nút ẩn
ngay: chuyển phần xử lý sang `on_click=` callback (callback chạy trước khi vẽ lại trang). Chưa sửa ở PR này để giữ
đúng bản F1 của đề và tránh conflict với bản `ui/app.py` được merge vào `main`.
