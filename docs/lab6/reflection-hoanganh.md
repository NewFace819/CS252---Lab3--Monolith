# Lab 6 — H2 reflection (Từ Hoàng Anh)

Asking a chatbot directly is like a closed-book exam: it answers from memory, sounds confident, and may invent a rule or a fee.
RAG turns it into an open-book exam: our search code first finds the right page in the faculty documents, then the model writes the answer only from that page.
If search finds no good page (the best score is below 2.0), we do not call the model at all and tell the student to ask the Training Office.
One thing our code checks that the model does not: every source id the model cites must be one we actually gave it, otherwise the answer is rejected.
If the model still fails after one retry, we quote the paragraph itself, which is less friendly but always true.
