"""
Phase 4 Integration Tests - Ending System
Tests all 6 endings and their connections to Phase 3 aftermath paths
"""

import pytest
from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.engine.ending_system import (
    EndingManager, EndingCalculator, EndingType, CoreLinkChoice,
    EndingNarrations, NPCFinalStates
)
from velinor.engine.corelink_scene import CoreLinkScene
from velinor.engine.event_timeline import AftermathPath
from velinor.engine.core import VelinorEngine, GameSession


class TestEndingCalculation:
    """Test the ending determination logic"""
    
    def test_ending_matrix_hopeful_synthesis(self):
        """Test Ending 1: Restart + Rebuild Together"""
        calculator = EndingCalculator()
        calculator.aftermath_path = AftermathPath.REBUILD_TOGETHER
        calculator.corelink_choice = CoreLinkChoice.RESTART_SYSTEM
        
        ending = calculator.determine_ending()
        assert ending == EndingType.HOPEFUL_SYNTHESIS
        assert ending.value == 1
    
    def test_ending_matrix_pyrrhic_restart(self):
        """Test Ending 2: Restart + Abandoned Building"""
        calculator = EndingCalculator()
        calculator.aftermath_path = AftermathPath.COMPLETE_SEPARATION
        calculator.corelink_choice = CoreLinkChoice.RESTART_SYSTEM
        
        ending = calculator.determine_ending()
        assert ending == EndingType.PYRRHIC_RESTART
        assert ending.value == 2
    
    def test_ending_matrix_honest_collapse(self):
        """Test Ending 3: Abandon + Abandoned Building"""
        calculator = EndingCalculator()
        calculator.aftermath_path = AftermathPath.COMPLETE_SEPARATION
        calculator.corelink_choice = CoreLinkChoice.ABANDON_SYSTEM
        
        ending = calculator.determine_ending()
        assert ending == EndingType.HONEST_COLLAPSE
        assert ending.value == 3
    
    def test_ending_matrix_earned_synthesis(self):
        """Test Ending 4: Abandon + Rebuild Together"""
        calculator = EndingCalculator()
        calculator.aftermath_path = AftermathPath.REBUILD_TOGETHER
        calculator.corelink_choice = CoreLinkChoice.ABANDON_SYSTEM
        
        ending = calculator.determine_ending()
        assert ending == EndingType.EARNED_SYNTHESIS
        assert ending.value == 4
    
    def test_ending_matrix_technical_solution(self):
        """Test Ending 5: Restart + Partial Rebuild"""
        calculator = EndingCalculator()
        calculator.aftermath_path = AftermathPath.STALEMATE
        calculator.corelink_choice = CoreLinkChoice.RESTART_SYSTEM
        
        ending = calculator.determine_ending()
        assert ending == EndingType.TECHNICAL_SOLUTION
        assert ending.value == 5
    
    def test_ending_matrix_stalemate(self):
        """Test Ending 6: Abandon + Partial Rebuild"""
        calculator = EndingCalculator()
        calculator.aftermath_path = AftermathPath.STALEMATE
        calculator.corelink_choice = CoreLinkChoice.ABANDON_SYSTEM
        
        ending = calculator.determine_ending()
        assert ending == EndingType.STALEMATE
        assert ending.value == 6


