"""
Phase 2.5: Context-Aware Glyph Selector
Selects glyphs based on conversation context, emotional trajectory, and multi-modal signals.
Provides most relevant glyph for specific situations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ConversationContext(Enum):
    """Types of conversation context."""
    OPENING = "opening"  # Starting conversation
    EXPLORATION = "exploration"  # Diving into topic
    CHALLENGE = "challenge"  # Addressing difficult topic
    BREAKTHROUGH = "breakthrough"  # Moment of insight
    INTEGRATION = "integration"  # Wrapping up, synthesis
    CLOSURE = "closure"  # Ending conversation


@dataclass
class ConversationState:
    """Current state of conversation."""
    context: ConversationContext
    turn_number: int
    emotional_trajectory: str  # "ascending", "descending", "stable", "volatile"
    intensity_level: float  # 0.0-1.0
    user_energy: float  # 0.0-1.0 (engagement level)
    previous_glyph: Optional[str] = None
    repetition_count: int = 0  # How many times this glyph used recently


@dataclass
class SelectionCriteria:
    """Criteria for glyph selection."""
    avoid_repetition: bool = True
    max_repetitions: int = 3
    consider_intensity: bool = True
    consider_energy: bool = True
    prefer_novelty: bool = False
    allow_failure_recovery: bool = True  # Allow trying similar glyphs if one failed


class ContextAwareSelector:
    """Selects glyphs based on conversation context and state."""

    def __init__(self):
        """Initialize context-aware selector."""
        self.context_glyph_map: Dict[str, List[str]] = {
            "opening": ["welcome", "presence", "attunement"],
            "exploration": ["curiosity", "depth", "clarity"],
            "challenge": ["courage", "strength", "witness"],
            "breakthrough": ["emergence", "radiance", "transformation"],
            "integration": ["harmony", "wholeness", "resonance"],
            "closure": ["gratitude", "blessing", "connection"],
        }

        self.intensity_responsive_glyphs = {
            "low": ["gentleness", "softness", "ease"],
            "medium": ["warmth", "engagement", "presence"],
            "high": ["intensity", "power", "luminescence"],
        }

        self.trajectory_responsive_glyphs = {
            "ascending": ["emergence", "elevation", "radiance"],
            "descending": ["grounding", "depth", "rest"],
            "stable": ["balance", "continuity", "presence"],
            "volatile": ["witness", "holding", "compassion"],
        }

    def select(
        self,
        conversation_state: ConversationState,
        available_glyphs: List[str],
        criteria: Optional[SelectionCriteria] = None,
        effectiveness_scores: Optional[Dict[str, float]] = None,
    ) -> Tuple[Optional[str], Dict]:
        """
        Select best glyph for current conversation state.

        Returns:
            (selected_glyph, metadata)
        """
        if criteria is None:
            criteria = SelectionCriteria()

        metadata = {
            "context": conversation_state.context.value,
            "selection_reasoning": [],
            "reasoning": [],
            "candidates": [],
            "rejected": [],
            "selected": None,
        }

        # Get candidate glyphs from context
        context_candidates = self._get_context_candidates(
            conversation_state,
            available_glyphs
        )
        metadata["candidates"].extend(context_candidates)

        # Filter by repetition if needed
        if criteria.avoid_repetition and conversation_state.previous_glyph:
            filtered = self._filter_by_repetition(
                context_candidates,
                conversation_state.previous_glyph,
                conversation_state.repetition_count,
                criteria.max_repetitions
            )
            rejected = [g for g in context_candidates if g not in filtered]
            metadata["rejected"].extend(rejected)
            context_candidates = filtered

        # Score by intensity if applicable
        if criteria.consider_intensity:
            scored_candidates = self._score_by_intensity(
                context_candidates,
                conversation_state.intensity_level,
                effectiveness_scores
            )
            metadata["reasoning"].append(
                f"Scored for intensity level {conversation_state.intensity_level:.1f}"
            )
            context_candidates = [g[0] for g in scored_candidates]

        # Score by trajectory if applicable
        if criteria.consider_energy:
            scored_candidates = self._score_by_trajectory(
                context_candidates,
                conversation_state.emotional_trajectory,
                effectiveness_scores
            )
            metadata["reasoning"].append(
                f"Scored for {conversation_state.emotional_trajectory} trajectory"
            )
            context_candidates = [g[0] for g in scored_candidates]

        if not context_candidates:
            metadata["reasoning"].append(
                "No candidates after filtering, using fallback")
            selected = self._select_fallback(
                conversation_state,
                available_glyphs,
                effectiveness_scores
            )
        else:
            selected = context_candidates[0][0] if isinstance(
                context_candidates[0], tuple) else context_candidates[0]

        metadata["selected"] = selected
        return selected, metadata

    def _get_context_candidates(
        self,
        state: ConversationState,
        available_glyphs: List[str]
    ) -> List[str]:
        """Get glyph candidates for conversation context."""
        context_key = state.context.value
        recommended = self.context_glyph_map.get(context_key, [])

        # Filter to only available glyphs
        candidates = [g for g in recommended if g in available_glyphs]

        # If no match, use all available as candidates
        if not candidates:
            candidates = available_glyphs

        return candidates

    def _filter_by_repetition(
        self,
        candidates: List[str],
        previous_glyph: str,
        repetition_count: int,
        max_repetitions: int
    ) -> List[str]:
        """Filter out repeated glyphs."""
        if repetition_count >= max_repetitions:
            # Must change
            return [g for g in candidates if g != previous_glyph]
        elif repetition_count > 0:
            # Deprioritize but allow
            return candidates
        else:
            # Can use same
            return candidates

    def _score_by_intensity(
        self,
        candidates: List[str],
        intensity: float,
        effectiveness_scores: Optional[Dict[str, float]] = None
    ) -> List[Tuple[str, float]]:
        """Score glyphs by appropriateness for intensity level."""
        if intensity < 0.4:
            intensity_tier = "low"
        elif intensity < 0.7:
            intensity_tier = "medium"
        else:
            intensity_tier = "high"

        tier_glyphs = set(
            self.intensity_responsive_glyphs.get(intensity_tier, []))

        scored = []
        for glyph in candidates:
            base_score = effectiveness_scores.get(
                glyph, 0.5) if effectiveness_scores else 0.5
            intensity_match = 1.2 if glyph in tier_glyphs else 1.0
            score = base_score * intensity_match
            scored.append((glyph, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _score_by_trajectory(
        self,
        candidates: List[str],
        trajectory: str,
        effectiveness_scores: Optional[Dict[str, float]] = None
    ) -> List[Tuple[str, float]]:
        """Score glyphs by appropriateness for emotional trajectory."""
        trajectory_glyphs = set(
            self.trajectory_responsive_glyphs.get(trajectory, []))

        scored = []
        for glyph in candidates:
            base_score = effectiveness_scores.get(
                glyph, 0.5) if effectiveness_scores else 0.5
            trajectory_match = 1.2 if glyph in trajectory_glyphs else 1.0
            score = base_score * trajectory_match
            scored.append((glyph, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _select_fallback(
        self,
        state: ConversationState,
        available_glyphs: List[str],
        effectiveness_scores: Optional[Dict[str, float]] = None
    ) -> Optional[str]:
        """Select fallback glyph when no context match."""
        if not available_glyphs:
            return None

        if effectiveness_scores:
            # Choose by effectiveness
            best = max(available_glyphs,
                       key=lambda g: effectiveness_scores.get(g, 0.5))
            return best
        else:
            # Choose first available
            return available_glyphs[0]

    def detect_context(
        self,
        turn_number: int,
        emotional_valence: float,
        emotional_arousal: float,
        user_input_length: int,
        recent_glyphs: List[str]
    ) -> ConversationContext:
        """Detect conversation context from signals."""
        # Opening (early turns, cautious)
        if turn_number <= 2:
            return ConversationContext.OPENING

        # Closure (long messages, wrapping signals)
        if turn_number > 15 and user_input_length > 200:
            return ConversationContext.CLOSURE

        # Challenge (low valence, high arousal)
        if emotional_valence < 0.4 and emotional_arousal > 0.6:
            return ConversationContext.CHALLENGE

        # Breakthrough (high valence, rising arousal)
        if emotional_valence > 0.7 and emotional_arousal > 0.5:
            return ConversationContext.BREAKTHROUGH

        # Integration (medium valence, low arousal, many turns)
        if 0.4 < emotional_valence < 0.7 and emotional_arousal < 0.5 and turn_number > 10:
            return ConversationContext.INTEGRATION

        # Exploration (default mid-conversation)
        return ConversationContext.EXPLORATION
