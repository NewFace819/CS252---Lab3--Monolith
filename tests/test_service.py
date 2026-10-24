import json
import logging

from assistant_core.models import Intent, Message


def test_greeting(service):
    r = service.handle(Message(text="hi"))
    assert r.intent is Intent.GREETING
    assert r.answer == "Hello! I can help with offices, fees and rules."


def test_fee_uses_settings_and_formats_vnd(service):
    r = service.handle(Message(text="tuition for 18 credits and 2 retake"))
    assert r.intent is Intent.FEE
    assert r.answer == "Your tuition is 9,450,000 VND."


def test_fee_invalid_request_becomes_answer(service):
    r = service.handle(Message(text="tuition please"))
    assert r.intent is Intent.FEE
    assert r.answer == "How many credits?"


def test_office(service):
    r = service.handle(Message(text="where is the library"))
    assert r.intent is Intent.OFFICE
    assert r.answer == "Library: room B.201, open Mon-Sat 07:00-20:00."


def test_rule_has_source(service):
    r = service.handle(Message(text="thesis registration credits"))
    assert r.intent is Intent.RULE
    assert [s.id for s in r.sources] == ["H26-5.3"]
    assert not r.degraded


def test_fallback_when_provider_fails(service):
    service.responder.fail = True
    r = service.handle(Message(text="thesis registration credits"))
    assert r.degraded and r.sources
    assert r.answer.startswith("Thesis registration:")


def test_unknown_when_no_rule_matches(service):
    r = service.handle(Message(text="what is the weather"))
    assert r.intent is Intent.UNKNOWN
    assert r.sources == []


def test_log_has_intent_but_not_user_text(service, caplog):
    with caplog.at_level(logging.INFO, logger="assistant_core"):
        service.handle(Message(text="thesis registration secret-question", session_id="s1"))
    record = next(rec for rec in caplog.records if rec.getMessage() == "handled")
    assert record.intent == "rule" and record.session == "s1"
    assert "secret-question" not in json.dumps(record.__dict__, default=str)
