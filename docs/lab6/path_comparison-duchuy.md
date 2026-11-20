# Lab 6 — Three assistant paths (Đức Huy)

Chạy `python eval/compare_paths.py` ở thư mục gốc sau khi làm A1 + A2, với `.env` mặc định:
`LLM_PROVIDER=stub`, `RETRIEVAL_KIND=bm25`, `RETRIEVAL_MIN_SCORE=2.0`, 20 câu E01–E20.

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.5   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.0     0.1   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.2     0.8   fails: E13 E14 E15 E19
```

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7 | 5 | 0.0 ms | 5 | chỉ có router + tool (học phí, phòng ban), câu hỏi quy định nào cũng thành "không biết" |
| retrieval | 16 | 4 | 0.0 ms | 4 | BM25 chỉ so từ: câu diễn đạt lại thì đoạn đúng tụt xuống hạng 2 (E13, E14); câu không có trong tài liệu nhưng trùng từ khoá lại được điểm cao nên không abstain (E19) |
| llm (provider: stub) | 16 | 4 | 0.2 ms | 3 | sai y hệt retrieval vì stub chỉ viết lại đoạn đầu tiên; model thật thêm độ trễ và rủi ro bịa, chỉ an toàn nhờ A1 + A2 đứng trước |

## Vì sao 4 câu fail

Mình in top-3 hit của BM25 cho từng câu để xem nó sai ở đâu:

| Câu | Hit #1 (điểm) | Đoạn đúng | Nguyên nhân |
|---|---|---|---|
| E13 "when is tuition due" | F26#1 (2.28) | F26#3 (1.48, hạng 2) | "due" không khớp "deadline"; F26#1 có nhiều chữ "tuition" hơn |
| E14 "can I take 32 credits" | H26#7.2 (2.09) | H26#6.1 (1.48, hạng 2) | chữ hiếm "take" khớp "take the exam" ở 7.2 nên được điểm IDF cao; "credits" có ở nhiều đoạn nên gần như không cộng điểm, còn "32" không khớp "30" |
| E15 "how long can I keep a library book" | S26#1 (2.30) — đúng | S26#1 | retrieval tìm đúng, nhưng router thấy "library" nên trả phòng thư viện (intent OFFICE) trước khi tới RAG |
| E19 "is the final exam open-book" | H26#7.2 (5.62) | không có, phải abstain | "final exam" trùng mạnh với mục 7.2 *Exam absence*, điểm vượt xa ngưỡng 2.0 nên A1 không chặn được |

**Lưu ý về ngưỡng A1:** `RETRIEVAL_MIN_SCORE=2.0` là thang điểm BM25. Với `RETRIEVAL_KIND=tfidf` (cosine ≤ 1) thì câu nào cũng
abstain và retrieval tụt còn 7/20, bằng deterministic; đặt `RETRIEVAL_MIN_SCORE=0.2` thì lại được 16/20. `hybrid` vẫn trả điểm BM25 nên không bị.

## Ba câu hỏi

**Nên dùng đường nào cho câu hỏi handbook?** Mình chọn **retrieval**: đúng 16/20 bằng llm, nhanh hơn, và câu trả lời là nguyên văn đoạn handbook kèm mã nguồn nên sinh viên tự kiểm tra được.

**Vì sao?** Với stub, llm không thêm được câu đúng nào mà lại tăng độ trễ và thêm một chỗ có thể hỏng (sai JSON, trích nguồn lạ). Chỉ nên bật llm khi có model thật diễn đạt tốt hơn, và khi đó grounding check (A2) với abstain (A1) phải luôn đứng trước.

**Sửa lỗi nào trước?** Mình sửa **E19** trước. Ba câu kia trả lời sai kiểu "không giúp được", còn E19 trả lời sai mà tự tin: sinh viên hỏi thi có được mở sách không thì nhận về quy định nộp giấy khám bệnh trong 3 ngày làm việc, kèm nguồn trông rất đáng tin. Điểm số một mình không chặn được trường hợp này, nên cần thêm một điều kiện abstain: phải có ít nhất một từ nội dung của câu hỏi ngoài các từ chủ đề ("exam", "final") xuất hiện trong đoạn được chọn, ở đây là "open"/"book". Sau đó mới tới E14 (stemming của Gia Huy ở H3 làm "credits" khớp thêm tiêu đề "Credit load"; theo README thì H3 sửa được E14) và E15 (router không nên giành câu hỏi kiểu "how long" chỉ vì có tên phòng).
