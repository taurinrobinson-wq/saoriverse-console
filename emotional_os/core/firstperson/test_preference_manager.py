"""
Tests for Phase 2.4 Preference Manager
"""

import pytest
from datetime import datetime, timedelta
from emotional_os.core.firstperson.preference_manager import (
    GlyphPreference,
    PreferenceLevel,
    UserPreferences,
    PreferenceManager
)


class TestGlyphPreference:
    """Test individual glyph preference tracking."""

    def test_creation(self):
        """Test creating a glyph preference."""
        pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8
        )
        assert pref.glyph_name == "warmth"
        assert pref.preference_level == PreferenceLevel.NEUTRAL
        assert pref.effectiveness_score == 0.5

    def test_effectiveness_percentage(self):
        """Test effectiveness percentage calculation."""
        pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8,
            effectiveness_score=0.75
        )
        assert pref.get_effectiveness_percentage() == 75.0

    def test_acceptance_rate(self):
        """Test acceptance rate calculation."""
        pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8,
            uses_count=10,
            accepts_count=7
        )
        assert pref.get_acceptance_rate() == 0.7

    def test_rejection_rate(self):
        """Test rejection rate calculation."""
        pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8,
            uses_count=10,
            rejections_count=3
        )
        assert pref.get_rejection_rate() == 0.3

    def test_zero_uses(self):
        """Test rates with zero uses."""
        pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8
        )
        assert pref.get_acceptance_rate() == 0.0
        assert pref.get_rejection_rate() == 0.0

    def test_is_stale(self):
        """Test staleness detection."""
        old_pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8,
            last_used=datetime.now() - timedelta(days=40)
        )
        assert old_pref.is_stale(days=30) is True

        recent_pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8,
            last_used=datetime.now() - timedelta(days=10)
        )
        assert recent_pref.is_stale(days=30) is False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8,
            preference_level=PreferenceLevel.LIKED,
            effectiveness_score=0.75,
            uses_count=10,
            accepts_count=8
        )
        data = pref.to_dict()
        assert data['glyph_name'] == "warmth"
        assert data['preference_level'] == "LIKED"
        assert data['effectiveness_percentage'] == 75.0
        assert data['acceptance_rate'] == 0.8


