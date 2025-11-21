import pytest

from emotional_os.core import parse_input, signal_lexicon_path, glyph_db_path


def test_parse_input_returns_glyph():
    """Ensure that parse_input returns at least one glyph for an emotional sample.

    This is a lightweight regression test to catch path or DB mismatches.
    """
    lex = str(signal_lexicon_path())
    db = str(glyph_db_path())

    sample = "I'm holding too much and I feel like I'm unraveling."

    res = parse_input(sample, lex, db_path=db,
                      conversation_context={'messages': []})

    # The parser should always provide a non-empty list of glyph candidates
    glyphs = res.get('glyphs') or []
    assert len(
        glyphs) > 0, f"Expected at least one glyph, got 0. debug_sql={res.get('debug_sql')}"
