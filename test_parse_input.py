#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test of parse_input to see what voltage_response is returned."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from emotional_os.core.signal_parser import parse_input

test_inputs = [
    "I am feeling quite frustrated these days",
    "I just met someone who really sees me",
    "I feel overwhelmed",
]

for test_input in test_inputs:
    separator = "=" * 60
    print("\n" + separator)
    print("Input: " + test_input)
    print(separator)
    
    try:
        result = parse_input(
            test_input,
            lexicon_path="emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
            db_path="emotional_os/glyphs/glyphs.db",
            conversation_context={},
        )
        
        print("✓ parse_input succeeded")
        voltage = result.get('voltage_response', 'MISSING')
        if len(str(voltage)) > 100:
            print("  - voltage_response: " + str(voltage)[:100] + "...")
        else:
            print("  - voltage_response: " + str(voltage))
        print("  - signals: " + str(result.get('signals', [])))
        best_glyph_name = result.get('best_glyph', {}).get('glyph_name', 'NONE')
        print("  - best_glyph: " + str(best_glyph_name))
        print("  - response_source: " + str(result.get('response_source')))
        
    except Exception as e:
        print("✗ parse_input failed: " + str(e))
        import traceback
        traceback.print_exc()
