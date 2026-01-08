from emotional_os.safety.sanctuary_handler import handle_consent_reply


def test_handle_stay_reply():
    res = handle_consent_reply("A", "high")
    assert res["action"] == "stay"
    assert "here with you" in res["response"].lower()


def test_handle_resources_reply():
    res = handle_consent_reply("B", "high")
    assert res["action"] == "resources"
    assert res["resources"] is not None


def test_handle_escalate_reply():
    res = handle_consent_reply("C", "high")
    assert res["action"] == "escalate"
    assert "guide you" in res["response"]


def test_handle_unknown_reply():
    res = handle_consent_reply("maybe", "medium")
    assert res["action"] == "unknown"
    assert "reply with a" in res["response"].lower()
