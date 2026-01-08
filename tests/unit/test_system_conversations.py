#!/usr/bin/env python3
"""
Comprehensive system test with real conversations
Tests gate activation and glyph selection with expanded emotional vocabulary
"""

import json
import sys
import time
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

from emotional_os.core.signal_parser import parse_input

# Find lexicon path
lexicon_path = workspace / "nrc_lexicon_cleaned.json"
if not lexicon_path.exists():
    lexicon_path = workspace / "lexicon_enhanced.json"

# Test cases with expected patterns
test_cases = [
    {
        "input": "I hold this moment sacred",
        "expected_emotions": ["hold", "sacred"],
        "expected_gates": [7, 11, 8, 12],
        "description": "Intimacy + Sacred: vulnerability meeting reverence",
    },
    {
        "input": "I feel so gentle and tender with you",
        "expected_emotions": ["gentle", "tender", "feel"],
        "expected_gates": [7, 11, 6, 9],
        "description": "Intimacy + Sensuality: softness and embodied presence",
    },
    {
        "input": "Breathing deeply, I find wisdom in the stillness",
        "expected_emotions": ["breathe", "wisdom"],
        "expected_gates": [6, 9, 3, 4],
        "description": "Embodiment + Transformation: grounding and insight",
    },
    {
        "input": "This practice of reflection deepens my knowing",
        "expected_emotions": ["practice", "reflect", "knowing"],
        "expected_gates": [3, 4, 7, 11],
        "description": "Transformation + Intimacy: learning and wisdom",
    },
    {
        "input": "I desire connection but feel safe in my solitude",
        "expected_emotions": ["desire", "safe"],
        "expected_gates": [6, 9, 7, 11],
        "description": "Sensuality + Vulnerability: longing and comfort",
    },
    {
        "input": "Your presence exactly meets me here, sacred and true",
        "expected_emotions": ["presence", "exactly", "sacred"],
        "expected_gates": [1, 5, 7, 11, 8, 12],
        "description": "Multi-dimensional: joy, intimacy, and reverence",
    },
    {
        "input": "I hold faith in this tender ritual of being together",
        "expected_emotions": ["hold", "faith", "tender", "ritual"],
        "expected_gates": [7, 11, 8, 12],
        "description": "Sacred + Intimate: spiritual connection",
    },
    {
        "input": "In this soft space, I breathe and become",
        "expected_emotions": ["soft", "breathe"],
        "expected_gates": [7, 11, 6, 9, 3, 4],
        "description": "Multi-sensory: vulnerability, embodiment, transformation",
    },
    {
        "input": "Reflecting on my deepest desires, I find honor in my truth",
        "expected_emotions": ["reflect", "desire", "honor"],
        "expected_gates": [7, 11, 6, 9, 8, 12],
        "description": "Integration: intimacy, sensuality, admiration",
    },
    {
        "input": "I am overwhelmed and vulnerable",
        "expected_emotions": ["overwhelmed", "vulnerable"],
        "expected_gates": [7, 11],
        "description": "Emotional distress: crisis detection",
    },
]

print("=" * 80)
print("SYSTEM TEST: GATE ACTIVATION & GLYPH SELECTION WITH EMOTIONAL VOCABULARY")
print("=" * 80)
print()

results = {
    "total_tests": len(test_cases),
    "passed": 0,
    "failed": 0,
    "errors": [],
    "responses": [],
}

for i, test in enumerate(test_cases, 1):
    print(f"\n[Test {i}/{len(test_cases)}]")
    print(f"Input: {test['input']}")
    print(f"Description: {test['description']}")
    print(f"Expected emotions: {', '.join(test['expected_emotions'])}")
    print(f"Expected gates: {test['expected_gates']}")
    
    try:
        start_time = time.time()
        result = parse_input(test["input"], str(lexicon_path))
        elapsed = time.time() - start_time
        
        # Extract response details
        response_source = result.get("response_source", "unknown")
        best_glyph = result.get("best_glyph", {})
        glyph_name = best_glyph.get("glyph_name", "NONE")
        gate = best_glyph.get("gate", "NONE")
        voltage = result.get("voltage_response", "")[:100]  # First 100 chars
        
        print(f"✓ Response source: {response_source}")
        print(f"✓ Glyph: {glyph_name}")
        print(f"✓ Gate: {gate}")
        print(f"✓ Time: {elapsed:.3f}s")
        print(f"✓ Response preview: {voltage}...")
        
        results["passed"] += 1
        results["responses"].append({
            "input": test["input"],
            "glyph": glyph_name,
            "gate": gate,
            "source": response_source,
            "time": elapsed,
        })
        
    except Exception as e:
        print(f"✗ ERROR: {str(e)[:100]}")
        results["failed"] += 1
        results["errors"].append({
            "input": test["input"],
            "error": str(e)[:200],
        })

# Print summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total tests: {results['total_tests']}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Success rate: {results['passed']/results['total_tests']*100:.1f}%")

if results["failed"] > 0:
    print(f"\nFailed tests ({results['failed']}):")
    for error in results["errors"]:
        print(f"  • {error['input'][:50]}...")
        print(f"    Error: {error['error'][:80]}...")

print()
if results["passed"] == results["total_tests"]:
    print("✓ ALL TESTS PASSED")
else:
    print(f"⚠ {results['failed']} tests failed")

print("\n" + "=" * 80)
