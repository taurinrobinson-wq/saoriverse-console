"""Load test: Many humanlike inputs with latency checks."""

import pytest
import time
from emotional_os.deploy.modules.ui_components.pipeline.parse_phase import parse_input_signals
from emotional_os.deploy.modules.ui_components.pipeline.interpret_phase import interpret_emotional_context
from emotional_os.deploy.modules.ui_components.pipeline.generate_phase import generate_enhanced_response


HUMANLIKE_INPUTS = [
    "Lowkey proud of myself today.",
    "I'm so tired of being the responsible one.",
    "Be honest, am I overthinking this?",
    "I feel weirdly calm and I don't trust it.",
    "Today was actually really good, not gonna lie.",
    "I keep saying I'm fine but I'm not.",
    "Tell me something grounding.",
    "I don't know what I'm doing with my life.",
    "I'm in a silly goofy mood.",
    "Please don't give me a generic answer.",
]


@pytest.mark.parametrize("user_input", HUMANLIKE_INPUTS)
def test_load_many_inputs(user_input):
    """Test that system handles diverse inputs within reasonable time."""
    start = time.time()
    
    parsed = parse_input_signals(user_input, {})
    interpretation = interpret_emotional_context(user_input, parsed, {})
    output, generate_time = generate_enhanced_response(user_input, interpretation, {})
    
    elapsed = time.time() - start
    
    assert isinstance(output, str)
    assert len(output.strip()) > 0
    # Allow up to 3 seconds per response (generous for slow systems)
    assert elapsed < 3.0, f"Response too slow for input '{user_input}': {elapsed:.2f}s"


def test_load_batch_latency():
    """Test average latency across batch of inputs."""
    times = []
    
    for user_input in HUMANLIKE_INPUTS[:5]:  # Test first 5
        start = time.time()
        
        parsed = parse_input_signals(user_input, {})
        interpretation = interpret_emotional_context(user_input, parsed, {})
        output, _ = generate_enhanced_response(user_input, interpretation, {})
        
        elapsed = time.time() - start
        times.append(elapsed)
        
        assert len(output) > 0
    
    average = sum(times) / len(times)
    # Average should be reasonable (allow 1s per response on average)
    assert average < 1.5, f"Average latency too high: {average:.2f}s"


if __name__ == "__main__":
    print("Running load test...")
    
    total_time = 0
    errors = 0
    
    for user_input in HUMANLIKE_INPUTS:
        start = time.time()
        try:
            parsed = parse_input_signals(user_input, {})
            interpretation = interpret_emotional_context(user_input, parsed, {})
            output, _ = generate_enhanced_response(user_input, interpretation, {})
            elapsed = time.time() - start
            total_time += elapsed
            print(f"✓ {user_input[:40]:40} | {elapsed:.2f}s | {len(output)} chars")
        except Exception as e:
            errors += 1
            print(f"✗ {user_input[:40]:40} | ERROR: {e}")
    
    avg_time = total_time / len(HUMANLIKE_INPUTS)
    print(f"\nResults: {len(HUMANLIKE_INPUTS) - errors}/{len(HUMANLIKE_INPUTS)} passed")
    print(f"Average time: {avg_time:.2f}s, Total time: {total_time:.2f}s")
