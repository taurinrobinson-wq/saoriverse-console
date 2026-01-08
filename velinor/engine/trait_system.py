"""
Trait System for Velinor: Remnants of the Tone

This module implements the emotional OS trait tracking and pattern recognition system.

Core principle: The game responds to PATTERNS of player choices, not individual decisions.
Players have four foundational traits that form through their choices across the game.

Traits:
- Empathy (0-100): Responds to emotional states, chooses comfort over judgment
- Skepticism (0-100): Questions assumptions, holds others accountable, maintains critical distance
- Integration (0-100): Holds multiple truths simultaneously, advocates for synthesis
- Awareness (0-100): Sees subtext, notices body language, recognizes patterns

Each trait interaction creates a "weighted history" of the last 5-10 choices.
NPC behavior responds to the PATTERN (coherent empathist? contradictory skeptic? synthesis advocate?)
not to individual choices.

Coherence measures the consistency between player's declared traits and actual behavior.
High coherence = world trusts the player, reveals deeper dialogue
Low coherence = world is suspicious, keeps distance
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from collections import deque
import json


class TraitType(Enum):
    """Four foundational traits in Velinor's emotional OS"""
    EMPATHY = "empathy"
    SKEPTICISM = "skepticism"
    INTEGRATION = "integration"
    AWARENESS = "awareness"


@dataclass
class TraitChoice:
    """A single player choice tagged with trait implications"""
    choice_id: str
    dialogue_option: str
    primary_trait: TraitType
    trait_weight: float  # How strongly this choice maps to the trait (0.0-1.0)
    secondary_trait: Optional[TraitType] = None
    secondary_weight: float = 0.0
    npc_name: str = ""
    scene_name: str = ""
    coherence_bonus: float = 0.0  # Bonus if consistent with recent pattern


@dataclass
class TraitProfile:
    """
    Current player trait state with history tracking.
    
    Traits are on a 0-100 scale, but more importantly we track PATTERNS.
    A player with high Empathy that makes skeptical choices breaks coherence.
    """
    empathy: float = 50.0
    skepticism: float = 50.0
    integration: float = 50.0
    awareness: float = 50.0
    
    # Coherence tracks consistency between traits and choices
    coherence: float = 100.0
    
    # History of recent choices for pattern matching
    recent_choices: deque = field(default_factory=lambda: deque(maxlen=10))
    
    # For tracking secondary traits that emerge during gameplay
    secondary_traits: Dict[str, float] = field(default_factory=dict)
    
    # Track which NPCs see player as what
    npc_perceptions: Dict[str, str] = field(default_factory=dict)


