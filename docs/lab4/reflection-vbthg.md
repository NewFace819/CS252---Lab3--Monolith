# H2 — Thông (vbthg)

1. Ở Lab 3, chương trình gọi trực tiếp `service.handle()` và nhận một đối tượng Python trong cùng tiến trình.
2. Ở Lab 4, client gửi HTTP POST đến `/v1/chat` với dữ liệu JSON, rồi server mới gọi service để xử lý.
3. Kết quả được trả về dưới dạng JSON kèm mã trạng thái HTTP, nên client không cần biết các lớp Python bên trong.
4. Nhờ vậy, giao diện web hoặc ứng dụng trên máy khác có thể dùng chung backend mà không phải viết lại logic trợ lý.
5. Nhóm có thể phát triển giao diện và backend riêng, miễn là thống nhất dữ liệu gửi nhận và cách báo lỗi của API.
