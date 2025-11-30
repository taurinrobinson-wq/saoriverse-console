import pytest

from emotional_os.core import signal_parser as sp


def test_glyph_tiebreak_is_deterministic_by_input_order():
    # Two glyphs that both contain the signal keyword "match" should get the same score (+6)
    glyph_a = {"glyph_name": "Alpha match", "description": "", "gate": "Gate 2"}
    glyph_b = {"glyph_name": "Beta match", "description": "", "gate": "Gate 2"}

    signals = [{"keyword": "match", "signal": "β", "voltage": "medium", "tone": "containment"}]

    # Order A then B
    best, (response, fb), src, selected = sp.select_best_glyph_and_response(
        [glyph_a, glyph_b], signals, input_text="match"
    )
    assert len(selected) >= 2
    # Both selected glyphs should have equal score (the signal-keyword boost)
    scores = [g.get("score") for g in selected]
    assert scores[0] == scores[1]
    # Tie-breaker should favor the first glyph in the input order (stable sort)
    assert selected[0]["glyph_name"] == "Alpha match"

    # Now reverse input order: B then A
    best2, (response2, fb2), src2, selected2 = sp.select_best_glyph_and_response(
        [glyph_b, glyph_a], signals, input_text="match"
    )
    assert len(selected2) >= 2
    assert selected2[0]["glyph_name"] == "Beta match"