class TraitProfiler:
    """
    Tracks player traits through choices and pattern recognition.
    
    This is the core system that drives NPC responses and ending eligibility.
    """
    
    def __init__(self, player_name: str = "Player"):
        self.player_name = player_name
        self.profile = TraitProfile()
        self.all_choices: List[TraitChoice] = []
    
    def record_choice(self, trait_choice: TraitChoice) -> None:
        """
        Record a player choice and update trait profile.
        
        This doesn't just add raw values. It:
        1. Updates the trait value
        2. Records the choice in history
        3. Calculates coherence impact
        4. Potentially shifts NPC perceptions
        """
        # Record the choice
        self.all_choices.append(trait_choice)
        self.profile.recent_choices.append(trait_choice)
        
        # Update primary trait
        trait_value = self._get_trait_value(trait_choice.primary_trait)
        new_value = trait_value + (trait_choice.trait_weight * 10.0)
        self._set_trait_value(trait_choice.primary_trait, new_value)
        
        # Update secondary trait if present
        if trait_choice.secondary_trait:
            secondary_value = self._get_trait_value(trait_choice.secondary_trait)
            new_secondary = secondary_value + (trait_choice.secondary_weight * 10.0)
            self._set_trait_value(trait_choice.secondary_trait, new_secondary)
        
        # Update coherence
        self._update_coherence(trait_choice)
    
    def get_primary_trait(self) -> TraitType:
        """
        Determine the player's dominant trait based on recent pattern.
        
        Returns the trait with highest value among recent choices.
        Not based on current trait scores, but on what the player HAS BEEN DOING lately.
        """
        trait_counts = {trait: 0.0 for trait in TraitType}
        
        for choice in self.profile.recent_choices:
            trait_counts[choice.primary_trait] += choice.trait_weight
            if choice.secondary_trait:
                trait_counts[choice.secondary_trait] += choice.secondary_weight
        
        if not trait_counts or max(trait_counts.values()) == 0:
            return TraitType.INTEGRATION  # Neutral default
        
        return max(trait_counts, key=trait_counts.get)
    
    def get_trait_pattern(self) -> Dict[str, float]:
        """
        Return the pattern of traits in recent choices (last 5-10 actions).
        
        This is what NPCs actually respond to - the PATTERN not the absolute values.
        """
        if not self.profile.recent_choices:
            return {trait.value: 0.5 for trait in TraitType}
        
        pattern = {trait.value: 0.0 for trait in TraitType}
        choice_count = len(self.profile.recent_choices)
        
        for choice in self.profile.recent_choices:
            pattern[choice.primary_trait.value] += choice.trait_weight / choice_count
            if choice.secondary_trait:
                pattern[choice.secondary_trait.value] += (
                    choice.secondary_weight / choice_count
                )
        
        # Normalize to 0-1 range
        max_pattern = max(pattern.values()) if pattern else 1.0
        if max_pattern > 0:
            for trait in pattern:
                pattern[trait] = pattern[trait] / max_pattern
        
        return pattern
    
    def is_coherent(self) -> bool:
        """
        Is the player's behavior coherent with their pattern?
        
        Example:
        - High empathy player keeps making empathetic choices → Coherent
        - High skepticism player keeps making skeptical choices → Coherent
        - High empathy player suddenly makes brutal skeptical choice → Incoherent
        
        Incoherence isn't bad - it's just noticed by the world.
        """
        return self.profile.coherence > 70.0
    
    def get_coherence_status(self) -> str:
        """Return narrative description of coherence level"""
        if self.profile.coherence >= 95:
            return "crystal_clear"  # NPCs see player as very consistent
        elif self.profile.coherence >= 80:
            return "clear"
        elif self.profile.coherence >= 60:
            return "mixed"  # Some confusion
        elif self.profile.coherence >= 40:
            return "confused"  # Contradictory
        else:
            return "contradictory"  # Wildly inconsistent
    
    def get_npc_perception(self, npc_name: str) -> str:
        """
        What does this specific NPC think the player is?
        
        May differ from overall pattern based on NPC's own biases and what they've witnessed.
        """
        if npc_name not in self.profile.npc_perceptions:
            # Default: describe player as their primary trait
            return f"someone_{self.get_primary_trait().value}"
        
        return self.profile.npc_perceptions[npc_name]
    
    def get_trait_summary(self) -> Dict[str, any]:
        """
        Return full trait state for UI/dialogue system.
        
        This is what the dialogue engine consults when deciding NPC responses.
        """
        return {
            "player_name": self.player_name,
            "primary_trait": self.get_primary_trait().value,
            "trait_pattern": self.get_trait_pattern(),
            "trait_scores": {
                "empathy": self.profile.empathy,
                "skepticism": self.profile.skepticism,
                "integration": self.profile.integration,
                "awareness": self.profile.awareness,
            },
            "coherence": self.profile.coherence,
            "coherence_status": self.get_coherence_status(),
            "choices_made": len(self.all_choices),
            "npc_perceptions": self.profile.npc_perceptions,
        }
    
    # ========== Private Methods ==========
    
    def _get_trait_value(self, trait: TraitType) -> float:
        """Get current value of a trait"""
        if trait == TraitType.EMPATHY:
            return self.profile.empathy
        elif trait == TraitType.SKEPTICISM:
            return self.profile.skepticism
        elif trait == TraitType.INTEGRATION:
            return self.profile.integration
        elif trait == TraitType.AWARENESS:
            return self.profile.awareness
    
    def _set_trait_value(self, trait: TraitType, value: float) -> None:
        """Set trait value (clamped to 0-100)"""
        value = max(0.0, min(100.0, value))
        if trait == TraitType.EMPATHY:
            self.profile.empathy = value
        elif trait == TraitType.SKEPTICISM:
            self.profile.skepticism = value
        elif trait == TraitType.INTEGRATION:
            self.profile.integration = value
        elif trait == TraitType.AWARENESS:
            self.profile.awareness = value
    
    def _update_coherence(self, new_choice: TraitChoice) -> None:
        """
        Update coherence based on whether this choice matches recent pattern.
        
        High coherence = consistent player
        Low coherence = contradictory choices
        """
        if len(self.profile.recent_choices) < 2:
            return  # Need at least 2 choices to establish pattern
        
        # Get pattern before this choice
        pattern = self.get_trait_pattern()
        
        # Does this choice align with dominant pattern?
        primary_trait_value = pattern.get(new_choice.primary_trait.value, 0.0)
        
        if primary_trait_value > 0.6:
            # Strong alignment with recent pattern
            self.profile.coherence = min(
                100.0,
                self.profile.coherence + (new_choice.coherence_bonus or 2.0)
            )
        elif primary_trait_value < 0.4:
            # Contradicts recent pattern
            self.profile.coherence = max(
                0.0,
                self.profile.coherence - 5.0
            )
        # else: neutral, no change
    
    def to_dict(self) -> dict:
        """Serialize trait profile to dict for saving"""
        return {
            "player_name": self.player_name,
            "profile": {
                "empathy": self.profile.empathy,
                "skepticism": self.profile.skepticism,
                "integration": self.profile.integration,
                "awareness": self.profile.awareness,
                "coherence": self.profile.coherence,
            },
            "choices_count": len(self.all_choices),
            "recent_choices": [
                {
                    "choice_id": c.choice_id,
                    "primary_trait": c.primary_trait.value,
                    "npc": c.npc_name,
                    "scene": c.scene_name,
                }
                for c in list(self.profile.recent_choices)
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TraitProfiler":
        """Deserialize trait profile from dict (for loading)"""
        profiler = cls(player_name=data.get("player_name", "Player"))
        profile_data = data.get("profile", {})
        profiler.profile.empathy = profile_data.get("empathy", 50.0)
        profiler.profile.skepticism = profile_data.get("skepticism", 50.0)
        profiler.profile.integration = profile_data.get("integration", 50.0)
        profiler.profile.awareness = profile_data.get("awareness", 50.0)
        profiler.profile.coherence = profile_data.get("coherence", 100.0)
        return profiler


# ========== Trait Choice Presets ==========
# Common trait choices for dialogue options throughout the game

EMPATHY_CHOICE = TraitChoice(
    choice_id="",  # Set by caller
    dialogue_option="",  # Set by caller
    primary_trait=TraitType.EMPATHY,
    trait_weight=0.3,
    coherence_bonus=1.0,
)

SKEPTICISM_CHOICE = TraitChoice(
    choice_id="",
    dialogue_option="",
    primary_trait=TraitType.SKEPTICISM,
    trait_weight=0.3,
    coherence_bonus=1.0,
)

INTEGRATION_CHOICE = TraitChoice(
    choice_id="",
    dialogue_option="",
    primary_trait=TraitType.INTEGRATION,
    trait_weight=0.3,
    secondary_trait=TraitType.AWARENESS,
    secondary_weight=0.15,
    coherence_bonus=2.0,  # Synthesis is harder, more bonus when consistent
)

AWARENESS_CHOICE = TraitChoice(
    choice_id="",
    dialogue_option="",
    primary_trait=TraitType.AWARENESS,
    trait_weight=0.25,
    coherence_bonus=1.0,
)
