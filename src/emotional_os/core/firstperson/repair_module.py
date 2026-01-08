"""Repair Module for Phase 2.3 - Correction Detection and Learning.

Detects when users reject or correct glyph-aware responses, learns which glyphs
resonate for each user, and refines glyph selection over time.

Key responsibilities:
- Detect rejection patterns in user input
- Track glyph effectiveness per user and emotional state
- Suggest alternative glyphs when current one misses
- Learn user preferences and refine composition strategy
- Maintain repair history for feedback loops

Pattern detection:
- Explicit rejection: "that's not it", "doesn't feel right", "nope", etc.
- Implicit correction: User rephrases or provides clarification
- Suggestion: "sounds more like X than Y"
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RejectionPattern:
    """Data class for tracked rejection patterns."""

    timestamp: datetime
    user_id: str
    tone: str  # sad, anxious, angry, etc.
    arousal: float
    valence: float
    suggested_glyph: str  # The glyph that was rejected
    rejection_type: str  # explicit, implicit, unclear
    user_correction: Optional[str] = None  # What user said instead
    accepted_glyph: Optional[str] = None  # If user suggested alternative


@dataclass
class GlyphEffectiveness:
    """Track how well a glyph works for a user's emotional states."""

    glyph_name: str
    tone: str
    total_presented: int = 0
    total_accepted: int = 0
    total_rejected: int = 0
    average_arousal: float = 0.5
    average_valence: float = -0.5
    # "too poetic": 1, etc.
    user_feedback: Dict[str, int] = field(default_factory=dict)

    @property
    def effectiveness_score(self) -> float:
        """Score from 0-1 indicating how well this glyph works."""
        if self.total_presented == 0:
            return 0.5  # Neutral if never presented
        return self.total_accepted / self.total_presented


class RejectionDetector:
    """Detects rejection patterns in user input."""

    # Common rejection patterns
    EXPLICIT_REJECTIONS = {
        "not it",
        "that's not",
        "doesn't feel",
        "doesn't sound",
        "wrong",
        "nope",
        "no",
        "not really",
        "not quite",
        "off",
        "weird",
        "doesn't fit",
        "misses",
        "more like",
        "it's more",
    }

    # Patterns indicating implicit correction
    IMPLICIT_PATTERNS = {
        "actually",
        "well",
        "i mean",
        "more",
        "less",
        "it's actually",
        "i guess",
    }

    @staticmethod
    def detect_rejection(user_input: str) -> Tuple[bool, str, Optional[str]]:
        """Detect if user is rejecting previous response.

        Args:
            user_input: User's message

        Returns:
            Tuple of (is_rejection, rejection_type, correction_hint)
            - is_rejection: bool, True if rejection detected
            - rejection_type: 'explicit', 'implicit', or None
            - correction_hint: User's suggested alternative or None
        """
        lower_input = user_input.lower()

        # Check explicit rejections
        for pattern in RejectionDetector.EXPLICIT_REJECTIONS:
            if pattern in lower_input:
                # Try to extract correction hint
                hint = RejectionDetector._extract_correction(user_input)
                return True, "explicit", hint

        # Check implicit corrections
        for pattern in RejectionDetector.IMPLICIT_PATTERNS:
            if pattern in lower_input:
                hint = RejectionDetector._extract_correction(user_input)
                if hint:
                    return True, "implicit", hint

        return False, None, None

    @staticmethod
    def _extract_correction(user_input: str) -> Optional[str]:
        """Try to extract what the user thinks better fits.

        Args:
            user_input: User's message

        Returns:
            Suggested alternative or None
        """
        # Look for "it's more like X" or "sounds like X" patterns
        patterns = [
            ("more like ", ""),
            ("sounds like ", ""),
            ("feels like ", ""),
            ("it's actually ", ""),
            ("i mean ", ""),
        ]

        for prefix, _ in patterns:
            if prefix in user_input.lower():
                idx = user_input.lower().index(prefix) + len(prefix)
                # Get next 2-3 words as hint
                words = user_input[idx:].split()[:3]
                return " ".join(words).strip(".,!?;")

        return None


