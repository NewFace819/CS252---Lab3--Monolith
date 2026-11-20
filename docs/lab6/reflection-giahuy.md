# Lab 6 — H2 reflection (Gia Huy)

RAG giống thi mở sách: trợ lý tìm đoạn liên quan trong tài liệu chính thức trước khi viết câu trả lời.
Ví dụ, hỏi về đăng ký luận văn thì hệ thống lấy H26#5.3 để có điều kiện 120 tín chỉ và GPA 2.0.
Model dùng đoạn đã lấy để diễn đạt; truy xuất được nguồn không bảo đảm model hiểu hay trả lời đúng mọi chi tiết.
Code kiểm tra JSON, schema và source_ids chỉ thuộc tập nguồn đã truy xuất, thay vì tin model tự tuân thủ lời nhắc.
Nếu nguồn quá yếu thì abstain và hướng người dùng đến phòng đào tạo; nếu model lỗi thì trích nguồn làm fallback.
