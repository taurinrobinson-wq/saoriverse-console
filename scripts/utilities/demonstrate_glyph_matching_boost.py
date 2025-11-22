#!/usr/bin/env python3
"""
Demonstration of Glyph Matching Boost functionality
Tests the enhanced glyph selection with spaCy syntactic analysis.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emotional_os.glyphs.signal_parser import parse_input

def test_glyph_matching_boost():
    """Test cases demonstrating glyph matching boost with syntactic elements."""

    test_cases = [
        {
            'input': "I feel overwhelmed and anxious about all these changes",
            'expected_syntactic': ['feel', 'overwhelm', 'anxious', 'change'],
            'description': 'Emotional verbs and nouns should boost containment/insight glyphs'
        },
        {
            'input': "I'm grieving the loss of my grandmother",
            'expected_syntactic': ['grieve', 'loss', 'grandmother'],
            'description': 'Emotional verbs should boost grief-related glyphs'
        },
        {
            'input': "This situation makes me so angry and frustrated",
            'expected_syntactic': ['make', 'angry', 'frustrated'],
            'description': 'Emotional adjectives should boost longing/ache glyphs'
        },
        {
            'input': "I feel joyful and excited about the future",
            'expected_syntactic': ['feel', 'joyful', 'excited', 'future'],
            'description': 'Positive emotional words should boost joy glyphs'
        },
        {
            'input': "I'm ashamed and embarrassed about what happened",
            'expected_syntactic': ['ashamed', 'embarrassed', 'happen'],
            'description': 'Emotional adjectives should boost boundary/containment glyphs'
        }
    ]

    print("🧠 Testing Glyph Matching Boost with Syntactic Analysis")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['description']}")
        print(f"Input: \"{test_case['input']}\"")
        print(f"Expected syntactic elements: {test_case['expected_syntactic']}")

        try:
            result = parse_input(
                input_text=test_case['input'],
                lexicon_path="velonix_lexicon.json",
                db_path="emotional_os/glyphs/glyphs.db"
            )

            print("\nSignals detected:")
            for signal in result.get('signals', []):
                print(f"  - {signal.get('keyword', 'unknown')} ({signal.get('signal', 'unknown')})")

            print("\nGates activated:")
            print(f"  {result.get('gates', [])}")

            print("\nGlyphs retrieved:")
            for glyph in result.get('glyphs', []):
                print(f"  - {glyph.get('glyph_name', 'unknown')}")

            best_glyph = result.get('best_glyph')
            if best_glyph:
                print(f"\n🏆 Best glyph selected: {best_glyph.get('glyph_name', 'unknown')}")
                print(f"Description: {best_glyph.get('description', '')[:100]}...")
            else:
                print("\n🏆 No best glyph selected")

            print(f"\n💬 Response: {result.get('voltage_response', '')[:150]}...")

        except Exception as e:
            print(f"❌ Error processing test case: {e}")

        print("-" * 40)

    print("\n✅ Glyph Matching Boost demonstration complete!")
    print("\nKey improvements:")
    print("- spaCy extracts emotional verbs, nouns, and adjectives from input")
    print("- Glyphs containing matching syntactic elements get score boosts")
    print("- Emotional verbs: +8 points, Nouns: +6 points, Adjectives: +4 points")
    print("- This creates more relevant glyph selections based on linguistic structure")

if __name__ == "__main__":
    test_glyph_matching_boost()