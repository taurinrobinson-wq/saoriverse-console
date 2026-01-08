#!/usr/bin/env python3
"""
Integration validation test
Verifies that the lexicon is properly integrated into signal_parser.parse_input() and parse_signals()
"""

import json
import sys
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

from emotional_os.core.signal_parser import parse_input, parse_signals

# Load the signal map for reference
signal_lexicon_path = workspace / "emotional_os" / "data" / "signal_lexicon.json"
if signal_lexicon_path.exists():
    with open(signal_lexicon_path) as f:
        signal_map = json.load(f)
else:
    signal_map = {}
    print("[WARNING] signal_lexicon.json not found at expected location")

# Find lexicon path for parse_input
lexicon_path = workspace / "nrc_lexicon_cleaned.json"
if not lexicon_path.exists():
    lexicon_path = workspace / "lexicon_enhanced.json"

print("=" * 70)
print("LEXICON INTEGRATION VALIDATION TEST")
print("=" * 70)

test_cases = [
    {
        "input": "I hold this moment sacred",
        "expected_emotional": True,
        "expected_words": ["hold", "sacred"],
    },
    {
        "input": "I feel safe being tender with you",
        "expected_emotional": True,
        "expected_words": ["feel", "safe", "tender"],
    },
    {
        "input": "Your presence exactly meets me here",
        "expected_emotional": True,
        "expected_words": ["exactly"],
    },
    {
        "input": "I'm feeling overwhelmed and vulnerable",
        "expected_emotional": True,
        "expected_words": ["overwhelmed", "vulnerable"],
    },
    {
        "input": "What time is the meeting?",
        "expected_emotional": False,
        "expected_words": [],
    },
]

print("\n[Testing parse_input() emotional detection]\n")

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}: {test['input']}")
    
    try:
        # Call parse_input with required arguments
        result = parse_input(
            test["input"],
            str(lexicon_path),
        )
        
        # Check if we got an emotional response (response_source should indicate emotion processing)
        response_source = result.get("response_source", "")
        is_emotional = response_source != "short_circuit_gratitude"
        
        status = "[OK]" if is_emotional == test["expected_emotional"] else "[FAIL]"
        print(f"  {status} Emotional detection: {is_emotional} (expected: {test['expected_emotional']})")
        print(f"     Response source: {response_source}")
        
    except Exception as e:
        print(f"  [ERROR] {str(e)[:100]}")
    
    print()

print("=" * 70)
print("[Testing parse_signals() integration]\n")

# Test signal detection with actual inputs
test_signals = [
    "I hold this moment sacred",
    "I feel safe and tender",
    "This exactly resonates",
    "I feel overwhelmed",
]

for input_text in test_signals:
    print(f"Input: {input_text}")
    signals = parse_signals(input_text, signal_map)
    
    if signals:
        print(f"  Detected {len(signals)} signals:")
        for sig in signals[:5]:  # Show first 5
            print(f"    - {sig.get('keyword', '?')}: {sig.get('signal', '?')} "
                  f"(voltage: {sig.get('voltage', '?')}, gates: {sig.get('gates', [])})")
    else:
        print("  No signals detected (fallback to fuzzy matching)")
    
    print()

print("=" * 70)
print("[OK] Integration validation complete!")
print("=" * 70)
