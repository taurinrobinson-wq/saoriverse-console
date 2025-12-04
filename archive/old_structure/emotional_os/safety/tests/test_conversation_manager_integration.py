from emotional_os.safety.conversation_manager import SanctuaryConversationManager


def test_consent_prompt_and_reply_flow():
    manager = SanctuaryConversationManager()
    session = "session1"
    user_hash = "user123"

    # Step 1: user sends a high-risk message -> consent_prompt returned
    msg = "I think I'm going to kill myself tonight"
    res = manager.process_user_message(session, user_hash, msg)
    assert res["type"] == "consent_prompt"
    assert "A)" in res["payload"] or "reply" in res["payload"].lower()

    # Step 2: user replies 'A' to stay
    res2 = manager.process_user_message(session, user_hash, "A")
    assert res2["type"] == "consent_reply"
    assert res2["payload"]["action"] == "stay"

    # Step 3: session should no longer be pending; next safe message goes to analysis
    res3 = manager.process_user_message(session, user_hash, "I'm feeling a bit better now")
    assert res3["type"] in ("analysis",)
