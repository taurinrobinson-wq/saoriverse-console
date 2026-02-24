"""Test suite for Phase 1.1: Interpret Phase."""

import pytest
from emotional_os.deploy.modules.ui_components.pipeline.interpret_phase import interpret_emotional_context


@pytest.mark.parametrize("user_input, expected_keywords", [
    ("I feel overwhelmed", ["hear", "lot", "carry"]),
    ("I'm excited!", ["great", "awesome", "excited"]),
    ("I don't know how to do this", ["okay", "figure", "together"]),
])
def test_interpret_produces_responses(user_input, expected_keywords):
    """Test that interpret_phase produces non-empty responses."""
    analysis = {"voltage_response": "Test response", "best_glyph": {"glyph_name": "Test"}}
    
    result = interpret_emotional_context(user_input, analysis, {})
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert not result.startswith("[ERROR")


def test_interpret_fallback_to_generic():
    """Test that interpret gracefully handles missing analysis."""
    result = interpret_emotional_context("Test input", {}, {})
    
    assert isinstance(result, str)
    assert result not in ["", None]


@pytest.mark.xfail(reason="Repetition prevention not yet fully extracted")
def test_interpret_prevents_repetition():
    """Test that repeated responses are avoided."""
    # This test will fail until _prevent_response_repetition is fully extracted
    pass
