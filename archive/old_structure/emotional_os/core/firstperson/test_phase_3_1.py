"""Comprehensive test suite for Phase 3.1: Memory Integration.

Tests emotional profile management, session coherence tracking, and
preference evolution over time.
"""

import pytest
from datetime import datetime, timedelta
from emotional_os.core.firstperson.emotional_profile import (
    EmotionalProfileManager,
    EmotionalTone,
    EmotionalSnapshot,
    RecurringTheme,
)
from emotional_os.core.firstperson.session_coherence import (
    SessionCoherenceTracker,
    SessionQuality,
    ThemeSegment,
)
from emotional_os.core.firstperson.preference_evolution import (
    PreferenceEvolutionTracker,
    PreferenceType,
    PreferenceSnapshot,
)


# ============================================================================
# EMOTIONAL PROFILE TESTS
# ============================================================================

class TestEmotionalProfileManager:
    """Test emotional profile creation and management."""

    def test_profile_initialization(self):
        """Test creating a new emotional profile."""
        manager = EmotionalProfileManager("user_123")

        assert manager.user_id == "user_123"
        assert manager.profile.user_id == "user_123"
        assert len(manager.profile.snapshots) == 0
        assert len(manager.profile.recurring_themes) == 0

    def test_record_single_interaction(self):
        """Test recording a single user interaction."""
        manager = EmotionalProfileManager("user_123")

        manager.record_interaction(
            tone=EmotionalTone.GROUNDED,
            intensity="medium",
            themes=["self-compassion", "acceptance"],
            glyph_response="Sanctuary",
            user_satisfaction=0.8,
        )

        assert len(manager.profile.snapshots) == 1
        assert manager.profile.primary_tones[EmotionalTone.GROUNDED] == 1
        assert "self-compassion" in manager.profile.recurring_themes
        assert "acceptance" in manager.profile.recurring_themes
        # Score is exponential moving average (0.7*0 + 0.3*0.8 = 0.24)
        assert manager.profile.preferred_glyph_types["Sanctuary"] == 0.24

    def test_record_multiple_interactions(self):
        """Test recording multiple interactions and tracking patterns."""
        manager = EmotionalProfileManager("user_123")

        # Record grounded interactions
        for _ in range(3):
            manager.record_interaction(
                tone=EmotionalTone.GROUNDED,
                intensity="low",
                themes=["safety", "grounding"],
                glyph_response="Ground",
                user_satisfaction=0.9,
            )

        # Record anxious interactions
        for _ in range(2):
            manager.record_interaction(
                tone=EmotionalTone.ANXIOUS,
                intensity="high",
                themes=["worry", "overwhelm"],
                glyph_response="Sanctuary",
                user_satisfaction=0.7,
            )

        assert len(manager.profile.snapshots) == 5
        assert manager.profile.primary_tones[EmotionalTone.GROUNDED] == 3
        assert manager.profile.primary_tones[EmotionalTone.ANXIOUS] == 2
        assert manager.profile.recurring_themes["safety"].occurrences == 3
        assert manager.profile.recurring_themes["worry"].occurrences == 2

    def test_emotional_trajectory(self):
        """Test retrieving emotional tone trajectory over time."""
        manager = EmotionalProfileManager("user_123")

        tones = [
            EmotionalTone.ANXIOUS,
            EmotionalTone.ANXIOUS,
            EmotionalTone.REFLECTIVE,
            EmotionalTone.GROUNDED,
        ]

        for tone in tones:
            manager.record_interaction(
                tone=tone,
                intensity="medium",
                themes=["test"],
                glyph_response="Test",
            )

        trajectory = manager.get_emotional_trajectory(days=30)
        assert len(trajectory) == 4
        assert trajectory[0][1] == EmotionalTone.ANXIOUS
        assert trajectory[3][1] == EmotionalTone.GROUNDED

    def test_dominant_themes(self):
        """Test retrieving dominant themes."""
        manager = EmotionalProfileManager("user_123")

        # Create frequency variation in themes
        themes_by_count = {
            "grounding": 10,
            "safety": 7,
            "connection": 5,
            "growth": 3,
            "vulnerability": 1,
        }

        for theme, count in themes_by_count.items():
            for _ in range(count):
                manager.record_interaction(
                    tone=EmotionalTone.GROUNDED,
                    intensity="medium",
                    themes=[theme],
                    glyph_response="Test",
                )

        dominant = manager.get_dominant_themes(limit=3)

        assert len(dominant) == 3
        assert dominant[0][0] == "grounding"
        assert dominant[0][1] == 10
        assert dominant[1][0] == "safety"
        assert dominant[2][0] == "connection"

    def test_temporal_pattern_analysis(self):
        """Test analyzing when themes emerge."""
        manager = EmotionalProfileManager("user_123")

        # Record interactions at specific times
        base_time = datetime.now().replace(hour=9, minute=0)

        for i in range(5):
            # Mock datetime by recording and verifying manually
            manager.record_interaction(
                tone=EmotionalTone.ANXIOUS,
                intensity="high",
                themes=["morning_anxiety"],
                glyph_response="Test",
            )

        # Analyze temporal pattern
        pattern = manager.get_time_patterns("morning_anxiety")
        assert pattern is not None
        assert pattern.theme == "morning_anxiety"
        assert pattern.predictability_score >= 0

    def test_predict_upcoming_themes(self):
        """Test theme prediction based on patterns."""
        manager = EmotionalProfileManager("user_123")

        # Record multiple interactions to establish pattern
        for _ in range(5):
            manager.record_interaction(
                tone=EmotionalTone.ANXIOUS,
                intensity="high",
                themes=["anxiety"],
                glyph_response="Test",
            )

        # Get predictions
        predictions = manager.predict_upcoming_themes(lookahead_hours=4)

        # Should return list of (theme, probability) tuples
        assert isinstance(predictions, list)
        if predictions:  # If pattern data available
            assert isinstance(predictions[0], tuple)
            assert 0 <= predictions[0][1] <= 1.0

    def test_session_coherence_calculation(self):
        """Test session coherence scoring."""
        manager = EmotionalProfileManager("user_123")

        # Build up a profile
        for _ in range(3):
            manager.record_interaction(
                tone=EmotionalTone.GROUNDED,
                intensity="medium",
                themes=["grounding"],
                glyph_response="Test",
            )

        # Calculate coherence
        coherence = manager.get_session_coherence()

        assert 0 <= coherence <= 1.0

    def test_profile_export(self):
        """Test exporting profile for storage."""
        manager = EmotionalProfileManager("user_123")

        manager.record_interaction(
            tone=EmotionalTone.GROUNDED,
            intensity="low",
            themes=["test"],
            glyph_response="Test",
            user_satisfaction=0.8,
        )

        export = manager.export_profile()

        assert export["user_id"] == "user_123"
        assert "grounded" in export["primary_tones"]
        assert export["session_count"] == 0


