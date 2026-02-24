"""E2E test suite: Real-world human conversation scenarios."""

import pytest
from emotional_os.deploy.modules.ui_components.pipeline.parse_phase import parse_input_signals
from emotional_os.deploy.modules.ui_components.pipeline.interpret_phase import interpret_emotional_context
from emotional_os.deploy.modules.ui_components.pipeline.generate_phase import generate_enhanced_response


# Helper: Assert qualitative traits
def assert_contains_any(text, keywords):
    """Assert that text contains at least one keyword (case-insensitive)."""
    assert any(k.lower() in text.lower() for k in keywords), \
        f"Expected one of {keywords} in: {text}"


def assert_not_repetitive(text):
    """Assert that response doesn't repeat the same line."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    assert len(lines) == len(set(lines)), "Response contains repeated lines"


# Test 1: Emotional vulnerability
def test_e2e_vulnerability():
    """Test response to expressing feeling overwhelmed."""
    user_input = "I feel like I'm failing at everything lately."
    
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, _ = generate_enhanced_response(user_input, interpretation, {})
    
    # Should acknowledge struggle, not reinforce negative self-talk
    assert isinstance(output, str)
    assert len(output) > 10
    assert "fail" not in output.lower() or "you're not" in output.lower()
    assert_not_repetitive(output)


# Test 2: Playful banter
def test_e2e_banter():
    """Test lighthearted, playful conversation."""
    user_input = "Okay but be honest, do you think I'm dramatic?"
    
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, _ = generate_enhanced_response(user_input, interpretation, {})
    
    assert isinstance(output, str)
    assert len(output) > 10
    assert_not_repetitive(output)


# Test 3: High-energy excitement
def test_e2e_excited():
    """Test response to good news / excitement."""
    user_input = "Bro I just got the job!!"
    
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, _ = generate_enhanced_response(user_input, interpretation, {})
    
    assert isinstance(output, str)
    assert len(output) > 10
    # Should be positive, celebratory
    assert_not_repetitive(output)


# Test 4: Boundary-setting
def test_e2e_boundary():
    """Test respectful boundary acknowledgment."""
    user_input = "I don't want to talk about that right now."
    
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, _ = generate_enhanced_response(user_input, interpretation, {})
    
    assert isinstance(output, str)
    assert len(output) > 10
    # Should not interrogate boundaries
    assert "why" not in output.lower() and "can you tell me" not in output.lower()
    assert_not_repetitive(output)


# Test 5: Repair after misalignment
def test_e2e_repair():
    """Test graceful repair when misaligned."""
    user_input = "That wasn't what I meant at all."
    
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, _ = generate_enhanced_response(user_input, interpretation, {})
    
    assert isinstance(output, str)
    assert len(output) > 10
    assert_not_repetitive(output)


# Test 6: Humor + light teasing
def test_e2e_teasing():
    """Test playful, confident teasing."""
    user_input = "Don't hype me up too much, I'll get cocky."
    
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, _ = generate_enhanced_response(user_input, interpretation, {})
    
    assert isinstance(output, str)
    assert len(output) > 10
    assert_not_repetitive(output)


# Test 7: Existential heaviness
def test_e2e_existential():
    """Test response to existential questioning."""
    user_input = "Sometimes I wonder what the point of any of this is."
    
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, _ = generate_enhanced_response(user_input, interpretation, {})
    
    assert isinstance(output, str)
    assert len(output) > 10
    # Should validate the question, not dismiss
    assert_not_repetitive(output)


if __name__ == "__main__":
    # Simple local runner
    tests = [
        ("vulnerability", test_e2e_vulnerability),
        ("banter", test_e2e_banter),
        ("excited", test_e2e_excited),
        ("boundary", test_e2e_boundary),
        ("repair", test_e2e_repair),
        ("teasing", test_e2e_teasing),
        ("existential", test_e2e_existential),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