class TestEndingNarrations:
    """Test that all 6 endings have full narrations"""
    
    def test_hopeful_synthesis_narration(self):
        """Ending 1 narration exists and is substantial"""
        narration = EndingNarrations.get_ending_narration(EndingType.HOPEFUL_SYNTHESIS)
        assert len(narration) > 1000
        assert "synthesis" in narration.lower()
        assert "Corelink" in narration
        assert "Malrik" in narration and "Elenya" in narration
    
    def test_pyrrhic_restart_narration(self):
        """Ending 2 narration exists and is substantial"""
        narration = EndingNarrations.get_ending_narration(EndingType.PYRRHIC_RESTART)
        assert len(narration) > 1000
        assert "fracture" in narration.lower() or "apart" in narration.lower()
        assert "Corelink" in narration
        assert "restarted" in narration.lower() or "restart" in narration.lower()
    
    def test_honest_collapse_narration(self):
        """Ending 3 narration exists and is substantial"""
        narration = EndingNarrations.get_ending_narration(EndingType.HONEST_COLLAPSE)
        assert len(narration) > 1000
        assert "dark" in narration.lower() or "dark" in narration
        assert "honest" in narration.lower()
        assert "communities" in narration.lower() or "community" in narration.lower()
    
    def test_earned_synthesis_narration(self):
        """Ending 4 narration exists and is substantial"""
        narration = EndingNarrations.get_ending_narration(EndingType.EARNED_SYNTHESIS)
        assert len(narration) > 1000
        assert "earned" in narration.lower()
        assert "rebuild" in narration.lower()
        assert "archive" in narration.lower()
    
    def test_technical_solution_narration(self):
        """Ending 5 narration exists and is substantial"""
        narration = EndingNarrations.get_ending_narration(EndingType.TECHNICAL_SOLUTION)
        assert len(narration) > 1000
        assert "support" in narration.lower()
        assert "system" in narration.lower()
    
    def test_stalemate_narration(self):
        """Ending 6 narration exists and is substantial"""
        narration = EndingNarrations.get_ending_narration(EndingType.STALEMATE)
        assert len(narration) > 1000
        assert "uncertain" in narration.lower() or "community" in narration.lower()


class TestNPCFinalStates:
    """Test NPC final states for each ending"""
    
    def test_hopeful_synthesis_npc_states(self):
        """NPCs in hopeful synthesis: together and hopeful"""
        states = NPCFinalStates.get_npc_final_states(EndingType.HOPEFUL_SYNTHESIS)
        
        assert len(states) >= 3
        assert "malrik" in states and "elenya" in states
        
        malrik = states["malrik"]
        assert malrik.position == "rebuilt_together"
        assert malrik.emotional_state == "hopeful"
        assert malrik.final_location == "archive"
    
    def test_pyrrhic_restart_npc_states(self):
        """NPCs in pyrrhic restart: separated and resigned"""
        states = NPCFinalStates.get_npc_final_states(EndingType.PYRRHIC_RESTART)
        
        assert len(states) >= 3
        malrik = states["malrik"]
        elenya = states["elenya"]
        
        assert malrik.position == "abandoned"
        assert elenya.position == "abandoned"
        assert malrik.emotional_state == "resigned"
        assert elenya.emotional_state == "resigned"
    
    def test_honest_collapse_npc_states(self):
        """NPCs in honest collapse: separated and grieving"""
        states = NPCFinalStates.get_npc_final_states(EndingType.HONEST_COLLAPSE)
        
        assert len(states) >= 3
        malrik = states["malrik"]
        
        assert malrik.position == "abandoned"
        assert malrik.emotional_state == "grieving"
    
    def test_earned_synthesis_npc_states(self):
        """NPCs in earned synthesis: together and determined"""
        states = NPCFinalStates.get_npc_final_states(EndingType.EARNED_SYNTHESIS)
        
        assert len(states) >= 3
        malrik = states["malrik"]
        elenya = states["elenya"]
        
        assert malrik.position == "rebuilt_together"
        assert elenya.position == "rebuilt_together"
        assert malrik.emotional_state == "determined"
        assert elenya.emotional_state == "determined"
    
    def test_technical_solution_npc_states(self):
        """NPCs in technical solution: together with system support"""
        states = NPCFinalStates.get_npc_final_states(EndingType.TECHNICAL_SOLUTION)
        
        assert len(states) >= 3
        malrik = states["malrik"]
        
        assert malrik.position == "rebuilt_together"
        assert malrik.emotional_state == "hopeful"
    
    def test_stalemate_npc_states(self):
        """NPCs in stalemate: uncertain but working"""
        states = NPCFinalStates.get_npc_final_states(EndingType.STALEMATE)
        
        assert len(states) >= 3
        malrik = states["malrik"]
        
        assert malrik.position == "uncertain"
        assert malrik.emotional_state == "cautious"


