# H2 — Reflection (Đức Huy, npdwuy)

1. A plain LLM answers like a student in a closed-book exam: fluent, confident, and free to misremember a deadline or a fee because nothing forces it to look anything up.
2. RAG makes it an open-book exam where our code hands over the book: BM25 picks the best paragraphs from `data/kb`, and if the best score is below `RETRIEVAL_MIN_SCORE` we abstain and point the student to the Training Office instead of calling the model at all.
3. The model then gets only those paragraphs and must reply in JSON that cites them; a missing source or an id we never retrieved is rejected and we fall back to quoting the paragraph, so a wrong answer can still slip through only when retrieval picks the wrong page, as E19 and E39 show.
4. Everything that must be exact stays in ordinary code: the router, the fee calculator, the retrieval threshold and the checks on the model's output.
5. One thing our code checks that the model does not: for "I missed my final exam on 2026-11-20", the model only repeats "within 3 working days", while my Lab 3 H1 code turns it into "Wednesday 2026-11-25" by skipping the weekend, and gives no exact date when the question has several dates.
