import pytest

from response_selector import classify_signal, select_first_turn_response


def test_positive_signal():
    user_input = "I just met someone who really sees me."
    category = classify_signal(user_input)
    assert category == "positive"
    response = select_first_turn_response(user_input)
    assert any(k in response.lower() for k in ("meaningful", "wonderful", "glad"))


def test_silence_signal_with_typo():
    user_input = "I've been trying to understand my dad's silince lately."
    category = classify_signal(user_input)
    assert category == "silence"
    response = select_first_turn_response(user_input)
    assert any(k in response.lower() for k in ("silent", "silence"))


def test_overwhelm_signal_with_typo():
    user_input = "Everything just changed. I feel like I'm spining."
    category = classify_signal(user_input)
    assert category == "overwhelm"
    response = select_first_turn_response(user_input)
    assert any(k in response.lower() for k in ("overwhelm", "take your time", "overwhelming"))


def test_loss_signal():
    user_input = "I'm struggling with a great los."
    category = classify_signal(user_input)
    # fuzzy match should catch "los" ~ "loss"
    assert category == "loss"
    response = select_first_turn_response(user_input)
    assert any(k in response.lower() for k in ("painful", "grief"))


def test_ambiguous_signal():
    user_input = "Things have been different."
    category = classify_signal(user_input)
    assert category == "ambiguous"
    response = select_first_turn_response(user_input)
    assert any(k in response.lower() for k in ("important", "detail", "listen"))
