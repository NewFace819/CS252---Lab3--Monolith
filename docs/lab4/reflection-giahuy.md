# H2 Reflection — Đỗ Gia Huy (Group 01)

1. Việc chuyển đổi từ monolith CLI sang REST API bằng FastAPI giúp tách biệt rõ ràng giữa core domain logic và web delivery layer.
2. Việc thiết kế `OfficeDirectory.all()` trong `assistant_core.knowledge` giúp endpoint `GET /v1/offices` tái sử dụng dữ liệu sạch mà không phá vỡ module leaf boundary.
3. Nhờ chuẩn hóa Exception Handling và App Factory (`create_app`), các router thành viên (như `offices_router`) dễ dàng plug-and-play vào `main.py` chỉ với một dòng `include_router`.
4. Việc thêm tính năng Rate Limiting bảo vệ endpoint `/v1/chat` khỏi spam request và chuẩn hóa mã lỗi HTTP 429 đúng với spec lỗi chung của cả nhóm.
5. Quy trình phân công nhiệm vụ và TDD song song giúp nhóm làm việc độc lập hiệu quả trên các nhánh feature mà không bị conflict.
