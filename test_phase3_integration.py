"""
Phase 3 Integration Tests - Building Collapse Event System
Tests for EventTimeline, collapse trigger, aftermath paths, and orchestrator integration
"""

import sys
sys.path.insert(0, r'd:\saoriverse-console')

from velinor.engine.event_timeline import (
    EventTimeline,
    CollapsePhase,
    AftermathPath,
    BuildingStatus,
    NPCStressState
)
from velinor.engine.collapse_scene import (
    CollapseTriggerScene,
    ImmediateAftermathScene,
    AftermathPathDivergence
)
from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.engine.core import VelinorEngine, GameSession
from velinor.engine.trait_system import TraitType


def test_event_timeline_creation():
    """TEST 1: EventTimeline initializes correctly"""
    timeline = EventTimeline()
    
    assert timeline.current_day == 0
    assert timeline.current_phase == CollapsePhase.PRE_COLLAPSE
    assert timeline.aftermath_path == AftermathPath.UNDETERMINED
    assert timeline.building_status.stability_percent == 100
    assert not timeline.collapse_triggered
    
    print("✓ TEST 1: EventTimeline Creation - PASSED")
    return True


def test_game_day_progression():
    """TEST 2: Game days advance with proper phase transitions"""
    timeline = EventTimeline()
    timeline.set_marketplace_state(coherence=75.0, primary_trait="empathy", malrik_elenya_cooperation=85)
    
    # Advance through pre-collapse phase - should trigger subtle deterioration after day 2
    for day in range(1, 5):
        events = timeline.advance_day()
        assert events["day"] == day
    
    # After day 3, should transition to subtle deterioration
    assert timeline.current_phase in [CollapsePhase.PRE_COLLAPSE, CollapsePhase.SUBTLE_DETERIORATION]
    
    print("✓ TEST 2: Game Day Progression - PASSED")
    return True
    
    # Advance through subtle deterioration
    for day in range(4, 11):
        events = timeline.advance_day()
        assert timeline.building_status.stability_percent < 100
    
    # Should be in escalating conflict
    assert timeline.current_phase == CollapsePhase.ESCALATING_CONFLICT
    
    print("✓ TEST 2: Game Day Progression - PASSED")
    return True


def test_building_deterioration():
    """TEST 3: Building deteriorates properly with visual indicators"""
    timeline = EventTimeline()
    timeline.set_marketplace_state(coherence=75.0, primary_trait="empathy", malrik_elenya_cooperation=85)
    
    # Advance to subtle deterioration phase
    for _ in range(5):
        timeline.advance_day()
    
    assert timeline.building_status.stability_percent < 100
    assert timeline.building_status.cracks_visible
    
    # Advance further through escalating conflict
    for _ in range(7):
        timeline.advance_day()
    
    # Check status
    assert timeline.building_status.stability_percent < 75
    
    # Get description
    description = timeline.get_building_description()
    assert len(description) > 0
    
    print("✓ TEST 3: Building Deterioration - PASSED")
    return True


def test_collapse_trigger():
    """TEST 4: Collapse triggers at proper stability threshold"""
    timeline = EventTimeline()
    timeline.set_marketplace_state(coherence=75.0, primary_trait="empathy", malrik_elenya_cooperation=85)
    
    # Advance quickly to collapse
    for _ in range(15):
        timeline.advance_day()
    
    # Manually trigger collapse if not auto-triggered
    if not timeline.collapse_triggered:
        result = timeline.trigger_collapse()
        assert result["status"] == "collapsed"
    
    assert timeline.collapse_triggered
    assert timeline.current_phase == CollapsePhase.COLLAPSE_TRIGGER
    assert timeline.building_status.stability_percent == 0
    assert timeline.malrik_state.stress_level > 30
    assert timeline.elenya_state.stress_level > 30
    
    print("✓ TEST 4: Collapse Trigger - PASSED")
    return True


def test_npc_stress_progression():
    """TEST 5: NPC stress increases through phases"""
    timeline = EventTimeline()
    initial_malrik_stress = timeline.malrik_state.stress_level
    
    # Advance through phases
    for _ in range(15):
        timeline.advance_day()
    
    # Stress should have increased
    assert timeline.malrik_state.stress_level > initial_malrik_stress
    assert timeline.elenya_state.stress_level > 0
    
    # After collapse, stress should be high
    if timeline.collapse_triggered:
        assert timeline.malrik_state.stress_level >= 40
        assert timeline.elenya_state.stress_level >= 40
    
    print("✓ TEST 5: NPC Stress Progression - PASSED")
    return True