# ============================================================================
# SESSION COHERENCE TESTS
# ============================================================================

class TestSessionCoherenceTracker:
    """Test session coherence tracking and quality assessment."""

    def test_session_initialization(self):
        """Test creating a new session coherence tracker."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        assert tracker.session_id == "session_001"
        assert tracker.user_id == "user_123"
        assert tracker.coherence.turn_count == 0
        assert len(tracker.coherence.theme_segments) == 0

    def test_record_single_turn(self):
        """Test recording a single user turn."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        tracker.record_turn(
            turn_number=1,
            user_input="I'm feeling overwhelmed",
            themes=["overwhelm", "anxiety"],
            emotional_tone="anxious",
            glyph_response="Sanctuary",
        )

        assert tracker.coherence.turn_count == 1
        assert len(tracker.coherence.emotional_tones) == 1
        assert tracker.coherence.emotional_tones[0] == "anxious"

    def test_theme_segment_tracking(self):
        """Test that theme segments are properly tracked."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        # Same theme for multiple turns
        for i in range(1, 4):
            tracker.record_turn(
                turn_number=i,
                user_input=f"Turn {i}",
                themes=["grounding"],
                emotional_tone="grounded",
                glyph_response="Ground",
            )

        # New theme
        tracker.record_turn(
            turn_number=4,
            user_input="Turn 4",
            themes=["reflection"],
            emotional_tone="reflective",
            glyph_response="Mirror",
        )

        assert len(tracker.coherence.theme_segments) == 2
        assert tracker.coherence.theme_segments[0].dominant_theme == "grounding"
        assert tracker.coherence.theme_segments[0].end_turn == 3
        assert tracker.coherence.theme_segments[1].dominant_theme == "reflection"

    def test_theme_transitions(self):
        """Test tracking theme transitions."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        tracker.record_turn(
            turn_number=1,
            user_input="Test",
            themes=["theme1"],
            emotional_tone="tone1",
            glyph_response="Glyph1",
        )

        tracker.record_turn(
            turn_number=2,
            user_input="Test",
            themes=["theme2"],
            emotional_tone="tone2",
            glyph_response="Glyph2",
        )

        assert len(tracker.coherence.theme_transitions) == 1
        assert tracker.coherence.theme_transitions[0][0] == "theme1"
        assert tracker.coherence.theme_transitions[0][1] == "theme2"

    def test_fragmentation_calculation(self):
        """Test fragmentation index calculation."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        # Highly fragmented session
        themes = ["theme1", "theme2", "theme3", "theme1", "theme4"]
        for i, theme in enumerate(themes, 1):
            tracker.record_turn(
                turn_number=i,
                user_input=f"Turn {i}",
                themes=[theme],
                emotional_tone="varied",
                glyph_response="Test",
            )

        # Should have high fragmentation
        assert tracker.coherence.fragmentation_index > 0.5

    def test_tone_consistency(self):
        """Test tone consistency calculation."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        # Consistent tone
        for i in range(1, 5):
            tracker.record_turn(
                turn_number=i,
                user_input=f"Turn {i}",
                themes=[f"theme{i}"],
                emotional_tone="grounded",  # Same tone
                glyph_response="Test",
            )

        # Should have high consistency
        assert tracker.coherence.tone_consistency > 0.7

    def test_frustration_tracking(self):
        """Test tracking frustration markers."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        tracker.record_turn(
            turn_number=1,
            user_input="Test",
            themes=["test"],
            emotional_tone="neutral",
            glyph_response="Test",
        )

        tracker.record_turn(
            turn_number=2,
            user_input="This isn't helping",
            themes=["frustration"],
            emotional_tone="frustrated",
            glyph_response="Test",
            has_frustration=True,
        )

        assert 2 in tracker.coherence.frustration_markers

    def test_breakthrough_tracking(self):
        """Test tracking breakthrough moments."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        tracker.record_turn(
            turn_number=3,
            user_input="Oh, I see it now!",
            themes=["insight"],
            emotional_tone="reflective",
            glyph_response="Mirror",
            has_breakthrough=True,
        )

        assert 3 in tracker.coherence.breakthrough_markers

    def test_session_quality_assessment(self):
        """Test session quality assessment."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        # Record a coherent session
        for i in range(1, 6):
            tracker.record_turn(
                turn_number=i,
                user_input=f"Turn {i}",
                themes=["grounding"],
                emotional_tone="grounded",
                glyph_response="Test",
            )

        # Quality should be good
        assert tracker.coherence.quality in [
            SessionQuality.EXCELLENT,
            SessionQuality.GOOD,
            SessionQuality.ADEQUATE,
        ]

    def test_end_session(self):
        """Test ending a session and finalizing metrics."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        for i in range(1, 4):
            tracker.record_turn(
                turn_number=i,
                user_input=f"Turn {i}",
                themes=["test"],
                emotional_tone="neutral",
                glyph_response="Test",
            )

        result = tracker.end_session(user_satisfaction=0.85)

        assert result.end_time is not None
        # Duration may be 0 if recorded too quickly (in same millisecond)
        assert result.total_duration >= 0
        assert result.user_satisfaction == 0.85

    def test_coherence_report(self):
        """Test generating coherence report."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        for i in range(1, 4):
            tracker.record_turn(
                turn_number=i,
                user_input=f"Turn {i}",
                themes=["test"],
                emotional_tone="neutral",
                glyph_response="Test",
            )

        tracker.end_session(user_satisfaction=0.8)
        report = tracker.get_coherence_report()

        assert "session_id" in report
        assert "coherence_score" in report
        assert "quality" in report
        assert report["turn_count"] == 3

    def test_improvement_suggestions(self):
        """Test getting improvement suggestions."""
        tracker = SessionCoherenceTracker("session_001", "user_123")

        # Create a fragmented session
        themes = ["t1", "t2", "t1", "t3", "t1", "t4"]
        for i, theme in enumerate(themes, 1):
            tracker.record_turn(
                turn_number=i,
                user_input="Test",
                themes=[theme],
                emotional_tone="varied",
                glyph_response="Test",
            )

        suggestions = tracker.suggest_improvements()

        assert isinstance(suggestions, list)
        # Fragmented session should get suggestions
        assert len(suggestions) > 0


# ============================================================================
# PREFERENCE EVOLUTION TESTS
# ============================================================================

class TestPreferenceEvolutionTracker:
    """Test preference evolution tracking over time."""

    def test_tracker_initialization(self):
        """Test creating a preference evolution tracker."""
        tracker = PreferenceEvolutionTracker("user_123")

        assert tracker.user_id == "user_123"
        assert len(tracker.snapshots) == 0
        assert len(tracker.trends) == 0

    def test_record_preference(self):
        """Test recording a preference."""
        tracker = PreferenceEvolutionTracker("user_123")

        tracker.record_preference(
            preference_type=PreferenceType.GLYPH,
            item="Sanctuary",
            score=0.8,
            interactions=5,
        )

        assert len(tracker.snapshots) == 1
        assert tracker.snapshots[0].score == 0.8
        assert "glyph:Sanctuary" in tracker.trends

    def test_preference_trend_tracking(self):
        """Test tracking how preferences trend over time."""
        tracker = PreferenceEvolutionTracker("user_123")

        # Record increasing preference
        scores = [0.3, 0.5, 0.7, 0.8]
        for score in scores:
            tracker.record_preference(
                preference_type=PreferenceType.GLYPH,
                item="Ground",
                score=score,
            )

        trend = tracker.trends["glyph:Ground"]
        assert trend.direction == "increasing"
        assert trend.current_score == 0.8
        assert trend.first_score == 0.3

    def test_emerging_preferences(self):
        """Test identifying emerging preferences."""
        tracker = PreferenceEvolutionTracker("user_123")

        # Record increasing preference
        for score in [0.1, 0.3, 0.6, 0.8]:
            tracker.record_preference(
                preference_type=PreferenceType.THEME,
                item="grounding",
                score=score,
            )

        emerging = tracker.get_emerging_preferences(days=30, threshold=0.3)

        assert any("grounding" in pref for pref, _, _ in emerging)

    def test_fading_preferences(self):
        """Test identifying fading preferences."""
        tracker = PreferenceEvolutionTracker("user_123")

        # Record decreasing preference
        for score in [0.9, 0.7, 0.4, 0.2]:
            tracker.record_preference(
                preference_type=PreferenceType.GLYPH,
                item="OldGlyph",
                score=score,
            )

        fading = tracker.get_fading_preferences(days=30, threshold=0.3)

        assert any("OldGlyph" in pref for pref, _, _ in fading)

    def test_stable_preferences(self):
        """Test identifying stable preferences."""
        tracker = PreferenceEvolutionTracker("user_123")

        # Record stable preference
        for _ in range(5):
            tracker.record_preference(
                preference_type=PreferenceType.GLYPH,
                item="StableGlyph",
                score=0.75,
            )

        stable = tracker.get_stable_preferences(threshold=0.1)

        assert any("StableGlyph" in pref for pref, _ in stable)

    def test_volatility_calculation(self):
        """Test calculating preference volatility."""
        tracker = PreferenceEvolutionTracker("user_123")

        # High volatility preference
        for score in [0.2, 0.9, 0.3, 0.8]:
            tracker.record_preference(
                preference_type=PreferenceType.GLYPH,
                item="VolatileGlyph",
                score=score,
            )

        volatility = tracker.get_preference_volatility()

        assert "glyph:VolatileGlyph" in volatility
        assert volatility["glyph:VolatileGlyph"] > 0.5

    def test_acceleration_calculation(self):
        """Test calculating preference acceleration."""
        tracker = PreferenceEvolutionTracker("user_123")

        # Accelerating preference (increasingly rapid growth)
        for score in [0.3, 0.35, 0.5, 0.8]:
            tracker.record_preference(
                preference_type=PreferenceType.THEME,
                item="accelerating",
                score=score,
            )

        acceleration = tracker.get_preference_acceleration()

        assert "theme:accelerating" in acceleration

    def test_preference_trajectory_prediction(self):
        """Test predicting where preferences are headed."""
        tracker = PreferenceEvolutionTracker("user_123")

        # Establish trend
        for score in [0.3, 0.5, 0.7, 0.9]:
            tracker.record_preference(
                preference_type=PreferenceType.GLYPH,
                item="Ascending",
                score=score,
            )

        prediction = tracker.predict_preference_trajectory(
            "glyph:Ascending",
            days_ahead=30,
        )

        assert prediction is not None
        assert prediction["current_score"] == 0.9
        assert prediction["projected_score"] >= 0.9

    def test_preference_clustering(self):
        """Test identifying preference clusters."""
        tracker = PreferenceEvolutionTracker("user_123")

        # Create multiple preferences of same type with high scores
        for glyph in ["Glyph1", "Glyph2", "Glyph3"]:
            tracker.record_preference(
                preference_type=PreferenceType.GLYPH,
                item=glyph,
                score=0.8,
            )

        clusters = tracker.identify_preference_clusters()

        assert any("cluster" in cluster_name for cluster_name, _ in clusters)

    def test_preference_export(self):
        """Test exporting preference evolution data."""
        tracker = PreferenceEvolutionTracker("user_123")

        tracker.record_preference(
            preference_type=PreferenceType.GLYPH,
            item="Test",
            score=0.7,
        )

        export = tracker.export_evolution()

        assert export["user_id"] == "user_123"
        assert export["snapshots_count"] == 1
        assert "glyph:Test" in export["trends"]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase3Integration:
    """Test integration between Phase 3.1 components."""

    def test_profile_and_coherence_integration(self):
        """Test profile manager with session coherence."""
        profile_mgr = EmotionalProfileManager("user_123")
        session_tracker = SessionCoherenceTracker(
            "session_001", "user_123", profile_mgr)

        # Build profile
        for _ in range(3):
            profile_mgr.record_interaction(
                tone=EmotionalTone.GROUNDED,
                intensity="medium",
                themes=["grounding"],
                glyph_response="Ground",
            )

        # Record session turns
        for i in range(1, 4):
            session_tracker.record_turn(
                turn_number=i,
                user_input="Test",
                themes=["grounding"],
                emotional_tone="grounded",
                glyph_response="Ground",
            )

        # Should have profile alignment
        assert session_tracker.coherence.profile_alignment >= 0

    def test_multi_component_workflow(self):
        """Test complete Phase 3.1 workflow."""
        # Initialize all components
        profile_mgr = EmotionalProfileManager("user_123")
        session_tracker = SessionCoherenceTracker(
            "session_001", "user_123", profile_mgr)
        pref_tracker = PreferenceEvolutionTracker("user_123")

        # Simulate interaction
        themes = ["grounding", "safety"]
        profile_mgr.record_interaction(
            tone=EmotionalTone.GROUNDED,
            intensity="low",
            themes=themes,
            glyph_response="Ground",
            user_satisfaction=0.85,
        )

        session_tracker.record_turn(
            turn_number=1,
            user_input="I feel grounded",
            themes=themes,
            emotional_tone="grounded",
            glyph_response="Ground",
        )

        pref_tracker.record_preference(
            preference_type=PreferenceType.GLYPH,
            item="Ground",
            score=0.85,
        )

        # Verify all tracked correctly
        assert len(profile_mgr.profile.snapshots) == 1
        assert session_tracker.coherence.turn_count == 1
        assert len(pref_tracker.trends) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
