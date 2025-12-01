#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple demonstration of auto-evolving glyph concept
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

        # Simple ASCII symbol mapping
        symbol_map = {
            "joy": "L",
            "grief": "T",
            "ache": "G",
            "clarity": "E",
            "stillness": "D",
            "connection": "A",
            "confusion": "Z",
        }

        symbol1 = symbol_map.get(primary, "A")
        symbol2 = symbol_map.get(secondary, "B")

        glyph_symbol = symbol1 + " x " + symbol2
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
                print("-> Would generate glyph: " + str(glyph_concept["tag_name"]))
                print("   Symbol: " + str(glyph_concept["glyph_symbol"]))
                generated_glyphs.append(glyph_concept)
        else:
            print("-> No glyph needed")

        print()

    print("Summary:")
    print("Conversations processed: " + str(len(test_conversations)))
    print("New glyphs that would be generated: " + str(len(generated_glyphs)))

    if generated_glyphs:
        print()
        print("Generated Glyphs:")
        for glyph in generated_glyphs:
            print("- " + glyph["tag_name"] + " (" + glyph["glyph_symbol"] + ")")

    print()
    print("What this system does:")
    print("1. Monitors conversations for complex emotional patterns")
    print("2. Creates new glyphs when patterns appear frequently")
    print("3. Automatically adds them to your emotional_tags database")
    print("4. Makes Saori more nuanced and human-like over time")
    print()
    print("Files I created for you:")
    print("- glyph_generator.py (main system)")
    print("- evolving_glyph_integrator.py (connects to your existing code)")
    print("- config_template.py (configuration)")
    print("- Various demo files")
    print()
    print("Next steps:")
    print("1. Add your Supabase credentials to config_template.py")
    print("2. Integrate with your conversation processing flow")
    print("3. Watch as your emotional OS automatically evolves!")


if __name__ == "__main__":
    main()