class TestUserPreferences:
    """Test user-level preference aggregation."""

    def test_creation(self):
        """Test creating user preferences."""
        prefs = UserPreferences(user_id="user123")
        assert prefs.user_id == "user123"
        assert len(prefs.preferences) == 0

    def test_add_preference(self):
        """Test adding a preference."""
        prefs = UserPreferences(user_id="user123")
        pref = GlyphPreference(
            glyph_name="warmth",
            tone="compassionate",
            arousal=0.4,
            valence=0.8
        )
        prefs.add_preference(pref)
        assert len(prefs.preferences) == 1
        assert "warmth:compassionate" in prefs.preferences

    def test_record_use_acceptance(self):
        """Test recording accepted glyph use."""
        prefs = UserPreferences(user_id="user123")
        prefs.record_use("warmth", "compassionate", accepted=True)

        pref = prefs.preferences["warmth:compassionate"]
        assert pref.uses_count == 1
        assert pref.accepts_count == 1
        assert pref.effectiveness_score == 0.55  # 0.5 + 0.05

    def test_record_use_rejection(self):
        """Test recording rejected glyph use."""
        prefs = UserPreferences(user_id="user123")
        prefs.record_use("warmth", "compassionate", accepted=False)

        pref = prefs.preferences["warmth:compassionate"]
        assert pref.uses_count == 1
        assert pref.rejections_count == 1
        assert pref.effectiveness_score == 0.45  # 0.5 - 0.05

    def test_preference_upgrade(self):
        """Test automatic preference upgrade on consistent acceptance."""
        prefs = UserPreferences(user_id="user123")

        # Record 3 acceptances to meet threshold
        for _ in range(3):
            prefs.record_use("warmth", "compassionate", accepted=True)

        pref = prefs.preferences["warmth:compassionate"]
        assert pref.preference_level == PreferenceLevel.LIKED

    def test_preference_downgrade(self):
        """Test automatic preference downgrade on consistent rejection."""
        prefs = UserPreferences(user_id="user123")

        # Record 3 rejections to meet threshold
        for _ in range(3):
            prefs.record_use("coldness", "harsh", accepted=False)

        pref = prefs.preferences["coldness:harsh"]
        assert pref.preference_level == PreferenceLevel.DISLIKED

    def test_manual_override(self):
        """Test manual glyph override."""
        prefs = UserPreferences(user_id="user123")
        prefs.set_manual_override(
            "compassionate", "warmth", notes="My favorite")

        assert prefs.manual_overrides["compassionate"] == "warmth"
        assert "warmth:compassionate" in prefs.preferences
        assert prefs.preferences["warmth:compassionate"].manual_override is True
        assert prefs.preferences["warmth:compassionate"].notes == "My favorite"

    def test_get_best_glyph_for_tone_with_override(self):
        """Test getting best glyph respects manual override."""
        prefs = UserPreferences(user_id="user123")

        # Add some preferences
        prefs.record_use("warmth", "compassionate", accepted=True)
        prefs.record_use("brightness", "compassionate", accepted=False)

        # Without override, warmth should win
        assert prefs.get_best_glyph_for_tone("compassionate") == "warmth"

        # With override, alternative should win
        prefs.set_manual_override("compassionate", "brightness")
        assert prefs.get_best_glyph_for_tone("compassionate") == "brightness"

    def test_get_top_glyphs(self):
        """Test getting top glyphs by effectiveness."""
        prefs = UserPreferences(user_id="user123")

        # Create glyphs with different effectiveness
        pref1 = GlyphPreference("glyph1", "tone1", 0.5,
                                0.5, effectiveness_score=0.9)
        pref2 = GlyphPreference("glyph2", "tone1", 0.5,
                                0.5, effectiveness_score=0.7)
        pref3 = GlyphPreference("glyph3", "tone1", 0.5,
                                0.5, effectiveness_score=0.5)

        prefs.add_preference(pref1)
        prefs.add_preference(pref2)
        prefs.add_preference(pref3)

        top = prefs.get_top_glyphs(limit=2)
        assert len(top) == 2
        assert top[0][0] == "glyph1"
        assert top[1][0] == "glyph2"

    def test_get_bottom_glyphs(self):
        """Test getting bottom glyphs by effectiveness."""
        prefs = UserPreferences(user_id="user123")

        pref1 = GlyphPreference("glyph1", "tone1", 0.5,
                                0.5, effectiveness_score=0.9)
        pref2 = GlyphPreference("glyph2", "tone1", 0.5,
                                0.5, effectiveness_score=0.3)

        prefs.add_preference(pref1)
        prefs.add_preference(pref2)

        bottom = prefs.get_bottom_glyphs(limit=1)
        assert bottom[0][0] == "glyph2"

    def test_preference_summary(self):
        """Test preference summary generation."""
        prefs = UserPreferences(user_id="user123")
        prefs.record_use("warmth", "compassionate", accepted=True)
        prefs.record_use("brightness", "hopeful", accepted=True)
        prefs.record_use("coldness", "harsh", accepted=False)

        summary = prefs.get_preference_summary()
        assert summary['total_glyphs_tracked'] == 3
        assert summary['total_uses'] == 3
        assert summary['total_acceptances'] == 2

    def test_get_insights_empty(self):
        """Test insights with no data."""
        prefs = UserPreferences(user_id="user123")
        insights = prefs.get_insights()
        assert len(insights) > 0
        assert "No preference data yet" in insights[0]

    def test_get_insights_with_data(self):
        """Test insights with preference data."""
        prefs = UserPreferences(user_id="user123")

        # Create strong pattern
        for _ in range(5):
            prefs.record_use("warmth", "compassionate", accepted=True)

        insights = prefs.get_insights()
        assert len(insights) > 0
        assert any(
            "Excellent" in insight or "excellent" in insight for insight in insights)

    def test_export_json(self):
        """Test JSON export."""
        prefs = UserPreferences(user_id="user123")
        prefs.record_use("warmth", "compassionate", accepted=True)

        json_str = prefs.export_json()
        assert isinstance(json_str, str)
        assert "user123" in json_str
        assert "warmth" in json_str
        assert "summary" in json_str
        assert "insights" in json_str


