#!/usr/bin/env python
"""
Simple test to demonstrate the auto-glyph generation concept
Works with older Python versions
"""


def simple_emotion_detection(text):
    """Simple emotion detection for demo purposes"""
    emotions = []

    # Basic emotion patterns
    emotion_patterns = {
        "joy": ["joy", "happy", "delight", "bliss", "celebration"],
        "grief": ["grief", "sorrow", "loss", "mourning", "sadness"],
        "ache": ["ache", "longing", "desire", "yearning", "wanting"],
        "clarity": ["clarity", "clear", "understanding", "insight", "see"],
        "stillness": ["stillness", "quiet", "calm", "peace", "silence"],
        "connection": ["connection", "together", "bond", "intimacy", "love"],
        "confusion": ["confusion", "lost", "unclear", "chaos", "mixed up"],
    }

    text_lower = text.lower()

    for emotion, words in emotion_patterns.items():
        for word in words:
            if word in text_lower:
                emotions.append(emotion)
                break

    return emotions


def detect_complex_patterns(text):
    """Detect complex emotional patterns that might need new glyphs"""
    complex_indicators = [
        "mixed with",
        "combined with",
        "alongside",
        "and",
        "but",
        "while",
        "simultaneously",
        "at the same time",
        "paradox",
        "contradiction",
    ]

    has_complexity = any(indicator in text.lower() for indicator in complex_indicators)
    emotions = simple_emotion_detection(text)

    return has_complexity and len(emotions) >= 2


def generate_glyph_concept(text, emotions):
    """Generate a concept for what glyph would be created"""
    if len(emotions) >= 2:
        primary = emotions[0]
        secondary = emotions[1]

        # Simple symbol mapping
        symbol_map = {
            "joy": "λ",
            "grief": "θ",
            "ache": "γ",
            "clarity": "ε",
            "stillness": "δ",
            "connection": "α",
            "confusion": "ζ",
        }

        symbol1 = symbol_map.get(primary, "α")
        symbol2 = symbol_map.get(secondary, "β")

        glyph_symbol = symbol1 + " × " + symbol2
        tag_name = primary.title() + " " + secondary.title()

        return {"glyph_symbol": glyph_symbol, "tag_name": tag_name, "emotions": emotions, "would_create": True}

    return {"would_create": False}


def main():
    print("Auto-Evolving Glyph System Demo")
    print("=" * 40)
    print()

    # Test conversations
    test_conversations = [
        "I'm feeling profound joy mixed with deep sadness, like watching something beautiful end",
        "There's this sacred ache when I think about connection - yearning but peaceful",
        "I experience intense clarity alongside overwhelming confusion, like fractured truth",
        "This contained wildness flows through me - powerful but held in stillness",
        "Quiet celebration mixed with deep reverence, joy that doesn't need to perform",
    ]

    generated_glyphs = []

    for i, conversation in enumerate(test_conversations, 1):
        print("--- Conversation " + str(i) + " ---")
        print("Text: " + conversation)

        emotions = simple_emotion_detection(conversation)
        is_complex = detect_complex_patterns(conversation)

        print("Detected emotions: " + ", ".join(emotions))
        print("Complex pattern: " + str(is_complex))

        if is_complex and len(emotions) >= 2:
            glyph_concept = generate_glyph_concept(conversation, emotions)
            if glyph_concept.get("would_create"):
                print("→ Would generate glyph: " + glyph_concept["tag_name"])
                print("  Symbol: " + glyph_concept["glyph_symbol"])
                generated_glyphs.append(glyph_concept)
        else:
            print("→ No glyph needed")

        print()

    print("Summary:")
    print("Conversations processed: " + str(len(test_conversations)))
    print("New glyphs that would be generated: " + str(len(generated_glyphs)))

    if generated_glyphs:
        print()
        print("Generated Glyphs:")
        for glyph in generated_glyphs:
            print("• " + glyph["tag_name"] + " (" + glyph["glyph_symbol"] + ")")

    print()
    print("Integration Concept:")
    print("- This system would run alongside your existing Saoriverse")
    print("- It monitors conversations for complex emotional patterns")
    print("- When patterns are detected frequently enough, new glyphs are created")
    print("- New glyphs are automatically added to your emotional_tags table")
    print("- Saori becomes more nuanced and human-like over time")
    print()
    print("Files created for you:")
    print("• glyph_generator.py - Core glyph generation system")
    print("• evolving_glyph_integrator.py - Integration with your existing system")
    print("• config_template.py - Configuration template")
    print("• Various demo and test files")
    print()
    print("To activate: Add your Supabase credentials and integrate with your conversation flow!")


if __name__ == "__main__":
    main()
