#!/usr/bin/env python3
"""Test the expanded glyph processing system"""

from emotional_os.glyphs.signal_parser import parse_input

def test_enhanced_system():
    test_message = "I feel overwhelmed by all the changes in my life"
    
    print("🔮 Enhanced Emotional Processing Test:")
    print(f"Input: '{test_message}'")
    print()
    
    result = parse_input(test_message, lexicon_path="emotional_os/parser/signal_lexicon.json", db_path="emotional_os/glyphs/glyphs.db")
    
    print(f"✨ Selected Glyph: {result['best_glyph']['glyph_name']}")
    print(f"🚪 Gate: {result['best_glyph']['gate']}")
    print(f"📝 Description: {result['best_glyph']['description']}")
    print(f"💬 Response: {result['voltage_response']}")
    print(f"📊 Total Available Glyphs: {len(result['glyphs'])}")

if __name__ == "__main__":
    test_enhanced_system()