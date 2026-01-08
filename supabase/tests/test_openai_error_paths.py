import pytest


class FakeOpenAIError(Exception):
    pass


def call_openai_with_handling(callable_obj):
    """Wrapper used in tests to simulate calling OpenAI and handling errors.

    It expects `callable_obj` to be a callable that may raise exceptions.
    The wrapper returns a dict with either 'result' or 'error' describing fallback.
    """
    try:
        res = callable_obj()
        return {"result": res}
    except TimeoutError:
        return {"error": "timeout", "recoverable": True}
    except FakeOpenAIError:
        return {"error": "api_error", "recoverable": True}
    except Exception:
        return {"error": "unknown", "recoverable": False}


def test_openai_timeout_handled():
    def raise_timeout():
        raise TimeoutError("timed out")

    out = call_openai_with_handling(raise_timeout)
    assert out["error"] == "timeout" and out["recoverable"] is True


def test_openai_api_error_handled():
    def raise_api_error():
        raise FakeOpenAIError("rate limit")

    out = call_openai_with_handling(raise_api_error)
    assert out["error"] == "api_error" and out["recoverable"] is True


def test_openai_malformed_response_handled():
    def raise_value_error():
        raise ValueError("malformed response")

    out = call_openai_with_handling(raise_value_error)
    assert out["error"] == "unknown" and out["recoverable"] is False
