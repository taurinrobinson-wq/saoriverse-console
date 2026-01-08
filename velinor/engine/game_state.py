"""
Game State Serialization - Phase 5
Captures the complete game state from all phases (1-4)
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class GameStateSnapshot:
    """Snapshot of complete game state for serialization"""
    
    # Metadata
    version: str = "1.0"
    save_timestamp: str = ""
    player_name: str = ""
    play_duration_seconds: int = 0
    
    # Phase 1: Trait System
    trait_choices: Dict[str, Any] = None
    coherence_score: float = 0.0
    coherence_level: str = ""
    primary_trait: str = ""
    secondary_trait: str = ""
    
    # Phase 2: Marketplace & Orchestration
    marketplace_visited: bool = False
    marketplace_path_chosen: str = ""  # "direct", "directed", "faction"
    npc_compatibility: Dict[str, float] = None
    marketplace_conclusion_coherence: float = 0.0
    
    # Phase 3: Collapse Event System
    current_day: int = 0
    current_phase: str = ""
    building_stability_percent: int = 100
    malrik_stress: int = 0
    elenya_stress: int = 0
    malrik_elenya_cooperation: int = 0
    collapse_triggered: bool = False
    aftermath_path: str = ""
    player_interventions: list = None
    rebuild_potential: int = 0
    
    # Phase 4: Ending System
    ending_type: Optional[int] = None
    ending_title: str = ""
    corelink_choice: str = ""  # "restart" or "abandon"
    game_completed: bool = False
    
    # NPC Final States
    npc_final_states: Dict[str, Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Ensure datetime is serializable
        data['save_timestamp'] = self.save_timestamp or datetime.now().isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameStateSnapshot':
        """Create snapshot from dictionary"""
        # Handle missing keys with defaults
        return cls(
            version=data.get('version', '1.0'),
            save_timestamp=data.get('save_timestamp', ''),
            player_name=data.get('player_name', ''),
            play_duration_seconds=data.get('play_duration_seconds', 0),
            trait_choices=data.get('trait_choices', {}),
            coherence_score=data.get('coherence_score', 0.0),
            coherence_level=data.get('coherence_level', ''),
            primary_trait=data.get('primary_trait', ''),
            secondary_trait=data.get('secondary_trait', ''),
            marketplace_visited=data.get('marketplace_visited', False),
            marketplace_path_chosen=data.get('marketplace_path_chosen', ''),
            npc_compatibility=data.get('npc_compatibility', {}),
            marketplace_conclusion_coherence=data.get('marketplace_conclusion_coherence', 0.0),
            current_day=data.get('current_day', 0),
            current_phase=data.get('current_phase', ''),
            building_stability_percent=data.get('building_stability_percent', 100),
            malrik_stress=data.get('malrik_stress', 0),
            elenya_stress=data.get('elenya_stress', 0),
            malrik_elenya_cooperation=data.get('malrik_elenya_cooperation', 0),
            collapse_triggered=data.get('collapse_triggered', False),
            aftermath_path=data.get('aftermath_path', ''),
            player_interventions=data.get('player_interventions', []),
            rebuild_potential=data.get('rebuild_potential', 0),
            ending_type=data.get('ending_type'),
            ending_title=data.get('ending_title', ''),
            corelink_choice=data.get('corelink_choice', ''),
            game_completed=data.get('game_completed', False),
            npc_final_states=data.get('npc_final_states', {})
        )


class GameStateBuilder:
    """Builds a game state snapshot from the orchestrator"""
    
    @staticmethod
    def build_from_orchestrator(orchestrator: Any) -> GameStateSnapshot:
        """
        Build complete game state snapshot from orchestrator
        
        Args:
            orchestrator: VelinorTwineOrchestrator instance
            
        Returns:
            GameStateSnapshot with all current game data
        """
        snapshot = GameStateSnapshot()
        
        # Metadata
        snapshot.version = "1.0"
        snapshot.save_timestamp = datetime.now().isoformat()
        snapshot.player_name = orchestrator.trait_profiler.player_name
        
        # Phase 1: Traits
        snapshot.trait_choices = GameStateBuilder._extract_trait_choices(orchestrator)
        coherence_report = orchestrator.coherence_calculator.get_coherence_report()
        snapshot.coherence_score = coherence_report.overall_coherence
        snapshot.coherence_level = coherence_report.level.value if hasattr(coherence_report, 'level') else 'UNKNOWN'
        primary_trait = orchestrator.trait_profiler.get_primary_trait()
        snapshot.primary_trait = primary_trait.value if primary_trait else ""
        # Secondary trait comes from CoherenceReport
        snapshot.secondary_trait = coherence_report.secondary_pattern.value if coherence_report.secondary_pattern else ""
        
        # Phase 2: Marketplace
        # Marketplace state is stored as individual attributes in event_timeline
        snapshot.marketplace_visited = orchestrator.event_timeline.player_marketplace_coherence != 75.0 or orchestrator.event_timeline.player_marketplace_primary_trait != "empathy"
        snapshot.marketplace_path_chosen = orchestrator.event_timeline.player_marketplace_primary_trait
        snapshot.marketplace_conclusion_coherence = orchestrator.event_timeline.player_marketplace_coherence
        
        # NPC Compatibility (use trust level as proxy)
        snapshot.npc_compatibility = {
            'malrik': 75.0 if orchestrator.npc_response_engine.should_npc_trust_player('malrik') else 25.0,
            'elenya': 75.0 if orchestrator.npc_response_engine.should_npc_trust_player('elenya') else 25.0,
            'coren': 50.0,  # Coren is a neutral observer
        }
        
        # Phase 3: Collapse Event
        snapshot.current_day = orchestrator.event_timeline.current_day
        snapshot.current_phase = orchestrator.event_timeline.current_phase.value
        snapshot.building_stability_percent = orchestrator.event_timeline.building_status.stability_percent
        snapshot.malrik_stress = orchestrator.event_timeline.malrik_state.stress_level
        snapshot.elenya_stress = orchestrator.event_timeline.elenya_state.stress_level
        snapshot.malrik_elenya_cooperation = orchestrator.event_timeline.malrik_state.cooperation_level
        snapshot.collapse_triggered = orchestrator.event_timeline.collapse_triggered
        snapshot.aftermath_path = orchestrator.event_timeline.aftermath_path.value if orchestrator.event_timeline.aftermath_path else ""
        snapshot.rebuild_potential = orchestrator.event_timeline.player_interventions.get_rebuild_potential()
        
        # Player interventions (simplified)
        interventions = []
        for intervention in orchestrator.event_timeline.player_interventions.interventions:
            interventions.append({
                'day': intervention.day,
                'phase': intervention.phase,
                'choice': intervention.choice,
                'effectiveness': intervention.effectiveness,
            })
        snapshot.player_interventions = interventions
        
        # Phase 4: Ending
        if orchestrator.ending_manager.current_ending:
            snapshot.ending_type = orchestrator.ending_manager.current_ending.value
            snapshot.ending_title = orchestrator.ending_manager.current_ending.name
            snapshot.corelink_choice = orchestrator.ending_manager.calculator.corelink_choice.value
            snapshot.game_completed = True
            snapshot.npc_final_states = GameStateBuilder._extract_npc_final_states(orchestrator)
        
        return snapshot
    
    @staticmethod
    def _extract_trait_choices(orchestrator: Any) -> Dict[str, Any]:
        """Extract trait choice history"""
        choices = {}
        for i, choice in enumerate(orchestrator.trait_profiler.all_choices):
            choices[f"choice_{i}"] = {
                'trait': choice.primary_trait.value if hasattr(choice.primary_trait, 'value') else str(choice.primary_trait),
                'direction': choice.direction if hasattr(choice, 'direction') else '',
                'context': choice.context if hasattr(choice, 'context') else "",
            }
        return choices
    
    @staticmethod
    def _extract_npc_final_states(orchestrator: Any) -> Dict[str, Dict[str, Any]]:
        """Extract NPC final states"""
        states = {}
        if orchestrator.ending_manager.npc_final_states:
            for name, state in orchestrator.ending_manager.npc_final_states.items():
                states[name] = {
                    'position': state.position,
                    'emotional_state': state.emotional_state,
                    'final_location': state.final_location,
                    'final_dialogue': state.final_dialogue,
                }
        return states


class GameStateRestorer:
    """Restores game state from a snapshot"""
    
    @staticmethod
    def restore_to_orchestrator(snapshot: GameStateSnapshot, orchestrator: Any) -> bool:
        """
        Restore game state from snapshot to orchestrator
        
        Args:
            snapshot: GameStateSnapshot with saved data
            orchestrator: VelinorTwineOrchestrator instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify version compatibility
            if snapshot.version != "1.0":
                print(f"Warning: Save file version {snapshot.version} may not be compatible")
            
            # Restore Phase 1: Traits
            GameStateRestorer._restore_traits(snapshot, orchestrator)
            
            # Restore Phase 2: Marketplace
            GameStateRestorer._restore_marketplace_state(snapshot, orchestrator)
            
            # Restore Phase 3: Collapse
            GameStateRestorer._restore_collapse_state(snapshot, orchestrator)
            
            # Note: Phase 4 (Ending) is read-only in restore (player sees ending they earned)
            
            return True
        except Exception as e:
            print(f"Error restoring game state: {e}")
            return False
    
    @staticmethod
    def _restore_traits(snapshot: GameStateSnapshot, orchestrator: Any) -> None:
        """Restore trait system state"""
        # Restore trait choice history
        for choice_key, choice_data in snapshot.trait_choices.items():
            # This is simplified - in reality would need to replay choices
            pass
        
        # Coherence will be recalculated from choices
    
    @staticmethod
    def _restore_marketplace_state(snapshot: GameStateSnapshot, orchestrator: Any) -> None:
        """Restore marketplace state"""
        if snapshot.marketplace_visited:
            orchestrator.event_timeline.marketplace_state = {
                'entry_point': snapshot.marketplace_path_chosen,
                'coherence_at_conclusion': snapshot.marketplace_conclusion_coherence,
                'visited': True,
            }
    
    @staticmethod
    def _restore_collapse_state(snapshot: GameStateSnapshot, orchestrator: Any) -> None:
        """Restore collapse event system state"""
        orchestrator.event_timeline.current_day = snapshot.current_day
        orchestrator.event_timeline.collapse_triggered = snapshot.collapse_triggered
        orchestrator.event_timeline.rebuild_potential = snapshot.rebuild_potential
        
        # Note: Full restoration of detailed collapse state would require
        # more granular snapshot data. This is a simplified version.


