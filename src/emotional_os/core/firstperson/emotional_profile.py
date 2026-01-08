"""Phase 3.1: Emotional Profile Integration.

Builds persistent user emotional profiles across sessions by integrating:
- Phase 1 (Story-start + Frequency reflection)
- Phase 2.3 (Repair module learning)
- Phase 2.5 (Temporal patterns + Context)

Creates long-term memory of user's emotional patterns, recurring themes,
and response preferences to enhance personalization over time.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


class EmotionalTone(Enum):
    """Primary emotional tones tracked over time."""
    GROUNDED = "grounded"
    ANXIOUS = "anxious"
    OVERWHELMED = "overwhelmed"
    REFLECTIVE = "reflective"
    PROTECTIVE = "protective"
    CONNECTING = "connecting"
    VULNERABLE = "vulnerable"
    RESILIENT = "resilient"


@dataclass
class EmotionalSnapshot:
    """Point-in-time emotional state capture."""
    timestamp: datetime
    primary_tone: EmotionalTone
    intensity: str  # "low", "medium", "high"
    themes: List[str]
    context: Optional[str] = None
    glyph_response: Optional[str] = None
    user_satisfaction: Optional[float] = None  # 0.0-1.0


@dataclass
class RecurringTheme:
    """Tracked emotional theme across time."""
    theme: str
    first_seen: datetime
    last_seen: datetime
    occurrences: int = 0
    intensity_trend: str = "stable"  # "increasing", "decreasing", "stable"
    related_themes: List[str] = field(default_factory=list)
    effective_responses: List[str] = field(default_factory=list)
    ineffective_responses: List[str] = field(default_factory=list)


@dataclass
class TimePatterns:
    """When themes tend to emerge (circadian/weekly patterns)."""
    theme: str
    peak_hours: List[int]  # Hours 0-23 when theme most common
    peak_days: List[str]  # Days when theme peaks (Mon-Sun)
    frequency: Dict[str, int]  # Time period -> count
    predictability_score: float = 0.0  # 0.0-1.0


@dataclass
class UserEmotionalProfile:
    """Complete long-term emotional profile for a user."""
    user_id: str
    created_at: datetime
    updated_at: datetime

    # Emotional tendencies
    primary_tones: Dict[EmotionalTone, int] = field(
        default_factory=dict)  # tone -> frequency
    tone_transitions: Dict[Tuple[EmotionalTone, EmotionalTone], int] = field(
        default_factory=dict)

    # Theme tracking
    recurring_themes: Dict[str, RecurringTheme] = field(default_factory=dict)
    theme_evolution: List[Tuple[datetime, str, int]
                          ] = field(default_factory=list)

    # Temporal patterns
    time_patterns: Dict[str, TimePatterns] = field(default_factory=dict)

    # Response preferences learned
    preferred_glyph_types: Dict[str, float] = field(
        default_factory=dict)  # glyph -> score
    repair_patterns: List[Tuple[str, str, bool]] = field(
        default_factory=list)  # (original, alternative, effective)

    # Session coherence
    session_count: int = 0
    avg_session_length: int = 0
    session_quality_trend: List[float] = field(default_factory=list)

    # Snapshot history
    snapshots: List[EmotionalSnapshot] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize profile for storage."""
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "primary_tones": {t.value: count for t, count in self.primary_tones.items()},
            "recurring_themes": {name: {
                "occurrences": theme.occurrences,
                "intensity_trend": theme.intensity_trend,
                "related_themes": theme.related_themes,
            } for name, theme in self.recurring_themes.items()},
            "preferred_glyph_types": self.preferred_glyph_types,
            "session_count": self.session_count,
            "avg_session_length": self.avg_session_length,
        }


