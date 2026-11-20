# Lab 6 — H2 reflection (Hải)

1. Hỏi thẳng một chatbot giống thi đóng sách: nó trả lời bằng trí nhớ, nghe rất trôi chảy nhưng có thể bịa ra một quy định hay một con số.
2. RAG biến bài thi thành thi mở sách: trước tiên code của mình tìm đúng trang trong tài liệu chính thức của khoa (BM25 trên `data/kb`).
3. Sau đó mới đưa trang đó cho model và dặn "chỉ trả lời từ trang này, không có thì nói không biết"; nếu không tìm được trang nào đủ liên quan thì mình dừng luôn, không gọi model.
4. Model chỉ lo phần viết câu trả lời cho dễ đọc; tìm tài liệu, tính học phí và kiểm tra kết quả đều là code bình thường.
5. Một thứ code của mình kiểm tra mà model không tự kiểm tra: grounding check — câu trả lời phải trích ít nhất một nguồn, và mọi nguồn được trích phải nằm trong những đoạn mình đã đưa cho model, nếu không thì loại câu trả lời đó.
