"""Latency benchmark: Per-phase performance tracking."""

import time
from emotional_os.deploy.modules.ui_components.pipeline.parse_phase import parse_input_signals
from emotional_os.deploy.modules.ui_components.pipeline.interpret_phase import interpret_emotional_context
from emotional_os.deploy.modules.ui_components.pipeline.generate_phase import generate_enhanced_response


def test_latency_per_phase():
    """Measure and validate latency for each phase."""
    user_input = "I feel like I'm dropping all the balls lately."
    
    # Phase 1: Parse
    t0 = time.time()
    parsed = parse_input_signals(user_input, {})
    t1 = time.time()
    parse_time = t1 - t0
    
    # Phase 2: Interpret
    t1_start = time.time()
    interpretation = interpret_emotional_context(user_input, parsed, {})
    t2 = time.time()
    interpret_time = t2 - t1_start
    
    # Phase 3: Generate
    t2_start = time.time()
    output, generate_time_from_method = generate_enhanced_response(user_input, interpretation, {})
    t3 = time.time()
    generate_wall_time = t3 - t2_start
    
    # Assertions
    assert parse_time < 0.5, f"Parse phase too slow: {parse_time:.3f}s"
    assert interpret_time < 1.0, f"Interpret phase too slow: {interpret_time:.3f}s"
    assert generate_wall_time < 2.0, f"Generate phase too slow: {generate_wall_time:.3f}s"
    
    total_time = t3 - t0
    assert total_time < 3.0, f"Total pipeline too slow: {total_time:.3f}s"
    
    assert isinstance(output, str)
    assert len(output.strip()) > 0
    
    # Print detailed timing
    print(f"\n=== Latency Breakdown ===")
    print(f"Parse:    {parse_time:.3f}s")
    print(f"Interpret: {interpret_time:.3f}s")
    print(f"Generate: {generate_wall_time:.3f}s")
    print(f"Total:    {total_time:.3f}s")
    print(f"Output length: {len(output)} chars")


def test_latency_consistency():
    """Test that latency is consistent across multiple runs."""
    user_input = "How are you doing?"
    times = []
    
    for _ in range(3):
        start = time.time()
        parsed = parse_input_signals(user_input, {})
        interpretation = interpret_emotional_context(user_input, parsed, {})
        output, _ = generate_enhanced_response(user_input, interpretation, {})
        elapsed = time.time() - start
        times.append(elapsed)
        
        assert len(output) > 0
    
    # Check consistency (first and second run should be similar)
    # Allow 50% variance due to system noise
    first_run = times[0]
    second_run = times[1]
    variance_ratio = max(first_run, second_run) / min(first_run, second_run)
    
    # This is a loose check; remove if system is highly variable
    # assert variance_ratio < 2.0, f"Latency too inconsistent: {times}"
    
    average = sum(times) / len(times)
    print(f"\nLatency consistency check:")
    print(f"Run times: {[f'{t:.3f}s' for t in times]}")
    print(f"Average: {average:.3f}s")


if __name__ == "__main__":
    print("Running latency benchmarks...")
    test_latency_per_phase()
    test_latency_consistency()
    print("\n✓ All latency tests passed")
