#!/usr/bin/env python3
"""Quick test of parse_input responses."""
import sys
import time
import traceback

from emotional_os.core.signal_parser import parse_input

print("=" * 70)
print("TESTING DIRECT RESPONSE GENERATION")
print("=" * 70)

tests = [
    "I am feeling stressed today",
    "I had to deal with an employee who was drinking on the job",
]

for test_input in tests:
    print("\n>>> Input: " + test_input)
    
    try:
        start = time.time()
        result = parse_input(test_input)
        elapsed = time.time() - start
        
        response = result.get("voltage_response", "ERROR: No response")
        source = result.get("response_source", "unknown")
        glyph = result.get("best_glyph", {})
        glyph_name = glyph.get("glyph_name") if glyph else "None"
        
        print("Source: " + source)
        print("Glyph: " + str(glyph_name))
        resp_display = (response[:150] + "...") if len(response) > 150 else response
        print("Response: " + resp_display)
        print("Time: {:.3f}s".format(elapsed))
    except Exception as e:
        print("ERROR: " + str(e))
        traceback.print_exc()
    
    print("-" * 70)
