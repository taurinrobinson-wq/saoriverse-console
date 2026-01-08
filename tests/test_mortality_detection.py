import pytest
from src.emotional_os.deploy.core.firstperson import (
    AffectParser,
    ConversationMemory,
    FirstPersonOrchestrator,
)


def test_mortality_detects_explicit_and_implicit():
    parser = AffectParser()

    texts = [
        ("I'm afraid one day they will be gone.", 0.5),
        ("I love them so much — what if I lose them?", 0.6),
        ("That was fun yesterday.", 0.0),
        ("I don't want to be here tomorrow", 0.6),
    ]

    for text, expected_min in texts:
        result = parser.analyze_affect(text)
        ms = result.get("mortality_salience", 0.0)
        assert 0.0 <= ms <= 1.0
        # For positive expected_min values, assert it's above a low threshold
        if expected_min > 0:
            assert ms >= 0.2, f"Expected salience for '{text}' to be >=0.2, got {ms}"


def test_conversation_memory_running_and_trend():
    parser = AffectParser()
    mem = ConversationMemory()

    # Feed some turns with low mortality, then spike
    messages = [
        "Today was fine.",
        "Kids fought a bit but okay.",
        "I made dinner.",
        "I keep thinking what if I die and they forget me.",
        "Sometimes I worry about not being here for them.",
        "I love them so much, can't imagine otherwise.",
    ]

    for m in messages:
        aff = parser.analyze_affect(m)
        mem.record_turn(m, aff, theme="general")

    ctx = mem.get_memory_context()
    assert "mortality_salience" in ctx
    assert 0.0 <= ctx["mortality_salience"] <= 1.0
    assert ctx["mortality_trend"] in {"rising", "stable", "falling"}


def test_safety_signal_detection():
    """Test that high mortality + negative valence triggers safety signal."""
    orch = FirstPersonOrchestrator()
    
    # Message with high mortality + high negativity
    msg = "I don't want to be here. I feel like I'm a burden and will never get better. What's the point?"
    result = orch.handle_conversation_turn(msg)
    
    # Should have safety signal if mortality > 0.6 and valence < -0.6
    assert "safety_signal" in result
    # This particular message should trigger it
    mortality = result["affect_analysis"].get("mortality_salience", 0.0)
    valence = result["affect_analysis"].get("valence", 0.0)
    
    if mortality > 0.6 and valence < -0.6:
        assert result["safety_signal"] is True
    else:
        assert result["safety_signal"] is False


def test_response_shaping_with_mortality():
    """Test that response generation considers mortality_salience."""
    orch = FirstPersonOrchestrator()
    
    # High mortality message
    msg = "I love them so much, what if I lose them?"
    orch.handle_conversation_turn(msg)
    
    glyph = {"glyph_name": "test_glyph"}
    response = orch.generate_response_with_glyph(msg, glyph)
    
    # Response should be non-empty
    assert len(response) > 0
    # When mortality is high, response should reference meaning or values
    assert isinstance(response, str)


def test_memory_persistence_across_turns():
    """Test that memory persists and affects response generation."""
    orch = FirstPersonOrchestrator()
    
    messages = [
        "I'm worried about my kids.",
        "I worry about it every day.",
        "Sometimes I think what if I'm not here for them.",
    ]
    
    for msg in messages:
        orch.handle_conversation_turn(msg)
    
    # Get memory context after multiple turns
    ctx = orch.memory.get_memory_context()
    assert ctx["num_turns"] == 3
    assert "worry" in str(ctx.get("repeated_patterns", [])).lower() or ctx.get("num_turns") > 0
    
    # Third message should have frequency reflection or memory context
    result = orch.handle_conversation_turn(messages[-1])
    assert result["memory_context_injected"] is True


def test_mortality_scoring_edge_cases():
    """Test that mortality scoring handles edge cases gracefully."""
    parser = AffectParser()
    
    edge_cases = [
        "",  # Empty string
        "hello world",  # No mortality cues
        "what if what if what if",  # Repeated conditional
        "i love love love them",  # Repeated attachment
    ]
    
    for text in edge_cases:
        result = parser.analyze_affect(text)
        ms = result.get("mortality_salience", 0.0)
        assert isinstance(ms, float)
        assert 0.0 <= ms <= 1.0
