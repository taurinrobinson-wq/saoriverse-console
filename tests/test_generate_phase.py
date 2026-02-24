"""Test suite for Phase 1.2: Generate Phase."""

import pytest
import streamlit as st
from emotional_os.deploy.modules.ui_components.pipeline.generate_phase import generate_enhanced_response


def test_strip_prosody_in_generate():
    """Test that prosody markers are handled in generate phase."""
    # Just test that generate doesn't crash with prosody text
    result, elapsed = generate_enhanced_response(
        "test", 
        "[SOFT]Hello[WARM] there",
        {}
    )
    
    assert isinstance(result, str)
    assert isinstance(elapsed, float)


def test_generate_empty_base_response():
    """Test graceful handling of empty base response."""
    result, elapsed = generate_enhanced_response("Test input", "", {})
    
    assert isinstance(result, str)
    assert isinstance(elapsed, float)
    assert elapsed >= 0


def test_generate_returns_tuple():
    """Test that generate returns (text, time) properly."""
    result, elapsed = generate_enhanced_response("Test", "Base response", {})
    
    assert isinstance(result, str)
    assert isinstance(elapsed, float)
    assert len(result) > 0
