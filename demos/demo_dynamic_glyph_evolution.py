#!/usr/bin/env python3
"""
Demo: Dynamic Glyph Evolution in Action

This script demonstrates how glyphs are automatically created during
live user-AI conversations through the hybrid processor.

Run this to see:
1. Adaptive signal extraction
2. Hybrid learning from dialogue
3. Pattern detection in conversation
4. Automatic glyph generation
5. Session summary with all discovered glyphs
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def demo_dynamic_glyph_evolution():
    """Run a complete demo of the system."""

    print("\n" + "=" * 90)
    print("DYNAMIC GLYPH EVOLUTION DEMO")
    print("Automatic Glyph Creation During User-AI Dialogue")
    print("=" * 90)

    try:
        # Import components
        print("\n[INITIALIZING] Loading system components...")

        from hybrid_processor_with_evolution import create_integrated_processor

        from emotional_os.learning.adaptive_signal_extractor import (
            AdaptiveSignalExtractor,
        )
        from emotional_os.learning.hybrid_learner_v2 import (
            HybridLearnerWithUserOverrides,
        )

        print("  ✓ Hybrid Learner")
        print("  ✓ Adaptive Signal Extractor")
        print("  ✓ Integrated Processor")

        # Initialize components
        print("\n[CREATING] Initializing components...")

        learner = HybridLearnerWithUserOverrides(
            shared_lexicon_path="emotional_os/parser/signal_lexicon.json",
            user_overrides_dir="learning/user_overrides",
        )
        print("  ✓ Hybrid Learner initialized")

        extractor = AdaptiveSignalExtractor(adaptive=True, use_discovered=True)
        print("  ✓ Adaptive Signal Extractor initialized")

        processor = create_integrated_processor(
            hybrid_learner=learner,
            adaptive_extractor=extractor,
            user_id="demo_user_001",
        )
        print("  ✓ Integrated Processor ready")

        # Demo conversation: A poignant exchange about vulnerability and love
        print("\n" + "=" * 90)
        print("DEMO CONVERSATION: Finding Courage in Vulnerability")
        print("=" * 90)

        conversation_id = "demo_conv_001"

        # Turn 1: Confession
        print("\n[TURN 1] The Confession")
        print("-" * 90)

        user_input_1 = "I want to let someone in, but the fear is overwhelming. I feel exposed."
        ai_response_1 = (
            "That exposed feeling—it's the threshold of intimacy itself. "
            "Being vulnerable is not weakness; it's the greatest strength we possess. "
            "To love deeply, we must risk being deeply seen."
        )

        print(f"💭 User:  {user_input_1}")
        print(f"🤖 AI:    {ai_response_1}")

        result_1 = processor.process_user_message(
            user_message=user_input_1,
            ai_response=ai_response_1,
            conversation_id=conversation_id,
        )

        print(
            f"\n  Signals detected: {', '.join([str(s) for s in result_1['pipeline_stages']['signal_extraction']['signals']])}"
        )
        glyphs_1 = result_1["pipeline_stages"]["glyph_generation"].get("new_glyphs_generated", [])
        if glyphs_1:
            print(f"  ✨ NEW GLYPHS: {len(glyphs_1)} generated!")
            for glyph in glyphs_1:
                print(f"     - {glyph.get('symbol')} {glyph.get('name')}")

        # Turn 2: Recognition
        print("\n[TURN 2] The Recognition")
        print("-" * 90)

        user_input_2 = (
            "You're right. When I'm with them, the fear turns into something beautiful—like I'm becoming more myself."
        )
        ai_response_2 = (
            "Yes. That transformation—from fear into becoming—is love in its truest form. "
            "The person who makes you feel safe to change is sacred. "
            "That intimacy, that witness to your becoming—hold it with gratitude."
        )

        print(f"💭 User:  {user_input_2}")
        print(f"🤖 AI:    {ai_response_2}")

        result_2 = processor.process_user_message(
            user_message=user_input_2,
            ai_response=ai_response_2,
            conversation_id=conversation_id,
        )

        print(
            f"\n  Signals detected: {', '.join([str(s) for s in result_2['pipeline_stages']['signal_extraction']['signals']])}"
        )
        glyphs_2 = result_2["pipeline_stages"]["glyph_generation"].get("new_glyphs_generated", [])
        if glyphs_2:
            print(f"  ✨ NEW GLYPHS: {len(glyphs_2)} generated!")
            for glyph in glyphs_2:
                print(f"     - {glyph.get('symbol')} {glyph.get('name')}")

        # Turn 3: Deepening
        print("\n[TURN 3] The Deepening")
        print("-" * 90)

        user_input_3 = (
            "There's something sacred about being known. About letting my walls down. It feels like coming home."
        )
        ai_response_3 = (
            "That homecoming—when someone sees you fully and loves you still—"
            "that's the deepest intimacy humans know. "
            "You're experiencing what poets have chased across centuries: "
            "being held in the gaze of genuine love."
        )

        print(f"💭 User:  {user_input_3}")
        print(f"🤖 AI:    {ai_response_3}")

        result_3 = processor.process_user_message(
            user_message=user_input_3,
            ai_response=ai_response_3,
            conversation_id=conversation_id,
        )

        print(
            f"\n  Signals detected: {', '.join([str(s) for s in result_3['pipeline_stages']['signal_extraction']['signals']])}"
        )
        glyphs_3 = result_3["pipeline_stages"]["glyph_generation"].get("new_glyphs_generated", [])
        if glyphs_3:
            print(f"  ✨ NEW GLYPHS: {len(glyphs_3)} generated!")
            for glyph in glyphs_3:
                print(f"     - {glyph.get('symbol')} {glyph.get('name')}")

        # Summary
        print("\n" + "=" * 90)
        print("SESSION SUMMARY")
        print("=" * 90)

        processor.print_session_summary()

        # Detailed glyph information
        print("\n[DISCOVERED GLYPHS DETAILS]")
        print("-" * 90)

        all_glyphs = processor.get_all_generated_glyphs()
        if all_glyphs:
            for i, glyph in enumerate(all_glyphs, 1):
                print(f"\n{i}. {glyph.get('symbol')} {glyph.get('name')}")
                print(f"   Emotions: {' + '.join(glyph.get('core_emotions', []))}")
                print(f"   Keywords: {', '.join(glyph.get('associated_keywords', []))}")
                print(f"   Response: {glyph.get('response_cue')}")
                print(f"   Story: {glyph.get('narrative_hook')}")
                print(f"   Created: From dialogue (user {glyph.get('user_id')})")
        else:
            print("No glyphs generated in this session.")

        # Export glyphs
        print("\n[EXPORTING]")
        print("-" * 90)

        export_file = "learning/demo_session_glyphs.json"
        export_result = processor.export_session_glyphs(export_file)

        if export_result.get("success"):
            print(f"✓ Exported {export_result['count']} glyphs to {export_file}")

            # Show file contents
            with open(export_file, "r") as f:
                exported = json.load(f)
            print(f"  File size: {Path(export_file).stat().st_size / 1024:.1f} KB")
            print("  Ready for system integration")

        # Show conversation summary
        print("\n[CONVERSATION ANALYSIS]")
        print("-" * 90)

        conv_summary = processor.get_conversation_summary(conversation_id)
        print(f"Conversation ID: {conversation_id}")
        print(f"Total turns: {conv_summary['turns']}")
        print(
            f"All signals found: {len(set([s.get('signal') or s.get('name') for s in conv_summary.get('all_signals', []) if s]))}"
        )
        print(f"Total glyphs generated: {len(conv_summary.get('all_glyphs_generated', []))}")

        # Information about the pipeline
        print("\n" + "=" * 90)
        print("HOW IT WORKS")
        print("=" * 90)
        print(
            """
