import json
import re
import pytest


# Local test-only fake error to avoid importing the installed `supabase` package
class FakeOpenAIError(Exception):
    pass


def assemble_stream_and_extract(generator_callable):
    """Consume a generator-producing callable that yields string chunks.

    Returns a dict with either 'result' (parsed JSON) or flags describing
    incomplete/error conditions along with the collected buffer for
    inspection.
    """
    buf = ""
    try:
        for chunk in generator_callable():
            # chunks may be bytes in real streams; tests use str for simplicity
            buf += chunk
    except TimeoutError:
        return {"incomplete": True, "buffer": buf}
    except FakeOpenAIError:
        return {"error": "api_error", "buffer": buf}
    except Exception:
        return {"error": "unknown", "buffer": buf}

    # Attempt to robustly extract the first JSON object from the collected text
    m = re.search(r"\{.*\}", buf, re.DOTALL)
    if not m:
        return {"incomplete": True, "buffer": buf}

    js = m.group(0)
    try:
        return {"result": json.loads(js)}
    except Exception:
        return {"incomplete": True, "buffer": buf}


def test_streaming_complete_reassembles():
    def generator():
        yield "Here is the result:\n```json\n"
        yield '{"glyphs": ['
        yield '{"name": "streamed_one", "description": "desc"}'
        yield ']}'
        yield '\n```\n'

    out = assemble_stream_and_extract(lambda: generator())
    assert 'result' in out
    assert out['result']['glyphs'][0]['name'] == 'streamed_one'


def test_streaming_truncated_returns_incomplete():
    def generator():
        yield "Here is the result:\n```json\n"
        yield '{"glyphs": ['
        # partial chunk for the object name
        yield '{"name": "partial'
        raise TimeoutError('stream timed out')

    out = assemble_stream_and_extract(lambda: generator())
    assert out.get('incomplete') is True
    assert out.get('buffer', '').startswith('Here is the result')


def test_streaming_api_error_during_stream():
    def generator():
        yield 'Beginning of reply...'
        # simulate remote API throwing during streaming
        raise FakeOpenAIError('internal API error while streaming')

    out = assemble_stream_and_extract(lambda: generator())
    assert out.get('error') == 'api_error'
    assert 'Beginning of reply' in out.get('buffer', '')
