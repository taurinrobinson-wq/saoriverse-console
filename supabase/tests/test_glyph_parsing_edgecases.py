from supabase.tests.glyph_utils import normalize_glyphs, is_valid_glyph_shape


def test_empty_input_returns_empty_list():
    assert normalize_glyphs(None) == []
    assert normalize_glyphs({}) == []


def test_malformed_glyph_entries_are_ignored():
    raw = {'glyphs': [
        {'name': 'valid_one', 'description': 'ok'},
        {'no_name': True},
        'just a string',
        123,
        {'name': ''},
    ]}

    out = normalize_glyphs(raw)
    assert len(out) == 1
    assert out[0]['name'] == 'valid_one'


def test_name_and_description_truncation_and_depth_clamp():
    long_name = 'n' * 200
    long_desc = 'd' * 1000
    raw = [{'name': long_name, 'description': long_desc,
            'depth': 10}, {'name': 'a', 'depth': -5}]

    out = normalize_glyphs(raw)
    assert out[0]['name'] == long_name[:80]
    assert len(out[0]['description']) == 300
    assert out[0]['depth'] == 5
    assert out[1]['depth'] == 1


def test_optional_fields_copied_and_truncated():
    raw = [{'name': 'x', 'response_layer': 'r' * 200,
            'glyph_type': 't'}, {'name': 'y', 'symbolic_pairing': 123}]
    out = normalize_glyphs(raw)
    assert out[0]['response_layer'] == 'r' * 80
    # non-string optional is skipped for second glyph
    assert 'symbolic_pairing' not in out[1]


def test_is_valid_glyph_shape():
    assert is_valid_glyph_shape({'glyphs': []})
    assert is_valid_glyph_shape([{'name': 'a'}])
    assert not is_valid_glyph_shape({'not_glyphs': 1})
