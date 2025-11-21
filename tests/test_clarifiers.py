import re
from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer


def test_make_clarifying_question_has_i_hear_for_emo():
    c = DynamicResponseComposer()
    extracted = {"emotional_words": ["anxious"]}
    q = c._make_clarifying_question("I am feeling anxious", extracted)
    assert "I hear" in q, f"Clarifier did not contain 'I hear': {q}"
    assert "I can hear" not in q, f"Clarifier contains 'I can hear': {q}"


def test_make_clarifying_question_has_i_hear_for_nonemo():
    c = DynamicResponseComposer()
    extracted = {}
    q = c._make_clarifying_question("Not sure", extracted)
    # Non-emotional variants should still include 'I hear' (or similar phrasing we've enforced)
    assert re.search(r"I hear", q), f"Clarifier did not contain 'I hear': {q}"
    assert "I can hear" not in q, f"Clarifier contains 'I can hear': {q}"


def test_compose_multi_glyph_response_clarifier():
    c = DynamicResponseComposer()
    out = c.compose_multi_glyph_response("I am feeling anxious", [])
    assert "I hear" in out, f"Compose output missing 'I hear': {out}"
    assert "I can hear" not in out, f"Compose output contains 'I can hear': {out}"
