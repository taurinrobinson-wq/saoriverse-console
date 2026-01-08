#!/usr/bin/env python3
"""Test fetch_glyphs and select_best_glyph_and_response"""

import sys
sys.path.insert(0, 'src')

from emotional_os.core.signal_parser import fetch_glyphs, select_best_glyph_and_response, parse_signals, convert_signal_names_to_codes, evaluate_gates

# Test input
input_text = "I'm stressed"

# Use empty signal map - the heuristic map will handle it
signal_map = {}
print("[OK] Using heuristic emotion mapping for signal detection")

# Parse signals
try:
    signals = parse_signals(input_text, signal_map)
    print(f"\n[OK] Parsed signals: {len(signals)} signals found")
    if signals:
        print(f"  - First signal: {signals[0].get('keyword')} -> {signals[0].get('signal')}")
except Exception as e:
    print(f"[ERROR] Failed to parse signals: {e}")
    signals = []

# Convert and evaluate gates
signals = convert_signal_names_to_codes(signals)
gates = evaluate_gates(signals)
print(f"\n[OK] Gates evaluated: {gates}")

# Fetch glyphs for these gates
if gates:
    glyphs = fetch_glyphs(gates, 'glyphs.db')
    print(f"[OK] Fetched {len(glyphs)} glyphs")
    
    # Select best glyph
    try:
        result = select_best_glyph_and_response(glyphs, signals, input_text, {})
        if result and len(result) >= 4:
            best_glyph, (response, feedback), source, selected = result
            print(f"\n[OK] GLYPH-BASED RESPONSE SELECTED!")
            print(f"  - Glyph: {best_glyph.get('glyph_name') if best_glyph else 'NONE'}")
            print(f"  - Response: {response[:120]}")
            print(f"  - Source: {source}")
        else:
            print(f"[WARN] Unexpected result format")
    except Exception as e:
        print(f"[ERROR] in select_best_glyph_and_response: {e}")
else:
    print("[WARN] No gates evaluated - no glyphs can be selected")
