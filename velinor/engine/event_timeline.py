"""
Event Timeline System for Velinor
Tracks game progression across in-game days, phases, and collapse events
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


class CollapsePhase(Enum):
    """Phases of the building collapse event"""
    PRE_COLLAPSE = "pre_collapse"
    SUBTLE_DETERIORATION = "subtle_deterioration"
    ESCALATING_CONFLICT = "escalating_conflict"
    FINAL_WARNING = "final_warning"
    COLLAPSE_TRIGGER = "collapse_trigger"
    IMMEDIATE_AFTERMATH = "immediate_aftermath"
    AFTERMATH_RESOLUTION = "aftermath_resolution"
    POST_COLLAPSE = "post_collapse"


class AftermathPath(Enum):
    """Possible aftermath paths after collapse"""
    UNDETERMINED = "undetermined"
    REBUILD_TOGETHER = "rebuild_together"
    STALEMATE = "stalemate"
    COMPLETE_SEPARATION = "complete_separation"


@dataclass
class BuildingStatus:
    """Tracks the archive building's structural integrity"""
    stability_percent: int = 100
    cracks_visible: bool = False
    water_damage: bool = False
    roof_sagging: bool = False
    debris_in_courtyard: bool = False
    
    def deteriorate(self, amount: int = 10) -> None:
        """Gradually deteriorate the building"""
        self.stability_percent = max(0, self.stability_percent - amount)
        
        if self.stability_percent < 100:
            self.cracks_visible = True
        if self.stability_percent < 85:
            self.water_damage = True
        if self.stability_percent < 70:
            self.roof_sagging = True
        if self.stability_percent < 50:
            self.debris_in_courtyard = True


@dataclass
class NPCStressState:
    """Tracks NPC emotional state during collapse"""
    stress_level: int = 0  # 0-100
    separation_distance: int = 0  # How far apart Malrik/Elenya are
    cooperation_level: int = 100  # 0-100, relationship quality
    
    def increase_stress(self, amount: int = 5) -> None:
        """Increase NPC stress"""
        self.stress_level = min(100, self.stress_level + amount)
    
    def decrease_cooperation(self, amount: int = 5) -> None:
        """Decrease cooperation between Malrik/Elenya"""
        self.cooperation_level = max(0, self.cooperation_level - amount)


@dataclass
class PlayerInterventionLog:
    """Tracks player interventions during aftermath"""
    interventions: List[Dict[str, Any]] = field(default_factory=list)
    empathy_toward_malrik: int = 0
    empathy_toward_elenya: int = 0
    advocacy_for_reunion: int = 0
    total_intervention_count: int = 0
    
    def log_intervention(self, npc_name: str, choice: str, effectiveness: int) -> None:
        """Log a player intervention"""
        self.interventions.append({
            "npc": npc_name,
            "choice": choice,
            "effectiveness": effectiveness,
            "timestamp": datetime.now().isoformat()
        })
        self.total_intervention_count += 1
        
        if npc_name == "malrik" and effectiveness > 0:
            self.empathy_toward_malrik += 1
        elif npc_name == "elenya" and effectiveness > 0:
            self.empathy_toward_elenya += 1
        
        if choice == "advocate_reunion":
            self.advocacy_for_reunion += 1
    
    def get_rebuild_potential(self) -> int:
        """Calculate likelihood of rebuild based on interventions"""
        base = 10  # Base rebuild potential without intervention
        per_intervention = 15
        
        rebuild_potential = base + (self.total_intervention_count * per_intervention)
        return min(85, rebuild_potential)  # Cap at 85


