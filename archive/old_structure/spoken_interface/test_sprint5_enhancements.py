"""Tests for Sprint 5: Performance, Prosody Refinement, and UX Enhancements

Tests for performance profiling, advanced prosody, session logging,
and enhanced UI with edge case handling.
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from spoken_interface.performance_profiler import (
    LatencyMeasurement,
    PerformanceProfiler,
    ModelPerformanceBenchmark,
    LatencyOptimizer,
)

from spoken_interface.advanced_prosody import (
    BreathStyle,
    EmphasisType,
    AdvancedProsodyPlanner,
    EmotionalContinuityTracker,
)

from spoken_interface.session_logger import (
    InteractionEvent,
    SessionSummary,
    SessionLogger,
)

from spoken_interface.voice_ui_enhancements import (
    EdgeCaseHandler,
    EdgeCaseManager,
    VoiceUIEnhancements,
)


class TestPerformanceProfiler:
    """Test performance profiling."""

    def test_profiler_initialization(self):
        """Should initialize profiler."""
        profiler = PerformanceProfiler()
        assert profiler.measurements == []
        assert profiler.session_start is not None

    def test_measure_function(self):
        """Should measure function execution time."""
        profiler = PerformanceProfiler()

        def slow_func():
            import time
            time.sleep(0.01)
            return "result"

        result = profiler.measure("test_op", slow_func)

        assert result == "result"
        assert len(profiler.measurements) == 1
        assert profiler.measurements[0].duration_ms >= 10

    def test_get_summary(self):
        """Should generate performance summary."""
        profiler = PerformanceProfiler()

        # Add measurements
        profiler.measurements.append(LatencyMeasurement("op1", 0.0, 0.1))
        profiler.measurements.append(LatencyMeasurement("op1", 0.2, 0.25))
        profiler.measurements.append(LatencyMeasurement("op2", 0.3, 0.35))

        summary = profiler.get_summary()

        assert "by_operation" in summary
        assert "op1" in summary["by_operation"]
        assert summary["by_operation"]["op1"]["count"] == 2
        assert 50 < summary["by_operation"]["op1"]["mean_ms"] < 150


class TestModelPerformanceBenchmark:
    """Test model benchmarking."""

    def test_whisper_recommendation(self):
        """Should recommend appropriate Whisper model."""
        model = ModelPerformanceBenchmark.get_whisper_recommendation(150)
        assert model in ["tiny", "small", "base", "medium"]

    def test_tts_recommendation(self):
        """Should recommend appropriate TTS model."""
        model = ModelPerformanceBenchmark.get_tts_recommendation(150)
        assert model in ModelPerformanceBenchmark.TTS_MODELS.keys()

    def test_fast_model_for_fast_target(self):
        """Should recommend fastest model for tight latency."""
        model = ModelPerformanceBenchmark.get_whisper_recommendation(50)
        assert model == "tiny"  # Fastest Whisper model


class TestAdvancedProsodyPlanner:
    """Test advanced prosody planning."""

    def test_plan_advanced_prosody(self):
        """Should create advanced prosody plan."""
        planner = AdvancedProsodyPlanner()

        plan = planner.plan_advanced_prosody(
            text="That's wonderful!",
            voltage=0.8,
            tone="excited",
            attunement=0.9,
            certainty=0.8,
        )

        assert plan.base_rate > 0
        assert len(plan.pitch_contour) > 0
        assert len(plan.energy_contour) > 0

    def test_breath_style_excited(self):
        """Excited speech should have gasping breath."""
        planner = AdvancedProsodyPlanner()

        plan = planner.plan_advanced_prosody(
            text="Amazing!",
            voltage=0.9,
            tone="excited",
            attunement=0.8,
            certainty=0.9,
        )

        assert plan.breath_style == BreathStyle.GASPING

    def test_breath_style_sad(self):
        """Sad speech should have shallow breath."""
        planner = AdvancedProsodyPlanner()

        plan = planner.plan_advanced_prosody(
            text="I'm sorry to hear that.",
            voltage=0.2,
            tone="sad",
            attunement=0.7,
            certainty=0.5,
        )

        assert plan.breath_style == BreathStyle.SHALLOW

    def test_emphasis_high_attunement(self):
        """High attunement should add emphasis."""
        planner = AdvancedProsodyPlanner()

        plan = planner.plan_advanced_prosody(
            text="This is really important!",
            voltage=0.5,
            tone="neutral",
            attunement=0.9,
            certainty=0.8,
        )

        assert len(plan.emphasis_points) > 0


class TestEmotionalContinuityTracker:
    """Test emotional continuity tracking."""

    def test_add_response(self):
        """Should add responses to history."""
        tracker = EmotionalContinuityTracker()

        tracker.add_response("Hello", 0.5, "neutral", 0.5)
        assert len(tracker.response_history) == 1

    def test_consistency_single_response(self):
        """Single response should have baseline consistency."""
        tracker = EmotionalContinuityTracker()
        tracker.add_response("Hello", 0.5, "neutral", 0.5)

        consistency = tracker.get_emotional_continuity_score()
        assert 0 <= consistency <= 1


class TestSessionLogger:
    """Test session logging."""

    def test_logger_initialization(self):
        """Should initialize logger."""
        logger = SessionLogger()

        assert logger.session_id is not None
        assert logger.summary.total_user_messages == 0
        assert logger.summary.total_assistant_messages == 0

    def test_log_user_message(self):
        """Should log user message."""
        logger = SessionLogger()

        logger.log_user_message("Hello", confidence=0.95)

        assert logger.summary.total_user_messages == 1
        assert len(logger.events) == 1
        assert logger.events[0].speaker == "user"

    def test_log_assistant_message(self):
        """Should log assistant message."""
        logger = SessionLogger()

        logger.log_assistant_message(
            "Hi there!",
            emotional_state={"voltage": 0.5, "tone": "friendly"}
        )

        assert logger.summary.total_assistant_messages == 1
        assert logger.events[0].speaker == "assistant"

    def test_calculate_metrics(self):
        """Should calculate session metrics."""
        logger = SessionLogger()

        logger.log_user_message("Hello", latency_ms=100)
        logger.log_assistant_message(
            "Hi!",
            emotional_state={"voltage": 0.5, "tone": "friendly"},
            latency_ms=150
        )

        metrics = logger.calculate_session_metrics()

        assert "avg_latency_ms" in metrics
        assert metrics["total_user_messages"] == 1
        assert metrics["total_assistant_messages"] == 1

    def test_save_session(self):
        """Should save session to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = SessionLogger(save_dir=tmpdir)

            logger.log_user_message("Hello")
            save_path = logger.save_session()

            assert Path(save_path).exists()

            # Verify saved data
            with open(save_path) as f:
                data = json.load(f)
                assert "summary" in data
                assert "metrics" in data


