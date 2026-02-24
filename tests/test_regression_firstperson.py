"""Regression test suite: Known tricky cases that should NOT happen."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from emotional_os.deploy.modules.ui_components.pipeline.parse_phase import parse_input_signals
from emotional_os.deploy.modules.ui_components.pipeline.interpret_phase import interpret_emotional_context
from emotional_os.deploy.modules.ui_components.pipeline.generate_phase import generate_enhanced_response


def _full_pipeline(user_input):
    """Run full pipeline: parse → interpret → generate."""
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, _ = generate_enhanced_response(user_input, interpretation, {})
    return output


@pytest.mark.parametrize("user_input,forbidden_words", [
    ("I said I don't want advice.", ["you should", "have you tried"]),
    ("Stop calling me resilient, I'm tired.", ["resilient", "bounce back"]),
    ("I'm joking, I'm actually fine lol.", ["are you sure you're okay?"]),
    ("I'm not asking you to fix it.", ["solution", "fix this"]),
])
def test_regression_respects_stated_needs(user_input, forbidden_words):
    """Verify system respects explicit opt-outs and declarations."""
    output = _full_pipeline(user_input)
    
    for word in forbidden_words:
        assert word.lower() not in output.lower(), \
            f"Forbidden word '{word}' found in response: {output}"


def test_regression_no_generic_canned_responses():
    """Verify responses aren't canned/templated."""
    inputs = [
        "I'm overwhelmed.",
        "I feel lost.",
        "Help me.",
    ]
    
    responses = [_full_pipeline(inp) for inp in inputs]
    
    # Responses should be different from each other  (not all identical)
    assert len(set(responses)) > 1, "All responses are identical (likely canned)"


def test_regression_validates_not_dismisses():
    """Verify system validates concerns rather than dismissing them."""
    output = _full_pipeline("I'm worried I'm not good enough.")
    
    # Should validate, not dismiss
    dismissive_phrases = [
        "don't worry",
        "it's fine",
        "you're overthinking",
        "everyone feels that way",
    ]
    
    for phrase in dismissive_phrases:
        assert phrase.lower() not in output.lower(), \
            f"Dismissive phrase '{phrase}' found in response"


def test_regression_no_toxic_reframes():
    """Verify system doesn't reframe pain as growth/opportunity."""
    output = _full_pipeline("I've been really struggling and it hurts.")
    
    # Should NOT immediately jump to "this is an opportunity"
    toxic_reframes = [
        "this is an opportunity",
        "you'll come out stronger",
        "this is a gift",
        "everything happens for a reason",
    ]
    
    for reframe in toxic_reframes:
        assert reframe.lower() not in output.lower(), \
            f"Toxic reframe '{reframe}' found in response"


if __name__ == "__main__":
    print("Running regression tests...")
    
    test_cases = [
        ("I said I don't want advice.", ["you should", "have you tried"]),
        ("Stop calling me resilient, I'm tired.", ["resilient", "bounce back"]),
        ("I'm joking, I'm actually fine lol.", ["are you sure you're okay?"]),
        ("I'm not asking you to fix it.", ["solution", "fix this"]),
    ]
    
    passed = 0
    failed = 0
    
    for user_input, forbidden_words in test_cases:
        try:
            output = _full_pipeline(user_input)
            for word in forbidden_words:
                assert word.lower() not in output.lower()
            print(f"✓ {user_input[:50]:50}")
            passed += 1
        except Exception as e:
            print(f"✗ {user_input[:50]:50} | {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