class TestEndingTitlesAndDescriptions:
    """Test that all endings have proper titles and descriptions"""
    
    def test_all_endings_have_titles(self):
        """All 6 endings have titles"""
        for ending_type in EndingType:
            title = EndingNarrations.get_ending_title(ending_type)
            assert len(title) > 0
            assert title != "Unknown Ending"
    
    def test_all_endings_have_descriptions(self):
        """All 6 endings have descriptions"""
        for ending_type in EndingType:
            description = EndingNarrations.get_ending_description(ending_type)
            assert len(description) > 0
    
    def test_ending_titles_are_unique(self):
        """All ending titles are unique"""
        titles = set()
        for ending_type in EndingType:
            title = EndingNarrations.get_ending_title(ending_type)
            assert title not in titles, f"Duplicate title: {title}"
            titles.add(title)
    
    def test_ending_titles_match_type_names(self):
        """Ending titles contain key words from the ending"""
        title_keywords = {
            EndingType.HOPEFUL_SYNTHESIS: "Synthesis",
            EndingType.PYRRHIC_RESTART: "Pyrrhic",
            EndingType.HONEST_COLLAPSE: "Collapse",
            EndingType.EARNED_SYNTHESIS: "Earned",
            EndingType.TECHNICAL_SOLUTION: "Solution",
            EndingType.STALEMATE: "Stalemate",
        }
        
        for ending_type, keyword in title_keywords.items():
            title = EndingNarrations.get_ending_title(ending_type)
            assert keyword in title, f"Expected '{keyword}' in title '{title}'"


class TestCoreLinkScene:
    """Test the Corelink chamber scene"""
    
    def test_chamber_entrance_narration(self):
        """Chamber entrance has substantial narration"""
        scene = CoreLinkScene()
        narration = scene.get_chamber_entrance_narration()
        assert len(narration) > 500
        assert "Corelink" in narration
        assert "Saori" in narration
    
    def test_setup_monologue(self):
        """Setup monologue helps player understand their choice"""
        scene = CoreLinkScene()
        monologue = scene.get_setup_monologue()
        assert len(monologue) > 300
        assert "restart" in monologue.lower()
        assert "abandon" in monologue.lower() or "rest" in monologue.lower()
    
    def test_choice_prompt_structure(self):
        """Choice prompt has both options with descriptions"""
        scene = CoreLinkScene()
        choices = scene.get_choice_prompt()
        
        assert "restart" in choices
        assert "abandon" in choices
        
        restart_choice = choices["restart"]
        assert "label" in restart_choice
        assert "description" in restart_choice
        assert "consequence_preview" in restart_choice
        assert len(restart_choice["label"]) > 0
    
    def test_choice_confirmation_narration(self):
        """Choice confirmation has appropriate narration"""
        scene = CoreLinkScene()
        
        restart_confirmation = scene.get_choice_confirmation("restart")
        assert restart_confirmation["choice"] == "restart"
        assert len(restart_confirmation["confirmation_narration"]) > 500
        
        abandon_confirmation = scene.get_choice_confirmation("abandon")
        assert abandon_confirmation["choice"] == "abandon"
        assert len(abandon_confirmation["confirmation_narration"]) > 500
    
    def test_after_choice_reflection(self):
        """After-choice reflection varies by choice"""
        scene = CoreLinkScene()
        
        restart_reflection = scene.get_after_choice_reflection("restart")
        abandon_reflection = scene.get_after_choice_reflection("abandon")
        
        assert len(restart_reflection) > 200
        assert len(abandon_reflection) > 200
        assert restart_reflection != abandon_reflection


