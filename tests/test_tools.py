import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition


def test_tuition_matches_monolith():
    # characterisation: monolith answered "tuition for 18 credits and 2 retake" with 9450000 VND
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000


def test_tuition_without_retake():
    assert tuition(18, 0, 450_000, 1.5, 30) == 8_100_000


@pytest.mark.parametrize("credits", [1, 30])
def test_tuition_accepts_bounds(credits):
    assert tuition(credits, 0, 450_000, 1.5, 30) == credits * 450_000


@pytest.mark.parametrize("credits", [0, 31])
def test_tuition_rejects_out_of_range(credits):
    with pytest.raises(InvalidRequest):
        tuition(credits, 0, 450_000, 1.5, 30)


def test_tuition_rejects_negative_retake():
    with pytest.raises(InvalidRequest):
        tuition(18, -1, 450_000, 1.5, 30)


def test_parse_with_retake():
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_parse_with_plural_retakes_and_punctuation():
    assert parse_credits("Fee for 18 credits, 2 retakes?") == (18, 2)


def test_parse_without_retake():
    assert parse_credits("what is the fee for 15 credits?") == (15, 0)


def test_parse_retake_before_credits():
    assert parse_credits("fee with 3 retake credits and 12 credits") == (12, 3)


def test_parse_keeps_out_of_range_for_tuition_to_reject():
    assert parse_credits("tuition 40 credits") == (40, 0)


def test_parse_without_number_asks_for_credits():
    with pytest.raises(InvalidRequest, match="How many credits?"):
        parse_credits("how much is the tuition?")
