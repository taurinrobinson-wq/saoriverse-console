#!/usr/bin/env python3
"""Test improved emotional glyph matching"""

from emotional_os.glyphs.signal_parser import parse_input

test_messages = [
    "I am ashamed of how I have been acting lately",
    "I feel so disappointed in myself",
    "I feel broken and don't know how to fix it",
    "Nobody would understand what I'm going through",
    "This is hard but I'm not giving up",
    "I'm learning to be kinder to myself",
    "I'm ready to let go of this pain",
    "I wonder if anyone really knows the real me"
]

print("Testing improved glyph matching:\n")
print("=" * 80)

glyphs_found = 0
glyphs_none = 0

for msg in test_messages:
    result = parse_input(msg, 'emotional_os/parser/signal_lexicon.json', 'emotional_os/glyphs/glyphs.db')
    glyph = result['best_glyph']['glyph_name'] if result['best_glyph'] else 'None'

    if glyph != 'None':
        glyphs_found += 1
    else:
        glyphs_none += 1

    print(f"\n📝 Message: {msg}")
    print(f"✨ Glyph: {glyph}")
    print(f"💬 Response: {result['voltage_response'][:100]}...")
    print(f"🎯 Signals: {[s['keyword'] for s in result['signals']]}")
    print("-" * 80)

print(f"\n📊 SUMMARY: {glyphs_found}/{len(test_messages)} messages got glyphs ({glyphs_found*100//len(test_messages)}%)")
print(f"   ✓ With glyphs: {glyphs_found}")
print(f"   ✗ No glyph: {glyphs_none}")
