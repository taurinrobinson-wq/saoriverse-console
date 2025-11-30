#!/usr/bin/env python3
"""
Local test script to verify glyph signal matching
Tests the messages from your earlier test run
"""

import sys

sys.path.insert(0, "str(Path(__file__).resolve().parent)")

from parser.signal_parser import load_signal_map, parse_signals

# Test messages from earlier
test_messages = {
    "joy": "I just got promoted! I'm so excited and proud of myself right now!",
    "sunset": "The sunset was absolutely breathtaking today. Pure magic.",
    "grief": "I miss them every day. The silence is almost unbearable.",
    "loneliness": "I feel so alone even though I'm surrounded by people.",
    "betrayal": "I can't believe they betrayed me like this! How could they do that?",
    "fury": "This is absolutely unacceptable! I'm furious!",
    "fear": "What if I fail? I'm terrified of disappointing everyone.",
    "anxiety": "My heart won't stop racing. I can't focus on anything.",
    "love": "Being with you makes everything feel right in the world.",
    "gratitude": "I'm so grateful for the people who truly understand me.",
    "overwhelm": "There's too much happening at once. I don't know where to start.",
    "exhaustion": "Everyone needs something from me and I have nothing left to give.",
    "hope": "Things are hard right now, but I believe tomorrow will be better.",
    "light": "I can see the light at the end of the tunnel.",
}


def test_signal_matching():
    print("=" * 70)
    print("GLYPH SIGNAL MATCHING TEST")
    print("=" * 70)

    # Load signal lexicon
    lexicon_path = "parser/signal_lexicon.json"
    signal_map = load_signal_map(lexicon_path)

    print(f"\n📚 Loaded signal lexicon with {len(signal_map)} keywords")
    print(f"   Path: {lexicon_path}\n")

    for category, message in test_messages.items():
        print(f"\n{'─' * 70}")
        print(f"Category: {category.upper()}")
        print(f'Message: "{message}"')
        print(f"{'─' * 70}")

        # Parse signals
        signals = parse_signals(message, signal_map)

        if signals:
            print(f"✓ Signals detected: {signals}")
            print(f"  Unique signals: {set(signals)}")
        else:
            print("✗ NO SIGNALS DETECTED")

        # Show which keywords matched
        matched_keywords = []
        lowered = message.lower()
        for keyword, signal in signal_map.items():
            if keyword.lower() in lowered or keyword.lower() in lowered.split():
                matched_keywords.append((keyword, signal))

        if matched_keywords:
            print("  Matched keywords:")
            for keyword, signal in matched_keywords:
                print(f"    - '{keyword}' → {signal}")


if __name__ == "__main__":
    test_signal_matching()
