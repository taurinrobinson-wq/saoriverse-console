from emotional_os.safety.sanctuary_handler import (
    build_consent_prompt,
    classify_risk,
    detect_crisis,
)


def test_classify_risk_high():
    text = "I just want to end my life. I'm going to kill myself tonight."
    assert classify_risk(text) == "high"
    assert detect_crisis(text) is True


def test_classify_risk_low_medium():
    text_low = "I've had flashbacks and feel triggered but not sure what to do."
    assert classify_risk(text_low) in ("low", "medium")

    text_medium = "I'm having overwhelming panic and flashbacks from trauma."
    assert classify_risk(text_medium) == "medium"


def test_build_consent_prompt_contains_options():
    prompt = build_consent_prompt("high")
    assert "A)" in prompt and "B)" in prompt and "C)" in prompt
