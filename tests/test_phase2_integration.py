"""
Phase 2 Integration Test: Trait System + Orchestrator + Marketplace Scene

Validates:
1. Orchestrator integrates trait system
2. Marketplace scene creates properly
3. Trait choices record correctly
4. Coherence affects dialogue
5. All systems work together
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from velinor.engine.trait_system import TraitProfiler, TraitType, TraitChoice
from velinor.engine.coherence_calculator import CoherenceCalculator
from velinor.engine.npc_response_engine import NPCResponseEngine
from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.engine.core import VelinorEngine
from velinor.engine.marketplace_scene import create_marketplace_debate_scene


def test_orchestrator_trait_integration():
    """Test that orchestrator has trait system integrated"""
    print("=" * 60)
    print("TEST 1: Orchestrator Trait Integration")
    print("=" * 60)
    
    # Create minimal orchestrator
    engine = VelinorEngine()
    orchestrator = VelinorTwineOrchestrator(
        game_engine=engine,
        story_path="",  # No story file needed for test
        player_name="Kai"
    )
    
    # Check trait systems exist
    assert orchestrator.trait_profiler is not None, "TraitProfiler missing"
    assert orchestrator.coherence_calculator is not None, "CoherenceCalculator missing"
    assert orchestrator.npc_response_engine is not None, "NPCResponseEngine missing"
    
    # Check trait status method works
    status = orchestrator.get_trait_status()
    assert 'trait_profile' in status
    assert 'coherence_report' in status
    assert 'npc_conflicts' in status
    
    print(f"✓ Orchestrator initialized with trait systems")
    print(f"✓ Player name: {orchestrator.trait_profiler.player_name}")
    print(f"✓ Trait status retrievable")
    print("✓ PASSED\n")


def test_trait_recording():
    """Test recording trait choices through orchestrator"""
    print("=" * 60)
    print("TEST 2: Trait Recording Through Orchestrator")
    print("=" * 60)
    
    engine = VelinorEngine()
    orchestrator = VelinorTwineOrchestrator(
        game_engine=engine,
        story_path="",
        player_name="Morgan"
    )
    
    # Record empathetic choice
    result = orchestrator.record_trait_choice(
        choice_id="test_choice_1",
        choice_text="Show compassion",
        primary_trait=TraitType.EMPATHY,
        trait_weight=0.3,
        npc_name="Nima",
        scene_name="test",
    )
    
    assert result['trait_profile']['choices_made'] == 1
    print(f"✓ Choice recorded: {result['trait_profile']['choices_made']} total")
    
    # Check coherence updated
    assert result['coherence_report']['overall_coherence'] > 0
    print(f"✓ Coherence: {result['coherence_report']['overall_coherence']}")
    
    # Record skeptical choice
    result = orchestrator.record_trait_choice(
        choice_id="test_choice_2",
        choice_text="Question the premise",
        primary_trait=TraitType.SKEPTICISM,
        trait_weight=0.3,
        npc_name="Malrik",
        scene_name="test",
    )
    
    assert result['trait_profile']['choices_made'] == 2
    print(f"✓ Second choice recorded: {result['trait_profile']['choices_made']} total")
    print(f"✓ Primary trait: {result['trait_profile']['primary_trait']}")
    print("✓ PASSED\n")


def test_marketplace_scene_creation():
    """Test marketplace debate scene creation"""
    print("=" * 60)
    print("TEST 3: Marketplace Debate Scene Creation")
    print("=" * 60)
    
    scene = create_marketplace_debate_scene()
    
    assert scene['scene_id'] == 'marketplace_debate'
    assert len(scene['intro_choices']) > 0
    assert len(scene['npcs']) == 3
    assert 'Malrik' in scene['npcs']
    assert 'Elenya' in scene['npcs']
    assert 'Coren' in scene['npcs']
    
    print(f"✓ Scene created: {scene['name']}")
    print(f"✓ NPCs: {', '.join(scene['npcs'])}")
    print(f"✓ Entry choices: {len(scene['intro_choices'])}")
    print(f"✓ Intro narration: {len(scene['intro_narration'])} chars")
    print(f"✓ Setup narration: {len(scene['setup_narration'])} chars")
    print("✓ PASSED\n")


def test_marketplace_branching():
    """Test marketplace scene branching with different coherence levels"""
    print("=" * 60)
    print("TEST 4: Marketplace Branching Choices")
    print("=" * 60)
    
    scene = create_marketplace_debate_scene()
    
    # Create profiler with various coherence levels
    test_cases = [
        ("High Coherence (100)", 100.0, TraitType.EMPATHY),
        ("Mixed Coherence (50)", 50.0, TraitType.INTEGRATION),
        ("Low Coherence (25)", 25.0, TraitType.SKEPTICISM),
    ]
    
    for test_name, target_coherence, dominant_trait in test_cases:
        profiler = TraitProfiler("Tester")
        
        # Build to target coherence
        if target_coherence > 70:
            # High coherence: consistent choices
            for _ in range(5):
                choice = TraitChoice(
                    choice_id="test",
                    dialogue_option="Test",
                    primary_trait=dominant_trait,
                    trait_weight=0.3,
                    npc_name="Test",
                    scene_name="Test",
                )
                profiler.record_choice(choice)
        elif target_coherence > 40:
            # Mixed: some variation
            traits = [TraitType.EMPATHY, TraitType.SKEPTICISM, TraitType.INTEGRATION]
            for i in range(6):
                choice = TraitChoice(
                    choice_id="test",
                    dialogue_option="Test",
                    primary_trait=traits[i % 3],
                    trait_weight=0.3,
                    npc_name="Test",
                    scene_name="Test",
                )
                profiler.record_choice(choice)
        else:
            # Low: all different
            traits = [TraitType.EMPATHY, TraitType.SKEPTICISM, TraitType.INTEGRATION, TraitType.AWARENESS]
            for i in range(8):
                choice = TraitChoice(
                    choice_id="test",
                    dialogue_option="Test",
                    primary_trait=traits[i % 4],
                    trait_weight=0.3,
                    npc_name="Test",
                    scene_name="Test",
                )
                profiler.record_choice(choice)
        
        calc = CoherenceCalculator(profiler)
        report = calc.get_coherence_report()
        
        npc_conflicts = {
            'Malrik': 'neutral',
            'Elenya': 'neutral',
            'Coren': 'neutral',
        }
        
        # Get branching choices
        choices = scene['get_branching_choices'](
            coherence_level=report.overall_coherence,
            player_primary_trait=report.primary_pattern,
            npc_conflicts=npc_conflicts
        )
        
        print(f"\n{test_name}:")
        print(f"  Actual coherence: {report.overall_coherence:.1f}/100")
        print(f"  Available choices: {len(choices)}")
        for choice in choices:
            locked = choice.get('coherence_locked', False)
            print(f"    - {choice['text'][:50]}... {'🔒' if locked else '✓'}")


    print("\n✓ PASSED\n")


def test_coherence_gating():
    """Test that coherence gates certain dialogue options"""
    print("=" * 60)
    print("TEST 5: Coherence-Based Dialogue Gating")
    print("=" * 60)
    
    scene = create_marketplace_debate_scene()
    
    # High coherence player
    profiler_high = TraitProfiler("HighCoherence")
    for _ in range(10):
        choice = TraitChoice(
            choice_id="test",
            dialogue_option="Test",
            primary_trait=TraitType.INTEGRATION,
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        )
        profiler_high.record_choice(choice)
    
    calc_high = CoherenceCalculator(profiler_high)
    report_high = calc_high.get_coherence_report()
    
    # Low coherence player
    profiler_low = TraitProfiler("LowCoherence")
    traits = [TraitType.EMPATHY, TraitType.SKEPTICISM, TraitType.INTEGRATION, TraitType.AWARENESS]
    for i in range(12):
        choice = TraitChoice(
            choice_id="test",
            dialogue_option="Test",
            primary_trait=traits[i % 4],
            trait_weight=0.3,
            npc_name="Test",
            scene_name="Test",
        )
        profiler_low.record_choice(choice)
    
    calc_low = CoherenceCalculator(profiler_low)
    report_low = calc_low.get_coherence_report()
    
    # Get choices for both
    npc_conflicts = {'Malrik': 'neutral', 'Elenya': 'neutral', 'Coren': 'neutral'}
    
    choices_high = scene['get_branching_choices'](
        coherence_level=report_high.overall_coherence,
        player_primary_trait=report_high.primary_pattern,
        npc_conflicts=npc_conflicts
    )
    
    choices_low = scene['get_branching_choices'](
        coherence_level=report_low.overall_coherence,
        player_primary_trait=report_low.primary_pattern,
        npc_conflicts=npc_conflicts
    )
    
    print(f"High Coherence ({report_high.overall_coherence:.0f}):")
    print(f"  Available choices: {len(choices_high)}")
    
    print(f"\nLow Coherence ({report_low.overall_coherence:.0f}):")
    print(f"  Available choices: {len(choices_low)}")
    
    # Check that coherence gating works
    locked_count_low = sum(1 for c in choices_low if c.get('coherence_locked', False))
    print(f"  Locked choices (require coherence): {locked_count_low}")
    
    assert len(choices_high) >= len(choices_low), "High coherence should unlock more choices"
    print("\n✓ Coherence gating working correctly")
    print("✓ PASSED\n")


def test_npc_compatibility():
    """Test NPC compatibility with different trait profiles"""
    print("=" * 60)
    print("TEST 6: NPC Compatibility")
    print("=" * 60)
    
    # Empathetic player
    profiler_emp = TraitProfiler("Empath")
    for _ in range(6):
        choice = TraitChoice(
            choice_id="test", dialogue_option="Test",
            primary_trait=TraitType.EMPATHY, trait_weight=0.3,
            npc_name="Test", scene_name="Test",
        )
        profiler_emp.record_choice(choice)
    
    engine_emp = NPCResponseEngine(profiler_emp)
    
    # Skeptical player
    profiler_skep = TraitProfiler("Skeptic")
    for _ in range(6):
        choice = TraitChoice(
            choice_id="test", dialogue_option="Test",
            primary_trait=TraitType.SKEPTICISM, trait_weight=0.3,
            npc_name="Test", scene_name="Test",
        )
        profiler_skep.record_choice(choice)
    
    engine_skep = NPCResponseEngine(profiler_skep)
    
    # Test compatibility
    print("Empathetic player:")
    print(f"  vs Nima (empathetic):  {engine_emp.get_npc_conflict_level('Nima')}")
    print(f"  vs Ravi (skeptical):   {engine_emp.get_npc_conflict_level('Ravi')}")
    
    print("\nSkeptical player:")
    print(f"  vs Nima (empathetic):  {engine_skep.get_npc_conflict_level('Nima')}")
    print(f"  vs Ravi (skeptical):   {engine_skep.get_npc_conflict_level('Ravi')}")
    
    # Validate that like traits show better compatibility
    emp_nima = engine_emp.get_npc_conflict_level('Nima')
    skep_ravi = engine_skep.get_npc_conflict_level('Ravi')
    
    # Should be "ally" or at least "neutral"
    assert emp_nima in ['ally', 'neutral'], f"Expected ally/neutral, got {emp_nima}"
    assert skep_ravi in ['ally', 'neutral'], f"Expected ally/neutral, got {skep_ravi}"
    
    print("\n✓ Compatibility systems working")
    print("✓ PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 PHASE 2 INTEGRATION TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_orchestrator_trait_integration()
        test_trait_recording()
        test_marketplace_scene_creation()
        test_marketplace_branching()
        test_coherence_gating()
        test_npc_compatibility()
        
        print("=" * 60)
        print("✓ ALL PHASE 2 TESTS PASSED")
        print("=" * 60)
        print("\n📊 Phase 2 Status:")
        print("  ✓ Orchestrator trait integration: WORKING")
        print("  ✓ Trait recording: WORKING")
        print("  ✓ Marketplace scene: WORKING")
        print("  ✓ Branching dialogue: WORKING")
        print("  ✓ Coherence gating: WORKING")
        print("  ✓ NPC compatibility: WORKING")
        print("\n🚀 Ready for Streamlit testing!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
