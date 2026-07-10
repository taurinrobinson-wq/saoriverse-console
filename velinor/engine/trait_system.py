"""
TONE Tracking System for Velinor: Remnants of the Tone

This module implements player TONE stance tracking and REMNANTS effect calculation.

Core principle: The game responds to PATTERNS of player choices, not individual decisions.
Players develop TONE stances through their choices across the game:
- Trust: Trusting others, seeking connection
- Observation: Watching, understanding, pattern recognition
- Narrative Presence: Assertiveness, being seen, commanding space
- Empathy: Responding to emotional states, choosing comfort

Each choice affects both player TONE and NPC REMNANTS traits via canonical mapping:
- Trust (T) → +Trust, +Resolve; -Skepticism (NPC)
- Observation (O) → +Nuance, +Memory; -Authority (NPC)
- Narrative Presence (N) → +Authority, +Resolve; -Nuance (NPC)
- Empathy (E) → +Empathy, +Need; -Resolve (NPC)

Coherence measures consistency: Do NPC perceptions match player's actual behavior?
High coherence = world trusts the player, reveals deeper dialogue
Low coherence = world is suspicious, keeps distance
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import json


# TONE Stances (canonical player stats)
TONE_TRUST = "trust"
TONE_OBSERVATION = "observation"
TONE_NARRATIVE_PRESENCE = "narrative_presence"
TONE_EMPATHY = "empathy"

ALL_TONES = [TONE_TRUST, TONE_OBSERVATION, TONE_NARRATIVE_PRESENCE, TONE_EMPATHY]

# TONE → REMNANTS Mapping (canonical effect rules)
TONE_TO_REMNANTS_MAPPING = {
    TONE_TRUST: {
        "positive": ["trust", "resolve"],
        "negative": ["skepticism"]
    },
    TONE_OBSERVATION: {
        "positive": ["nuance", "memory"],
        "negative": ["authority"]
    },
    TONE_NARRATIVE_PRESENCE: {
        "positive": ["authority", "resolve"],
        "negative": ["nuance"]
    },
    TONE_EMPATHY: {
        "positive": ["empathy", "need"],
        "negative": ["resolve"]
    }
}


@dataclass
class ToneChoice:
    """A single player choice tagged with TONE implications"""
    choice_id: str
    dialogue_option: str
    primary_tone: str  # One of: trust, observation, narrative_presence, empathy
    tone_weight: float  # How strongly this choice maps to the TONE (0.0-1.0)
    secondary_tone: Optional[str] = None
    secondary_weight: float = 0.0
    npc_name: str = ""
    scene_name: str = ""
    coherence_bonus: float = 0.0  # Bonus if consistent with recent pattern


@dataclass
class ToneProfile:
    """
    Current player TONE state with history tracking.
    
    TONE stats are on a 0-100 scale, but more importantly we track PATTERNS.
    A player with high Trust that makes skeptical choices breaks coherence.
    """
    trust: float = 50.0
    observation: float = 50.0
    narrative_presence: float = 50.0
    empathy: float = 50.0
    
    # Coherence tracks consistency between TONE and choices
    coherence: float = 100.0
    
    # History of recent choices for pattern matching
    recent_choices: deque = field(default_factory=lambda: deque(maxlen=10))
    
    # Track which NPCs see player as what
    npc_perceptions: Dict[str, str] = field(default_factory=dict)


class ToneProfiler:
    """
    Tracks player TONE through choices and pattern recognition.
    
    This is the core system that drives NPC responses and ending eligibility.
    Maintains TONE scores and calculates REMNANTS effects on NPCs.
    """
    
    def __init__(self, player_name: str = "Player"):
        self.player_name = player_name
        self.profile = ToneProfile()
        self.all_choices: List[ToneChoice] = []
    
    def record_choice(self, tone_choice: ToneChoice) -> None:
        """
        Record a player choice and update TONE profile.
        
        This doesn't just add raw values. It:
        1. Updates the TONE value
        2. Records the choice in history
        3. Calculates coherence impact
        4. Determines NPC REMNANTS effects via canonical mapping
        """
        # Record the choice
        self.all_choices.append(tone_choice)
        self.profile.recent_choices.append(tone_choice)
        
        # Update primary TONE
        tone_value = self._get_tone_value(tone_choice.primary_tone)
        new_value = tone_value + (tone_choice.tone_weight * 10.0)
        self._set_tone_value(tone_choice.primary_tone, new_value)
        
        # Update secondary TONE if present
        if tone_choice.secondary_tone:
            secondary_value = self._get_tone_value(tone_choice.secondary_tone)
            new_secondary = secondary_value + (tone_choice.secondary_weight * 10.0)
            self._set_tone_value(tone_choice.secondary_tone, new_secondary)
        
        # Update coherence
        self._update_coherence(tone_choice)
    
    def get_primary_tone(self) -> str:
        """
        Determine the player's dominant TONE based on recent pattern.
        
        Returns the TONE with highest weight in recent choices.
        Not based on current TONE scores, but on what the player HAS BEEN DOING lately.
        """
        tone_weights = {tone: 0.0 for tone in ALL_TONES}
        
        for choice in self.profile.recent_choices:
            tone_weights[choice.primary_tone] += choice.tone_weight
            if choice.secondary_tone:
                tone_weights[choice.secondary_tone] += choice.secondary_weight
        
        if not tone_weights or max(tone_weights.values()) == 0:
            return TONE_OBSERVATION  # Neutral default
        
        return max(tone_weights, key=lambda t: tone_weights[t])
    
    def get_tone_pattern(self) -> Dict[str, float]:
        """
        Return the pattern of TONEs in recent choices (last 5-10 actions).
        
        This is what NPCs actually respond to - the PATTERN not the absolute values.
        """
        if not self.profile.recent_choices:
            return {tone: 0.25 for tone in ALL_TONES}
        
        pattern = {tone: 0.0 for tone in ALL_TONES}
        choice_count = len(self.profile.recent_choices)
        
        for choice in self.profile.recent_choices:
            pattern[choice.primary_tone] += choice.tone_weight / choice_count
            if choice.secondary_tone:
                pattern[choice.secondary_tone] += (
                    choice.secondary_weight / choice_count
                )
        
        # Normalize to 0-1 range
        max_pattern = max(pattern.values()) if pattern else 1.0
        if max_pattern > 0:
            for tone in pattern:
                pattern[tone] = pattern[tone] / max_pattern
        
        return pattern
    
    def get_tone_remnants_effects(self, tone: str) -> Tuple[List[str], List[str]]:
        """
        Get the REMNANTS effects for a given TONE choice.
        
        Returns tuple of (positive_effects, negative_effects) on NPC traits.
        """
        if tone in TONE_TO_REMNANTS_MAPPING:
            mapping = TONE_TO_REMNANTS_MAPPING[tone]
            return mapping["positive"], mapping["negative"]
        return [], []
    
    def is_coherent(self) -> bool:
        """
        Is the player's behavior coherent with their TONE pattern?
        
        Example:
        - High Trust player keeps making trusting choices → Coherent
        - High Trust player suddenly makes skeptical choice → Incoherent
        
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
            # Default: describe player as their primary TONE
            return f"someone_{self.get_primary_tone()}"
        
        return self.profile.npc_perceptions[npc_name]
    
    def set_npc_perception(self, npc_name: str, perception: str) -> None:
        """Record what an NPC believes about the player"""
        self.profile.npc_perceptions[npc_name] = perception
    
    # ========== Private Methods ==========
    
    def _get_tone_value(self, tone: str) -> float:
        """Get current value of a TONE"""
        if tone == TONE_TRUST:
            return self.profile.trust
        elif tone == TONE_OBSERVATION:
            return self.profile.observation
        elif tone == TONE_NARRATIVE_PRESENCE:
            return self.profile.narrative_presence
        elif tone == TONE_EMPATHY:
            return self.profile.empathy
        return 50.0
    
    def _set_tone_value(self, tone: str, value: float) -> None:
        """Set TONE value (clamped to 0-100)"""
        value = max(0.0, min(100.0, value))
        if tone == TONE_TRUST:
            self.profile.trust = value
        elif tone == TONE_OBSERVATION:
            self.profile.observation = value
        elif tone == TONE_NARRATIVE_PRESENCE:
            self.profile.narrative_presence = value
        elif tone == TONE_EMPATHY:
            self.profile.empathy = value
    
    def _update_coherence(self, new_choice: ToneChoice) -> None:
        """
        Update coherence based on whether this choice matches recent pattern.
        
        High coherence = consistent player
        Low coherence = contradictory choices
        """
        if len(self.profile.recent_choices) < 2:
            return  # Need at least 2 choices to establish pattern
        
        # Get pattern before this choice
        pattern = self.get_tone_pattern()
        
        # Does this choice align with dominant pattern?
        primary_tone_value = pattern.get(new_choice.primary_tone, 0.0)
        
        if primary_tone_value > 0.6:
            # Strong alignment with recent pattern
            self.profile.coherence = min(
                100.0,
                self.profile.coherence + (new_choice.coherence_bonus or 2.0)
            )
        elif primary_tone_value < 0.4:
            # Contradicts recent pattern
            self.profile.coherence = max(
                0.0,
                self.profile.coherence - 5.0
            )
        # else: neutral, no change
    
    def to_dict(self) -> dict:
        """Serialize TONE profile to dict for saving"""
        return {
            "player_name": self.player_name,
            "profile": {
                "trust": self.profile.trust,
                "observation": self.profile.observation,
                "narrative_presence": self.profile.narrative_presence,
                "empathy": self.profile.empathy,
                "coherence": self.profile.coherence,
            },
            "choices_count": len(self.all_choices),
            "recent_choices": [
                {
                    "choice_id": c.choice_id,
                    "primary_tone": c.primary_tone,
                    "npc": c.npc_name,
                    "scene": c.scene_name,
                }
                for c in list(self.profile.recent_choices)
            ],
            "npc_perceptions": self.profile.npc_perceptions,
        }
    
    def get_tone_summary(self) -> Dict[str, Any]:
        """
        Return full TONE state for UI/dialogue system.
        
        This is what the dialogue engine consults when deciding NPC responses.
        """
        return {
            "player_name": self.player_name,
            "primary_tone": self.get_primary_tone(),
            "tone_pattern": self.get_tone_pattern(),
            "tone_scores": {
                "trust": self.profile.trust,
                "observation": self.profile.observation,
                "narrative_presence": self.profile.narrative_presence,
                "empathy": self.profile.empathy,
            },
            "coherence": self.profile.coherence,
            "coherence_status": self.get_coherence_status(),
            "choices_made": len(self.all_choices),
            "npc_perceptions": self.profile.npc_perceptions,
        }
