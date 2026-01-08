"""Tests for Supabase Manager Module (offline mode)."""

import pytest
from datetime import datetime, timezone
from emotional_os.core.firstperson.supabase_manager import (
    SupabaseManager,
    ThemeAnchor,
    ThemeHistory,
    TemporalPattern,
)


class TestSupabaseManagerOffline:
    """Test SupabaseManager in offline mode (no actual Supabase connection)."""

    @pytest.fixture
    def manager(self):
        """Create a manager instance without Supabase."""
        # This creates manager without actual connection
        return SupabaseManager(user_id="test_user_123")

    def test_manager_initialization(self, manager):
        """Test manager initialization."""
        assert manager.user_id == "test_user_123"
        # Should not have client when env vars missing
        assert isinstance(manager.is_available(), bool)

    def test_is_available_offline(self, manager):
        """Test is_available returns False when offline."""
        # Should return False when Supabase env vars not set
        assert manager.is_available() is False

    def test_theme_anchor_dataclass(self):
        """Test ThemeAnchor dataclass."""
        now = datetime.now(timezone.utc).isoformat()

        anchor = ThemeAnchor(
            theme="family_conflict",
            anchor="Kids are driving me crazy again",
            frequency=3,
            first_detected_at=now,
            last_detected_at=now,
            confidence=0.85,
            status="active",
            context={"session": "conversation_1"},
        )

        assert anchor.theme == "family_conflict"
        assert anchor.frequency == 3
        assert anchor.confidence == 0.85

    def test_theme_history_dataclass(self):
        """Test ThemeHistory dataclass."""
        now = datetime.now(timezone.utc).isoformat()

        history = ThemeHistory(
            theme="work_stress",
            frequency_at_time=2,
            detected_at=now,
            context={"keywords": ["boss", "deadline"]},
            affect_state={"valence": -0.6, "arousal": 0.8},
            time_of_day="afternoon",
            day_of_week="Monday",
        )

        assert history.theme == "work_stress"
        assert history.frequency_at_time == 2
        assert history.affect_state["arousal"] == 0.8

    def test_temporal_pattern_dataclass(self):
        """Test TemporalPattern dataclass."""
        pattern = TemporalPattern(
            theme="anxiety",
            time_of_day="evening",
            frequency=5,
            avg_intensity=0.7,
            day_of_week="Friday",
        )

        assert pattern.theme == "anxiety"
        assert pattern.frequency == 5
        assert pattern.day_of_week == "Friday"

    def test_record_theme_anchor_offline(self, manager):
        """Test recording theme anchor in offline mode."""
        # Should return False when offline
        result = manager.record_theme_anchor(
            theme="family_conflict",
            anchor="Kids fighting again",
            confidence=0.8,
        )

        assert result is False

    def test_get_theme_frequency_offline(self, manager):
        """Test getting theme frequency in offline mode."""
        # Should return empty list when offline
        result = manager.get_theme_frequency(theme="family_conflict")

        assert result == []

    def test_get_recent_anchors_offline(self, manager):
        """Test getting recent anchors in offline mode."""
        # Should return empty list when offline
        result = manager.get_recent_anchors(limit=20)

        assert result == []

    def test_record_theme_history_offline(self, manager):
        """Test recording theme history in offline mode."""
        # Should return False when offline
        result = manager.record_theme_history(
            theme="work_stress",
            conversation_id="conv_123",
            frequency_at_time=2,
            time_of_day="afternoon",
            day_of_week="Monday",
        )

        assert result is False

    def test_get_temporal_patterns_offline(self, manager):
        """Test getting temporal patterns in offline mode."""
        # Should return empty list when offline
        result = manager.get_temporal_patterns(time_of_day="evening")

        assert result == []

    def test_record_temporal_pattern_offline(self, manager):
        """Test recording temporal pattern in offline mode."""
        # Should return False when offline
        result = manager.record_temporal_pattern(
            theme="anxiety",
            time_of_day="evening",
            intensity=0.7,
            day_of_week="Friday",
        )

        assert result is False

    def test_get_recurring_patterns_offline(self, manager):
        """Test getting recurring patterns in offline mode."""
        # Should return empty list when offline
        result = manager.get_recurring_patterns(min_frequency=3)

        assert result == []

    def test_update_anchor_status_offline(self, manager):
        """Test updating anchor status in offline mode."""
        # Should return False when offline
        result = manager.update_anchor_status(
            anchor_id="anchor_123", new_status="resolved"
        )

        assert result is False


