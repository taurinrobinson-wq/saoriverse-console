import os

# Lightweight test skeleton to assert anti-fallback behavior when remote AI is disabled.
# This test is intentionally minimal and non-invasive; it does not require remote services.


def test_parse_input_returns_voltage_response_and_source():
    # Ensure remote AI is disabled for the test run
    os.environ['ALLOW_REMOTE_AI'] = '0'

    try:
        from emotional_os.glyphs.signal_parser import parse_input
    except Exception:
        # If the import fails, the test should fail to notify the reviewer
        assert False, "Could not import parse_input from emotional_os.glyphs.signal_parser"

    res = parse_input('I feel anxious and overwhelmed',
                      'emotional_os/parser/signal_lexicon.json', db_path='emotional_os/glyphs/glyphs.db')

    assert isinstance(res, dict)
    assert 'voltage_response' in res
    assert 'response_source' in res
    # Ensure we didn't crash into a None or missing field
    assert res.get('voltage_response') is not None
