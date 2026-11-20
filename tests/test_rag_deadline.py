"""The exam-absence deadline on the RAG path comes from the cited source text, not the model's wording
(review follow-up on #45)."""

import json
import re
from pathlib import Path

from assistant_core.config import Settings
from assistant_core.models import Message
from assistant_core.service import build_service

ROOT = Path(__file__).resolve().parents[1]
QUESTION = "I was absent from my final exam on 2026-11-02 for medical reasons, what is the deadline"


class ParaphrasingLLM:
    """A 'real' model that rewords the rule, so 'within 3 working days' never appears in its answer."""

    name = "paraphrase"

    def complete(self, prompt: str) -> str:
        first_id = re.search(r"^\[([^\]]+)\]", prompt, flags=re.M).group(1)
        answer = "Bring a medical certificate to the Training Office in the next three business days."
        return json.dumps({"answer": answer, "source_ids": [first_id], "confidence": 0.8, "abstain": False})


def service():
    return build_service(Settings(data_dir=ROOT / "data", kb_dir=ROOT / "data" / "kb"))


def test_deadline_survives_paraphrased_answer():
    svc = service()
    svc.rag.llm = ParaphrasingLLM()
    r = svc.handle(Message(text=QUESTION))
    assert r.path == "llm" and r.sources[0].id == "H26#7.2"
    assert "three business days" in r.answer
    assert "Deadline: Thursday 2026-11-05 (3 working days after 2026-11-02)." in r.answer


def test_deadline_on_stub_path_still_works():
    r = service().handle(Message(text=QUESTION))
    assert "Deadline: Thursday 2026-11-05" in r.answer


def test_no_deadline_without_a_date():
    r = service().handle(Message(text="I was sick during my final exam"))
    assert r.sources and "Deadline:" not in r.answer
