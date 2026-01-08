"""
Phase 2.5: Temporal Patterns
Tracks time-based patterns in glyph effectiveness and user preferences.
Enables time-aware glyph selection (morning vs evening, weekday vs weekend, etc).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, time, timedelta
from enum import Enum
from collections import defaultdict
import statistics


class TimeOfDay(Enum):
    """Time periods for pattern analysis."""
    MORNING = "morning"  # 6AM-12PM
    AFTERNOON = "afternoon"  # 12PM-6PM
    EVENING = "evening"  # 6PM-12AM
    NIGHT = "night"  # 12AM-6AM


class DayOfWeek(Enum):
    """Day periods for pattern analysis."""
    WEEKDAY = "weekday"  # Mon-Fri
    WEEKEND = "weekend"  # Sat-Sun
    MONDAY = "monday"
    FRIDAY = "friday"
    MONDAY_FRIDAY = "mon-fri"


@dataclass
class TemporalEvent:
    """Record of glyph use at a specific time."""
    glyph_name: str
    tone: str
    timestamp: datetime
    accepted: bool
    effectiveness_score: float
    arousal: float
    valence: float
    user_id: str


@dataclass
class TemporalPattern:
    """Pattern of glyph effectiveness over time."""
    glyph_name: str
    tone: str
    time_period: str  # e.g., "morning", "monday", "afternoon"
    average_effectiveness: float = 0.5
    use_count: int = 0
    acceptance_count: int = 0
    confidence: float = 0.0  # How confident we are in this pattern (0.0-1.0)
    last_updated: datetime = field(default_factory=datetime.now)

    def get_acceptance_rate(self) -> float:
        """Calculate acceptance rate for this temporal pattern."""
        if self.use_count == 0:
            return 0.0
        return self.acceptance_count / self.use_count

    def is_strong_pattern(self, min_uses: int = 3, min_confidence: float = 0.7) -> bool:
        """Check if pattern is statistically significant."""
        return self.use_count >= min_uses and self.confidence >= min_confidence


class TemporalAnalyzer:
    """Analyzes temporal patterns in glyph effectiveness."""

    def __init__(self):
        """Initialize temporal analyzer."""
        self.events: List[TemporalEvent] = []
        # key: "glyph:tone:period"
        self.patterns: Dict[str, TemporalPattern] = {}
        self._time_of_day_events: Dict[str,
                                       List[TemporalEvent]] = defaultdict(list)
        self._day_of_week_events: Dict[str,
                                       List[TemporalEvent]] = defaultdict(list)

    def record_event(self, event: TemporalEvent) -> None:
        """Record a glyph use event."""
        self.events.append(event)

        # Index by time of day
        time_period = self._get_time_of_day(event.timestamp)
        self._time_of_day_events[time_period].append(event)

        # Index by day of week
        day_period = self._get_day_of_week(event.timestamp)
        self._day_of_week_events[day_period].append(event)

        # Update patterns
        self._update_patterns()

    def _get_time_of_day(self, dt: datetime) -> str:
        """Determine time of day from datetime."""
        hour = dt.hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 24:
            return "evening"
        else:
            return "night"

    def _get_day_of_week(self, dt: datetime) -> str:
        """Determine day of week from datetime."""
        weekday = dt.weekday()  # 0=Monday, 6=Sunday
        if weekday < 5:
            return "weekday"
        else:
            return "weekend"

    def _update_patterns(self) -> None:
        """Recalculate temporal patterns from all events."""
        # Clear patterns
        self.patterns.clear()

        # Analyze by time of day
        for time_period in ["morning", "afternoon", "evening", "night"]:
            events = self._time_of_day_events.get(time_period, [])
            self._analyze_event_group(events, time_period)

        # Analyze by day of week
        for day_period in ["weekday", "weekend"]:
            events = self._day_of_week_events.get(day_period, [])
            self._analyze_event_group(events, day_period)

    def _analyze_event_group(self, events: List[TemporalEvent], period: str) -> None:
        """Analyze effectiveness for a group of events."""
        if not events:
            return

        # Group by glyph and tone
        glyph_tone_events: Dict[str, List[TemporalEvent]] = defaultdict(list)
        for event in events:
            key = f"{event.glyph_name}:{event.tone}"
            glyph_tone_events[key].append(event)

        # Create patterns
        for key, group_events in glyph_tone_events.items():
            glyph_name, tone = key.split(":")
            use_count = len(group_events)
            acceptance_count = sum(1 for e in group_events if e.accepted)

            # Calculate confidence based on sample size
            confidence = min(1.0, use_count / 5.0)

            pattern = TemporalPattern(
                glyph_name=glyph_name,
                tone=tone,
                time_period=period,
                average_effectiveness=statistics.mean(
                    e.effectiveness_score for e in group_events),
                use_count=use_count,
                acceptance_count=acceptance_count,
                confidence=confidence,
                last_updated=datetime.now()
            )

            pattern_key = f"{glyph_name}:{tone}:{period}"
            self.patterns[pattern_key] = pattern

    def get_best_glyph_for_time(
        self,
        tone: str,
        current_time: Optional[datetime] = None,
        min_confidence: float = 0.5
    ) -> Optional[Tuple[str, float]]:
        """Get best glyph for current time of day."""
        if current_time is None:
            current_time = datetime.now()

        time_period = self._get_time_of_day(current_time)
        return self.get_best_glyph_for_period(tone, time_period, min_confidence)

    def get_best_glyph_for_period(
        self,
        tone: str,
        period: str,
        min_confidence: float = 0.5
    ) -> Optional[Tuple[str, float]]:
        """Get best glyph for a specific period (time/day)."""
        matching_patterns = []

        for pattern in self.patterns.values():
            if (pattern.tone == tone and
                pattern.time_period == period and
                    pattern.confidence >= min_confidence):
                matching_patterns.append(pattern)

        if not matching_patterns:
            return None

        # Sort by effectiveness
        best = max(matching_patterns, key=lambda p: p.average_effectiveness)
        return (best.glyph_name, best.average_effectiveness)

    def get_patterns_for_glyph(self, glyph_name: str, tone: str) -> List[TemporalPattern]:
        """Get all temporal patterns for a glyph."""
        return [
            p for p in self.patterns.values()
            if p.glyph_name == glyph_name and p.tone == tone
        ]

    def get_time_based_insights(self, user_id: str) -> List[str]:
        """Generate insights about time-based patterns."""
        insights = []

        if not self.patterns:
            return ["Not enough temporal data yet. Patterns develop after more interactions."]

        # Find strong patterns
        strong_patterns = [
            p for p in self.patterns.values() if p.is_strong_pattern()]

        if strong_patterns:
            # Best time period
            best_by_period = {}
            for pattern in strong_patterns:
                period = pattern.time_period
                if period not in best_by_period or pattern.average_effectiveness > best_by_period[period][1]:
                    best_by_period[period] = (
                        pattern.glyph_name, pattern.average_effectiveness)

            if best_by_period:
                for period, (glyph, effectiveness) in best_by_period.items():
                    insights.append(
                        f"🕐 {period.capitalize()}: '{glyph}' is {effectiveness:.0%} effective"
                    )

        # Find time-dependent glyphs (different effectiveness by time)
        glyph_tone_periods = defaultdict(dict)
        for pattern in strong_patterns:
            key = f"{pattern.glyph_name}:{pattern.tone}"
            glyph_tone_periods[key][pattern.time_period] = pattern.average_effectiveness

        for key, period_scores in glyph_tone_periods.items():
            if len(period_scores) >= 2:
                scores = list(period_scores.values())
                variation = max(scores) - min(scores)
                if variation > 0.3:
                    best_time = max(period_scores, key=period_scores.get)
                    worst_time = min(period_scores, key=period_scores.get)
                    insights.append(
                        f"⏰ {key.split(':')[0]} works best in {best_time} ({period_scores[best_time]:.0%}), "
                        f"less in {worst_time} ({period_scores[worst_time]:.0%})"
                    )

        return insights

    def get_pattern_summary(self) -> Dict:
        """Get summary of all temporal patterns."""
        strong_patterns = [
            p for p in self.patterns.values() if p.is_strong_pattern()]

        return {
            "total_patterns": len(self.patterns),
            "strong_patterns": len(strong_patterns),
            "total_events": len(self.events),
            "time_periods_analyzed": list(set(p.time_period for p in self.patterns.values())),
            "average_pattern_confidence": statistics.mean(p.confidence for p in self.patterns.values()) if self.patterns else 0.0,
        }

    def export_patterns(self) -> Dict:
        """Export all patterns as dictionary."""
        return {
            pattern_key: {
                "glyph": pattern.glyph_name,
                "tone": pattern.tone,
                "period": pattern.time_period,
                "effectiveness": pattern.average_effectiveness,
                "acceptance_rate": pattern.get_acceptance_rate(),
                "uses": pattern.use_count,
                "confidence": pattern.confidence,
                "last_updated": pattern.last_updated.isoformat(),
            }
            for pattern_key, pattern in self.patterns.items()
        }


class CircadianGlyphSelector:
    """
    Selects glyphs based on circadian rhythms and temporal patterns.
    Adapts glyph selection to time of day, day of week, and seasonal patterns.
    """

    def __init__(self, temporal_analyzer: TemporalAnalyzer):
        """Initialize circadian selector with analyzer."""
        self.analyzer = temporal_analyzer
        self.user_circadian_profiles: Dict[str, Dict] = {}

    def build_user_profile(self, user_id: str) -> Dict:
        """Build circadian profile for a user from their temporal patterns."""
        profile = {
            "user_id": user_id,
            "morning_preferences": {},
            "afternoon_preferences": {},
            "evening_preferences": {},
            "night_preferences": {},
            "weekday_preferences": {},
            "weekend_preferences": {},
        }

        # Analyze temporal patterns
        for pattern in self.analyzer.patterns.values():
            if pattern.confidence < 0.5:
                continue

            period_key = f"{pattern.time_period}_preferences"
            glyph_key = f"{pattern.glyph_name}:{pattern.tone}"

            if period_key in profile:
                profile[period_key][glyph_key] = {
                    "effectiveness": pattern.average_effectiveness,
                    "acceptance_rate": pattern.get_acceptance_rate(),
                    "uses": pattern.use_count,
                }

        self.user_circadian_profiles[user_id] = profile
        return profile

    def select_glyph_for_moment(
        self,
        user_id: str,
        tone: str,
        current_time: Optional[datetime] = None
    ) -> Optional[Tuple[str, float]]:
        """Select best glyph for current moment considering circadian patterns."""
        if current_time is None:
            current_time = datetime.now()

        # Try temporal pattern first
        result = self.analyzer.get_best_glyph_for_time(tone, current_time)
        if result:
            return result

        # Fall back to day-of-week pattern
        day_period = "weekday" if current_time.weekday() < 5 else "weekend"
        return self.analyzer.get_best_glyph_for_period(tone, day_period)