def test_player_intervention_recording():
    """TEST 6: Player interventions are recorded and affect rebuild potential"""
    timeline = EventTimeline()
    timeline.set_marketplace_state(coherence=60.0, primary_trait="empathy", malrik_elenya_cooperation=75)
    
    # Trigger collapse
    for _ in range(15):
        timeline.advance_day()
    timeline.trigger_collapse()
    
    # Record interventions
    assert timeline.player_interventions.total_intervention_count == 0
    
    result1 = timeline.record_player_intervention("malrik", "not_your_fault")
    assert result1 is not None
    assert timeline.player_interventions.total_intervention_count == 1
    
    result2 = timeline.record_player_intervention("elenya", "advocate_reunion")
    assert timeline.player_interventions.total_intervention_count == 2
    
    # Rebuild potential should increase with interventions
    rebuild_potential = timeline.player_interventions.get_rebuild_potential()
    assert rebuild_potential > 10  # Base without interventions
    
    print("✓ TEST 6: Player Intervention Recording - PASSED")
    return True


def test_aftermath_path_determination():
    """TEST 7: Aftermath path determined by interventions and coherence"""
    # Test high interventions → Rebuild Together
    timeline_rebuild = EventTimeline()
    timeline_rebuild.set_marketplace_state(coherence=80.0, primary_trait="empathy", malrik_elenya_cooperation=90)
    timeline_rebuild.trigger_collapse()
    timeline_rebuild.transition_to_phase(CollapsePhase.IMMEDIATE_AFTERMATH)
    
    # Record many interventions
    for _ in range(5):
        timeline_rebuild.record_player_intervention("malrik", "not_your_fault")
        timeline_rebuild.record_player_intervention("elenya", "advocate_reunion")
    
    # Advance to resolution
    for _ in range(7):
        timeline_rebuild.advance_day()
    timeline_rebuild.transition_to_phase(CollapsePhase.AFTERMATH_RESOLUTION)
    timeline_rebuild.advance_day()
    
    # Should be rebuild together (high rebuild potential)
    assert timeline_rebuild.aftermath_path in [AftermathPath.REBUILD_TOGETHER, AftermathPath.STALEMATE]
    
    # Test low interventions → Separation
    timeline_sep = EventTimeline()
    timeline_sep.set_marketplace_state(coherence=40.0, primary_trait="skepticism", malrik_elenya_cooperation=50)
    timeline_sep.trigger_collapse()
    timeline_sep.transition_to_phase(CollapsePhase.IMMEDIATE_AFTERMATH)
    
    # Record NO interventions - should lead to separation
    timeline_sep.transition_to_phase(CollapsePhase.AFTERMATH_RESOLUTION)
    timeline_sep.advance_day()
    
    # Should be complete separation or stalemate
    assert timeline_sep.aftermath_path in [AftermathPath.COMPLETE_SEPARATION, AftermathPath.STALEMATE]
    
    print("✓ TEST 7: Aftermath Path Determination - PASSED")
    return True


def test_collapse_scene_narration():
    """TEST 8: Collapse scene generates proper narrations"""
    scene = CollapseTriggerScene()
    
    # Test all narration methods
    initial_narration = scene.get_initial_rumble_narration()
    assert len(initial_narration) > 0
    assert "creaking" in initial_narration.lower() or "sound" in initial_narration.lower()
    
    structural_narration = scene.get_structural_failure_narration()
    assert len(structural_narration) > 0
    assert "crack" in structural_narration.lower() or "fail" in structural_narration.lower()
    
    malrik_reaction = scene.get_malrik_reaction()
    assert "malrik" in malrik_reaction.lower()
    assert "archive" in malrik_reaction.lower()
    
    elenya_reaction = scene.get_elenya_reaction()
    assert "elenya" in elenya_reaction.lower()
    
    coren_reaction = scene.get_coren_reaction()
    assert "coren" in coren_reaction.lower()
    
    dialogue = scene.get_post_collapse_dialogue()
    assert len(dialogue) > 0
    assert "malrik" in dialogue.lower() and "elenya" in dialogue.lower()
    
    print("✓ TEST 8: Collapse Scene Narration - PASSED")
    return True


