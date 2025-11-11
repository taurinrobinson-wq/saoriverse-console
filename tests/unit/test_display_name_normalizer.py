from emotional_os.core.signal_parser import _normalize_display_name


def test_normalize_uses_display_name_when_present():
    g = {'display_name': 'Short Name', 'glyph_name': 'A longer original name'}
    assert _normalize_display_name(g) == 'Short Name'


def test_normalize_extracts_first_sentence():
    g = {'glyph_name': 'This is a full sentence. Then more. And more.'}
    assert _normalize_display_name(g) == 'This is a full sentence'


def test_normalize_truncates_long_name():
    long_name = 'Word ' * 20  # long repeated words
    g = {'glyph_name': long_name}
    out = _normalize_display_name(g)
    assert isinstance(out, str)
    # Should be truncated (shorter than original) and include an ellipsis when truncated
    assert len(out) < len(long_name)
    assert out.endswith('...') or len(out) <= 40
