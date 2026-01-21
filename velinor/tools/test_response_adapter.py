from response_adapter import (
    reflect_relationship,
    suggest_resonance_action,
    translate_emotional_response,
)


def test_translate_emotional_response_basic():
    out = translate_emotional_response(
        {"emotion": "longing", "intensity": "high", "context": "meeting", "resonance": "presence"}
    )
    assert "longing" in out
    assert "presence" in out


def test_reflect_relationship():
    r = reflect_relationship("Ari", {"emotional_tone": ["tender"], "recent_summary": "felt seen"})
    assert "Ari" in r and "felt seen" in r


def test_suggest_resonance_action():
    s = suggest_resonance_action("joy", "relationship")
    assert "explore" in s or "Would you" in s
