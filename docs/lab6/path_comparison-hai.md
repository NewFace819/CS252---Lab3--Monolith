# Lab 6 — Three assistant paths (Hải)

Chạy `python eval/compare_paths.py` ở thư mục gốc, `LLM_PROVIDER=stub`, `RETRIEVAL_KIND=bm25`, `RETRIEVAL_MIN_SCORE=2.0`, 20 câu E01–E20.

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.7   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.1     0.1   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.2     0.5   fails: E13 E14 E15 E19
```

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7 | 5 | 0.0 ms | 5 | chỉ trả lời học phí và phòng ban, mọi câu về quy định đều bị bỏ qua |
| retrieval | 16 | 4 | 0.1 ms | 4 | so khớp từ nguyên văn: "due" ≠ "deadline" (E13), "credits" ≠ "credit" (E14); E19 có đoạn liên quan với điểm cao nên không abstain |
| llm (provider: stub) | 16 | 4 | 0.2 ms | 3 | sai giống hệt retrieval vì stub chỉ diễn đạt lại đoạn văn đầu tiên; model thật sẽ chậm hơn và có thể bịa nếu không có grounding check |

E15 ("how long can I keep a library book") fail ở cả ba đường vì router thấy chữ "library" nên trả về phòng thư viện trước khi kịp tìm kiếm.

**Which path would you ship for policy questions, and why?**
Với câu hỏi về handbook, mình sẽ dùng đường **retrieval**: nó đúng 16/20, ngang với llm, nhanh hơn, và luôn trích nguyên văn đoạn trong tài liệu chính thức kèm nguồn nên không thể bịa ra quy định. Đường llm chỉ nên bật khi đã có model thật diễn đạt tốt hơn, và vẫn phải giữ grounding check (A2) cùng abstain (A1) phía trước. Lỗi mình sửa trước là **E14**: chỉ cần bỏ chữ "s" cuối trong `tokenize` là "credits" khớp "credit", sửa rất rẻ mà cả retrieval lẫn llm đều được lợi.

## H1 — năm câu hỏi thêm (E21–E25)

| ID | Câu hỏi | Mong đợi | Loại |
|---|---|---|---|
| E21 | how do I change my IT account password | `S26#2` | normal |
| E22 | how much is the student card replacement fee | `S26#3` | normal |
| E23 | can I get a refund after week 4 | `F26#4` | normal |
| E24 | who will win the football match | abstain | out-of-scope |
| E25 | what is the phone number of 22127001 | abstain | privacy |

Bảng mới (25 câu):

```
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.7   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23
retrieval             20/25       6/7     0.1     0.1   fails: E13 E14 E15 E19 E22
llm (stub)            20/25       6/7     0.2     0.4   fails: E13 E14 E15 E19 E22
```

**Câu nào fail?** E22 fail ở cả ba đường: router thấy chữ "fee" nên gửi câu hỏi sang máy tính học phí và trả lời "How many credits?" mà không tìm trong tài liệu, dù BM25 xếp đúng `S26#3` lên đầu (điểm 12.57) — cùng kiểu lỗi với E15, nên cần sửa router chứ không phải phần tìm kiếm.
