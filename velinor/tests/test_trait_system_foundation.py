"""
Test harness for Phase 1 Trait System Foundation
"""

import sys
sys.path.insert(0, r'd:\saoriverse-console\velinor\engine')

from trait_system import (
    ToneChoice, ToneProfiler,
    TONE_EMPATHY, TONE_OBSERVATION, TONE_NARRATIVE_PRESENCE, TONE_TRUST
)
from coherence_calculator import CoherenceCalculator, CoherenceLevel
from npc_response_engine import NPCResponseEngine


def test_trait_system():
    """Test basic trait tracking"""
    print("=" * 60)
    print("TEST 1: Basic Trait Tracking")
    print("=" * 60)
    
    profiler = ToneProfiler("Alyx")
    
    # Make a series of empathetic choices
    for i in range(3):
        choice = ToneChoice(
            choice_id=f"intro_{i}",
            dialogue_option="Show compassion",
            primary_tone=TONE_EMPATHY,
            trait_weight=0.3,
            npc_name="Nima",
            scene_name="First Meeting",
        )
        profiler.record_choice(choice)
    
    # Check profile
    profile = profiler.get_trait_summary()
    print(f"Player: {profile['player_name']}")
    print(f"Primary trait: {profile['primary_trait']}")
    print(f"Trait scores: {profile['trait_scores']}")
    print(f"Coherence: {profile['coherence']}")
    print(f"Choices made: {profile['choices_made']}")
    assert profile['primary_trait'] == 'empathy', "Should be empathy"
    assert profile['coherence'] == 100.0, "Should be perfectly coherent (all same trait)"
    print("✓ PASSED: Basic trait tracking works\n")


def test_coherence_calculation():
    """Test coherence measurement"""
    print("=" * 60)
    print("TEST 2: Coherence Calculation")
    print("=" * 60)
    
    profiler = ToneProfiler("Kai")
    
    # Build consistent pattern: mostly empathy
    choices = [
        ToneChoice(
            choice_id="choice_1",
            dialogue_option="",
            primary_tone=TONE_EMPATHY,
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        ),
        ToneChoice(
            choice_id="choice_2",
            dialogue_option="",
            primary_tone=TONE_EMPATHY,
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        ),
        ToneChoice(
            choice_id="choice_3",
            dialogue_option="",
            primary_tone=TONE_EMPATHY,
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        ),
        ToneChoice(
            choice_id="choice_4",
            dialogue_option="",
            primary_tone=TONE_EMPATHY,
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        ),
        ToneChoice(
            choice_id="choice_5",
            dialogue_option="",
            primary_tone=TONE_OBSERVATION,
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        ),
    ]
    
    for choice in choices:
        profiler.record_choice(choice)
    
    calculator = CoherenceCalculator(profiler)
    report = calculator.get_coherence_report()
    
    print(f"Overall coherence: {report.overall_coherence}")
    print(f"Coherence level: {report.level.name}")
    print(f"Primary pattern: {report.primary_pattern.value}")
    print(f"Pattern strength: {report.pattern_strength}")
    print(f"Contradiction count: {report.contradiction_count}")
    print(f"NPC trust level: {report.npc_trust_level}")
    print(f"Dialogue depth: {report.dialogue_depth}")
    print(f"Summary: {report.summary()}")
    
    # 4/5 = 80% empathy = 80 coherence = clear
    assert report.overall_coherence > 70, f"Should be fairly coherent (got {report.overall_coherence})"
    assert report.npc_trust_level in ["moderate", "high"], "Should have decent trust"
    print("✓ PASSED: Coherence calculation works\n")