1. USER INPUT: User shares a thought or feeling
   → "I want to let someone in, but the fear is overwhelming"

2. ADAPTIVE EXTRACTION: System extracts emotional signals
   → Signals: love, vulnerability, fear, intimacy

3. HYBRID LEARNING: System learns from the exchange
   → User's personal lexicon updated
   → Shared lexicon potentially updated (if quality passes)
   → Learning log recorded

4. PATTERN DETECTION: System looks for co-occurring emotions
   → Found: (love + vulnerability) appearing together
   → Found: (vulnerability + transformation) appearing together

5. GLYPH GENERATION: When pattern significance threshold reached
   → Creates new glyph: "Open-Hearted Love" (love + vulnerability)
   → Assigns symbol: ♥🌱
   → Generates response cue & narrative hook

6. INTEGRATION: New glyphs immediately available
   → Available for next dialogue turn
   → Saved to conversation_glyphs.json
   → Exported for system database

This creates a LIVING SYSTEM where:
• Each conversation teaches the system
• New emotional territories discovered automatically
• Glyphs grow from real human patterns
• AI becomes more attuned to user's unique emotional palette
        """
        )

        print("=" * 90)
        print("✓ DEMO COMPLETE")
        print("=" * 90)
        print("\nTo use this in your system:")
        print("  1. Import: from hybrid_processor_with_evolution import create_integrated_processor")
        print("  2. Create: processor = create_integrated_processor(learner, extractor)")
        print("  3. Process: result = processor.process_user_message(user_msg, ai_response)")
        print("  4. Access: processor.get_all_generated_glyphs()")
        print("\nSee DYNAMIC_GLYPH_EVOLUTION_GUIDE.md for full documentation")
        print("=" * 90 + "\n")

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Troubleshooting:")
        print("  - Ensure emotional_os module is installed")
        print("  - Check that required files exist: emotional_os/parser/signal_lexicon.json")
        print("  - Run from project root directory")


if __name__ == "__main__":
    demo_dynamic_glyph_evolution()
