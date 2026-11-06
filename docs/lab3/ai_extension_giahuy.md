# Lab 3 — AI extension review (H1) — Đỗ Gia Huy (wiih0521)

## 1. Feature

Vietnamese and bilingual alias matching for `OfficeDirectory`: when students inquire in Vietnamese (e.g. "phòng đào tạo ở đâu", "thư viện mở cửa khi nào", "công nghệ thông tin") or use common school acronyms ("pdt"), the knowledge module correctly matches the corresponding office without requiring the exact English name.

```text
$ python -m assistant_core "phòng đào tạo ở đâu vậy?"
Training Office: room I.101, open Mon-Fri 07:30-16:30.
```

## 2. Prompt used

> Extend the `OfficeDirectory` class in `src/assistant_core/knowledge.py` to support looking up offices via Vietnamese keywords and common abbreviations (e.g., 'phòng đào tạo' / 'pdt' for Training Office, 'thư viện' for Library, 'công nghệ thông tin' / 'it' for IT Helpdesk) in addition to exact English names. Add unit tests in `tests/test_knowledge.py`.

## 3. Review of the generated code

The AI draft attempted to modify `models.py`, `offices.csv`, and `knowledge.py`. Although initial basic tests passed, several architectural, design, and boundary flaws were uncovered during code review.

| # | What the AI generated | Problem you found | What you changed | Why |
|---|---|---|---|---|
| 1 | Modified `Office` in `models.py` to add `aliases: list[str] = []` and added an `aliases` column to `offices.csv`. | `models.py` is the shared domain contract. Changing `Office` alters dataclass fields across the entire monolith, breaking responder and serialization contracts. | Reverted `models.py` and `offices.csv`. Configured alias mapping internally inside `knowledge.py` as an encapsulation detail. | Preserves leaf module independence and maintains zero disruption to teammates' code. |
| 2 | Naive substring matching: `if alias in text.lower(): return office`. | Short aliases like "it" or "pdt" caused false positives in normal English words (e.g. "it" matched in "tuition", "wait", "visit"). | Implemented tokenized word boundary checking for short aliases (length <= 3) while allowing phrase matching for longer Vietnamese names. | Avoids routing fee or rule inquiries incorrectly to `Intent.OFFICE`. |
| 3 | Case-sensitive and accent-sensitive string comparison. | Students frequently chat without Vietnamese accents (e.g. "phong dao tao", "thu vien"). The AI draft failed all unaccented queries. | Added accent-folding normalization via `unicodedata.normalize('NFD', ...)` to match both accented and unaccented input. | Real-world conversational robustness on mobile and chat interfaces. |
| 4 | Loaded a hardcoded JSON alias file using relative path `open("aliases.json")`. | Broke when running commands or tests from directories other than the project root; also added an unhandled `FileNotFoundError` risk. | Stored the canonical built-in alias dictionary within the module, with fallback to directory names. Wrapped any file I/O safely in `DataError`. | Fails fast, deterministic, and supports testing from any working directory. |
| 5 | Only provided 2 trivial happy-path tests in `test_knowledge.py`. | No test coverage for unaccented text, short alias false-positive avoidance, punctuation stripping, or non-matching queries. | Added comprehensive unit tests covering accented Vietnamese, unaccented text, substring isolation, and empty/unmatched queries. | Guards against regressions and guarantees query accuracy. |

## 4. Checklist

- **Interfaces respected?** Yes. `models.py` (`Office`, `Rule`), router contracts, and `Response` dataclasses remain completely untouched.
- **New dependencies?** None (standard library `unicodedata` and `re`).
- **Secrets?** None used or logged.
- **Logging of user data?** No user text is logged.
- **Tests added and meaningful?** Yes; verified that both English canonical names and Vietnamese aliases resolve accurately.

## 5. What I would still change

For a production university assistant, alias mappings should be maintainable by school administrative staff via a dedicated configuration table or CMS rather than hardcoded mappings, and support semantic similarity matching (embeddings) for colloquial campus queries.

