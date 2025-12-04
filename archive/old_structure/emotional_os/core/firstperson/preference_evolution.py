"""Preference Evolution Tracking for Phase 3.1.

Monitors how user preferences change over time, identifying emerging
trends, seasonal patterns, and long-term learning effects.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


class PreferenceType(Enum):
    """Categories of preferences tracked."""
    GLYPH = "glyph"              # Specific glyphs favored/avoided
    THEME = "theme"              # Topics user engages with
    STYLE = "style"              # Response style preferences
    TIMING = "timing"            # When user prefers interactions
    DEPTH = "depth"              # Shallow vs deep exploration


@dataclass
class PreferenceSnapshot:
    """Point-in-time preference state."""
    timestamp: datetime
    preference_type: PreferenceType
    item: str  # e.g., "glyph:sanctuary", "theme:grounding", "style:direct"
    score: float  # 0.0-1.0
    interactions: int = 0  # Times user has selected this


@dataclass
class PreferenceTrend:
    """How a preference is evolving over time."""
    preference: str
    first_score: float
    current_score: float
    direction: str  # "increasing", "decreasing", "stable"
    change_magnitude: float  # 0.0-1.0 (how much it changed)
    time_period: timedelta
    transition_points: List[Tuple[datetime, float]
                            ] = field(default_factory=list)


class PreferenceEvolutionTracker:
    """Tracks how user preferences change and evolve.

    Integrates with:
    - PreferenceManager (current preferences)
    - EmotionalProfileManager (emotional context of preferences)
    - TemporalPatterns (timing/recency effects)
    """

    def __init__(self, user_id: str):
        """Initialize preference evolution tracker.

        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        self.snapshots: List[PreferenceSnapshot] = []
        self.trends: Dict[str, PreferenceTrend] = {}
        self._latest_scores: Dict[str, float] = {}

    def record_preference(
        self,
        preference_type: PreferenceType,
        item: str,
        score: float,
        interactions: int = 1,
    ) -> None:
        """Record current preference state.

        Args:
            preference_type: Type of preference
            item: Specific item being rated
            score: Preference score 0.0-1.0
            interactions: Number of interactions
        """
        snapshot = PreferenceSnapshot(
            timestamp=datetime.now(),
            preference_type=preference_type,
            item=item,
            score=score,
            interactions=interactions,
        )

        self.snapshots.append(snapshot)

        # Update latest score
        pref_key = f"{preference_type.value}:{item}"
        old_score = self._latest_scores.get(pref_key)
        self._latest_scores[pref_key] = score

        # Update or create trend
        if pref_key not in self.trends:
            self.trends[pref_key] = PreferenceTrend(
                preference=pref_key,
                first_score=score,
                current_score=score,
                direction="stable",
                change_magnitude=0.0,
                time_period=timedelta(days=0),
            )
        else:
            trend = self.trends[pref_key]
            trend.current_score = score

            # Update direction
            change = score - trend.first_score
            trend.change_magnitude = abs(change)

            if change > 0.1:
                trend.direction = "increasing"
            elif change < -0.1:
                trend.direction = "decreasing"
            else:
                trend.direction = "stable"

            # Record transition point
            trend.transition_points.append((datetime.now(), score))

            # Calculate time period
            if len(trend.transition_points) > 1:
                first_time = trend.transition_points[0][0]
                last_time = trend.transition_points[-1][0]
                trend.time_period = last_time - first_time

    def get_emerging_preferences(
        self,
        days: int = 30,
        threshold: float = 0.3,
    ) -> List[Tuple[str, float, str]]:
        """Get preferences that are newly emerging (low score becoming higher).

        Args:
            days: Look back period
            threshold: Minimum emergence strength

        Returns:
            List of (preference, emergence_strength, description)
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_snapshots = [s for s in self.snapshots if s.timestamp > cutoff]

        if not recent_snapshots:
            return []

        # Find preferences that are increasing
        emerging = []

        for pref_key, trend in self.trends.items():
            if trend.direction == "increasing" and trend.change_magnitude >= threshold:
                # This is emerging
                emergence_strength = trend.change_magnitude
                description = f"{pref_key} growing ({trend.first_score:.2f} → {trend.current_score:.2f})"

                emerging.append((pref_key, emergence_strength, description))

        # Sort by emergence strength
        emerging.sort(key=lambda x: x[1], reverse=True)

        return emerging

    def get_fading_preferences(
        self,
        days: int = 30,
        threshold: float = 0.3,
    ) -> List[Tuple[str, float, str]]:
        """Get preferences that are becoming less important (declining).

        Args:
            days: Look back period
            threshold: Minimum decline strength

        Returns:
            List of (preference, decline_strength, description)
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_snapshots = [s for s in self.snapshots if s.timestamp > cutoff]

        if not recent_snapshots:
            return []

        fading = []

        for pref_key, trend in self.trends.items():
            if trend.direction == "decreasing" and trend.change_magnitude >= threshold:
                decline_strength = trend.change_magnitude
                description = f"{pref_key} declining ({trend.first_score:.2f} → {trend.current_score:.2f})"

                fading.append((pref_key, decline_strength, description))

        fading.sort(key=lambda x: x[1], reverse=True)

        return fading

    def get_stable_preferences(self, threshold: float = 0.1) -> List[Tuple[str, float]]:
        """Get preferences that remain consistent over time.

        Args:
            threshold: Maximum change for "stable" classification

        Returns:
            List of (preference, current_score) sorted by score
        """
        stable = []

        for pref_key, trend in self.trends.items():
            if trend.change_magnitude < threshold and trend.current_score > 0.3:
                stable.append((pref_key, trend.current_score))

        stable.sort(key=lambda x: x[1], reverse=True)

        return stable

    def get_preference_volatility(self) -> Dict[str, float]:
        """Calculate volatility (how much variation) for each preference.

        Returns:
            Dictionary of preference -> volatility score 0.0-1.0
        """
        volatility = {}

        # Group snapshots by preference
        pref_groups: Dict[str, List[float]] = {}

        for snapshot in self.snapshots:
            pref_key = f"{snapshot.preference_type.value}:{snapshot.item}"
            if pref_key not in pref_groups:
                pref_groups[pref_key] = []
            pref_groups[pref_key].append(snapshot.score)

        # Calculate volatility for each
        for pref_key, scores in pref_groups.items():
            if len(scores) < 2:
                volatility[pref_key] = 0.0
                continue

            # Simple metric: std dev normalized
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            std_dev = variance ** 0.5

            # Normalize to 0-1 range (std_dev can't exceed ~0.5 for 0-1 scale)
            volatility[pref_key] = min(1.0, std_dev * 2)

        return volatility

    def get_preference_acceleration(self) -> Dict[str, float]:
        """Calculate how rapidly preferences are changing (acceleration).

        Returns:
            Dictionary of preference -> acceleration score
        """
        acceleration = {}

        for pref_key, trend in self.trends.items():
            if len(trend.transition_points) < 3:
                acceleration[pref_key] = 0.0
                continue

            # Calculate slopes over time windows
            points = trend.transition_points

            # Recent slope
            recent_change = points[-1][1] - points[-2][1]

            # Historical slope
            historical_change = (points[-1][1] - points[0][1]) / len(points)

            # Acceleration = how much recent change differs from average
            accel = recent_change - historical_change

            acceleration[pref_key] = min(1.0, max(-1.0, accel))

        return acceleration

    def predict_preference_trajectory(
        self,
        preference: str,
        days_ahead: int = 30,
    ) -> Optional[Dict]:
        """Predict where a preference might be headed.

        Args:
            preference: Preference key (e.g., "glyph:sanctuary")
            days_ahead: How many days to project forward

        Returns:
            Dictionary with projection or None if insufficient data
        """
        if preference not in self.trends:
            return None

        trend = self.trends[preference]

        if len(trend.transition_points) < 2:
            return None

        # Simple linear projection based on recent trend
        recent_points = trend.transition_points[-10:]  # Last 10 data points

        if len(recent_points) < 2:
            return None

        # Calculate average rate of change
        time_diffs = []
        score_diffs = []

        for i in range(len(recent_points) - 1):
            time_delta = (recent_points[i + 1][0] -
                          recent_points[i][0]).total_seconds()
            score_delta = recent_points[i + 1][1] - recent_points[i][1]

            if time_delta > 0:
                time_diffs.append(time_delta)
                score_diffs.append(score_delta)

        if not time_diffs:
            return None

        # Change per observation
        avg_rate = sum(score_diffs) / len(score_diffs)

        # Project forward
        current_score = trend.current_score
        projected_score = current_score + \
            (avg_rate * (days_ahead / 30))  # Normalize to 30 days
        projected_score = max(0.0, min(1.0, projected_score))  # Clamp to 0-1

        return {
            "preference": preference,
            "current_score": current_score,
            "projected_score": projected_score,
            "days_ahead": days_ahead,
            "direction": trend.direction,
            # More data = higher confidence
            "confidence": min(1.0, len(recent_points) / 20),
        }

    def get_preference_report(self, lookback_days: int = 90) -> Dict:
        """Generate comprehensive preference evolution report.

        Args:
            lookback_days: Period to analyze

        Returns:
            Dictionary with all preference analytics
        """
        cutoff = datetime.now() - timedelta(days=lookback_days)

        return {
            "user_id": self.user_id,
            "lookback_days": lookback_days,
            "total_preferences": len(self.trends),
            "emerging_preferences": self.get_emerging_preferences(lookback_days, 0.2),
            "fading_preferences": self.get_fading_preferences(lookback_days, 0.2),
            "stable_preferences": self.get_stable_preferences(),
            "volatility": {
                k: v for k, v in self.get_preference_volatility().items()
                if v > 0.1  # Only show volatile ones
            },
            "acceleration": {
                k: v for k, v in self.get_preference_acceleration().items()
                if abs(v) > 0.05  # Only show accelerating ones
            },
        }

    def identify_preference_clusters(self) -> List[Tuple[str, List[str]]]:
        """Identify which preferences tend to co-occur (clusters).

        Returns:
            List of (cluster_name, [preferences in cluster])
        """
        # Find preferences that co-occur in same session/period
        clusters = []

        # Group by type
        by_type: Dict[str, List[str]] = {}

        for pref_key in self.trends.keys():
            pref_type = pref_key.split(":")[0]
            if pref_type not in by_type:
                by_type[pref_type] = []
            by_type[pref_type].append(pref_key)

        for pref_type, prefs in by_type.items():
            if len(prefs) > 1:
                # Find which ones have positive scores
                high_prefs = [
                    p for p in prefs if self._latest_scores.get(p, 0) > 0.5]
                if len(high_prefs) >= 2:
                    clusters.append((f"{pref_type}_cluster", high_prefs))

        return clusters

    def export_evolution(self) -> Dict:
        """Export all preference evolution data.

        Returns:
            Dictionary suitable for storage
        """
        return {
            "user_id": self.user_id,
            "snapshots_count": len(self.snapshots),
            "trends": {
                k: {
                    "direction": v.direction,
                    "first_score": v.first_score,
                    "current_score": v.current_score,
                    "change_magnitude": v.change_magnitude,
                }
                for k, v in self.trends.items()
            },
            "latest_scores": self._latest_scores,
        }