class GameStateValidator:
    """Validates game state snapshots"""
    
    @staticmethod
    def validate_snapshot(snapshot: GameStateSnapshot) -> bool:
        """Validate that snapshot is valid and complete"""
        # Check required fields
        if not snapshot.player_name:
            return False
        if snapshot.coherence_score < 0 or snapshot.coherence_score > 100:
            return False
        if snapshot.current_day < 0:
            return False
        if snapshot.building_stability_percent < 0 or snapshot.building_stability_percent > 100:
            return False
        
        # If game completed, verify ending data
        if snapshot.game_completed and not snapshot.ending_type:
            return False
        
        return True
    
    @staticmethod
    def get_validation_errors(snapshot: GameStateSnapshot) -> list:
        """Get list of validation errors"""
        errors = []
        
        if not snapshot.player_name:
            errors.append("Player name is required")
        if snapshot.coherence_score < 0 or snapshot.coherence_score > 100:
            errors.append(f"Invalid coherence score: {snapshot.coherence_score}")
        if snapshot.current_day < 0:
            errors.append(f"Invalid current day: {snapshot.current_day}")
        if snapshot.building_stability_percent < 0 or snapshot.building_stability_percent > 100:
            errors.append(f"Invalid building stability: {snapshot.building_stability_percent}")
        if snapshot.game_completed and not snapshot.ending_type:
            errors.append("Game marked completed but no ending recorded")
        
        return errors