class EventTimeline:
    """Main system for tracking game progression and collapse events"""
    
    def __init__(self):
        """Initialize the event timeline"""
        self.current_day: int = 0
        self.current_phase: CollapsePhase = CollapsePhase.PRE_COLLAPSE
        self.aftermath_path: AftermathPath = AftermathPath.UNDETERMINED
        
        # Building and NPC state
        self.building_status = BuildingStatus()
        self.malrik_state = NPCStressState()
        self.elenya_state = NPCStressState()
        
        # Player tracking
        self.player_interventions = PlayerInterventionLog()
        
        # Phase timing
        self.phase_day_count: Dict[CollapsePhase, int] = {phase: 0 for phase in CollapsePhase}
        
        # Event triggers
        self.collapse_triggered: bool = False
        self.coren_warning_given: bool = False
        self.immediate_aftermath_started: bool = False
        
        # Marketplace connection
        self.player_marketplace_coherence: float = 75.0
        self.player_marketplace_primary_trait: str = "empathy"
        self.malrik_elenya_cooperation_at_marketplace: int = 100
    
    def set_marketplace_state(
        self,
        coherence: float,
        primary_trait: str,
        malrik_elenya_cooperation: int
    ) -> None:
        """Store the player state from marketplace scene"""
        self.player_marketplace_coherence = coherence
        self.player_marketplace_primary_trait = primary_trait
        self.malrik_elenya_cooperation_at_marketplace = malrik_elenya_cooperation
    
    def advance_day(self) -> Dict[str, Any]:
        """Advance one in-game day and trigger appropriate events"""
        self.current_day += 1
        self.phase_day_count[self.current_phase] += 1
        
        events = {"day": self.current_day, "triggered_events": []}
        
        # Phase-specific logic
        if self.current_phase == CollapsePhase.PRE_COLLAPSE:
            if self.current_day >= 3:
                self.transition_to_phase(CollapsePhase.SUBTLE_DETERIORATION)
                events["triggered_events"].append("marketplace_aftermath_visible")
        
        elif self.current_phase == CollapsePhase.SUBTLE_DETERIORATION:
            self.building_status.deteriorate(8)
            self.malrik_state.increase_stress(3)
            self.elenya_state.increase_stress(2)
            
            if self.current_day >= 6:
                self.transition_to_phase(CollapsePhase.ESCALATING_CONFLICT)
                events["triggered_events"].append("tension_escalates")
        
        elif self.current_phase == CollapsePhase.ESCALATING_CONFLICT:
            self.building_status.deteriorate(10)
            self.malrik_state.increase_stress(4)
            self.elenya_state.increase_stress(4)
            
            # Conflict degrades cooperation
            cooperation_loss = 8 if self.current_day % 2 == 0 else 0
            self.malrik_state.decrease_cooperation(cooperation_loss)
            
            if self.current_day >= 10:
                self.transition_to_phase(CollapsePhase.FINAL_WARNING)
                events["triggered_events"].append("coren_gives_warning")
                self.coren_warning_given = True
        
        elif self.current_phase == CollapsePhase.FINAL_WARNING:
            self.building_status.deteriorate(15)  # Rapid deterioration before collapse
            
            # Check collapse trigger
            if self.building_status.stability_percent <= 0:
                self.trigger_collapse()
                events["triggered_events"].append("building_collapses")
        
        elif self.current_phase == CollapsePhase.IMMEDIATE_AFTERMATH:
            if not self.immediate_aftermath_started:
                self.immediate_aftermath_started = True
                events["triggered_events"].append("aftermath_begins")
            
            # NPCs separate themselves
            if self.current_day == 1:
                self.malrik_state.separation_distance = 50
                self.elenya_state.separation_distance = 50
                self.malrik_state.decrease_cooperation(30)
                events["triggered_events"].append("factions_separate")
        
        elif self.current_phase == CollapsePhase.AFTERMATH_RESOLUTION:
            # This phase depends on player interventions
            # Calculate rebuild potential
            rebuild_potential = self.player_interventions.get_rebuild_potential()
            
            if rebuild_potential >= 65:
                self.aftermath_path = AftermathPath.REBUILD_TOGETHER
                events["triggered_events"].append("path_rebuild_together_unlocked")
            elif rebuild_potential >= 35:
                self.aftermath_path = AftermathPath.STALEMATE
                events["triggered_events"].append("path_stalemate_unlocked")
            else:
                self.aftermath_path = AftermathPath.COMPLETE_SEPARATION
                events["triggered_events"].append("path_separation_unlocked")
            
            if self.current_day >= 7:
                self.transition_to_phase(CollapsePhase.POST_COLLAPSE)
                events["triggered_events"].append("aftermath_resolution_complete")
        
        return events
    
    def trigger_collapse(self) -> Dict[str, Any]:
        """Trigger the building collapse event"""
        if self.collapse_triggered:
            return {"status": "already_triggered"}
        
        self.collapse_triggered = True
        self.transition_to_phase(CollapsePhase.COLLAPSE_TRIGGER)
        
        # Immediate effects
        self.building_status.stability_percent = 0
        self.malrik_state.increase_stress(40)
        self.elenya_state.increase_stress(40)
        self.malrik_state.decrease_cooperation(50)
        
        return {
            "status": "collapsed",
            "building_destroyed": True,
            "malrik_state": self.malrik_state.stress_level,
            "elenya_state": self.elenya_state.stress_level
        }
    
    def transition_to_phase(self, new_phase: CollapsePhase) -> None:
        """Transition to a new collapse phase"""
        self.current_phase = new_phase
        self.phase_day_count[new_phase] = 0
        
        # Special handling for immediate aftermath
        if new_phase == CollapsePhase.IMMEDIATE_AFTERMATH:
            self.immediate_aftermath_started = True
        
        # Reset for aftermath resolution phase
        if new_phase == CollapsePhase.AFTERMATH_RESOLUTION:
            self.malrik_state.stress_level = 30  # Still stressed but coping
            self.elenya_state.stress_level = 30
    
    def record_player_intervention(
        self,
        npc_name: str,
        choice: str,
        effectiveness: int = 1
    ) -> Dict[str, Any]:
        """Record a player intervention and return effects"""
        self.player_interventions.log_intervention(npc_name, choice, effectiveness)
        
        if npc_name == "malrik" and effectiveness > 0:
            self.malrik_state.increase_stress(-5)  # Reduce stress
        elif npc_name == "elenya" and effectiveness > 0:
            self.elenya_state.increase_stress(-5)
        
        if choice == "advocate_reunion":
            self.malrik_state.decrease_cooperation(-10)  # Improve cooperation
            self.elenya_state.decrease_cooperation(-10)
        
        return {
            "intervention_logged": True,
            "rebuild_potential": self.player_interventions.get_rebuild_potential(),
            "aftermath_path_probability": self._calculate_path_probabilities()
        }
    
    def _calculate_path_probabilities(self) -> Dict[str, float]:
        """Calculate probabilities of each aftermath path"""
        rebuild_potential = self.player_interventions.get_rebuild_potential()
        
        # Base probabilities
        rebuild_prob = rebuild_potential / 100.0
        stalemate_prob = (50 - abs(rebuild_potential - 50)) / 100.0
        separation_prob = (100 - rebuild_potential) / 100.0
        
        # Normalize
        total = rebuild_prob + stalemate_prob + separation_prob
        
        return {
            "rebuild_together": rebuild_prob / total,
            "stalemate": stalemate_prob / total,
            "complete_separation": separation_prob / total
        }
    
    def should_offer_coren_warning(self) -> bool:
        """Determine if Coren should give the final warning"""
        return (
            self.current_phase == CollapsePhase.FINAL_WARNING
            and not self.coren_warning_given
            and self.building_status.stability_percent <= 30
        )
    
    def get_building_description(self) -> str:
        """Get narrative description of building status"""
        stability = self.building_status.stability_percent
        
        if stability >= 90:
            return "The archive building looks solid, unchanged from before."
        elif stability >= 70:
            return "You notice a fine crack in the exterior wall. Water staining is visible on one side."
        elif stability >= 50:
            return "The building shows clear signs of deterioration. A corner of the roof sags slightly. Debris collects in the courtyard."
        elif stability >= 30:
            return "The building is visibly failing. Beams are cracked. The eastern wall shows a spreading fracture."
        elif stability > 0:
            return "The building is on the verge of collapse. The structure groans ominously."
        else:
            return "The archive building lies in ruins. The eastern half is completely destroyed."
    
    def get_npc_stress_description(self, npc_name: str) -> str:
        """Get narrative description of NPC stress state"""
        state = self.malrik_state if npc_name == "malrik" else self.elenya_state
        
        if state.stress_level < 20:
            return f"{npc_name.capitalize()} seems calm and composed."
        elif state.stress_level < 40:
            return f"{npc_name.capitalize()} shows subtle signs of worry."
        elif state.stress_level < 60:
            return f"{npc_name.capitalize()} is visibly stressed and anxious."
        elif state.stress_level < 80:
            return f"{npc_name.capitalize()} is in crisis, struggling to cope."
        else:
            return f"{npc_name.capitalize()} is devastated, barely holding together."
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get complete game state for UI display and persistence"""
        return {
            "current_day": self.current_day,
            "current_phase": self.current_phase.value,
            "aftermath_path": self.aftermath_path.value,
            "building_stability": self.building_status.stability_percent,
            "malrik_stress": self.malrik_state.stress_level,
            "elenya_stress": self.elenya_state.stress_level,
            "malrik_elenya_cooperation": self.malrik_state.cooperation_level,
            "collapse_triggered": self.collapse_triggered,
            "coren_warning_given": self.coren_warning_given,
            "player_interventions": len(self.player_interventions.interventions),
            "rebuild_potential": self.player_interventions.get_rebuild_potential()
        }