class EmotionalProfileManager:
    """Manages creation, updates, and analysis of emotional profiles.

    Integrates with:
    - MemoryManager (persistence layer)
    - FrequencyReflector (theme tracking)
    - TemporalAnalyzer (time patterns)
    - AffectParser (emotional tone detection)
    """

    def __init__(self, user_id: str, memory_manager=None):
        """Initialize profile manager.

        Args:
            user_id: User identifier
            memory_manager: Optional existing MemoryManager instance
        """
        self.user_id = user_id
        self.memory_manager = memory_manager

        # Load or create profile
        self.profile = UserEmotionalProfile(
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def record_interaction(
        self,
        tone: EmotionalTone,
        intensity: str,
        themes: List[str],
        glyph_response: str,
        user_satisfaction: Optional[float] = None,
        context: Optional[str] = None,
    ) -> None:
        """Record a single interaction in the profile.

        Args:
            tone: Primary emotional tone detected
            intensity: "low", "medium", or "high"
            themes: List of emotional themes present
            glyph_response: Which glyph was used
            user_satisfaction: Optional 0.0-1.0 feedback
            context: Optional context (repair, reflection, etc)
        """
        snapshot = EmotionalSnapshot(
            timestamp=datetime.now(),
            primary_tone=tone,
            intensity=intensity,
            themes=themes,
            glyph_response=glyph_response,
            user_satisfaction=user_satisfaction,
            context=context,
        )

        self.profile.snapshots.append(snapshot)
        self.profile.updated_at = datetime.now()

        # Update tone frequency
        self.profile.primary_tones[tone] = self.profile.primary_tones.get(
            tone, 0) + 1

        # Track theme occurrences and evolution
        for theme in themes:
            if theme not in self.profile.recurring_themes:
                self.profile.recurring_themes[theme] = RecurringTheme(
                    theme=theme,
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    occurrences=1,
                )
            else:
                self.profile.recurring_themes[theme].occurrences += 1
                self.profile.recurring_themes[theme].last_seen = datetime.now()

            self.profile.theme_evolution.append((datetime.now(), theme, 1))

        # Track glyph effectiveness
        if user_satisfaction is not None:
            if glyph_response not in self.profile.preferred_glyph_types:
                self.profile.preferred_glyph_types[glyph_response] = 0.0

            # Update preference score (exponential moving average)
            current_score = self.profile.preferred_glyph_types[glyph_response]
            self.profile.preferred_glyph_types[glyph_response] = (
                0.7 * current_score + 0.3 * user_satisfaction
            )

    def get_emotional_trajectory(self, days: int = 30) -> List[Tuple[datetime, EmotionalTone]]:
        """Get emotional tone trajectory over time period.

        Args:
            days: Number of days to look back

        Returns:
            List of (timestamp, tone) tuples
        """
        cutoff = datetime.now() - timedelta(days=days)
        trajectory = [
            (s.timestamp, s.primary_tone)
            for s in self.profile.snapshots
            if s.timestamp > cutoff
        ]
        return trajectory

    def get_dominant_themes(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most frequent emotional themes.

        Args:
            limit: Maximum themes to return

        Returns:
            List of (theme, occurrence_count) sorted by frequency
        """
        themes = sorted(
            [(name, theme.occurrences)
             for name, theme in self.profile.recurring_themes.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        return themes[:limit]

    def get_time_patterns(self, theme: str) -> Optional[TimePatterns]:
        """Get when a specific theme typically emerges.

        Args:
            theme: Theme name

        Returns:
            TimePatterns object or None if not enough data
        """
        if theme not in self.profile.time_patterns:
            self._analyze_temporal_pattern(theme)

        return self.profile.time_patterns.get(theme)

    def _analyze_temporal_pattern(self, theme: str) -> None:
        """Analyze when a theme tends to occur.

        Args:
            theme: Theme to analyze
        """
        hour_counts: Dict[int, int] = {}
        day_counts: Dict[str, int] = {}

        # Find snapshots containing this theme
        for snapshot in self.profile.snapshots:
            if theme in snapshot.themes:
                hour = snapshot.timestamp.hour
                day = snapshot.timestamp.strftime("%A")

                hour_counts[hour] = hour_counts.get(hour, 0) + 1
                day_counts[day] = day_counts.get(day, 0) + 1

        if not hour_counts:
            return

        # Find peak times
        peak_hours = sorted(
            [(h, c) for h, c in hour_counts.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:3]
        peak_hours_list = [h for h, c in peak_hours]

        peak_days = sorted(
            [(d, c) for d, c in day_counts.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:2]
        peak_days_list = [d for d, c in peak_days]

        # Calculate predictability
        total = sum(hour_counts.values())
        peak_total = sum(c for h, c in peak_hours)
        predictability = peak_total / total if total > 0 else 0.0

        pattern = TimePatterns(
            theme=theme,
            peak_hours=peak_hours_list,
            peak_days=peak_days_list,
            frequency=hour_counts,
            predictability_score=predictability,
        )

        self.profile.time_patterns[theme] = pattern

    def predict_upcoming_themes(self, lookahead_hours: int = 4) -> List[Tuple[str, float]]:
        """Predict which themes are likely to emerge in next hours.

        Args:
            lookahead_hours: How many hours to predict ahead

        Returns:
            List of (theme, probability) sorted by likelihood
        """
        predictions: Dict[str, float] = {}
        current_hour = datetime.now().hour
        current_day = datetime.now().strftime("%A")

        for theme, pattern in self.profile.time_patterns.items():
            probability = 0.0

            # Check if peak time coming up
            for hour_offset in range(lookahead_hours):
                check_hour = (current_hour + hour_offset) % 24
                if check_hour in pattern.peak_hours:
                    probability += 0.25

            # Check if peak day
            if current_day in pattern.peak_days:
                probability += 0.3

            # Apply predictability score as multiplier
            probability *= pattern.predictability_score

            if probability > 0:
                predictions[theme] = min(1.0, probability)

        sorted_predictions = sorted(
            predictions.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return sorted_predictions

    def get_session_coherence(self) -> float:
        """Measure how coherent/consistent current session is with profile.

        Returns:
            Score 0.0-1.0 (1.0 = very consistent with typical pattern)
        """
        if not self.profile.snapshots:
            return 0.5  # Unknown

        # Get recent snapshots (last session)
        recent = self.profile.snapshots[-20:]  # Last ~20 turns
        if not recent:
            return 0.5

        recent_tones = [s.primary_tone for s in recent]
        recent_themes = [t for s in recent for t in s.themes]

        # How much do recent patterns match historical?
        coherence = 0.0

        # Tone coherence
        if self.profile.primary_tones:
            historical_dominant_tone = max(
                self.profile.primary_tones.items(),
                key=lambda x: x[1],
            )[0]
            tone_match = sum(1 for t in recent_tones if t ==
                             historical_dominant_tone) / len(recent_tones)
            coherence += tone_match * 0.5

        # Theme coherence
        if self.profile.recurring_themes:
            historical_themes = set(self.profile.recurring_themes.keys())
            recent_theme_set = set(recent_themes)
            if historical_themes:
                theme_overlap = len(recent_theme_set &
                                    historical_themes) / len(historical_themes)
                coherence += theme_overlap * 0.5

        return min(1.0, coherence)

    def export_profile(self) -> Dict:
        """Export complete profile for storage/analysis.

        Returns:
            Dictionary representation of full profile
        """
        return self.profile.to_dict()

    def import_profile(self, profile_dict: Dict) -> None:
        """Import previously saved profile.

        Args:
            profile_dict: Dictionary from export_profile()
        """
        # Reconstruct profile from dictionary
        # Implementation depends on storage layer
        pass
