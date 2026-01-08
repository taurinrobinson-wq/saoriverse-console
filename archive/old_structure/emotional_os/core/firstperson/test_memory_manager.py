"""Tests for Memory Rehydration Module."""

import pytest
from datetime import datetime, timezone, timedelta
from emotional_os.core.firstperson.memory_manager import (
    MemoryManager,
    rehydrate_memory,
    format_memory_for_parser,
    get_memory_summary,
)
from emotional_os.core.firstperson.supabase_manager import ThemeAnchor


class TestMemoryManager:
    """Test suite for memory rehydration."""

    @pytest.fixture
    def manager(self):
        """Create a memory manager instance."""
        return MemoryManager(user_id="test_user_123")

    @pytest.fixture
    def sample_anchors(self):
        """Create sample anchors for testing."""
        now = datetime.now(timezone.utc).isoformat()
        yesterday = (datetime.now(timezone.utc) -
                     timedelta(days=1)).isoformat()

        return [
            ThemeAnchor(
                theme="family_conflict",
                anchor="Kids are driving me crazy",
                frequency=5,
                first_detected_at=yesterday,
                last_detected_at=now,
                confidence=0.85,
                status="active",
                context={"keywords": ["kids", "frustrated"]},
            ),
            ThemeAnchor(
                theme="work_stress",
                anchor="Boss expectations are unreasonable",
                frequency=3,
                first_detected_at=yesterday,
                last_detected_at=now,
                confidence=0.75,
                status="active",
                context={"keywords": ["boss", "deadline"]},
            ),
            ThemeAnchor(
                theme="anxiety",
                anchor="Can't stop worrying about the future",
                frequency=2,
                first_detected_at=yesterday,
                last_detected_at=yesterday,
                confidence=0.70,
                status="active",
                context={"keywords": ["worried", "uncertain"]},
            ),
        ]

    def test_manager_initialization(self, manager):
        """Test manager initialization."""
        assert manager.user_id == "test_user_123"
        assert manager.rehydrated_anchors == []
        assert manager.memory_context == {}

    def test_rehydrate_memory_empty(self, manager):
        """Test rehydration with no prior memory."""
        context = manager.rehydrate_memory()

        assert context["status"] == "new_session"
        assert context["anchor_count"] == 0
        assert context["unique_themes"] == 0
        assert context["memory_salience"] == 0.0

    def test_build_memory_context_empty(self, manager):
        """Test building context with no anchors."""
        context = manager._build_memory_context()

        assert context["status"] == "new_session"
        assert context["narrative_memory"] == "This is our first conversation."
        assert context["theme_frequencies"] == {}

    def test_build_narrative_summary_empty(self, manager):
        """Test narrative summary with no anchors."""
        summary = manager._build_narrative_summary({})

        assert summary == ""

    def test_build_narrative_summary_with_anchors(self, manager, sample_anchors):
        """Test narrative summary generation."""
        # Group anchors by theme
        themes_by_anchor = {}
        for anchor in sample_anchors:
            if anchor.theme not in themes_by_anchor:
                themes_by_anchor[anchor.theme] = []
            themes_by_anchor[anchor.theme].append(anchor)

        summary = manager._build_narrative_summary(themes_by_anchor)

        assert "family_conflict" in summary.lower()
        assert "work_stress" in summary.lower() or "work" in summary.lower()
        assert "5 times" in summary or "5" in summary  # family_conflict frequency

    def test_build_theme_frequencies(self, manager, sample_anchors):
        """Test theme frequency calculation."""
        themes_by_anchor = {}
        for anchor in sample_anchors:
            if anchor.theme not in themes_by_anchor:
                themes_by_anchor[anchor.theme] = []
            themes_by_anchor[anchor.theme].append(anchor)

        freqs = manager._build_theme_frequencies(themes_by_anchor)

        assert freqs["family_conflict"] == 5
        assert freqs["work_stress"] == 3
        assert freqs["anxiety"] == 2

    def test_build_temporal_context_empty(self, manager):
        """Test temporal context when Supabase unavailable."""
        context = manager._build_temporal_context()

        assert context["status"] in ["unavailable", "no_patterns"]

    def test_calculate_memory_salience_no_anchors(self, manager):
        """Test salience calculation with no anchors."""
        salience = manager._calculate_memory_salience()

        assert salience == 0.0

    def test_calculate_memory_salience_recent(self, manager, sample_anchors):
        """Test salience calculation with recent anchors."""
        manager.rehydrated_anchors = sample_anchors

        salience = manager._calculate_memory_salience()

        # Should have some salience with recent anchors
        assert 0 <= salience <= 1.0
        # Recent data should have higher salience
        assert salience > 0.2

    def test_format_memory_for_parser_empty(self, manager):
        """Test parser formatting with no memory."""
        formatted = manager.format_memory_for_parser()

        assert formatted["ready_for_injection"] is True
        assert "memory_signals" in formatted
        assert "memory_context" in formatted
        assert formatted["memory_signals"] == []

    def test_format_memory_for_parser_with_anchors(self, manager, sample_anchors):
        """Test parser formatting with anchors."""
        manager.rehydrated_anchors = sample_anchors
        manager.memory_context = manager._build_memory_context()

        formatted = manager.format_memory_for_parser()

        assert formatted["ready_for_injection"] is True
        assert len(formatted["memory_signals"]) == len(sample_anchors)

        # Check signal structure
        for signal in formatted["memory_signals"]:
            assert signal["type"] == "memory"
            assert signal["signal_type"] == "emotional_theme_anchor"
            assert "theme" in signal
            assert "anchor" in signal
            assert "frequency" in signal
            assert "confidence" in signal

    def test_get_top_themes_empty(self, manager):
        """Test getting top themes with no memory."""
        themes = manager.get_top_themes()

        assert themes == []

    def test_get_top_themes_with_context(self, manager, sample_anchors):
        """Test getting top themes."""
        manager.rehydrated_anchors = sample_anchors
        manager.memory_context = manager._build_memory_context()

        themes = manager.get_top_themes(limit=2)

        assert len(themes) <= 2
        # Family conflict should be first (highest frequency)
        assert themes[0] == "family_conflict"

    def test_get_memory_summary_empty(self, manager):
        """Test memory summary with no context."""
        summary = manager.get_memory_summary()

        assert summary == "No memory available yet."

    def test_get_memory_summary_with_context(self, manager, sample_anchors):
        """Test memory summary generation."""
        manager.rehydrated_anchors = sample_anchors
        manager.memory_context = manager._build_memory_context()

        summary = manager.get_memory_summary()

        assert summary != "No memory available yet."
        assert "family_conflict" in summary.lower()

    def test_build_empty_context(self, manager):
        """Test empty context structure."""
        context = manager._build_empty_context()

        # Should have all required fields
        assert context["status"] == "new_session"
        assert "memory_timestamp" in context
        assert context["anchor_count"] == 0
        assert context["unique_themes"] == 0
        assert context["narrative_memory"] == "This is our first conversation."
        assert context["theme_frequencies"] == {}
        assert context["memory_salience"] == 0.0


