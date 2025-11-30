from emotional_os.core import signal_parser


def make_glyph(name, desc, gate="Gate 6", display_name=None, response_template=None):
    return {
        "glyph_name": name,
        "description": desc,
        "gate": gate,
        "display_name": display_name,
        "response_template": response_template,
    }


def test_select_best_glyph_and_returns_glyphs_selected():
    # Create synthetic glyph candidates
    g1 = make_glyph("Still Insight", "Quiet revelation and noticing", gate="Gate 5")
    g2 = make_glyph("Spiral Joy", "A spinning delight", gate="Gate 5")
    g3 = make_glyph("Containment Shield", "Creates boundary", gate="Gate 2")

    # Provide a signal that should match Gate 5
    signals = [{"keyword": "joy", "signal": "λ", "voltage": "high", "tone": "joy"}]

    result = signal_parser.select_best_glyph_and_response([g1, g2, g3], signals, input_text="I feel joy")

    # select_best_glyph_and_response returns a quadruple in current API
    assert result is not None
    assert len(result) == 4
    best_glyph, (response_text, feedback), source, glyphs_selected = result

    # glyphs_selected should be a list sorted by score (desc)
    assert isinstance(glyphs_selected, list)
    assert all("score" in g for g in glyphs_selected), "Each selected glyph should include a 'score'"
    assert all("display_name" in g for g in glyphs_selected), "Each selected glyph should include a 'display_name'"

    # best_glyph should equal the first glyph in glyphs_selected (highest score)
    if glyphs_selected:
        assert best_glyph["glyph_name"] == glyphs_selected[0]["glyph_name"]
