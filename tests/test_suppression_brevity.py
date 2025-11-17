import re

from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer


def sentence_count(text: str) -> int:
    if not text or not text.strip():
        return 0
    # split conservatively on sentence terminators followed by space/newline
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    parts = [p for p in parts if re.search(r'[a-zA-Z0-9]', p)]
    return len(parts)


def test_extract_stop_phrases_quotes_and_unquoted():
    c = DynamicResponseComposer()
    inp = 'Please stop saying: "I\'m here with you" and also stop saying please be shorter'
    phrases = c._extract_stop_phrases(inp)
    # Expect phrase extracted from quotes and the unquoted phrase
    assert any("i'm here with you" in p.lower() for p in phrases)
    assert any('please be shorter' in p.lower() for p in phrases)


def test_suppressions_remove_phrases_from_output():
    c = DynamicResponseComposer()
    # Simulate conversation-level suppression
    ctx = {'suppress_phrases': ["i'm here with you"]}
    out = c.compose_multi_glyph_response(
        'anything', glyphs=[], conversation_context=ctx)
    # Output should not include the suppressed phrase (case-insensitive)
    assert "i'm here with you" not in (out or '').lower()


def test_prefer_short_forces_single_sentence():
    c = DynamicResponseComposer()
    ctx = {'prefer_short': True}
    out = c.compose_multi_glyph_response(
        'some input that would normally produce a long reply', glyphs=[], conversation_context=ctx)
    # Should be at most one sentence
    assert sentence_count(out) <= 1