class RepairPreferences:
    """Learns user preferences for glyphs per emotional state."""

    def __init__(self, user_id: str):
        """Initialize repair preferences for a user.

        Args:
            user_id: Unique user identifier
        """
        self.user_id = user_id
        self.glyph_history: List[RejectionPattern] = []
        self.effectiveness: Dict[Tuple[str, str], GlyphEffectiveness] = {}

    def record_acceptance(
        self, tone: str, arousal: float, valence: float, glyph_used: str
    ) -> None:
        """Record that a glyph was accepted.

        Args:
            tone: Detected emotional tone
            arousal: Arousal level (0-1)
            valence: Valence level (-1 to +1)
            glyph_used: Glyph that was accepted
        """
        key = (tone, glyph_used)
        if key not in self.effectiveness:
            self.effectiveness[key] = GlyphEffectiveness(
                glyph_name=glyph_used, tone=tone, average_arousal=arousal, average_valence=valence
            )

        eff = self.effectiveness[key]
        eff.total_presented += 1
        eff.total_accepted += 1
        # Update running average for arousal/valence
        eff.average_arousal = (eff.average_arousal + arousal) / 2
        eff.average_valence = (eff.average_valence + valence) / 2

    def record_rejection(
        self,
        tone: str,
        arousal: float,
        valence: float,
        glyph_used: str,
        rejection_type: str,
        user_correction: Optional[str] = None,
        accepted_glyph: Optional[str] = None,
    ) -> None:
        """Record that a glyph was rejected.

        Args:
            tone: Detected emotional tone
            arousal: Arousal level (0-1)
            valence: Valence level (-1 to +1)
            glyph_used: Glyph that was rejected
            rejection_type: 'explicit' or 'implicit'
            user_correction: What user said instead
            accepted_glyph: If user suggested alternative
        """
        key = (tone, glyph_used)
        if key not in self.effectiveness:
            self.effectiveness[key] = GlyphEffectiveness(
                glyph_name=glyph_used, tone=tone, average_arousal=arousal, average_valence=valence
            )

        eff = self.effectiveness[key]
        eff.total_presented += 1
        eff.total_rejected += 1

        # Store rejection for later analysis
        pattern = RejectionPattern(
            timestamp=datetime.now(),
            user_id=self.user_id,
            tone=tone,
            arousal=arousal,
            valence=valence,
            suggested_glyph=glyph_used,
            rejection_type=rejection_type,
            user_correction=user_correction,
            accepted_glyph=accepted_glyph,
        )
        self.glyph_history.append(pattern)

    def get_best_glyph_for_state(self, tone: str, arousal: float, valence: float) -> Optional[str]:
        """Get the best-performing glyph for a specific emotional state.

        Args:
            tone: Emotional tone
            arousal: Arousal level
            valence: Valence level

        Returns:
            Best glyph for this state based on learning history
        """
        # Find glyphs for this tone
        candidates = [
            (key, eff)
            for key, eff in self.effectiveness.items()
            if key[0] == tone and eff.total_presented > 0
        ]

        if not candidates:
            return None

        # Sort by effectiveness score (accepted / total)
        candidates.sort(key=lambda x: x[1].effectiveness_score, reverse=True)

        return candidates[0][1].glyph_name

    def get_alternative_glyph(self, tone: str, current_glyph: str) -> Optional[str]:
        """Get an alternative glyph when current one was rejected.

        Args:
            tone: Emotional tone
            current_glyph: The glyph that was rejected

        Returns:
            Alternative glyph or None
        """
        # Find glyphs for this tone excluding the rejected one
        candidates = [
            (key, eff)
            for key, eff in self.effectiveness.items()
            if key[0] == tone and key[1] != current_glyph and eff.total_presented > 0
        ]

        if not candidates:
            return None

        # Sort by effectiveness
        candidates.sort(key=lambda x: x[1].effectiveness_score, reverse=True)

        return candidates[0][1].glyph_name

    def get_rejection_summary(self) -> Dict[str, int]:
        """Get summary of rejections by pattern type.

        Returns:
            Dict with rejection counts and reasons
        """
        summary = {
            "total_rejections": len(self.glyph_history),
            "explicit_rejections": sum(1 for p in self.glyph_history if p.rejection_type == "explicit"),
            "implicit_corrections": sum(1 for p in self.glyph_history if p.rejection_type == "implicit"),
        }
        return summary


def should_attempt_repair(
    user_input: str, previous_response: Optional[str] = None
) -> Tuple[bool, str, Optional[str]]:
    """Determine if repair should be attempted.

    Args:
        user_input: User's current message
        previous_response: The response being potentially rejected

    Returns:
        Tuple of (should_repair, rejection_type, correction_hint)
    """
    if not previous_response or not user_input:
        return False, "", None

    is_rejection, rejection_type, correction = RejectionDetector.detect_rejection(
        user_input)

    return is_rejection, rejection_type, correction
