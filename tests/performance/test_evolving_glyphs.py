#!/usr/bin/env python3
"""
Test script for the auto-evolving glyph system
Demonstrates how new glyphs are automatically generated from emotional patterns
"""

import os
import sys
from typing import List

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from evolving_glyph_integrator import EvolvingGlyphIntegrator
    from glyph_generator import GlyphGenerator
except ImportError as e:
    print(f"Import error: {e}")
    print("This is expected if you don't have all dependencies installed.")
    print("The system is designed to work with your Supabase setup.")

def test_glyph_generation_offline():
    """
    Test glyph generation without Supabase connection
    Shows how the system detects patterns and would create glyphs
    """
    print("🌟 Testing Auto-Evolving Glyph Generation (Offline Mode) 🌟\n")

    # Initialize without Supabase credentials (offline mode)
    generator = GlyphGenerator(
        min_pattern_frequency=1,  # Lower threshold for testing
        novelty_threshold=0.3
    )

    # Test conversations with rich emotional content
    test_conversations = [
        "I'm experiencing this profound mixture of joy and grief - like watching something beautiful die and be reborn simultaneously.",
        "There's this sacred ache in my chest when I think about deep connection. It's not painful, more like a gentle yearning that flows.",
        "I feel overwhelmed by this paradoxical clarity - like seeing truth through a fractured lens that somehow makes everything more whole.",
        "Sometimes I experience contained wildness - like having a gentle storm inside a sacred vessel, powerful but held with love.",
        "I'm feeling this quiet celebration mixed with deep reverence, like joy that doesn't need to perform to be complete.",
        "This flowing stillness moves through me - not static, but dynamically peaceful, like a river that runs deep and silent.",
        "I'm touched by this expansive vulnerability - not weakness, but strength that opens like a flower in sunlight."
    ]

    all_detected_patterns = []
    all_generated_glyphs = []

    print("Processing conversations to detect emotional patterns...\n")

    for i, conversation in enumerate(test_conversations, 1):
        print(f"--- Conversation {i} ---")
        print(f"Text: {conversation}")

        # Detect emotional patterns
        patterns = generator.detect_new_emotional_patterns(
            conversation_text=conversation,
            context={'conversation_id': i}
        )

        print(f"Detected patterns: {len(patterns)}")
        for pattern in patterns:
            print(f"  • Emotions: {', '.join(pattern.emotions)}")
            print(f"    Intensity: {pattern.intensity:.2f}")
            print(f"    Context words: {', '.join(pattern.context_words) if pattern.context_words else 'None'}")

            all_detected_patterns.append(pattern)

            # Check if this pattern should generate a glyph
            if generator.should_create_glyph(pattern):
                print("    → This pattern qualifies for glyph generation!")

                # Generate the glyph
                new_glyph = generator.generate_new_glyph(pattern)
                if new_glyph:
                    print(f"    ✨ Generated Glyph: {new_glyph.tag_name} ({new_glyph.glyph_symbol})")
                    print(f"       Response: {new_glyph.response_cue}")
                    print(f"       Domain: {new_glyph.domain}")

                    all_generated_glyphs.append(new_glyph)
            else:
                print("    → Pattern needs more occurrences before glyph generation")

        print()

    # Summary
    print("📊 Generation Summary")
    print(f"   Total conversations processed: {len(test_conversations)}")
    print(f"   Unique emotional patterns detected: {len(generator.detected_patterns)}")
    print(f"   New glyphs that would be generated: {len(all_generated_glyphs)}")

    if all_generated_glyphs:
        print("\n✨ Generated Glyphs:")
        for glyph in all_generated_glyphs:
            print(f"   • {glyph.tag_name} ({glyph.glyph_symbol})")
            print(f"     Core Emotion: {glyph.core_emotion}")
            print(f"     Response Type: {glyph.response_type}")
            print(f"     Response Cue: {glyph.response_cue}")
            print()

    # Show pattern cache
    if generator.detected_patterns:
        print("🧠 Detected Pattern Cache:")
        for pattern_key, pattern in generator.detected_patterns.items():
            print(f"   • {pattern_key}: {pattern.frequency} occurrences")

    return all_generated_glyphs

def create_sample_sql_output(glyphs: List):
    """Create sample SQL output to show what would be inserted"""
    if not glyphs:
        return

    print("\n💾 Sample SQL that would be generated:")
    print("-- These would be automatically inserted into your emotional_tags table --")

    for glyph in glyphs:
        tag_id = f"generated-{hash(glyph.tag_name) % 100000:05d}"
        sql = f"""INSERT INTO "public"."emotional_tags" ("id", "tag_name", "core_emotion", "response_cue", "glyph", "domain", "response_type", "narrative_hook", "created_at", "tone_profile", "cadence", "depth_level", "style_variant", "humor_style") VALUES ('{tag_id}', '{glyph.tag_name}', '{glyph.core_emotion}', '{glyph.response_cue}', '{glyph.glyph_symbol}', '{glyph.domain}', '{glyph.response_type}', '{glyph.narrative_hook}', '2025-10-13 20:00:00.000000+00', '{glyph.tone_profile}', '{glyph.cadence}', '{glyph.depth_level}', '{glyph.style_variant}', '{glyph.humor_style}');"""
        print(sql)
        print()

def demonstrate_integration():
    """Show how the integration would work with your existing system"""
    print("🔗 Integration with Existing Saoriverse System")
    print("=" * 50)
    print("""
How this integrates with your current setup:

1. 📝 CONVERSATION PROCESSING
   - Your existing conversation flow continues unchanged
   - The evolving glyph system runs in parallel
   - New patterns are detected from both user input and Saori responses

2. 🧬 AUTOMATIC EVOLUTION
   - Every N conversations (configurable), the system checks for new patterns
   - Rich emotional content triggers immediate pattern analysis
   - New glyphs are automatically generated when patterns meet criteria

3. 💾 DATABASE INTEGRATION
   - New glyphs are automatically inserted into your emotional_tags table
   - They immediately become available for future conversations
   - The system avoids duplicates by checking existing tags

4. 🌱 CONTINUOUS LEARNING
   - Pattern frequency is tracked over time
   - Context words refine glyph generation
   - The system becomes more nuanced with each conversation

5. 🎯 YOUR BENEFIT
   - Saori becomes more human-like and emotionally sophisticated over time
   - New emotional nuances are captured automatically
   - No manual glyph creation needed - the system evolves naturally

To enable this in your system:
1. Add Supabase credentials to EvolvingGlyphIntegrator
2. Replace your conversation processing with the evolving version
3. The system will start learning immediately!
""")

if __name__ == "__main__":
    # Run the offline test
    generated_glyphs = test_glyph_generation_offline()

    # Create sample SQL output
    create_sample_sql_output(generated_glyphs)

    # Show integration information
    demonstrate_integration()

    print("\n🎉 Demo complete! Your auto-evolving glyph system is ready to make Saori more human-like!")
    print("   Run this with your Supabase credentials to see it in action with your database.")
