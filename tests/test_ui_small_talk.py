from ui.logic import small_talk_reply


def test_thanks_and_bye_get_a_friendly_reply():
    for text in ["thanks", "Thanks!", "  thank you so much. ", "THX", "cảm ơn", "Cảm ơn bạn!", "cam on", "cám ơn bạn"]:
        assert small_talk_reply(text).startswith("You're welcome")
    for text in ["bye", "Goodbye!", "tạm biệt", "tam biet"]:
        assert small_talk_reply(text).startswith("Goodbye")


def test_real_questions_still_go_to_the_assistant():
    for text in [
        "thanks, and where is the library?",
        "Can I register my thesis with 118 credits?",
        "I lost my student card",
        "hello",  # the backend already answers greetings
        "",
    ]:
        assert small_talk_reply(text) is None


def test_decomposed_vietnamese_is_matched():
    import unicodedata

    assert small_talk_reply(unicodedata.normalize("NFD", "cảm ơn")).startswith("You're welcome")
