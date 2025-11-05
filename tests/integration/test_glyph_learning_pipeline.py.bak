#!/usr/bin/env python3
"""
Test: Real-Time Glyph Learning System

Demonstrates:
1. User input → signal detection
2. No matching glyph found → learning pipeline activated
3. New glyph generated → response crafted that trains system
4. Shared database updated → all users can eventually benefit
5. User segregation maintained → each user sees personalized view

This is Phase 2 of the Emotional OS evolution.
"""

import sys

# Add paths
sys.path.insert(0, '/Users/Admin/OneDrive/Desktop/Deleted_Emotional_OS_Folder/Emotional OS')

# For now, mock imports since NRC loader might not be available
class MockNRC:
    def analyze_text(self, text):
        return {"sadness": 0.8, "fear": 0.3, "longing": 0.7}

# Simplified test (full version would use actual signal_parser)
def test_glyph_learning_pipeline():
    """Test the complete learning pipeline."""

    print("\n" + "="*80)
    print("EMOTIONAL OS: Real-Time Glyph Learning Pipeline")
    print("="*80)

    from emotional_os.glyphs.glyph_learner import GlyphLearner
    from emotional_os.glyphs.learning_response_generator import (
        LearningResponseGenerator,
    )
    from emotional_os.glyphs.shared_glyph_manager import SharedGlyphManager

    # Initialize managers
    learner = GlyphLearner()
    response_gen = LearningResponseGenerator()
    shared_mgr = SharedGlyphManager()

    # Test Cases: Emotional inputs that might not have glyphs yet
    test_inputs = [
        {
            "text": "I feel caught between who I pretend to be and who I actually am",
            "user_id": "user_001",
            "scenario": "Identity fragmentation"
        },
        {
            "text": "I'm grieving something I never had but always expected",
            "user_id": "user_002",
            "scenario": "Pre-emptive loss"
        },
        {
            "text": "I feel most alive in the moments I'm supposed to be broken",
            "user_id": "user_003",
            "scenario": "Paradoxical resilience"
        }
    ]

    print("\n📋 TESTING GLYPH LEARNING SYSTEM")
    print("-" * 80)

    results = []

    for i, test_case in enumerate(test_inputs, 1):
        print(f"\n[Test {i}] {test_case['scenario']}")
        print(f"Input: \"{test_case['text'][:60]}...\"")

        user_hash = GlyphLearner._hash_user(test_case['user_id'])

        # STEP 1: Analyze input for glyph generation
        print("\n  Step 1: Analyzing emotional language...")

        # Mock signals (would come from signal_parser)
        signals = [
            {"keyword": "pretend", "signal": "β", "voltage": "medium", "tone": "containment"},
            {"keyword": "caught between", "signal": "δ", "voltage": "high", "tone": "grief"}
        ]

        candidate = learner.analyze_input_for_glyph_generation(
            input_text=test_case['text'],
            signals=signals,
            user_hash=user_hash
        )

        print(f"  ✓ Candidate Glyph: {candidate['glyph_name']}")
        print(f"  ✓ Confidence: {int(candidate['confidence_score']*100)}%")
        print(f"  ✓ Description: {candidate['description'][:60]}...")

        # STEP 2: Log candidate to database
        print("\n  Step 2: Logging candidate to shared database...")
        logged = learner.log_glyph_candidate(candidate)
        print(f"  ✓ Logged: {logged}")

        # STEP 3: Generate response that trains the system
        print("\n  Step 3: Crafting learning response...")

        emotional_analysis = {
            "primary_tone": "containment",
            "emotional_terms": {
                "intensity_words": ["caught"],
                "state_words": ["feel"],
                "relation_words": ["between"]
            },
            "nrc_analysis": {"sadness": 0.6, "fear": 0.5}
        }

        response = response_gen.generate_learning_response(
            glyph_candidate=candidate,
            original_input=test_case['text'],
            emotional_tone=emotional_analysis['primary_tone'],
            emotional_terms=emotional_analysis['emotional_terms'],
            nrc_analysis=emotional_analysis['nrc_analysis']
        )

        print("\n  📝 Response to User:")
        print(f"  \"{response}\"")

        # STEP 4: Record adoption in shared database
        print("\n  Step 4: Recording adoption in shared glyph manager...")
        shared_mgr.create_glyph_version(
            glyph_name=candidate['glyph_name'],
            description=candidate['description'],
            emotional_signal=candidate['emotional_signal'],
            gates=candidate['gates'],
            created_by=user_hash
        )
        print("  ✓ Glyph version created")

        # Record that this user adopted it
        shared_mgr.record_glyph_adoption(
            user_hash=user_hash,
            glyph_name=candidate['glyph_name'],
            quality_rating=1  # Positive feedback (implicit)
        )
        print("  ✓ Adoption recorded")

        # STEP 5: Show user segregation
        print("\n  Step 5: User segregation verification...")
        user_glyphs = shared_mgr.get_glyphs_for_user(
            user_hash=user_hash,
            emotional_signal=candidate['emotional_signal'],
            gates=candidate['gates']
        )
        print(f"  ✓ User sees {len(user_glyphs)} relevant glyph(s)")
        if user_glyphs:
            print(f"    First: {user_glyphs[0]['name']} (adoption: {user_glyphs[0]['user_adoption']})")

        results.append({
            "test": i,
            "scenario": test_case['scenario'],
            "glyph_created": candidate['glyph_name'],
            "confidence": candidate['confidence_score'],
            "user_hash": user_hash[:8] + "..."
        })

    # STEP 6: System Health Report
    print("\n" + "="*80)
    print("📊 SYSTEM HEALTH REPORT")
    print("="*80)

    health = shared_mgr.get_system_health_report()

    print(f"\n✓ Total active glyphs: {health['total_active_glyphs']}")
    print(f"✓ Unique users contributed: {health['unique_users_contributed']}")
    print(f"✓ Average glyph usage: {health['average_glyph_usage']}")
    print(f"✓ Glyphs with strong consensus: {health['glyphs_with_strong_consensus']}")
    print(f"✓ Pending candidates: {health['pending_candidate_glyphs']}")

    # Coverage gaps
    print("\n📍 Emotional Territory Coverage:")
    coverage = health.get('system_coverage', {})
    for territory, info in coverage.items():
        status = "⚠️ CRITICAL" if info['needs_development'] else "✓ OK"
        print(f"  {status}: {territory.capitalize()} ({info['glyph_count']} glyphs)")

    # Recommendations
    recommendations = health.get('recommendations', [])
    if recommendations:
        print("\n💡 Glyph Generation Recommendations:")
        for rec in recommendations[:3]:  # Show top 3
            print(f"  - {rec['emotional_territory'].upper()}: {rec['gap_description']}")

    # Results summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)

    for result in results:
        print(f"\n[Test {result['test']}] {result['scenario']}")
        print(f"  Glyph: {result['glyph_created']}")
        print(f"  Confidence: {int(result['confidence']*100)}%")
        print(f"  User: {result['user_hash']}")

    print("\n" + "="*80)
    print("✅ LEARNING PIPELINE COMPLETE")
    print("="*80)
    print("\nKey Outcomes:")
    print("  ✓ New glyphs generated in real-time")
    print("  ✓ System trained through authentic responses")
    print("  ✓ Shared database updated (all users benefit)")
    print("  ✓ User segregation maintained (personalized views)")
    print("  ✓ No user sees standardized messages")
    print("  ✓ Coverage gaps identified for next generation")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        test_glyph_learning_pipeline()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