class TestEndingManager:
    """Test the ending manager orchestration"""
    
    def test_ending_manager_initialization(self):
        """Ending manager initializes properly"""
        manager = EndingManager()
        assert manager.current_ending is None
        assert manager.player_viewed_ending is False
    
    def test_setup_from_phase3(self):
        """Ending manager accepts Phase 3 state"""
        manager = EndingManager()
        
        manager.setup_from_phase3(
            aftermath_path=AftermathPath.REBUILD_TOGETHER,
            coherence=75.0,
            primary_trait="synthesis",
            rebuild_advocacy=80
        )
        
        assert manager.calculator.aftermath_path == AftermathPath.REBUILD_TOGETHER
        assert manager.calculator.player_coherence == 75.0
    
    def test_player_chooses_corelink_determines_ending(self):
        """Making Corelink choice determines ending"""
        manager = EndingManager()
        manager.setup_from_phase3(
            aftermath_path=AftermathPath.REBUILD_TOGETHER,
            coherence=75.0,
            primary_trait="synthesis",
            rebuild_advocacy=80
        )
        
        result = manager.player_chooses_corelink(CoreLinkChoice.RESTART_SYSTEM)
        
        assert result["ending_determined"] is True
        assert result["ending_type"] == 1  # Hopeful Synthesis
        assert manager.current_ending == EndingType.HOPEFUL_SYNTHESIS
    
    def test_get_ending_content_complete(self):
        """Getting ending content returns all required fields"""
        manager = EndingManager()
        manager.setup_from_phase3(
            aftermath_path=AftermathPath.REBUILD_TOGETHER,
            coherence=75.0,
            primary_trait="synthesis",
            rebuild_advocacy=80
        )
        manager.player_chooses_corelink(CoreLinkChoice.RESTART_SYSTEM)
        
        content = manager.get_ending_content()
        
        assert "ending_type" in content
        assert "ending_title" in content
        assert "ending_description" in content
        assert "narration" in content
        assert "npc_final_states" in content
        assert len(content["narration"]) > 1000
    
    def test_get_ending_status_before_choice(self):
        """Ending status before choice shows undetermined"""
        manager = EndingManager()
        status = manager.get_ending_status()
        
        assert status["ending_determined"] is False
        assert status["ending_type"] is None
    
    def test_get_ending_status_after_choice(self):
        """Ending status after choice shows determined"""
        manager = EndingManager()
        manager.setup_from_phase3(
            aftermath_path=AftermathPath.REBUILD_TOGETHER,
            coherence=85.0,
            primary_trait="synthesis",
            rebuild_advocacy=90
        )
        manager.player_chooses_corelink(CoreLinkChoice.ABANDON_SYSTEM)
        
        status = manager.get_ending_status()
        
        assert status["ending_determined"] is True
        assert status["ending_type"] == 4


