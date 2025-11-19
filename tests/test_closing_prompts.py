from main_response_engine import process_user_input
from emotional_os.adapter.closing_prompts import CLOSING_PROMPTS


def test_stress_closing_prompt_appended_by_intent():
    out = process_user_input("I'm feeling a lot of pressure at work", {
                             "emotion": "stress"})
    assert any(
        p in out for p in CLOSING_PROMPTS), "Expected one of the closing prompts to be appended"


def test_stress_closing_prompt_appended_by_text():
    out = process_user_input("I'm stressed about a deadline", {})
    assert any(p in out for p in CLOSING_PROMPTS), "Expected one of the closing prompts to be appended when text mentions stress"
