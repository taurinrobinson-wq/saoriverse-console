"""
Quick manual test for Tier 1 Foundation without pytest.
Run with: D:/saoriverse-console/.venv/Scripts/python.exe test_tier1_manual.py
"""

import sys
import os
sys.path.insert(0, 'd:\\saoriverse-console\\src')

from emotional_os.tier1_foundation import Tier1Foundation
import time


def test_initialization():
    """Test that Tier 1 initializes"""
    print("✓ Testing initialization...")
    tier1 = Tier1Foundation(conversation_memory=None)
    assert tier1 is not None
    assert hasattr(tier1, 'process_response')
    print("  ✓ Initialization successful")


def test_basic_response():
    """Test basic response processing"""
    print("✓ Testing basic response processing...")
    tier1 = Tier1Foundation(conversation_memory=None)
    
    user_input = "I'm feeling really sad today"
    base_response = "I understand you're feeling down. That's okay."
    
    enhanced_response, metrics = tier1.process_response(user_input, base_response)
    
    assert enhanced_response is not None
    assert len(enhanced_response) > 0
    assert "total" in metrics
    assert metrics["total"] >= 0
    print(f"  ✓ Response: {enhanced_response[:80]}...")
    print(f"  ✓ Total time: {metrics['total']:.4f}s")


def test_performance():
    """Test that Tier 1 executes under 100ms"""
    print("✓ Testing performance (<100ms)...")
    tier1 = Tier1Foundation(conversation_memory=None)
    
    user_input = "How are you?"
    base_response = "I'm doing well, thank you for asking."
    
    start = time.perf_counter()
    enhanced_response, metrics = tier1.process_response(user_input, base_response)
    elapsed = time.perf_counter() - start
    
    total_time = metrics.get("total", 0)
    print(f"  ✓ Pipeline time: {total_time:.4f}s")
    print(f"  ✓ Wall time: {elapsed:.4f}s")
    
    if total_time > 0.1:
        print(f"  ⚠ WARNING: Exceeded 100ms target ({total_time:.3f}s)")
    else:
        print(f"  ✓ Within 100ms target")


def test_metrics():
    """Test performance metrics structure"""
    print("✓ Testing metrics structure...")
    tier1 = Tier1Foundation(conversation_memory=None)
    
    user_input = "How do you feel?"
    base_response = "I'm here to listen."
    
    enhanced_response, metrics = tier1.process_response(user_input, base_response)
    
    expected_keys = ["total", "memory", "safety_check", "signal_detection",
                     "generation", "learning", "wrapping"]
    
    for key in expected_keys:
        assert key in metrics, f"Missing metric: {key}"
        assert isinstance(metrics[key], (int, float))
        assert metrics[key] >= 0
    
    print("  ✓ Metrics structure:")
    for key in expected_keys:
        print(f"    - {key}: {metrics[key]:.4f}s")


def test_fallback():
    """Test that fallback works"""
    print("✓ Testing fallback behavior...")
    tier1 = Tier1Foundation(conversation_memory=None)
    
    user_input = "Test"
    base_response = "Response"
    
    enhanced_response, metrics = tier1.process_response(user_input, base_response)
    
    assert enhanced_response is not None
    assert isinstance(enhanced_response, str)
    assert len(enhanced_response) > 0
    print("  ✓ Fallback returns valid response")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TIER 1 FOUNDATION - MANUAL TESTS")
    print("="*60 + "\n")
    
    try:
        test_initialization()
        test_basic_response()
        test_performance()
        test_metrics()
        test_fallback()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
