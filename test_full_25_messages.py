#!/usr/bin/env python3
"""
Test full 25-message suite to verify >85% glyph coverage
Tests the original failing messages plus additional emotional vocabulary
"""

from emotional_os.glyphs.signal_parser import parse_input

# 25 comprehensive test messages (mix of original failures + new vocabulary)
test_messages = [
    # Original failing messages (shame, disappointment, broken, trapped, etc.)
    "I am ashamed of how I have been acting lately",
    "I feel so disappointed in myself",
    "I feel broken and don't know how to fix it",
    "Nobody would understand what I'm going through",
    "This is hard but I'm not giving up",
    "I'm learning to be kinder to myself",
    "I'm ready to let go of this pain",
    "I wonder if anyone really knows the real me",
    
    # Additional emotional vocabulary (shame, vulnerability, recognition)
    "I'm so embarrassed about what happened",
    "I feel humiliated and want to hide",
    "I'm trapped in this cycle and can't escape",
    "I feel stuck and don't know how to move forward",
    "I'm lost and can't find my way",
    "I feel like nobody understands me",
    "I'm so grateful for this moment",
    "I'm proud of myself for trying",
    
    # Growth and healing vocabulary
    "I'm healing from something deep",
    "I'm learning to love myself more",
    "I feel hopeful about the future",
    "I'm grieving what I've lost",
    "I'm holding onto love despite everything",
    "I feel terrified but I'm moving forward anyway",
    "I miss what we had",
    "I'm pretending everything is fine when it's not",
    "I'm struggling but I won't give up",
]

print(f"Testing {len(test_messages)} messages for glyph coverage...\n")
print("=" * 80)

glyphs_found = 0
glyphs_not_found = []

for i, msg in enumerate(test_messages, 1):
    lexicon_path = 'emotional_os/parser/signal_lexicon.json'
    db_path = 'emotional_os/glyphs/glyphs.db'
    result = parse_input(msg, lexicon_path=lexicon_path, db_path=db_path)
    best_glyph = result.get('best_glyph')
    signals = result.get('signals', [])
    response = result.get('voltage_response', '')[:80]  # First 80 chars
    
    glyph_name = best_glyph.get('glyph_name') if best_glyph else None
    status = "✓" if glyph_name else "✗"
    
    if glyph_name:
        glyphs_found += 1
    else:
        glyphs_not_found.append(msg)
    
    print(f"\n[{i:2d}] {status} {msg[:50]:<50}")
    print(f"     Signals: {signals}")
    print(f"     Glyph: {glyph_name if glyph_name else 'None'}")
    print(f"     Response: {response}...")

print("\n" + "=" * 80)
coverage_pct = (glyphs_found * 100) // len(test_messages)
print(f"\n📊 RESULTS:")
print(f"   ✓ Glyphs found: {glyphs_found}/{len(test_messages)} ({coverage_pct}%)")
print(f"   ✗ No glyph: {len(glyphs_not_found)}")

if glyphs_not_found:
    print(f"\n⚠️  Messages without glyphs:")
    for msg in glyphs_not_found:
        print(f"   - {msg}")

print(f"\n🎯 Target: >85% coverage")
if coverage_pct >= 85:
    print(f"✅ TARGET MET! ({coverage_pct}% >= 85%)")
else:
    print(f"⚠️  Below target. Current: {coverage_pct}%, Need: 85%+")
