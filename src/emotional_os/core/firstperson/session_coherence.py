"""Session Coherence Tracking for Phase 3.1.

Monitors how well individual sessions flow and maintain thematic consistency.
Integrates with emotional_profile.py to compare against long-term patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


class SessionQuality(Enum):
    """Quality assessment of a session."""
    EXCELLENT = "excellent"     # High coherence, user satisfied
    GOOD = "good"               # Solid coherence, mostly on-track
    ADEQUATE = "adequate"       # Some coherence, minor deviations
    POOR = "poor"               # Low coherence, frustrated user
    FRAGMENTED = "fragmented"   # Multiple sudden theme shifts


@dataclass
class ThemeSegment:
    """A contiguous portion of session with consistent themes."""
    start_turn: int
    end_turn: int
    dominant_theme: str
    secondary_themes: List[str] = field(default_factory=list)
    emotional_tone: Optional[str] = None
    stability: float = 0.8  # 0.0-1.0 (how consistent was this segment)


@dataclass
class SessionCoherence:
    """Coherence metrics for a complete session."""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    # Session structure
    turn_count: int = 0
    total_duration: int = 0  # seconds

    # Theme tracking
    theme_segments: List[ThemeSegment] = field(default_factory=list)
    theme_transitions: List[Tuple[str, str, int]] = field(
        default_factory=list)  # (from, to, turn_number)
    theme_diversity: float = 0.0  # 0.0-1.0 (how many unique themes)

    # Emotional arc
    emotional_tones: List[str] = field(default_factory=list)
    tone_consistency: float = 0.0  # 0.0-1.0

    # Quality metrics
    quality: SessionQuality = SessionQuality.ADEQUATE
    coherence_score: float = 0.0  # 0.0-1.0
    fragmentation_index: float = 0.0  # 0.0-1.0 (higher = more fragmented)

    # Comparison to profile
    # 0.0-1.0 (how well matches user's typical patterns)
    profile_alignment: float = 0.0
    anomaly_count: int = 0  # Number of unexpected patterns

    # User satisfaction
    user_satisfaction: Optional[float] = None  # 0.0-1.0
    frustration_markers: List[int] = field(
        default_factory=list)  # Turn numbers with frustration
    breakthrough_markers: List[int] = field(
        default_factory=list)  # Turn numbers with breakthroughs


class SessionCoherenceTracker:
    """Tracks coherence for current session in real-time.

    Integrates with:
    - EmotionalProfileManager (for comparison baseline)
    - FrequencyReflector (theme identification)
    - IntegrationOrchestrator (for turn-by-turn updates)
    """

    def __init__(self, session_id: str, user_id: str, profile_manager=None):
        """Initialize session tracker.

        Args:
            session_id: Unique identifier for this session
            user_id: User identifier
            profile_manager: Optional EmotionalProfileManager for comparison
        """
        self.session_id = session_id
        self.user_id = user_id
        self.profile_manager = profile_manager

        self.coherence = SessionCoherence(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now(),
        )

        self._turn_history: List[Dict] = []

    def record_turn(
        self,
        turn_number: int,
        user_input: str,
        themes: List[str],
        emotional_tone: str,
        glyph_response: str,
        has_frustration: bool = False,
        has_breakthrough: bool = False,
    ) -> None:
        """Record a single user turn.

        Args:
            turn_number: Turn sequence number
            user_input: User's input text
            themes: Identified themes in input
            emotional_tone: Detected emotional tone
            glyph_response: Glyph used in response
            has_frustration: Whether user showed frustration
            has_breakthrough: Whether user had a breakthrough
        """
        turn_data = {
            "turn": turn_number,
            "timestamp": datetime.now(),
            "themes": themes,
            "tone": emotional_tone,
            "glyph": glyph_response,
            "frustration": has_frustration,
            "breakthrough": has_breakthrough,
        }

        self._turn_history.append(turn_data)
        self.coherence.turn_count = turn_number

        # Track frustration and breakthroughs
        if has_frustration:
            self.coherence.frustration_markers.append(turn_number)
        if has_breakthrough:
            self.coherence.breakthrough_markers.append(turn_number)

        # Update emotional tones
        self.coherence.emotional_tones.append(emotional_tone)

        # Update theme tracking
        self._update_theme_tracking(themes, emotional_tone)

        # Recalculate coherence metrics
        self._recalculate_metrics()

    def _update_theme_tracking(self, themes: List[str], tone: str) -> None:
        """Update theme segments and transitions.

        Args:
            themes: Themes in current turn
            tone: Emotional tone
        """
        if not themes:
            return

        current_theme = themes[0]  # Primary theme
        secondary = themes[1:] if len(themes) > 1 else []

        # Check if continuing previous theme
        if (self.coherence.theme_segments and
                self.coherence.theme_segments[-1].dominant_theme == current_theme):
            # Continue segment
            segment = self.coherence.theme_segments[-1]
            segment.end_turn = self.coherence.turn_count
        else:
            # New segment
            if self.coherence.theme_segments:
                # Record transition
                old_theme = self.coherence.theme_segments[-1].dominant_theme
                self.coherence.theme_transitions.append(
                    (old_theme, current_theme, self.coherence.turn_count)
                )

            segment = ThemeSegment(
                start_turn=self.coherence.turn_count,
                end_turn=self.coherence.turn_count,
                dominant_theme=current_theme,
                secondary_themes=secondary,
                emotional_tone=tone,
            )
            self.coherence.theme_segments.append(segment)

    def _recalculate_metrics(self) -> None:
        """Recalculate all coherence metrics.

        Called after each turn to update scores.
        """
        if not self._turn_history:
            return

        # Theme diversity
        unique_themes = set()
        for turn in self._turn_history:
            unique_themes.update(turn["themes"])

        if self.coherence.turn_count > 0:
            self.coherence.theme_diversity = len(
                unique_themes) / (self.coherence.turn_count + 1)

        # Tone consistency
        if self.coherence.emotional_tones:
            tone_counts = {}
            for tone in self.coherence.emotional_tones:
                tone_counts[tone] = tone_counts.get(tone, 0) + 1

            dominant_count = max(tone_counts.values())
            self.coherence.tone_consistency = dominant_count / \
                len(self.coherence.emotional_tones)

        # Fragmentation (rapid theme changes)
        if len(self.coherence.theme_segments) > 0:
            segment_lengths = [
                s.end_turn - s.start_turn + 1
                for s in self.coherence.theme_segments
            ]

            if segment_lengths:
                avg_length = sum(segment_lengths) / len(segment_lengths)
                min_length = min(segment_lengths) if segment_lengths else 5

                # Shorter segments = more fragmented
                self.coherence.fragmentation_index = 1.0 - \
                    (avg_length / max(avg_length, 5))

        # Profile alignment (if profile manager available)
        if self.profile_manager:
            self._calculate_profile_alignment()

        # Overall coherence score
        self._calculate_coherence_score()

        # Session quality
        self._assess_session_quality()

    def _calculate_profile_alignment(self) -> None:
        """Calculate how well session aligns with user's typical patterns.

        Uses profile manager to compare against historical patterns.
        """
        if not self.profile_manager or not self.coherence.emotional_tones:
            self.coherence.profile_alignment = 0.5
            return

        # Get profile's dominant tone
        profile_tones = self.profile_manager.profile.primary_tones
        if not profile_tones:
            self.coherence.profile_alignment = 0.5
            return

        dominant_profile_tone = max(
            profile_tones.items(),
            key=lambda x: x[1],
        )[0]

        # Compare current session tones to profile
        matching_tones = sum(
            1 for t in self.coherence.emotional_tones
            if t == dominant_profile_tone.value
        )

        tone_alignment = matching_tones / len(self.coherence.emotional_tones)

        # Compare themes
        session_themes = set()
        for turn in self._turn_history:
            session_themes.update(turn["themes"])

        profile_themes = set(
            self.profile_manager.profile.recurring_themes.keys())

        if profile_themes:
            theme_overlap = len(
                session_themes & profile_themes) / len(profile_themes)
        else:
            theme_overlap = 0.5  # Unknown

        # Weighted alignment
        self.coherence.profile_alignment = (
            tone_alignment * 0.6 + theme_overlap * 0.4)

    def _calculate_coherence_score(self) -> None:
        """Calculate overall coherence score 0.0-1.0.

        Combines multiple factors:
        - Tone consistency (40%)
        - Theme continuity (40%)
        - Profile alignment (20%)
        """
        score = 0.0

        # Tone consistency component (high tone consistency = coherent)
        score += self.coherence.tone_consistency * 0.4

        # Theme continuity (low fragmentation = coherent)
        theme_continuity = 1.0 - self.coherence.fragmentation_index
        score += theme_continuity * 0.4

        # Profile alignment component
        score += self.coherence.profile_alignment * 0.2

        self.coherence.coherence_score = min(1.0, score)

    def _assess_session_quality(self) -> None:
        """Assess overall session quality based on coherence and user signals.

        Updates SessionCoherence.quality field.
        """
        # Start with coherence score
        quality_score = self.coherence.coherence_score

        # Adjust for frustration signals
        frustration_ratio = (
            len(self.coherence.frustration_markers) /
            max(self.coherence.turn_count, 1)
        )
        quality_score *= (1.0 - frustration_ratio * 0.3)

        # Boost for breakthroughs
        breakthrough_ratio = (
            len(self.coherence.breakthrough_markers) /
            max(self.coherence.turn_count, 1)
        )
        quality_score *= (1.0 + breakthrough_ratio * 0.2)

        # Determine quality
        if quality_score >= 0.85:
            self.coherence.quality = SessionQuality.EXCELLENT
        elif quality_score >= 0.70:
            self.coherence.quality = SessionQuality.GOOD
        elif quality_score >= 0.50:
            self.coherence.quality = SessionQuality.ADEQUATE
        elif quality_score >= 0.30:
            if self.coherence.fragmentation_index > 0.7:
                self.coherence.quality = SessionQuality.FRAGMENTED
            else:
                self.coherence.quality = SessionQuality.POOR
        else:
            self.coherence.quality = SessionQuality.POOR

    def end_session(self, user_satisfaction: Optional[float] = None) -> SessionCoherence:
        """End current session and finalize metrics.

        Args:
            user_satisfaction: Optional user satisfaction rating 0.0-1.0

        Returns:
            Final SessionCoherence object
        """
        self.coherence.end_time = datetime.now()
        self.coherence.total_duration = int(
            (self.coherence.end_time - self.coherence.start_time).total_seconds()
        )

        if user_satisfaction is not None:
            self.coherence.user_satisfaction = user_satisfaction

        return self.coherence

    def get_coherence_report(self) -> Dict:
        """Get comprehensive coherence report.

        Returns:
            Dictionary with all metrics for analysis/logging
        """
        return {
            "session_id": self.coherence.session_id,
            "user_id": self.coherence.user_id,
            "duration_seconds": self.coherence.total_duration,
            "turn_count": self.coherence.turn_count,
            "quality": self.coherence.quality.value,
            "coherence_score": self.coherence.coherence_score,
            "tone_consistency": self.coherence.tone_consistency,
            "theme_diversity": self.coherence.theme_diversity,
            "fragmentation_index": self.coherence.fragmentation_index,
            "profile_alignment": self.coherence.profile_alignment,
            "theme_segments": len(self.coherence.theme_segments),
            "theme_transitions": len(self.coherence.theme_transitions),
            "frustration_markers": self.coherence.frustration_markers,
            "breakthrough_markers": self.coherence.breakthrough_markers,
            "user_satisfaction": self.coherence.user_satisfaction,
        }

    def suggest_improvements(self) -> List[str]:
        """Suggest how to improve future sessions based on coherence.

        Returns:
            List of actionable suggestions
        """
        suggestions = []

        if self.coherence.fragmentation_index > 0.6:
            suggestions.append(
                "Session had frequent theme changes. Consider exploring themes more deeply "
                "before shifting topics."
            )

        if self.coherence.tone_consistency < 0.5:
            suggestions.append(
                "Emotional tone was inconsistent. Grounding techniques might help establish "
                "more stable emotional baseline."
            )

        if self.coherence.profile_alignment < 0.4:
            suggestions.append(
                "Session patterns diverged from typical patterns. This might indicate an "
                "unusual day. Consider check-in questions about what's different."
            )

        if len(self.coherence.frustration_markers) > self.coherence.turn_count / 3:
            suggestions.append(
                "User showed signs of frustration. Review responses for better attunement "
                "and consider slower pacing."
            )

        if len(self.coherence.breakthrough_markers) > 0:
            suggestions.append(
                f"User had {len(self.coherence.breakthrough_markers)} breakthrough moments! "
                "Explore these themes further in future sessions."
            )

        return suggestions
