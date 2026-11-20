# Lab 6 — So sánh ba đường trả lời (Thông)

Chạy `python eval/compare_paths.py` với provider `stub`, BM25 và ngưỡng 2.0. Độ trễ là số đo trên máy local, làm tròn theo script.

| Đường trả lời | Đúng /20 | Từ chối đúng /5 | p50 (ms) | Kiểm soát (1–5) | Lỗi chính |
|---|---:|---:|---:|---:|---|
| deterministic | 7/20 | 5/5 | 0.0 | 5 | Bỏ qua câu hỏi cần đọc tài liệu |
| retrieval | 16/20 | 4/5 | 0.1 | 4 | Từ khóa không khớp cách diễn đạt hoặc khớp nhầm tài liệu |
| llm (stub) | 16/20 | 4/5 | 0.3 | 3 | Dựa trên cùng bộ nguồn như retrieval nên vẫn kế thừa lỗi tìm nguồn |

Điểm kiểm soát là đánh giá định tính, dựa vào mức độ dự đoán được của câu trả lời và khả năng truy lại nguồn.

Với câu hỏi về quy định, mình sẽ dùng retrieval có trích dẫn vì nó đạt 16/20 và người đọc có thể kiểm tra nguyên văn. Stub cho cùng điểm nên bảng này chưa cho thấy lợi ích về độ đúng khi thêm bước sinh câu trả lời. Mình sẽ sửa E19 trước vì trả lời một câu hỏi về hình thức thi bằng nguồn không nói kỳ thi có mở sách hay không có thể khiến người đọc hiểu sai.
