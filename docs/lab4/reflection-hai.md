# H2 — Reflection (Võ Thanh Hải)

1. Ở Lab 3, mình gọi `service.handle(Message(...))` như một hàm Python bình thường: người gọi phải là code Python trong cùng tiến trình và đã cài `assistant_core`, kết quả là một object `Response`.
2. Ở Lab 4, người gọi chỉ cần gửi `POST /v1/chat` kèm JSON qua mạng. FastAPI kiểm tra dữ liệu trước (message rỗng thì trả 422 ngay, `handle()` không chạy), rồi mới gọi đúng `service.handle()` cũ và trả JSON, thêm `request_id` để sau này gắn feedback.
3. Nhóm nên chọn bản HTTP vì trình duyệt, app điện thoại hay chương trình viết bằng ngôn ngữ khác đều dùng chung một trợ lý qua một hợp đồng (đường dẫn, JSON, mã trạng thái), không cần biết bên trong là Python.
4. Giao diện, test và các dịch vụ khác có thể làm và triển khai riêng. Những thứ như khóa API cho `GET /v1/feedback` hay giới hạn 429 chỉ cần đặt một chỗ ở API, không phải sửa trong từng client.
5. Đổi lại sẽ có thêm lỗi mới như dữ liệu sai, API ngoài chậm hoặc sập (503). Vì vậy mọi lỗi dùng chung một dạng `{"error": {"code", "message"}}`, và khi gọi dịch vụ ngoài như thời tiết phải có timeout, thử lại một lần và dữ liệu cũ để dự phòng.
