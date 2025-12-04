"""
Phase 2.4: User Preference Manager
Tracks and manages user glyph preferences, effectiveness scores, and overrides.
Provides data export and visualization capabilities.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from enum import Enum


class PreferenceLevel(Enum):
    """Preference strength levels for user-glyph relationships."""
    STRONGLY_DISLIKED = -2
    DISLIKED = -1
    NEUTRAL = 0
    LIKED = 1
    STRONGLY_LIKED = 2


@dataclass
class GlyphPreference:
    """Represents a single user's preference for a glyph."""
    glyph_name: str
    tone: str
    arousal: float
    valence: float
    preference_level: PreferenceLevel = PreferenceLevel.NEUTRAL
    effectiveness_score: float = 0.5  # 0.0-1.0 scale
    uses_count: int = 0
    rejections_count: int = 0
    accepts_count: int = 0
    last_used: Optional[datetime] = None
    last_rejected: Optional[datetime] = None
    manual_override: bool = False
    notes: str = ""

    def get_effectiveness_percentage(self) -> float:
        """Return effectiveness as percentage."""
        return round(self.effectiveness_score * 100, 1)

    def get_acceptance_rate(self) -> float:
        """Calculate acceptance rate."""
        if self.uses_count == 0:
            return 0.0
        return round(self.accepts_count / self.uses_count, 2)

    def get_rejection_rate(self) -> float:
        """Calculate rejection rate."""
        if self.uses_count == 0:
            return 0.0
        return round(self.rejections_count / self.uses_count, 2)

    def is_stale(self, days: int = 30) -> bool:
        """Check if preference data is stale (not used recently)."""
        if self.last_used is None:
            return True
        return datetime.now() - self.last_used > timedelta(days=days)

    def to_dict(self) -> dict:
        """Convert to dictionary with serializable types."""
        data = asdict(self)
        data['preference_level'] = self.preference_level.name
        data['last_used'] = self.last_used.isoformat() if self.last_used else None
        data['last_rejected'] = self.last_rejected.isoformat(
        ) if self.last_rejected else None
        data['effectiveness_percentage'] = self.get_effectiveness_percentage()
        data['acceptance_rate'] = self.get_acceptance_rate()
        data['rejection_rate'] = self.get_rejection_rate()
        return data