class TestOrchestratorPhase4Integration:
    """Test Phase 4 integration with orchestrator"""
    
    def setup_method(self):
        """Create a fresh orchestrator for each test"""
        engine = VelinorEngine()
        self.orchestrator = VelinorTwineOrchestrator(
            game_engine=engine,
            story_path="",
            player_name="TestPlayer"
        )
    
    def test_orchestrator_has_ending_manager(self):
        """Orchestrator has Phase 4 systems"""
        assert hasattr(self.orchestrator, 'ending_manager')
        assert hasattr(self.orchestrator, 'corelink_scene')
    
    def test_initiate_ending_sequence(self):
        """Initiating ending sequence sets up properly"""
        # Set up Phase 3 state first
        from velinor.engine.event_timeline import EventTimeline
        
        self.orchestrator.event_timeline.aftermath_path = AftermathPath.REBUILD_TOGETHER
        
        result = self.orchestrator.initiate_ending_sequence()
        
        assert result["phase"] == "ending_sequence_started"
        assert "corelink_chamber_narration" in result
        assert "setup_monologue" in result
    
    def test_get_corelink_choice_prompt(self):
        """Getting choice prompt works"""
        result = self.orchestrator.get_corelink_choice_prompt()
        
        assert result["phase"] == "corelink_choice"
        assert "choices" in result
        assert "restart" in result["choices"]
        assert "abandon" in result["choices"]
    
    def test_make_corelink_choice_restart(self):
        """Making restart choice determines appropriate ending"""
        # Set up Phase 3 state
        self.orchestrator.event_timeline.aftermath_path = AftermathPath.REBUILD_TOGETHER
        self.orchestrator.initiate_ending_sequence()
        
        result = self.orchestrator.make_corelink_choice("restart")
        
        assert result["choice_made"] is True
        assert result["choice"] == "restart"
        assert result["ending_determined"] is True
        assert result["ending_type"] == 1  # Hopeful Synthesis
    
    def test_make_corelink_choice_abandon(self):
        """Making abandon choice determines appropriate ending"""
        # Set up Phase 3 state
        self.orchestrator.event_timeline.aftermath_path = AftermathPath.STALEMATE
        self.orchestrator.initiate_ending_sequence()
        
        result = self.orchestrator.make_corelink_choice("abandon")
        
        assert result["choice_made"] is True
        assert result["choice"] == "abandon"
        assert result["ending_determined"] is True
        assert result["ending_type"] == 6  # Stalemate
    
    def test_trigger_ending(self):
        """Triggering ending returns complete ending content"""
        # Set up and make a choice
        self.orchestrator.event_timeline.aftermath_path = AftermathPath.REBUILD_TOGETHER
        self.orchestrator.initiate_ending_sequence()
        self.orchestrator.make_corelink_choice("abandon")
        
        result = self.orchestrator.trigger_ending()
        
        assert result["phase"] == "ending"
        assert result["game_complete"] is True
        assert "narration" in result
        assert "npc_final_states" in result
        assert len(result["narration"]) > 1000
    
    def test_get_phase4_status(self):
        """Getting Phase 4 status works"""
        result = self.orchestrator.get_phase4_status()
        
        assert result["phase"] == 4
        assert "ending_status" in result
        assert "game_complete" in result


class TestEndingAccessibility:
    """Test that all endings are accessible"""
    
    def test_all_6_endings_accessible(self):
        """All 6 endings can be reached"""
        test_cases = [
            (AftermathPath.REBUILD_TOGETHER, CoreLinkChoice.RESTART_SYSTEM, EndingType.HOPEFUL_SYNTHESIS),
            (AftermathPath.COMPLETE_SEPARATION, CoreLinkChoice.RESTART_SYSTEM, EndingType.PYRRHIC_RESTART),
            (AftermathPath.COMPLETE_SEPARATION, CoreLinkChoice.ABANDON_SYSTEM, EndingType.HONEST_COLLAPSE),
            (AftermathPath.REBUILD_TOGETHER, CoreLinkChoice.ABANDON_SYSTEM, EndingType.EARNED_SYNTHESIS),
            (AftermathPath.STALEMATE, CoreLinkChoice.RESTART_SYSTEM, EndingType.TECHNICAL_SOLUTION),
            (AftermathPath.STALEMATE, CoreLinkChoice.ABANDON_SYSTEM, EndingType.STALEMATE),
        ]
        
        for aftermath_path, choice, expected_ending in test_cases:
            manager = EndingManager()
            manager.setup_from_phase3(
                aftermath_path=aftermath_path,
                coherence=50.0,
                primary_trait="unknown",
                rebuild_advocacy=50
            )
            manager.player_chooses_corelink(choice)
            
            assert manager.current_ending == expected_ending
    
    def test_ending_symmetry(self):
        """Endings have proper symmetry pairs"""
        # Endings 1 & 4: Both synthesis paths
        assert EndingNarrations.get_ending_title(EndingType.HOPEFUL_SYNTHESIS) != \
               EndingNarrations.get_ending_title(EndingType.EARNED_SYNTHESIS)
        
        # Both are synthesis but different system involvement
        desc1 = EndingNarrations.get_ending_description(EndingType.HOPEFUL_SYNTHESIS)
        desc4 = EndingNarrations.get_ending_description(EndingType.EARNED_SYNTHESIS)
        
        assert "Restart" in desc1 and "Rebuild Together" in desc1
        assert "Abandon" in desc4 and "Rebuild Together" in desc4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
