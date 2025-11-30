from emotional_os.deploy.reply_utils import polish_ai_reply


def test_polish_collapses_duplicates():
    s = "I'm here to listen.\n\nI'm here to listen."
    out = polish_ai_reply(s)
    assert "I'm here to listen" not in out or out != s


def test_polish_replaces_generic_fallbacks():
    s = "I'm here to listen."
    out = polish_ai_reply(s)
    # Should pick one of the alternatives
    assert out in {
        "I hear you — tell me more when you're ready.",
        "I'm listening. What's coming up for you right now?",
        "Thank you for sharing. I'm here to listen and support you.",
    }


def test_polish_preserves_long_responses():
    s = "Thank you for sharing. I'm here to listen and support you through whatever you're experiencing. Your feelings are valid and important."
    out = polish_ai_reply(s)
    assert out == s
