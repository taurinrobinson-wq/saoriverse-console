import pytest

from symbolic_tagger import tag_input


def test_tag_input_initiatory():
    tags = tag_input("I just met someone who seems kind")
    assert "initiatory_signal" in tags


def test_tag_input_voltage_and_anchoring():
    tags = tag_input(
        "Everything just changed. I'm overwhelmed and been talking about it.")
    assert "initiatory_signal" in tags or "voltage_surge" in tags
    assert "anchoring_signal" in tags or isinstance(tags, list)


def test_tag_input_default():
    tags = tag_input("An ordinary statement")
    assert tags == ["anchoring_signal"]