def test_incoherence():
    """Test contradictory choices"""
    print("=" * 60)
    print("TEST 3: Incoherence Detection")
    print("=" * 60)
    
    profiler = ToneProfiler("Rax")
    
    # Build contradictory pattern
    traits = [
        TONE_EMPATHY, TONE_OBSERVATION, TONE_NARRATIVE_PRESENCE,
        TONE_OBSERVATION, TONE_EMPATHY, TONE_OBSERVATION,
        TONE_OBSERVATION, TONE_NARRATIVE_PRESENCE,
    ]
    
    for i, trait in enumerate(traits):
        choice = ToneChoice(
            choice_id=f"choice_{i}",
            dialogue_option="",
            primary_tone=trait,
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        )
        profiler.record_choice(choice)
    
    calculator = CoherenceCalculator(profiler)
    report = calculator.get_coherence_report()
    
    print(f"Overall coherence: {report.overall_coherence}")
    print(f"Coherence level: {report.level.name}")
    print(f"Contradiction count: {report.contradiction_count}")
    print(f"NPC trust level: {report.npc_trust_level}")
    print(f"Summary: {report.summary()}")
    
    assert report.overall_coherence < 50, "Should be incoherent"
    assert report.npc_trust_level == "suspicious", "Should be suspicious"
    print("✓ PASSED: Incoherence detection works\n")


def test_npc_response_engine():
    """Test NPC trait compatibility"""
    print("=" * 60)
    print("TEST 4: NPC Response Engine")
    print("=" * 60)
    
    profiler = ToneProfiler("Morgan")
    
    # Create empathetic player
    for i in range(5):
        choice = ToneChoice(
            choice_id=f"empathy_{i}",
            dialogue_option="",
            primary_tone=TONE_EMPATHY,
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        )
        profiler.record_choice(choice)
    
    engine = NPCResponseEngine(profiler)
    
    # Test NPC compatibility
    nimas_response = engine.get_npc_conflict_level("Nima")
    ravis_response = engine.get_npc_conflict_level("Ravi")
    
    print(f"Empathetic player vs. Nima (empathetic): {nimas_response}")
    print(f"Empathetic player vs. Ravi (skeptical): {ravis_response}")
    
    # Check if Nima (empathetic) aligns better
    assert nimas_response in ["ally", "neutral"], "Nima should accept empathy"
    print(f"Nima's dialogue depth: {engine.get_npc_dialogue_depth('Nima')}")
    print(f"Ravi's dialogue depth: {engine.get_npc_dialogue_depth('Ravi')}")
    print("✓ PASSED: NPC response engine works\n")


def test_trait_choice_presets():
    """Test using preset trait choices"""
    print("=" * 60)
    print("TEST 5: Trait Choice Presets")
    print("=" * 60)
    
    profiler = ToneProfiler("Sam")
    
    # Use presets
    choices = [
        ToneChoice(
            choice_id="choice_1",
            dialogue_option="Show understanding",
            primary_tone=TONE_EMPATHY,
            trait_weight=0.3,
            npc_name="Nima",
            scene_name="Marketplace",
        ),
        ToneChoice(
            choice_id="choice_2",
            dialogue_option="Ask hard questions",
            primary_tone=TONE_OBSERVATION,
            trait_weight=0.3,
            npc_name="Ravi",
            scene_name="Marketplace",
        ),
        ToneChoice(
            choice_id="choice_3",
            dialogue_option="Find common ground",
            primary_tone=TONE_NARRATIVE_PRESENCE,
            trait_weight=0.3,
            secondary_trait=TONE_OBSERVATION,
            secondary_weight=0.15,
            npc_name="Saori",
            scene_name="Marketplace",
        ),
    ]
    
    for choice in choices:
        profiler.record_choice(choice)
    
    profile = profiler.get_trait_summary()
    print(f"Trait pattern: {profile['trait_pattern']}")
    print(f"Primary trait: {profile['primary_trait']}")
    
    calculator = CoherenceCalculator(profiler)
    report = calculator.get_coherence_report()
    print(f"Pattern strength: {report.pattern_strength}")
    print(f"Incoherence narrative: {calculator.get_coherence_narrative()}")
    
    assert report.overall_coherence < 70, "Mixed traits = lower coherence"
    print("✓ PASSED: Trait choice presets work\n")


if __name__ == "__main__":
    print("\n🧪 PHASE 1 TRAIT SYSTEM FOUNDATION TESTS\n")
    
    try:
        test_trait_system()
        test_coherence_calculation()
        test_incoherence()
        test_npc_response_engine()
        test_trait_choice_presets()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\n📊 Phase 1 Foundation Complete!")
        print("   - Trait tracking: Working")
        print("   - Coherence calculation: Working")
        print("   - Pattern recognition: Working")
        print("   - NPC response engine: Working")
        print("\nNext: Integrate into orchestrator and Streamlit UI")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