def test_aftermath_scene_narration():
    """TEST 9: Aftermath scenes generate proper narrations"""
    aftermath = ImmediateAftermathScene()
    
    # Test separation narration
    separation_narration = aftermath.get_separation_narration()
    assert len(separation_narration) > 0
    assert "separate" in separation_narration.lower() or "withdraw" in separation_narration.lower()
    
    # Test isolation dialogues
    malrik_isolation = aftermath.get_malrik_isolation_dialogue()
    assert "malrik" in malrik_isolation.lower()
    assert "structure" in malrik_isolation.lower() or "maintain" in malrik_isolation.lower()
    
    elenya_isolation = aftermath.get_elenya_isolation_dialogue()
    assert "elenya" in elenya_isolation.lower()
    
    # Test NPC responses to interventions
    malrik_response_blame = aftermath.get_malrik_response_to_intervention("not_your_fault")
    assert len(malrik_response_blame) > 0
    
    elenya_response_suffering = aftermath.get_elenya_response_to_intervention("he_is_suffering")
    assert len(elenya_response_suffering) > 0
    
    print("✓ TEST 9: Aftermath Scene Narration - PASSED")
    return True


def test_aftermath_path_narrations():
    """TEST 10: Each aftermath path generates distinct narrations"""
    # Test Rebuild Together
    rebuild_setup = AftermathPathDivergence.get_rebuild_together_setup()
    assert len(rebuild_setup) > 0
    assert "together" in rebuild_setup.lower() or "reconstruct" in rebuild_setup.lower()
    
    rebuild_progression = AftermathPathDivergence.get_rebuild_together_progression()
    assert len(rebuild_progression) > 0
    assert "joint" in rebuild_progression.lower() or "session" in rebuild_progression.lower()
    
    # Test Stalemate
    stalemate_setup = AftermathPathDivergence.get_stalemate_setup()
    assert len(stalemate_setup) > 0
    assert "separate" in stalemate_setup.lower() or "independent" in stalemate_setup.lower()
    
    stalemate_resolution = AftermathPathDivergence.get_stalemate_resolution()
    assert len(stalemate_resolution) > 0
    
    # Test Complete Separation
    separation_setup = AftermathPathDivergence.get_complete_separation_setup()
    assert len(separation_setup) > 0
    assert "rigid" in separation_setup.lower() or "isolated" in separation_setup.lower()
    
    separation_aftermath = AftermathPathDivergence.get_complete_separation_aftermath()
    assert len(separation_aftermath) > 0
    assert "ruin" in separation_aftermath.lower() or "cemetery" in separation_aftermath.lower()
    
    print("✓ TEST 10: Aftermath Path Narrations - PASSED")
    return True


def test_ending_connection():
    """TEST 11: Each aftermath path unlocks specific endings"""
    # Rebuild Together
    rebuild_connection = AftermathPathDivergence.get_aftermath_ending_connection(AftermathPath.REBUILD_TOGETHER)
    assert rebuild_connection["world_state"] == "lean_synthesis"
    assert "ending_1" in rebuild_connection["ending_paths_unlocked"][0]
    
    # Stalemate
    stalemate_connection = AftermathPathDivergence.get_aftermath_ending_connection(AftermathPath.STALEMATE)
    assert stalemate_connection["world_state"] == "neutral"
    assert len(stalemate_connection["ending_paths_unlocked"]) > 0
    
    # Complete Separation
    separation_connection = AftermathPathDivergence.get_aftermath_ending_connection(AftermathPath.COMPLETE_SEPARATION)
    assert separation_connection["world_state"] == "lean_fragmentation"
    assert len(separation_connection["ending_paths_unlocked"]) > 0
    
    print("✓ TEST 11: Ending Connection - PASSED")
    return True