class TestEdgeCaseManager:
    """Test edge case handling."""

    def test_validate_audio_empty(self):
        """Should reject empty audio."""
        manager = EdgeCaseManager()
        is_valid, msg = manager.validate_audio(b"")

        assert is_valid is False
        assert msg is not None

    def test_validate_audio_too_short(self):
        """Should reject audio shorter than min duration."""
        manager = EdgeCaseManager()
        # Small amount of bytes (~100ms)
        short_audio = b"\x00" * 1000

        is_valid, msg = manager.validate_audio(short_audio)

        assert is_valid is False

    def test_validate_transcription_low_confidence(self):
        """Should reject low confidence transcription."""
        manager = EdgeCaseManager()
        is_valid, msg = manager.validate_transcription(
            "Hello",
            confidence=0.2
        )

        assert is_valid is False

    def test_validate_transcription_empty(self):
        """Should reject empty transcription."""
        manager = EdgeCaseManager()
        is_valid, msg = manager.validate_transcription("", confidence=0.5)

        assert is_valid is False


class TestVoiceUIEnhancements:
    """Test enhanced UI features."""

    def test_enhancements_initialization(self):
        """Should initialize enhancements."""
        enhancements = VoiceUIEnhancements()

        assert enhancements.edge_case_manager is not None
        assert enhancements.visualizer is not None

    def test_handle_audio_edge_cases(self):
        """Should validate audio."""
        enhancements = VoiceUIEnhancements()

        # Empty audio
        is_valid, msg = enhancements.handle_audio_edge_cases(b"")
        assert is_valid is False

    def test_handle_transcription_edge_cases(self):
        """Should validate transcription."""
        enhancements = VoiceUIEnhancements()

        # Low confidence
        is_valid, msg = enhancements.handle_transcription_edge_cases(
            "Hello",
            confidence=0.2
        )
        assert is_valid is False

        # Good transcription
        is_valid, msg = enhancements.handle_transcription_edge_cases(
            "Hello",
            confidence=0.95
        )
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
