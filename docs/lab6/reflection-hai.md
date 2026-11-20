# Lab 6 — H2 reflection (Hải)

1. Asking a chatbot directly is like a closed-book exam: it answers from memory, sounds fluent, and may still invent a rule or a number.
2. RAG turns it into an open-book exam: first our own code finds the right page in the faculty's official documents (BM25 over `data/kb`).
3. Only then do we hand that page to the model and tell it "answer only from this page, or say you don't know"; if no page is relevant enough, we stop and never call the model.
4. The model only writes a friendly answer; finding the documents, computing fees and checking the result are all ordinary code.
5. One thing our code checks that the model does not: the grounding check — the answer must cite at least one source, and every cited source must be a paragraph we actually gave the model, otherwise we reject the answer.