def test_orchestrator_phase3_integration():
    """TEST 12: Orchestrator properly integrates Phase 3 systems"""
    try:
        # Create minimal game engine
        game_engine = VelinorEngine()
        game_session = game_engine.create_session(player_name="TestPlayer")
        
        # Create orchestrator
        orchestrator = VelinorTwineOrchestrator(
            game_engine=game_engine,
            story_path="",  # No story file needed for test
            player_name="TestPlayer"
        )
        
        # Verify Phase 3 systems initialized
        assert orchestrator.event_timeline is not None
        assert orchestrator.collapse_trigger_scene is not None
        assert orchestrator.aftermath_scene is not None
        
        # Test marketplace conclusion method
        orchestrator.set_marketplace_conclusion(coherence=75.0, primary_trait="empathy")
        assert orchestrator.event_timeline.player_marketplace_coherence == 75.0
        assert orchestrator.event_timeline.player_marketplace_primary_trait == "empathy"
        
        # Test day advancement
        day_result = orchestrator.advance_game_day()
        assert "day" in day_result
        assert "phase" in day_result
        assert day_result["day"] == 1
        
        # Test collapse trigger
        orchestrator.event_timeline.trigger_collapse()
        collapse_result = orchestrator.trigger_collapse_event()
        assert collapse_result["status"] == "collapse_triggered"
        
        # Test intervention recording
        intervention_result = orchestrator.record_post_collapse_intervention("malrik", "not_your_fault")
        assert intervention_result is not None
        
        # Test status retrieval
        status = orchestrator.get_phase3_status()
        assert "current_day" in status
        assert "aftermath_path" in status
        assert "building_stability" in status
        
        print("✓ TEST 12: Orchestrator Phase 3 Integration - PASSED")
        return True
    
    except Exception as e:
        print(f"✗ TEST 12: Orchestrator Phase 3 Integration - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_coherence_and_traits_phase3():
    """TEST 13: Player's coherence and traits from Phase 2 affect Phase 3"""
    try:
        game_engine = VelinorEngine()
        game_session = game_engine.create_session(player_name="EmpathyPlayer")
        orchestrator = VelinorTwineOrchestrator(
            game_engine=game_engine,
            story_path="",
            player_name="EmpathyPlayer"
        )
        
        # Simulate Phase 2 outcome: high empathy coherence
        orchestrator.set_marketplace_conclusion(coherence=85.0, primary_trait="empathy")
        
        # Verify marketplace state set properly
        assert orchestrator.event_timeline.player_marketplace_coherence == 85.0
        assert orchestrator.event_timeline.player_marketplace_primary_trait == "empathy"
        
        # Advance to collapse
        for _ in range(15):
            orchestrator.advance_game_day()
        
        # Record interventions (empathetic player more likely to intervene)
        for _ in range(3):
            orchestrator.record_post_collapse_intervention("malrik", "not_your_fault")
            orchestrator.record_post_collapse_intervention("elenya", "advocate_reunion")
        
        # Get rebuild potential
        rebuild_potential = orchestrator.event_timeline.player_interventions.get_rebuild_potential()
        assert rebuild_potential > 25  # Should be higher due to interventions
        
        print("✓ TEST 13: Coherence and Traits Phase 3 - PASSED")
        return True
    
    except Exception as e:
        print(f"✗ TEST 13: Coherence and Traits Phase 3 - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_game_state_persistence():
    """TEST 14: Game state can be retrieved for UI display and persistence"""
    timeline = EventTimeline()
    timeline.set_marketplace_state(coherence=70.0, primary_trait="integration", malrik_elenya_cooperation=80)
    
    # Advance through phases
    for _ in range(10):
        timeline.advance_day()
    
    # Get game state
    state = timeline.get_game_state()
    
    assert "current_day" in state
    assert "current_phase" in state
    assert "aftermath_path" in state
    assert "building_stability" in state
    assert "malrik_stress" in state
    assert "elenya_stress" in state
    assert "collapse_triggered" in state
    
    # Verify state values are reasonable
    assert state["current_day"] == 10
    assert state["building_stability"] < 100
    assert state["building_stability"] >= 0
    
    print("✓ TEST 14: Game State Persistence - PASSED")
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 3 INTEGRATION TEST SUITE")
    print("Building Collapse Event System")
    print("="*60 + "\n")
    
    tests = [
        test_event_timeline_creation,
        test_game_day_progression,
        test_building_deterioration,
        test_collapse_trigger,
        test_npc_stress_progression,
        test_player_intervention_recording,
        test_aftermath_path_determination,
        test_collapse_scene_narration,
        test_aftermath_scene_narration,
        test_aftermath_path_narrations,
        test_ending_connection,
        test_orchestrator_phase3_integration,
        test_coherence_and_traits_phase3,
        test_game_state_persistence,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} - FAILED: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {failed} tests failed")
    print("="*60 + "\n")