class TestMemoryManagerModuleLevelFunctions:
    """Test module-level functions."""

    def test_rehydrate_memory_function(self):
        """Test module-level rehydrate_memory function."""
        context = rehydrate_memory(user_id="test_user_456", limit=20)

        assert isinstance(context, dict)
        assert "status" in context
        assert "memory_timestamp" in context

    def test_format_memory_for_parser_function(self):
        """Test module-level format_memory_for_parser function."""
        formatted = format_memory_for_parser(user_id="test_user_456")

        assert isinstance(formatted, dict)
        assert "memory_signals" in formatted
        assert "memory_context" in formatted
        assert "ready_for_injection" in formatted

    def test_get_memory_summary_function(self):
        """Test module-level get_memory_summary function."""
        summary = get_memory_summary(user_id="test_user_456")

        assert isinstance(summary, str)


class TestMemoryRehydrationIntegration:
    """Integration tests for memory rehydration workflow."""

    def test_complete_rehydration_workflow(self):
        """Test complete workflow from initialization to parser format."""
        manager = MemoryManager(user_id="test_integration")

        # Step 1: Initialize
        assert manager.rehydrated_anchors == []

        # Step 2: Rehydrate (will be empty, no Supabase)
        context = manager.rehydrate_memory(limit=20)
        assert context["status"] in ["new_session", "rehydrated"]
        assert context["anchor_count"] >= 0

        # Step 3: Format for parser
        formatted = manager.format_memory_for_parser()
        assert formatted["ready_for_injection"] is True

        # Step 4: Get summary
        summary = manager.get_memory_summary()
        assert isinstance(summary, str)

    def test_memory_manager_user_isolation(self):
        """Test that different users have isolated memory."""
        manager1 = MemoryManager(user_id="user_1")
        manager2 = MemoryManager(user_id="user_2")

        manager1.rehydrate_memory()
        manager2.rehydrate_memory()

        assert manager1.user_id == "user_1"
        assert manager2.user_id == "user_2"
        assert manager1.user_id != manager2.user_id

    def test_memory_context_completeness(self):
        """Test that memory context has all required fields."""
        manager = MemoryManager(user_id="test_complete")
        context = manager.rehydrate_memory()

        required_fields = [
            "status",
            "memory_timestamp",
            "anchor_count",
            "unique_themes",
            "narrative_memory",
            "theme_frequencies",
            "temporal_patterns",
            "memory_salience",
        ]

        for field in required_fields:
            assert field in context, f"Missing required field: {field}"

    def test_signal_structure_for_parser(self):
        """Test that formatted signals have correct structure for parser."""
        now = datetime.now(timezone.utc).isoformat()

        manager = MemoryManager(user_id="test_signals")
        anchor = ThemeAnchor(
            theme="family_conflict",
            anchor="Test anchor",
            frequency=1,
            first_detected_at=now,
            last_detected_at=now,
            confidence=0.8,
            status="active",
        )
        manager.rehydrated_anchors = [anchor]
        manager.memory_context = manager._build_memory_context()

        formatted = manager.format_memory_for_parser()

        # Check that memory signal structure is correct
        assert len(formatted["memory_signals"]) == 1
        signal = formatted["memory_signals"][0]

        parser_required = [
            "type",
            "signal_type",
            "theme",
            "anchor",
            "frequency",
            "confidence",
            "source",
            "created_at",
            "metadata",
        ]

        for field in parser_required:
            assert field in signal, f"Missing parser signal field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
