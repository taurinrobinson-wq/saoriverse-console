#!/usr/bin/env python3
"""Test the improved overwhelm processing"""

from emotional_os.glyphs.signal_parser import parse_input


def test_overwhelm_processing():
    test_message = "I feel completely overwhelmed by all the changes happening in my life right now. My job is shifting, my relationship feels uncertain, and I don't know how to process it all."

    print("🔮 Testing Improved Overwhelm Processing:")
    print(f"Input: '{test_message}'")
    print()

    result = parse_input(
        test_message, lexicon_path="emotional_os/parser/signal_lexicon.json", db_path="emotional_os/glyphs/glyphs.db"
    )

    print(f"🔍 Signals Detected: {[s['signal'] + ' (' + s['keyword'] + ')' for s in result['signals']]}")
    print(f"🚪 Gates Activated: {result['gates']}")
    print(f"✨ Selected Glyph: {result['best_glyph']['glyph_name']}")
    print(f"📝 Description: {result['best_glyph']['description']}")
    print(f"💬 Response: {result['voltage_response']}")
    print(f"📊 Total Available Glyphs: {len(result['glyphs'])}")


if __name__ == "__main__":
    test_overwhelm_processing()
