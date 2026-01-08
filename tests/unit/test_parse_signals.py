#!/usr/bin/env python3
"""Test what parse_input returns for emotional words"""

from emotional_os.core.signal_parser import parse_input

tests = [
    "I'm feeling soft and vulnerable",
    "This moment feels sacred and tender",
    "I breathe deeply and find wisdom",
]

for test_input in tests:
    print(f"\n{'='*60}")
    print(f"Input: {test_input}")
    print('='*60)
    
    result = parse_input(
        test_input,
        "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
        db_path="emotional_os/glyphs/glyphs.db"
    )
    
    print(f"Signals detected: {result.get('signals', [])}")
    print(f"Gates: {result.get('gates', [])}")
    print(f"Best glyph: {result.get('best_glyph', {}).get('glyph_name')}")
    print(f"Response source: {result.get('response_source')}")
    print(f"Voltage response: {result.get('voltage_response', 'NONE')[:200]}")