class TestSupabaseManagerLogic:
    """Test business logic of Supabase manager (without actual DB calls)."""

    def test_manager_user_id_isolation(self):
        """Test that managers are isolated by user_id."""
        manager1 = SupabaseManager(user_id="user_1")
        manager2 = SupabaseManager(user_id="user_2")

        assert manager1.user_id == "user_1"
        assert manager2.user_id == "user_2"
        assert manager1.user_id != manager2.user_id

    def test_theme_anchor_context_optional(self):
        """Test that context is optional in ThemeAnchor."""
        now = datetime.now(timezone.utc).isoformat()

        anchor = ThemeAnchor(
            theme="family_conflict",
            anchor="Kids fighting",
            frequency=1,
            first_detected_at=now,
            last_detected_at=now,
            confidence=0.5,
        )

        assert anchor.context is None

    def test_temporal_pattern_day_optional(self):
        """Test that day_of_week is optional in TemporalPattern."""
        pattern = TemporalPattern(
            theme="anxiety",
            time_of_day="evening",
            frequency=3,
            avg_intensity=0.6,
        )

        assert pattern.day_of_week is None

    def test_theme_history_affect_optional(self):
        """Test that affect_state is optional in ThemeHistory."""
        now = datetime.now(timezone.utc).isoformat()

        history = ThemeHistory(
            theme="family_conflict",
            frequency_at_time=1,
            detected_at=now,
        )

        assert history.affect_state is None
        assert history.context is None


class TestSupabaseManagerInterfaceContract:
    """Test interface contract of SupabaseManager."""

    def test_all_public_methods_exist(self):
        """Test that all expected public methods exist."""
        manager = SupabaseManager(user_id="test")

        # All public methods should exist
        assert hasattr(manager, "is_available")
        assert hasattr(manager, "record_theme_anchor")
        assert hasattr(manager, "get_theme_frequency")
        assert hasattr(manager, "get_recent_anchors")
        assert hasattr(manager, "record_theme_history")
        assert hasattr(manager, "get_temporal_patterns")
        assert hasattr(manager, "record_temporal_pattern")
        assert hasattr(manager, "get_recurring_patterns")
        assert hasattr(manager, "update_anchor_status")

        # All methods should be callable
        assert callable(manager.is_available)
        assert callable(manager.record_theme_anchor)
        assert callable(manager.get_theme_frequency)
        assert callable(manager.get_recent_anchors)
        assert callable(manager.record_theme_history)
        assert callable(manager.get_temporal_patterns)
        assert callable(manager.record_temporal_pattern)
        assert callable(manager.get_recurring_patterns)
        assert callable(manager.update_anchor_status)

    def test_return_types(self):
        """Test that methods return expected types."""
        manager = SupabaseManager(user_id="test")

        # When offline, methods should return appropriate types
        assert isinstance(manager.is_available(), bool)
        assert isinstance(manager.record_theme_anchor("theme", "anchor"), bool)
        assert isinstance(manager.get_theme_frequency(), list)
        assert isinstance(manager.get_recent_anchors(), list)
        assert isinstance(manager.record_theme_history("theme"), bool)
        assert isinstance(manager.get_temporal_patterns(), list)
        assert isinstance(manager.record_temporal_pattern(
            "theme", "morning"), bool)
        assert isinstance(manager.get_recurring_patterns(), list)
        assert isinstance(manager.update_anchor_status("id", "status"), bool)

    def test_error_handling_robustness(self):
        """Test that methods handle None values gracefully."""
        manager = SupabaseManager(user_id="test")

        # Should not raise exceptions with None values
        try:
            manager.get_theme_frequency(theme=None)
            manager.get_temporal_patterns(time_of_day=None, theme=None)
            manager.get_recurring_patterns(min_frequency=1)
            assert True
        except Exception as e:
            pytest.fail(f"Manager raised exception with None values: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
