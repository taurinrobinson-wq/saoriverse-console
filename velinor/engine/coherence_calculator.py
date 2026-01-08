"""
Coherence Calculator for Velinor: Remnants of the Tone

This module measures the alignment between a player's expressed traits
and their actual behavior choices.

Coherence is the "emotional authenticity" score.
It drives:
1. NPC trust levels
2. Dialogue depth (more coherent = NPCs reveal more)
3. Ending eligibility (some endings require high coherence in specific traits)
4. World consequences (coherent players face different consequences than contradictory ones)

The core insight: A contradictory player isn't punished - the world just notices.
An empathetic skeptic is different from a confused person.
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from trait_system import TraitType, TraitChoice, TraitProfiler, TraitProfile


class CoherenceLevel(Enum):
    """Narrative categories of coherence"""
    CRYSTAL_CLEAR = 95  # Perfectly consistent
    CLEAR = 80  # Mostly consistent, rare contradictions
    MIXED = 60  # Balanced - some empathy, some skepticism
    CONFUSED = 40  # Contradictory - NPCs unsure what to expect
    CONTRADICTORY = 20  # Wildly inconsistent


@dataclass
class CoherenceReport:
    """Analysis of player coherence for current state"""
    overall_coherence: float
    level: CoherenceLevel
    primary_pattern: TraitType
    secondary_pattern: Optional[TraitType]
    pattern_strength: float  # How strong is the primary pattern (0-1)
    last_coherent_choice: Optional[TraitChoice]
    last_incoherent_choice: Optional[TraitChoice]
    contradiction_count: int
    npc_trust_level: str  # How much NPCs trust this player
    dialogue_depth: str  # How deep NPCs go with player
    
    def summary(self) -> str:
        """One-line narrative description of coherence state"""
        if self.level == CoherenceLevel.CRYSTAL_CLEAR:
            return f"A true {self.primary_pattern.value} - NPCs see exactly what they get"
        elif self.level == CoherenceLevel.CLEAR:
            return f"Mostly {self.primary_pattern.value}, occasionally {self.secondary_pattern.value if self.secondary_pattern else 'inconsistent'}"
        elif self.level == CoherenceLevel.MIXED:
            return "Genuinely balanced - holds multiple truths"
        elif self.level == CoherenceLevel.CONFUSED:
            return "Contradictory - NPCs watch carefully to understand what comes next"
        else:
            return "Wildly inconsistent - the world has stopped trying to predict you"


class CoherenceCalculator:
    """
    Calculates coherence scores and provides analysis.
    
    This is called by:
    1. NPC response engine (to determine dialogue depth)
    2. Ending calculator (to check ending eligibility)
    3. UI/diagnostics (to show player their pattern)
    """
    
    def __init__(self, profiler: TraitProfiler):
        self.profiler = profiler
    
    def calculate_coherence(self) -> float:
        """
        Overall coherence score (0-100).
        
        Based on:
        1. Consistency of recent choices
        2. Alignment between stated traits and behaviors
        3. Pattern strength (how clear is the player's style)
        """
        if len(self.profiler.all_choices) < 3:
            return 100.0  # Not enough data yet
        
        recent = list(self.profiler.profile.recent_choices)
        
        # Calculate trait consistency in recent choices
        trait_counts: Dict[TraitType, float] = {
            trait: 0.0 for trait in TraitType
        }
        
        for choice in recent:
            trait_counts[choice.primary_trait] += choice.trait_weight
            if choice.secondary_trait:
                trait_counts[choice.secondary_trait] += choice.secondary_weight
        
        # Find dominant trait
        total_weight = sum(trait_counts.values())
        if total_weight == 0:
            return 50.0
        
        max_count = max(trait_counts.values())
        
        # Calculate how much of the pattern is the dominant trait
        # If one trait is 80%+ of choices = clear pattern = high coherence
        # If traits are split evenly = confused pattern = low coherence
        dominant_percentage = max_count / total_weight if total_weight > 0 else 0
        
        # Convert to coherence score
        # 80%+ dominant = ~80+ coherence
        # 50%+ dominant = ~50 coherence  
        # 25%+ dominant = ~25 coherence
        coherence = dominant_percentage * 100.0
        
        return max(0.0, min(100.0, coherence))
    
    def get_pattern_analysis(self) -> Tuple[TraitType, Optional[TraitType], float]:
        """
        Analyze player's trait pattern.
        
        Returns:
        - Primary trait (what they do most)
        - Secondary trait (secondary tendency)
        - Pattern strength (0-1, how pure the pattern is)
        """
        if not self.profiler.profile.recent_choices:
            return TraitType.INTEGRATION, None, 0.5
        
        trait_counts: Dict[TraitType, float] = {
            trait: 0.0 for trait in TraitType
        }
        
        for choice in self.profiler.profile.recent_choices:
            trait_counts[choice.primary_trait] += choice.trait_weight
            if choice.secondary_trait:
                trait_counts[choice.secondary_trait] += choice.secondary_weight
        
        sorted_traits = sorted(
            trait_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        primary = sorted_traits[0][0]
        primary_strength = sorted_traits[0][1]
        secondary = sorted_traits[1][0] if len(sorted_traits) > 1 else None
        
        total_strength = sum(count for _, count in sorted_traits)
        if total_strength == 0:
            return TraitType.INTEGRATION, None, 0.5
        
        pattern_purity = primary_strength / total_strength
        
        return primary, secondary, pattern_purity
    
    def get_coherence_report(self) -> CoherenceReport:
        """
        Detailed analysis of player coherence state.
        
        This is what the dialogue system consults to decide NPC trust/depth.
        """
        # Recalculate coherence based on current pattern (not stored value)
        coherence = self.calculate_coherence()
        
        # Determine level
        if coherence >= 95:
            level = CoherenceLevel.CRYSTAL_CLEAR
        elif coherence >= 80:
            level = CoherenceLevel.CLEAR
        elif coherence >= 60:
            level = CoherenceLevel.MIXED
        elif coherence >= 40:
            level = CoherenceLevel.CONFUSED
        else:
            level = CoherenceLevel.CONTRADICTORY
        
        # Get pattern
        primary, secondary, strength = self.get_pattern_analysis()
        
        # Find recent contradictions
        contradictions = self._find_contradictions()
        
        # Find most recent coherent and incoherent choices
        last_coherent = None
        last_incoherent = None
        for choice in reversed(list(self.profiler.profile.recent_choices)):
            if last_coherent is None:
                if choice.primary_trait == primary:
                    last_coherent = choice
            if last_incoherent is None:
                if choice.primary_trait != primary:
                    last_incoherent = choice
        
        # Determine NPC trust based on coherence
        if coherence >= 80:
            trust = "high"
        elif coherence >= 60:
            trust = "moderate"
        elif coherence >= 40:
            trust = "low"
        else:
            trust = "suspicious"
        
        # Determine dialogue depth
        if coherence >= 85:
            depth = "intimate"  # NPCs reveal deep motivations
        elif coherence >= 70:
            depth = "personal"  # NPCs share backstory
        elif coherence >= 50:
            depth = "social"  # Normal conversation
        elif coherence >= 30:
            depth = "guarded"  # NPCs hold back
        else:
            depth = "minimal"  # NPCs say almost nothing
        
        return CoherenceReport(
            overall_coherence=coherence,
            level=level,
            primary_pattern=primary,
            secondary_pattern=secondary,
            pattern_strength=strength,
            last_coherent_choice=last_coherent,
            last_incoherent_choice=last_incoherent,
            contradiction_count=contradictions,
            npc_trust_level=trust,
            dialogue_depth=depth,
        )
    
    def would_be_coherent(self, next_choice: TraitChoice) -> bool:
        """
        Preview: Is this next choice coherent with the current pattern?
        
        Useful for dialogue system previewing NPC reactions before committing.
        """
        primary, _, _ = self.get_pattern_analysis()
        return next_choice.primary_trait == primary
    
    def get_npc_perception_of_player(self, npc_name: str) -> Dict[str, any]:
        """
        How does this specific NPC perceive the player based on coherence?
        
        Different NPCs with different personalities perceive the player differently.
        An empathetic NPC might respect a consistent skeptic.
        A skeptical NPC might be suspicious of an inconsistent person.
        """
        report = self.get_coherence_report()
        
        return {
            "npc": npc_name,
            "perceives_as": report.primary_pattern.value,
            "coherence_level": report.level.name,
            "trust": report.npc_trust_level,
            "dialogue_depth": report.dialogue_depth,
            "see_contradiction": report.contradiction_count > 3,
        }
    
    def get_coherence_narrative(self) -> str:
        """
        Narrative description of player's coherence for dialogue/UI.
        
        Example outputs:
        - "You've been consistently empathetic"
        - "Your choices contradict each other"
        - "You hold multiple truths in balance"
        """
        report = self.get_coherence_report()
        
        if report.level == CoherenceLevel.CRYSTAL_CLEAR:
            return f"The world sees you as a true {report.primary_pattern.value}."
        
        elif report.level == CoherenceLevel.CLEAR:
            if report.secondary_pattern:
                return f"You've been mostly {report.primary_pattern.value}, with hints of {report.secondary_pattern.value}."
            else:
                return f"Your {report.primary_pattern.value} commitment is clear to everyone."
        
        elif report.level == CoherenceLevel.MIXED:
            return "You hold empathy and skepticism in genuine balance."
        
        elif report.level == CoherenceLevel.CONFUSED:
            return f"Your contradictions are becoming hard to ignore. NPCs watch you carefully, trying to understand what comes next."
        
        else:
            return "You've been so inconsistent that the world has stopped trying to predict you."
    
    # ========== Private Methods ==========
    
    def _find_contradictions(self) -> int:
        """Count how many recent choices contradict the primary pattern"""
        if not self.profiler.profile.recent_choices:
            return 0
        
        primary, _, _ = self.get_pattern_analysis()
        
        count = 0
        for choice in self.profiler.profile.recent_choices:
            if choice.primary_trait != primary:
                count += 1
        
        return count
    
    def _calculate_pattern_stability(self) -> float:
        """
        Stability of current pattern (0-1).
        
        If player keeps flip-flopping traits, stability is low.
        If player has consistent pattern, stability is high.
        """
        if len(self.profiler.all_choices) < 5:
            return 0.5
        
        # Look at last 5 vs previous 5 choices
        recent_5 = list(self.profiler.profile.recent_choices)[-5:]
        
        if len(self.profiler.all_choices) < 10:
            previous_5 = list(self.profiler.profile.recent_choices)[:5]
        else:
            previous_5 = list(self.profiler.all_choices)[-10:-5]
        
        # Count dominant traits in each group
        recent_primary = max(
            (choice.primary_trait for choice in recent_5),
            key=lambda t: sum(
                1 for c in recent_5 if c.primary_trait == t
            )
        )
        
        previous_primary = max(
            (choice.primary_trait for choice in previous_5),
            key=lambda t: sum(
                1 for c in previous_5 if c.primary_trait == t
            )
        )
        
        # Same primary trait = stable (0.8-1.0)
        # Different = unstable (0.2-0.5)
        if recent_primary == previous_primary:
            return 0.9
        else:
            return 0.3


def calculate_dialogue_depth(profiler: TraitProfiler) -> str:
    """
    Quick helper: Get dialogue depth directly.
    
    Used by dialogue system to know how deep NPCs will go.
    """
    calculator = CoherenceCalculator(profiler)
    report = calculator.get_coherence_report()
    return report.dialogue_depth


def should_reveal_secret(profiler: TraitProfiler, secret_type: str) -> bool:
    """
    Decide if NPC should reveal this secret based on player coherence.
    
    Secrets require minimum coherence levels:
    - "personal_fear": coherence >= 70 (need trust)
    - "hidden_agenda": coherence >= 60 (need some trust)
    - "past_mistake": coherence >= 50 (moderate trust)
    - "plan": coherence >= 40 (even guarded people might plan with you)
    """
    calculator = CoherenceCalculator(profiler)
    coherence = calculator.profiler.profile.coherence
    
    thresholds = {
        "personal_fear": 70,
        "hidden_agenda": 60,
        "past_mistake": 50,
        "plan": 40,
    }
    
    required = thresholds.get(secret_type, 50)
    return coherence >= required