@dataclass
class UserPreferences:
    """Aggregated preference profile for a single user."""
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    preferences: Dict[str, GlyphPreference] = field(default_factory=dict)
    favorite_glyphs: List[str] = field(default_factory=list)
    disliked_glyphs: List[str] = field(default_factory=list)
    manual_overrides: Dict[str, str] = field(
        default_factory=dict)  # tone -> glyph override
    tone_preferences: Dict[str, PreferenceLevel] = field(default_factory=dict)
    arousal_threshold: float = 0.5  # Cutoff for high arousal responses
    valence_threshold: float = 0.5  # Cutoff for positive/negative responses

    def add_preference(self, preference: GlyphPreference) -> None:
        """Add or update a glyph preference."""
        key = self._make_key(preference.glyph_name, preference.tone)
        self.preferences[key] = preference
        self.updated_at = datetime.now()
        self._update_lists()

    def record_use(self, glyph_name: str, tone: str, accepted: bool = False) -> None:
        """Record that a glyph was used and whether it was accepted."""
        key = self._make_key(glyph_name, tone)
        if key not in self.preferences:
            self.preferences[key] = GlyphPreference(
                glyph_name=glyph_name,
                tone=tone,
                arousal=0.5,
                valence=0.5
            )

        pref = self.preferences[key]
        pref.uses_count += 1
        pref.last_used = datetime.now()

        if accepted:
            pref.accepts_count += 1
            pref.effectiveness_score = min(
                1.0, pref.effectiveness_score + 0.05)
            # Upgrade preference if consistently accepted
            if pref.get_acceptance_rate() > 0.8 and pref.uses_count >= 3:
                if pref.preference_level.value < PreferenceLevel.STRONGLY_LIKED.value:
                    pref.preference_level = PreferenceLevel(
                        pref.preference_level.value + 1)
        else:
            pref.rejections_count += 1
            pref.effectiveness_score = max(
                0.0, pref.effectiveness_score - 0.05)
            pref.last_rejected = datetime.now()
            # Downgrade preference if consistently rejected
            if pref.get_rejection_rate() > 0.5 and pref.uses_count >= 3:
                if pref.preference_level.value > PreferenceLevel.STRONGLY_DISLIKED.value:
                    pref.preference_level = PreferenceLevel(
                        pref.preference_level.value - 1)

        self.updated_at = datetime.now()
        self._update_lists()

    def set_manual_override(self, tone: str, glyph_name: str, notes: str = "") -> None:
        """Manually override preferred glyph for a specific tone."""
        self.manual_overrides[tone] = glyph_name

        # Update preference record
        key = self._make_key(glyph_name, tone)
        if key not in self.preferences:
            self.preferences[key] = GlyphPreference(
                glyph_name=glyph_name,
                tone=tone,
                arousal=0.5,
                valence=0.5,
                manual_override=True,
                notes=notes
            )
        else:
            self.preferences[key].manual_override = True
            self.preferences[key].notes = notes

        self.updated_at = datetime.now()
        self._update_lists()

    def get_best_glyph_for_tone(self, tone: str) -> Optional[str]:
        """Get the best glyph for a given tone based on preferences."""
        # Check manual override first
        if tone in self.manual_overrides:
            return self.manual_overrides[tone]

        # Find best glyph by effectiveness score for this tone
        best_glyph = None
        best_score = -float('inf')

        for key, pref in self.preferences.items():
            if pref.tone == tone and pref.effectiveness_score > best_score:
                best_score = pref.effectiveness_score
                best_glyph = pref.glyph_name

        return best_glyph

    def get_top_glyphs(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get top glyphs by effectiveness score."""
        sorted_prefs = sorted(
            self.preferences.values(),
            key=lambda p: (p.effectiveness_score, p.uses_count),
            reverse=True
        )
        return [(p.glyph_name, p.effectiveness_score) for p in sorted_prefs[:limit]]

    def get_bottom_glyphs(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get bottom glyphs by effectiveness score."""
        sorted_prefs = sorted(
            self.preferences.values(),
            key=lambda p: (p.effectiveness_score, p.uses_count),
            reverse=False
        )
        return [(p.glyph_name, p.effectiveness_score) for p in sorted_prefs[:limit]]

    def get_preference_summary(self) -> Dict:
        """Get summary statistics of all preferences."""
        if not self.preferences:
            return {
                'total_glyphs_tracked': 0,
                'average_effectiveness': 0.0,
                'favorite_count': 0,
                'disliked_count': 0,
                'total_uses': 0,
                'total_acceptances': 0,
                'overall_acceptance_rate': 0.0
            }

        prefs = list(self.preferences.values())
        total_uses = sum(p.uses_count for p in prefs)
        total_acceptances = sum(p.accepts_count for p in prefs)

        return {
            'total_glyphs_tracked': len(self.preferences),
            'average_effectiveness': round(
                sum(p.effectiveness_score for p in prefs) / len(prefs), 2
            ),
            'favorite_count': len(self.favorite_glyphs),
            'disliked_count': len(self.disliked_glyphs),
            'total_uses': total_uses,
            'total_acceptances': total_acceptances,
            'overall_acceptance_rate': round(
                total_acceptances / total_uses if total_uses > 0 else 0.0, 2
            )
        }

    def get_insights(self) -> List[str]:
        """Generate human-readable insights about user preferences."""
        insights = []
        summary = self.get_preference_summary()

        if summary['total_glyphs_tracked'] == 0:
            return ["No preference data yet. Start using glyphs to build your profile!"]

        # Insight 1: Overall effectiveness
        avg_eff = summary['average_effectiveness']
        if avg_eff > 0.7:
            insights.append(
                f"🎯 Excellent match! Your glyphs are {int(avg_eff * 100)}% effective.")
        elif avg_eff > 0.5:
            insights.append(
                f"✓ Good fit. Your glyphs are {int(avg_eff * 100)}% effective.")
        else:
            insights.append(
                f"◇ Learning stage. Try different glyphs to improve (currently {int(avg_eff * 100)}%).")

        # Insight 2: Acceptance rate
        accept_rate = summary['overall_acceptance_rate']
        if accept_rate > 0.75:
            insights.append(
                f"🌟 You're accepting responses at a {int(accept_rate * 100)}% rate - great resonance!")
        elif accept_rate > 0.5:
            insights.append(
                f"Good rapport. You accept responses {int(accept_rate * 100)}% of the time.")

        # Insight 3: Favorites
        if self.favorite_glyphs:
            insights.append(
                f"💝 Your favorite glyphs: {', '.join(self.favorite_glyphs[:3])}")

        # Insight 4: Disliked
        if self.disliked_glyphs:
            insights.append(
                f"✗ Rarely used: {', '.join(self.disliked_glyphs[:2])}")

        # Insight 5: Manual overrides
        if self.manual_overrides:
            insights.append(
                f"⚙️ You've customized {len(self.manual_overrides)} tone(s)")

        return insights

    def export_json(self) -> str:
        """Export preferences as JSON."""
        data = {
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'preferences': {k: v.to_dict() for k, v in self.preferences.items()},
            'favorite_glyphs': self.favorite_glyphs,
            'disliked_glyphs': self.disliked_glyphs,
            'manual_overrides': self.manual_overrides,
            'tone_preferences': {k: v.name for k, v in self.tone_preferences.items()},
            'summary': self.get_preference_summary(),
            'insights': self.get_insights()
        }
        return json.dumps(data, indent=2)

    def _make_key(self, glyph_name: str, tone: str) -> str:
        """Create unique key for preference lookup."""
        return f"{glyph_name}:{tone}"

    def _update_lists(self) -> None:
        """Update favorite and disliked glyph lists based on preferences."""
        self.favorite_glyphs = [
            pref.glyph_name for pref in self.preferences.values()
            if pref.preference_level == PreferenceLevel.STRONGLY_LIKED
        ]
        self.disliked_glyphs = [
            pref.glyph_name for pref in self.preferences.values()
            if pref.preference_level == PreferenceLevel.STRONGLY_DISLIKED
        ]


class PreferenceManager:
    """Manages all user preferences globally."""

    def __init__(self):
        """Initialize preference manager."""
        self.user_preferences: Dict[str, UserPreferences] = {}

    def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get or create preferences for a user."""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences(user_id=user_id)
        return self.user_preferences[user_id]

    def record_glyph_use(
        self,
        user_id: str,
        glyph_name: str,
        tone: str,
        accepted: bool = False
    ) -> None:
        """Record a glyph use and whether it was accepted."""
        user_prefs = self.get_user_preferences(user_id)
        user_prefs.record_use(glyph_name, tone, accepted)

    def set_manual_override(
        self,
        user_id: str,
        tone: str,
        glyph_name: str,
        notes: str = ""
    ) -> None:
        """Set manual glyph override for a user."""
        user_prefs = self.get_user_preferences(user_id)
        user_prefs.set_manual_override(tone, glyph_name, notes)

    def get_recommendation(self, user_id: str, tone: str) -> Optional[str]:
        """Get recommended glyph for a user and tone."""
        user_prefs = self.get_user_preferences(user_id)
        return user_prefs.get_best_glyph_for_tone(tone)

    def get_user_summary(self, user_id: str) -> Dict:
        """Get preference summary for a user."""
        user_prefs = self.get_user_preferences(user_id)
        return user_prefs.get_preference_summary()

    def get_user_insights(self, user_id: str) -> List[str]:
        """Get insights for a user."""
        user_prefs = self.get_user_preferences(user_id)
        return user_prefs.get_insights()

    def export_user_preferences(self, user_id: str) -> str:
        """Export user preferences as JSON."""
        user_prefs = self.get_user_preferences(user_id)
        return user_prefs.export_json()

    def get_all_user_summaries(self) -> Dict[str, Dict]:
        """Get summaries for all users."""
        return {
            user_id: prefs.get_preference_summary()
            for user_id, prefs in self.user_preferences.items()
        }
