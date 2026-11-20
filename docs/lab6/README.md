# Lab 6 — AI Services & RAG: phân công

Đề: *Lab 6 — Adding AI to the Assistant, Safely*. Starter của thầy đã được ghép vào `main` (PR setup của Hải),
nên mọi người **không cần giải nén gì thêm**: làm thẳng trên repo này.

## Setup (1 lần)

```powershell
git switch main; git pull
py -3.11 -m venv .venv            # Windows; macOS/Linux: python3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt; pip install -e .
copy .env.example .env            # mặc định LLM_PROVIDER=stub, không cần API key
pytest -q                         # trước khi làm A1/A2: chỉ 2 test trong tests/test_rag.py fail — bình thường
```

## Mỗi người làm (đề chấm điểm từng cá nhân)

`<tên>` = `hai`, `vbthg`, `giahuy`, `duchuy`, `hoanganh`.

### PR 1 — nộp cuối buổi học (branch `lab6/<tên>-core`)

| Việc | File | Kiểm tra |
|---|---|---|
| S1–S3 mini search (Part B) | `lab06/practice/<tên>/mini_search.py` | `cd lab06/practice/<tên>; pytest -q test_mini_search.py` → 4 passed |
| A2 grounding check (Part D.4) | `src/assistant_core/llm.py`, TODO A2 trong `parse_draft` | `pytest -q tests/test_rag.py -k citation` |
| A1 abstain (Part E.2) | `src/assistant_core/rag/answerer.py`, TODO A1 | `pytest -q` → tất cả xanh |
| Bảng so sánh + 3 câu (Part F) | `docs/lab6/path_comparison-<tên>.md` (mẫu: `lab06/worksheets/path_comparison.md`) | `python eval/compare_paths.py` chạy ở thư mục gốc |

Sau A1/A2, bảng phải ra: deterministic 7/20, retrieval 16/20, llm (stub) 16/20.

**Về A1/A2:** cả 5 người sửa cùng 4 dòng. Hải merge **một** bản vào `main`, các PR còn lại vẫn giữ làm minh chứng
(theo mục *Team Integration* của đề). Khi PR của bạn bị conflict ở `llm.py`/`answerer.py` thì giữ bản của `main`:
phần `lab06/practice/<tên>/` và `docs/lab6/` của bạn vẫn được merge.

### PR 2 — bài tập về nhà, hạn 23:59 ngày trước Lab 7 (branch `lab6/<tên>-hw`)

| Việc | File |
|---|---|
| H1: 5 câu hỏi (3 câu bình thường có `expect_source`, 2 câu `expect_abstain: true`) | `eval/cases.jsonl`, **chỉ dùng dải ID của mình** (bảng dưới) |
| H1: chạy lại `compare_paths.py`, dán bảng mới + 1 câu giải thích câu nào fail | cuối `docs/lab6/path_comparison-<tên>.md` |
| H2: reflection 5 dòng (giải thích RAG bằng ví dụ thi mở sách + 1 thứ code kiểm tra mà model không kiểm tra) | `docs/lab6/reflection-<tên>.md` |

| Người | GitHub | ID H1 |
|---|---|---|
| Hải | NewFace819 | E21–E25 |
| Thông | vbthg | E26–E30 |
| Gia Huy | wiih0521 | E31–E35 |
| Đức Huy | npdwuy | E36–E40 |
| Từ Hoàng Anh | hoanganhtu0922 | E41–E45 |

Mọi người cùng thêm dòng vào cuối `eval/cases.jsonl` nên PR merge sau sẽ conflict: `git pull origin main` rồi giữ **cả hai**
nhóm dòng.

## Phần chung theo module (giữ cách chia từ Lab 3)

| Người | Việc |
|---|---|
| Hải | ghép starter (PR setup), review + merge, tag `v0.6-ai` |
| Thông | test cho các trường config Lab 6 mới (`KB_DIR`, `RETRIEVAL_MIN_SCORE`, `LLM_MODEL`…) trong `tests/test_config.py` |
| Gia Huy | **Bonus H3**: `tokenize` trong `rag/index.py` bỏ chữ "s" cuối ở từ dài hơn 4 ký tự (sửa E14). Merge **sau cùng**, vì nó làm thay đổi bảng so sánh của mọi người |
| Đức Huy | `api-tests/` (curl + Postman): kiểm tra `/v1/chat` có `path`, `escalate`, `confidence`; thêm 1 case abstain |
| Từ Hoàng Anh | `docs/architecture.md`: thêm mục RAG (guard → retrieve → abstain → LLM JSON → grounding → fallback) |

Bonus Ollama (+1): ai có máy chạy được thì làm, ghi kết quả vào `path_comparison-<tên>.md` của mình.

## Điểm (theo đề)

S1–S3 2đ · A2 2đ · A1 2đ · bảng so sánh + 3 câu 1đ · H1 2đ · H2 1đ · bonus +1.

## Lưu ý

- Không commit `.env`, `*.db`, API key.
- Ghi việc dùng AI vào `docs/ai-use-log.md` như các lab trước.
- Đường RAG vẫn giữ tính năng tính hạn nộp đơn vắng thi (Lab 3 H1 của Đức Huy).
