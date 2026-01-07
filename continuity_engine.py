"""
Continuity Engine

Tracks emotional and relational progression across turns.
Ensures the system doesn't treat each message in isolation.

Continuity State Tracks:
- Emotional stance progression (arc across messages)
- Disclosure pace progression (how user evolves their pacing)
- Trust progression (increasing vulnerability markers)
- Identity signals (accumulating named individuals, durations)
- Contradictions (carried forward, refined)
- Pacing needs (evolving requirements)
- Agency work (tracking reclamation efforts)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime


@dataclass
class TurnState:
    """State of emotional/relational progression at a single turn"""
    message_index: int
    timestamp: datetime
    
    # Stance progression
    emotional_stance: str
    stance_progression: List[str] = field(default_factory=list)
    
    # Pacing progression
    disclosure_pace: str = ""
    pace_progression: List[str] = field(default_factory=list)
    
    # Trust development
    trust_level: float = 0.5  # 0.0-1.0
    trust_increase: bool = False
    
    # Identity signals accumulated
    named_individuals: List[str] = field(default_factory=list)
    identity_markers: Set[str] = field(default_factory=set)
    
    # Contradictions being held
    active_contradictions: List[str] = field(default_factory=list)
    
    # Pacing needs
    needs_pace_slowing: bool = False
    ready_to_go_deeper: bool = False
    
    # Agency work
    agency_loss_indicators: List[str] = field(default_factory=list)
    agency_reclamation_signals: List[str] = field(default_factory=list)
    
    # Response quality delivered
    safety_level_delivered: float = 0.0
    attunement_level_delivered: float = 0.0
    
    # Metadata
    session_notes: str = ""


@dataclass
class ConversationContinuity:
    """Full continuity state across entire conversation"""
    
    # Basic tracking
    turn_count: int = 0
    turns: List[TurnState] = field(default_factory=list)
    
    # Stance arc
    emotional_stance_arc: List[str] = field(default_factory=list)
    
    # Pacing arc
    disclosure_pace_arc: List[str] = field(default_factory=list)
    
    # Trust progression
    trust_arc: List[float] = field(default_factory=list)
    
    # Identity accumulation
    all_named_individuals: Set[str] = field(default_factory=set)
    all_duration_markers: Set[str] = field(default_factory=set)
    all_identity_signals: Set[str] = field(default_factory=set)
    
    # Contradiction development
    contradiction_history: List[Dict] = field(default_factory=list)
    active_contradictions: List[str] = field(default_factory=list)
    
    # Agency tracking
    agency_loss_trajectory: List[str] = field(default_factory=list)
    agency_reclamation_trajectory: List[str] = field(default_factory=list)
    
    # Quality delivered
    safety_trend: List[float] = field(default_factory=list)
    attunement_trend: List[float] = field(default_factory=list)
    
    # Pacing needs evolution
    pace_slowing_needed_at: List[int] = field(default_factory=list)
    depth_ready_at: List[int] = field(default_factory=list)
    
    # Session metadata
    session_start: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


class ContinuityEngine:
    """
    Manages conversation continuity state.
    
    Usage:
        engine = ContinuityEngine()
        
        # After parsing message 1
        engine.update_from_semantic_layer(layer1, 0)
        
        # After generating response 1
        engine.record_response_quality(safety=0.4, attunement=0.3)
        
        # After parsing message 2
        engine.update_from_semantic_layer(layer2, 1)
        
        # Check continuity awareness
        contradictions = engine.get_active_contradictions()
        trust_level = engine.get_trust_level()
    """

    def __init__(self):
        self.continuity = ConversationContinuity()

    def update_from_semantic_layer(self, semantic_layer, message_index: int) -> None:
        """
        Update continuity state from semantic layer output.
        
        Called after each message is parsed.
        """
        
        turn = TurnState(
            message_index=message_index,
            timestamp=datetime.now(),
            emotional_stance=semantic_layer.emotional_stance.value if hasattr(
                semantic_layer.emotional_stance, 'value'
            ) else str(semantic_layer.emotional_stance),
        )
        
        # Stance progression
        if self.continuity.emotional_stance_arc:
            turn.stance_progression = self.continuity.emotional_stance_arc.copy()
        turn.stance_progression.append(turn.emotional_stance)
        self.continuity.emotional_stance_arc.append(turn.emotional_stance)
        
        # Pacing progression
        if hasattr(semantic_layer, 'disclosure_pace'):
            turn.disclosure_pace = semantic_layer.disclosure_pace.value if hasattr(
                semantic_layer.disclosure_pace, 'value'
            ) else str(semantic_layer.disclosure_pace)
            
            if self.continuity.disclosure_pace_arc:
                turn.pace_progression = self.continuity.disclosure_pace_arc.copy()
            turn.pace_progression.append(turn.disclosure_pace)
            self.continuity.disclosure_pace_arc.append(turn.disclosure_pace)
        
        # Trust progression
        if hasattr(semantic_layer, 'trust_increase'):
            turn.trust_increase = semantic_layer.trust_increase
            
            # Update trust level
            if turn.trust_increase:
                # Increase trust by 0.15 per increase signal
                turn.trust_level = min(1.0, self.continuity.trust_arc[-1] + 0.15 if self.continuity.trust_arc else 0.65)
            else:
                turn.trust_level = self.continuity.trust_arc[-1] if self.continuity.trust_arc else 0.5
            
            self.continuity.trust_arc.append(turn.trust_level)
        
        # Identity signals
        if hasattr(semantic_layer, 'identity_signals'):
            if hasattr(semantic_layer.identity_signals, 'explicitly_named'):
                turn.named_individuals = semantic_layer.identity_signals.explicitly_named.copy()
                self.continuity.all_named_individuals.update(turn.named_individuals)
            
            # Collect all identity markers
            identity_attrs = [
                'explicitly_named', 'relational_labels_used', 'duration_references',
                'role_changes', 'complexity_markers'
            ]
            for attr in identity_attrs:
                if hasattr(semantic_layer.identity_signals, attr):
                    values = getattr(semantic_layer.identity_signals, attr)
                    if values:
                        turn.identity_markers.update(values)
                        self.continuity.all_identity_signals.update(values)
        
        # Contradictions
        if hasattr(semantic_layer, 'emotional_contradictions'):
            if semantic_layer.emotional_contradictions:
                for contradiction in semantic_layer.emotional_contradictions:
                    contradiction_str = f"{contradiction.surface_feeling} vs {contradiction.underlying_feeling}"
                    turn.active_contradictions.append(contradiction_str)
                    self.continuity.active_contradictions.append(contradiction_str)
                    
                    # Track contradiction history
                    self.continuity.contradiction_history.append({
                        "message_index": message_index,
                        "surface": contradiction.surface_feeling,
                        "underlying": contradiction.underlying_feeling,
                        "tension": contradiction.tension_level,
                    })
        
        # Pacing needs
        if hasattr(semantic_layer, 'meta_properties'):
            if hasattr(semantic_layer.meta_properties, 'needs_pace_slowing'):
                turn.needs_pace_slowing = semantic_layer.meta_properties.needs_pace_slowing
                if turn.needs_pace_slowing:
                    self.continuity.pace_slowing_needed_at.append(message_index)
            
            if hasattr(semantic_layer.meta_properties, 'ready_to_go_deeper'):
                turn.ready_to_go_deeper = semantic_layer.meta_properties.ready_to_go_deeper
                if turn.ready_to_go_deeper:
                    self.continuity.depth_ready_at.append(message_index)
        
        # Agency tracking
        if hasattr(semantic_layer, 'power_dynamics'):
            for dynamic in semantic_layer.power_dynamics:
                dynamic_str = dynamic.value if hasattr(dynamic, 'value') else str(dynamic)
                if 'agency_loss' in dynamic_str:
                    turn.agency_loss_indicators.append(dynamic_str)
                    self.continuity.agency_loss_trajectory.append(dynamic_str)
                if 'reclaim' in dynamic_str.lower():
                    turn.agency_reclamation_signals.append(dynamic_str)
                    self.continuity.agency_reclamation_trajectory.append(dynamic_str)
        
        # Record turn
        self.continuity.turns.append(turn)
        self.continuity.turn_count += 1
        self.continuity.last_updated = datetime.now()

    def record_response_quality(
        self,
        safety_level: float,
        attunement_level: float,
    ) -> None:
        """
        Record quality of response delivered.
        
        Called after response is generated.
        """
        if self.continuity.turns:
            last_turn = self.continuity.turns[-1]
            last_turn.safety_level_delivered = safety_level
            last_turn.attunement_level_delivered = attunement_level
            
            self.continuity.safety_trend.append(safety_level)
            self.continuity.attunement_trend.append(attunement_level)

    def get_active_contradictions(self) -> List[str]:
        """Get contradictions user is currently holding"""
        return self.continuity.active_contradictions.copy()

    def get_trust_level(self) -> float:
        """Get current trust level (0.0-1.0)"""
        if self.continuity.trust_arc:
            return self.continuity.trust_arc[-1]
        return 0.5

    def get_stance_arc(self) -> List[str]:
        """Get emotional stance progression"""
        return self.continuity.emotional_stance_arc.copy()

    def get_pacing_arc(self) -> List[str]:
        """Get disclosure pacing progression"""
        return self.continuity.disclosure_pace_arc.copy()

    def get_identity_summary(self) -> Dict:
        """Get summary of accumulated identity signals"""
        return {
            "named_individuals": list(self.continuity.all_named_individuals),
            "duration_markers": list(self.continuity.all_duration_markers),
            "total_identity_signals": len(self.continuity.all_identity_signals),
        }

    def get_pacing_needs(self) -> Dict:
        """Get current pacing needs"""
        return {
            "needs_slowing": len(self.continuity.pace_slowing_needed_at) > 0,
            "ready_to_go_deeper": len(self.continuity.depth_ready_at) > 0,
            "slowing_at_messages": self.continuity.pace_slowing_needed_at.copy(),
            "depth_ready_at_messages": self.continuity.depth_ready_at.copy(),
        }

    def get_agency_trajectory(self) -> Dict:
        """Get agency loss and reclamation trajectory"""
        return {
            "agency_loss_indicators": self.continuity.agency_loss_trajectory.copy(),
            "reclamation_signals": self.continuity.agency_reclamation_trajectory.copy(),
            "trajectory_type": self._identify_agency_trajectory(),
        }

    def _identify_agency_trajectory(self) -> str:
        """Identify pattern of agency work"""
        loss_count = len(self.continuity.agency_loss_trajectory)
        reclaim_count = len(self.continuity.agency_reclamation_trajectory)
        
        if loss_count > 0 and reclaim_count == 0:
            return "loss_accumulating"
        elif loss_count > 0 and reclaim_count > 0:
            return "loss_then_reclamation"
        elif reclaim_count > loss_count:
            return "actively_reclaiming"
        else:
            return "neutral"

    def get_quality_trend(self) -> Dict:
        """Get trend of response quality delivered"""
        if not self.continuity.safety_trend:
            return {
                "safety_trend": [],
                "attunement_trend": [],
                "average_safety": 0.0,
                "average_attunement": 0.0,
            }
        
        avg_safety = sum(self.continuity.safety_trend) / len(self.continuity.safety_trend)
        avg_attunement = sum(self.continuity.attunement_trend) / len(
            self.continuity.attunement_trend
        )
        
        return {
            "safety_trend": self.continuity.safety_trend.copy(),
            "attunement_trend": self.continuity.attunement_trend.copy(),
            "average_safety": avg_safety,
            "average_attunement": avg_attunement,
        }

    def get_conversation_summary(self) -> Dict:
        """Get complete continuity summary"""
        return {
            "turn_count": self.continuity.turn_count,
            "stance_arc": self.get_stance_arc(),
            "pacing_arc": self.get_pacing_arc(),
            "trust_progression": self.continuity.trust_arc.copy(),
            "active_contradictions": self.get_active_contradictions(),
            "identity_summary": self.get_identity_summary(),
            "pacing_needs": self.get_pacing_needs(),
            "agency_trajectory": self.get_agency_trajectory(),
            "quality_trend": self.get_quality_trend(),
            "session_duration_seconds": (
                self.continuity.last_updated - self.continuity.session_start
            ).total_seconds(),
        }

    def validate_continuity_awareness(self) -> Dict[str, bool]:
        """
        Validate that system is aware of continuity elements.
        
        Returns dict of continuity checks.
        """
        
        return {
            "tracks_stance_progression": len(self.continuity.emotional_stance_arc) > 0,
            "tracks_pacing_progression": len(self.continuity.disclosure_pace_arc) > 0,
            "tracks_trust_development": len(self.continuity.trust_arc) > 1,
            "tracks_contradictions": len(self.continuity.active_contradictions) > 0,
            "tracks_identity_signals": len(self.continuity.all_identity_signals) > 0,
            "tracks_agency_work": (
                len(self.continuity.agency_loss_trajectory) > 0 or
                len(self.continuity.agency_reclamation_trajectory) > 0
            ),
            "tracks_response_quality": len(self.continuity.safety_trend) > 0,
            "all_continuity_tracked": all([
                len(self.continuity.emotional_stance_arc) > 0,
                len(self.continuity.disclosure_pace_arc) > 0,
                len(self.continuity.trust_arc) > 1,
                len(self.continuity.active_contradictions) > 0,
            ]),
        }
