import os

from emotional_os.adapter.comfort_gestures import ASCII_COMFORT_MAP, add_comfort_gesture


def test_add_comfort_gesture_prepends():
    msg = "Thanks for sharing that, I hear you."
    out = add_comfort_gesture("sadness", msg)
    # should prepend one of the sadness gestures
    variants = ASCII_COMFORT_MAP["sadness"]
    assert any(out.startswith(v) for v in variants), f"Output did not start with any sadness variant: {out!r}"
    assert msg in out


def test_deterministic_with_session_seed():
    msg = "A stable test message"
    a = add_comfort_gesture("joy", msg, session_seed="seed123")
    b = add_comfort_gesture("joy", msg, session_seed="seed123")
    assert a == b


def test_add_comfort_gesture_disabled_by_env(monkeypatch):
    monkeypatch.setenv("COMFORT_GESTURES_ENABLED", "false")
    msg = "Thanks for sharing that, I hear you."
    out = add_comfort_gesture("sadness", msg)
    assert out == msg
