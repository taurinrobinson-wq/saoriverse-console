"""Repair Orchestrator for Phase 2.3 - Integration with Main Response Engine.

Bridges the repair module with the main conversation pipeline. Detects when users
reject or correct responses, learns glyph preferences, and suggests alternatives.

Architecture:
- Sits between user input and response generation
- Detects rejections in user input
- Tracks effectiveness of glyphs per user
- Suggests better alternatives when current glyph misses
- Learns user preferences over time

Integration points:
- Before response: Check if this is a correction to previous response
- After response: Record glyph effectiveness (acceptance/rejection)
- Feedback loop: Suggests alternative glyphs when user rejects
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timezone

from .repair_module import (
    RejectionDetector,
    RepairPreferences,
    should_attempt_repair,
)


@dataclass
class RepairAnalysis:
    """Analysis of whether repair is needed."""

    is_rejection: bool
    rejection_type: Optional[str]  # 'explicit', 'implicit'
    user_correction: Optional[str]  # What user said instead
    suggested_alternative: Optional[str]  # Recommended next glyph
    confidence: float  # 0-1 confidence in correction


@dataclass
class GlyphCompositionContext:
    """Context for composing glyph-aware responses."""

    tone: str
    arousal: float
    valence: float
    glyph_name: str
    user_id: str
    timestamp: str = None

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class RepairOrchestrator:
    """Orchestrates repair detection and learning."""

    def __init__(self, user_id: str):
        """Initialize repair orchestrator.

        Args:
            user_id: User identifier for tracking preferences
        """
        self.user_id = user_id
        self.user_preferences = RepairPreferences(user_id=user_id)
        self.previous_response: Optional[str] = None
        self.previous_glyph_context: Optional[GlyphCompositionContext] = None
        self.repair_history: List[Dict[str, Any]] = []

    def analyze_for_repair(
        self, user_input: str
    ) -> RepairAnalysis:
        """Analyze user input to detect if repair is needed.

        Args:
            user_input: User's message

        Returns:
            RepairAnalysis with rejection detection and alternatives
        """
        # Check if user is rejecting previous response
        should_repair, rejection_type, correction = should_attempt_repair(
            user_input=user_input,
            previous_response=self.previous_response,
        )

        if not should_repair:
            return RepairAnalysis(
                is_rejection=False,
                rejection_type=None,
                user_correction=None,
                suggested_alternative=None,
                confidence=0.0,
            )

        # Record rejection in preferences if we have context
        if self.previous_glyph_context:
            ctx = self.previous_glyph_context
            self.user_preferences.record_rejection(
                tone=ctx.tone,
                arousal=ctx.arousal,
                valence=ctx.valence,
                glyph_used=ctx.glyph_name,
                rejection_type=rejection_type or "explicit",
                user_correction=correction,
            )

        # Suggest alternative glyph
        suggested_alternative = None
        confidence = 0.5  # Base confidence for any rejection

        if self.previous_glyph_context:
            ctx = self.previous_glyph_context
            # Try to get better alternative
            alternative = self.user_preferences.get_alternative_glyph(
                tone=ctx.tone,
                current_glyph=ctx.glyph_name,
            )

            if alternative:
                suggested_alternative = alternative
                # Higher confidence if we have learned this alternative is better
                eff = self.user_preferences.effectiveness.get(
                    (ctx.tone, alternative))
                if eff:
                    confidence = min(0.9, eff.effectiveness_score + 0.2)

        # Record this repair attempt
        repair_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_input": user_input,
            "rejection_type": rejection_type,
            "user_correction": correction,
            "previous_glyph": self.previous_glyph_context.glyph_name
            if self.previous_glyph_context
            else None,
            "suggested_alternative": suggested_alternative,
            "confidence": confidence,
        }
        self.repair_history.append(repair_record)

        return RepairAnalysis(
            is_rejection=True,
            rejection_type=rejection_type,
            user_correction=correction,
            suggested_alternative=suggested_alternative,
            confidence=confidence,
        )

    def record_acceptance(self, context: GlyphCompositionContext) -> None:
        """Record when user accepts a glyph-aware response.

        Args:
            context: Glyph composition context with tone, arousal, valence, glyph
        """
        self.user_preferences.record_acceptance(
            tone=context.tone,
            arousal=context.arousal,
            valence=context.valence,
            glyph_used=context.glyph_name,
        )

        # Update context for next turn
        self.previous_glyph_context = context

    def record_response(self, response_text: str) -> None:
        """Record the response we just gave (before knowing if accepted).

        Args:
            response_text: The response we generated
        """
        self.previous_response = response_text

    def get_best_glyph_for_state(
        self, tone: str, arousal: float, valence: float
    ) -> Optional[str]:
        """Get best-performing glyph for this emotional state based on history.

        Args:
            tone: Emotional tone
            arousal: Arousal level (0-1)
            valence: Valence level (-1 to 1)

        Returns:
            Best glyph name for this state or None
        """
        return self.user_preferences.get_best_glyph_for_state(tone, arousal, valence)

    def get_repair_summary(self) -> Dict[str, Any]:
        """Get summary of repairs and learning for this session.

        Returns:
            Dictionary with repair statistics and user preferences
        """
        rejection_summary = self.user_preferences.get_rejection_summary()

        # Count repairs by type
        explicit_count = sum(
            1 for r in self.repair_history if r["rejection_type"] == "explicit"
        )
        implicit_count = sum(
            1 for r in self.repair_history if r["rejection_type"] == "implicit"
        )

        # Get most rejected glyphs
        most_rejected = {}
        for record in self.user_preferences.glyph_history:
            glyph = record.suggested_glyph
            most_rejected[glyph] = most_rejected.get(glyph, 0) + 1

        # Get most effective glyphs per tone
        best_by_tone = {}
        for (tone, glyph), eff in self.user_preferences.effectiveness.items():
            if tone not in best_by_tone:
                best_by_tone[tone] = []
            if eff.total_presented > 0:
                best_by_tone[tone].append(
                    {
                        "glyph": glyph,
                        "effectiveness": eff.effectiveness_score,
                        "times_used": eff.total_presented,
                    }
                )

        # Sort by effectiveness
        for tone in best_by_tone:
            best_by_tone[tone].sort(
                key=lambda x: x["effectiveness"], reverse=True)

        return {
            "total_repairs": len(self.repair_history),
            "explicit_rejections": explicit_count,
            "implicit_corrections": implicit_count,
            "most_rejected_glyphs": most_rejected,
            "best_glyphs_by_tone": best_by_tone,
            "all_rejections_summary": rejection_summary,
        }

    def reset_session(self) -> None:
        """Reset session state but keep learning history.

        Used when starting new conversation with same user.
        """
        self.previous_response = None
        self.previous_glyph_context = None
        self.repair_history = []

    def clear_all(self) -> None:
        """Clear all learning history and session state.

        WARNING: This resets user preferences completely.
        """
        self.user_preferences = RepairPreferences(user_id=self.user_id)
        self.previous_response = None
        self.previous_glyph_context = None
        self.repair_history = []
