# Lab 7 — D.4 (Thông)

Kiểm tra ngày 27/11/2026 bằng Chrome với Streamlit, FastAPI và SQLite chạy cục bộ. Backend dùng `LLM_PROVIDER=stub`.

| Thử | Thấy gì | Đúng chưa |
|---|---|---|
| Bấm câu ví dụ về luận văn ở sidebar | Câu hỏi xuất hiện trong lịch sử và trợ lý trả lời. [Ảnh 1](img/vbthg-d4-01-sidebar.png) | Đạt |
| Gõ `Can I register my thesis with 118 credits?` | Câu trả lời kèm `Sources: H26#5.3 — 5.3 Thesis registration`. [Ảnh 2](img/vbthg-d4-02-sources.png) | Đạt |
| Gõ `what is the capital of France` | Ô ghi chú hướng người dùng tới Training Office, phòng I.101. [Ảnh 3](img/vbthg-d4-03-escalation.png) | Đạt |
| Nhấn Enter khi ô trống | Lịch sử giữ nguyên và log API không có thêm `POST /v1/chat`. [Ảnh 4](img/vbthg-d4-04-empty.png) | Đạt |
| Bấm 👍 dưới câu trả lời | Hiện toast `Thanks for your feedback!`, hai nút của câu đó biến mất. SQLite lưu rating `1`. [Ảnh 5](img/vbthg-d4-05-thumbs-up.png) | Đạt |
| Tắt API rồi hỏi `Where is the library?` | Trang báo backend không chạy và hiển thị `Cannot reach the assistant. Is the backend running?`. [Ảnh 6](img/vbthg-d4-06-offline.png) | Đạt |

F1: bấm 👎 thấy toast `Thanks — we will look at this answer.`, nút biến mất và SQLite lưu rating `-1`. [Ảnh F1](img/vbthg-d4-07-thumbs-down.png)