class TestPreferenceManager:
    """Test global preference management."""

    def test_creation(self):
        """Test creating preference manager."""
        manager = PreferenceManager()
        assert len(manager.user_preferences) == 0

    def test_get_user_preferences(self):
        """Test getting user preferences."""
        manager = PreferenceManager()
        prefs = manager.get_user_preferences("user1")
        assert prefs.user_id == "user1"

        # Getting again returns same instance
        prefs2 = manager.get_user_preferences("user1")
        assert prefs is prefs2

    def test_record_glyph_use(self):
        """Test recording glyph use through manager."""
        manager = PreferenceManager()
        manager.record_glyph_use(
            "user1", "warmth", "compassionate", accepted=True)

        prefs = manager.get_user_preferences("user1")
        assert prefs.preferences["warmth:compassionate"].uses_count == 1

    def test_set_manual_override(self):
        """Test setting manual override through manager."""
        manager = PreferenceManager()
        manager.set_manual_override(
            "user1", "compassionate", "warmth", "My favorite")

        prefs = manager.get_user_preferences("user1")
        assert prefs.manual_overrides["compassionate"] == "warmth"

    def test_get_recommendation(self):
        """Test getting recommendation through manager."""
        manager = PreferenceManager()
        manager.record_glyph_use(
            "user1", "warmth", "compassionate", accepted=True)
        manager.record_glyph_use(
            "user1", "brightness", "compassionate", accepted=False)

        rec = manager.get_recommendation("user1", "compassionate")
        assert rec == "warmth"

    def test_get_user_summary(self):
        """Test getting user summary through manager."""
        manager = PreferenceManager()
        manager.record_glyph_use(
            "user1", "warmth", "compassionate", accepted=True)

        summary = manager.get_user_summary("user1")
        assert summary['total_uses'] == 1
        assert summary['total_acceptances'] == 1

    def test_get_user_insights(self):
        """Test getting user insights through manager."""
        manager = PreferenceManager()
        manager.record_glyph_use(
            "user1", "warmth", "compassionate", accepted=True)

        insights = manager.get_user_insights("user1")
        assert len(insights) > 0

    def test_export_user_preferences(self):
        """Test exporting user preferences through manager."""
        manager = PreferenceManager()
        manager.record_glyph_use(
            "user1", "warmth", "compassionate", accepted=True)

        json_str = manager.export_user_preferences("user1")
        assert isinstance(json_str, str)
        assert "user1" in json_str

    def test_get_all_user_summaries(self):
        """Test getting all user summaries."""
        manager = PreferenceManager()
        manager.record_glyph_use(
            "user1", "warmth", "compassionate", accepted=True)
        manager.record_glyph_use(
            "user2", "brightness", "hopeful", accepted=True)

        summaries = manager.get_all_user_summaries()
        assert len(summaries) == 2
        assert "user1" in summaries
        assert "user2" in summaries

    def test_multiple_users_isolation(self):
        """Test that user preferences are isolated."""
        manager = PreferenceManager()
        manager.record_glyph_use(
            "user1", "warmth", "compassionate", accepted=True)
        manager.record_glyph_use("user2", "coldness", "harsh", accepted=False)

        prefs1 = manager.get_user_preferences("user1")
        prefs2 = manager.get_user_preferences("user2")

        assert "warmth:compassionate" in prefs1.preferences
        assert "coldness:harsh" in prefs2.preferences
        assert "coldness:harsh" not in prefs1.preferences
        assert "warmth:compassionate" not in prefs2.preferences
