# Lab 5 H2 — Thêm một câu hỏi về dữ liệu trợ lý (Đức Huy, npdwuy)

## Câu hỏi

**Trong các câu trả lời đã giải quyết (`resolved = 1`), bao nhiêu phần trăm phải dùng đường lui `degraded`, tính theo từng intent và từng topic (quy định trong sổ tay)?**

Câu hỏi này không trùng với F1–F3 (số request theo intent, latency trung bình theo intent, topic bị thumbs-down nhiều nhất).
Tôi không chọn "giờ cao điểm nhất" vì dữ liệu seed được tạo trong vài giây nên cột `created_at` gần như giống nhau và kết quả sẽ vô nghĩa.

## Vì sao hữu ích

- Một câu trả lời `degraded` là câu trả lời mà trợ lý đã tìm được đúng rule nhưng lời giải thích từ nhà cung cấp AI (`responder.explain`) bị lỗi (`ProviderError`), nên phải trả lời bằng mẫu dự phòng (`fallback`), xem `src/assistant_core/service.py` (`_rule`). Người dùng vẫn nhận được câu trả lời nhưng kém tự nhiên hơn, nên tỉ lệ này cho thấy chất lượng đang giảm ngay cả khi chưa ai bấm thumbs-down.
- Người hành động: thành viên backend dùng bảng này để quyết định có cần thêm timeout/retry hay đổi nhà cung cấp không, và ưu tiên kiểm tra các rule có tỉ lệ cao trước (ví dụ rule có nội dung dài khiến lời gọi AI dễ quá thời gian). Rule không khớp thì không nằm ở đây: trường hợp đó trả về intent `unknown`.
- Khác với F2, ở đây ta so sánh theo topic, nên chỉ ra được lỗi đường lui tập trung ở *rule nào*, không chỉ *intent nào* chậm.

## Câu SQL

```sql
SELECT intent,
       COALESCE(topic, '-')                       AS topic,
       COUNT(*)                                   AS answers,
       SUM(degraded)                              AS degraded,
       ROUND(100.0 * SUM(degraded) / COUNT(*), 1) AS degraded_pct,
       ROUND(AVG(latency_ms), 1)                  AS avg_latency_ms
FROM interaction
WHERE resolved = 1
GROUP BY intent, topic
ORDER BY degraded_pct DESC, answers DESC;
```

Chỉ tính `resolved = 1` vì intent `unknown` không bao giờ được xem là degraded; nếu đưa vào sẽ làm tỉ lệ chung bị loãng.

## Kết quả (300 dòng seed)

| intent | topic | answers | degraded | degraded_pct | avg_latency_ms |
|---|---|---:|---:|---:|---:|
| rule | H26-7.2 | 11 | 4 | 36.4 | 127.1 |
| rule | H26-4.2 | 45 | 11 | 24.4 | 80.0 |
| rule | H26-5.3 | 84 | 19 | 22.6 | 67.5 |
| greeting | - | 26 | 2 | 7.7 | 2.4 |
| office | - | 47 | 1 | 2.1 | 3.4 |
| fee | - | 61 | 1 | 1.6 | 5.1 |

(Tổng 274 câu `resolved` trên 300 dòng; 38 câu `degraded`.)

## Nhận xét

Các câu hỏi về rule có tỉ lệ `degraded` cao nhất (22–36%), trong đó H26-7.2 cao nhất và cũng chậm nhất, còn greeting/office/fee gần như không dùng đường lui.
Nếu đây là dữ liệu thật, H26-7.2 sẽ là rule cần kiểm tra đầu tiên, nhưng chỉ có 11 câu nên con số 36,4% còn rất không chắc chắn; H26-4.2 và H26-5.3 có nhiều dữ liệu hơn nên đáng tin hơn.

**Lưu ý:** dữ liệu do `scripts/seed.py` sinh ngẫu nhiên (`random.seed(7)`), tỉ lệ degraded được cài sẵn theo từng intent trong script (ví dụ rule H26-7.2 có tỉ lệ thành công 0,70), nên kết quả chỉ chứng minh câu SQL chạy đúng, không phải kết luận về người dùng thật. Seed cũng gán `degraded` cho cả greeting/office/fee, trong khi code thật chỉ đặt `degraded=True` ở nhánh rule.

## Cách chạy lại

Từ thư mục gốc của repo:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt -e .   # Linux/macOS: .venv/bin/python
.venv/Scripts/python scripts/migrate.py assistant.db           # tạo bảng
.venv/Scripts/python scripts/seed.py assistant.db 300          # 300 dòng giả lập
.venv/Scripts/python - <<'PY'
import sqlite3
con = sqlite3.connect("assistant.db")
cur = con.execute("""
SELECT intent, COALESCE(topic, '-') AS topic, COUNT(*) AS answers, SUM(degraded) AS degraded,
       ROUND(100.0 * SUM(degraded) / COUNT(*), 1) AS degraded_pct, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction WHERE resolved = 1
GROUP BY intent, topic ORDER BY degraded_pct DESC, answers DESC""")
print([d[0] for d in cur.description])
for row in cur:
    print(row)
PY
```

Hoặc dán câu SQL ở trên vào `sqlite3 assistant.db`. Không commit `assistant.db` (đã nằm trong `.gitignore`).
