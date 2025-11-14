import json
import re
from supabase.tests.glyph_utils import normalize_glyphs
from supabase.tests.test_openai_error_paths import call_openai_with_handling, FakeOpenAIError


def extract_json_from_text(text: str):
    """Attempt to extract a JSON object from an LLM response string.

    This simulates the robust extraction the edge function uses when the model
    returns markdown or extra commentary around the JSON payload.
    """
    # Find the first JSON object-looking substring
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("No JSON object found")
    js = m.group(0)
    return json.loads(js)


def test_extract_json_from_markdown_wrapper():
    payload = {"glyphs": [
        {"name": "chest_tightening", "description": "A tight chest."}]}
    text = "Here is the result:\n```json\n" + \
        json.dumps(payload) + "\n```\nThanks"

    parsed = extract_json_from_text(text)
    out = normalize_glyphs(parsed)
    assert len(out) == 1
    assert out[0]['name'] == 'chest_tightening'


def test_malformed_extractor_response_returns_empty_on_parse_error():
    bad = "{" + '"glyphs": [{"name": "missing_end"'  # intentionally broken
    try:
        _ = extract_json_from_text(bad)
        parsed = True
    except Exception:
        parsed = False
    assert parsed is False
    # When parser can't get JSON, normalizer should be given an empty or invalid input
    assert normalize_glyphs(None) == []


def test_openai_rate_limit_treated_as_recoverable():
    # Reuse the test wrapper to simulate an API error
    def raise_rate_limit():
        raise FakeOpenAIError('rate limit exceeded')

    out = call_openai_with_handling(raise_rate_limit)
    assert out.get('error') == 'api_error'
    assert out.get('recoverable') is True


def test_unicode_and_duplicate_names_preserved():
    raw = [
        {'name': 'café', 'description': 'first'},
        {'name': 'café', 'description': 'second'},
        {'name': 'emoji 😕', 'description': 'emoji present'}
    ]

    out = normalize_glyphs(raw)
    assert len(out) == 3
    assert out[0]['name'] == 'café'
    assert out[1]['name'] == 'café'
    assert 'emoji' in out[2]['name']


def test_ambiguous_name_formats_are_kept_and_truncated():
    long_name = '—' * 200  # em-dash heavy name
    raw = [{'name': long_name, 'description': 'd'}, {
        'name': 'weird/name,with:chars', 'description': 'x'}]
    out = normalize_glyphs(raw)
    assert out[0]['name'] == long_name[:80]
    assert out[1]['name'].startswith('weird/name')
