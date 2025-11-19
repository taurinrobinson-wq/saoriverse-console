import os

from emotional_os.adapter.comfort_gestures import add_comfort_gesture, ASCII_COMFORT_MAP


def test_add_comfort_gesture_prepends():
    msg = "Thanks for sharing that, I hear you."
    out = add_comfort_gesture("sadness", msg)
    # should prepend the sadness gesture
    assert out.startswith(ASCII_COMFORT_MAP["sadness"][0])
    assert msg in out


def test_add_comfort_gesture_disabled_by_env(monkeypatch):
    monkeypatch.setenv("COMFORT_GESTURES_ENABLED", "false")
    msg = "Thanks for sharing that, I hear you."
    out = add_comfort_gesture("sadness", msg)
    assert out == msg
