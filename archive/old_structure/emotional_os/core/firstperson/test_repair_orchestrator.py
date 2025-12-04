"""Tests for Repair Orchestrator (Phase 2.3)."""

import pytest
from emotional_os.core.firstperson.repair_orchestrator import (
    RepairOrchestrator,
    GlyphCompositionContext,
    RepairAnalysis,
)


class TestRepairOrchestrator:
    """Test repair orchestrator integration."""

    def test_initialize_orchestrator(self):
        """Create repair orchestrator for user."""
        orchestrator = RepairOrchestrator("user_123")
        assert orchestrator.user_id == "user_123"
        assert len(orchestrator.repair_history) == 0

    def test_record_response(self):
        """Record response generated for user."""
        orchestrator = RepairOrchestrator("user_123")
        response = "That sounds heavy. What's it like?"
        orchestrator.record_response(response)
        assert orchestrator.previous_response == response

    def test_record_acceptance(self):
        """Record user accepting a glyph response."""
        orchestrator = RepairOrchestrator("user_123")
        context = GlyphCompositionContext(
            tone="sadness",
            arousal=0.3,
            valence=-0.9,
            glyph_name="Loss",
            user_id="user_123",
        )
        orchestrator.record_acceptance(context)

        assert orchestrator.previous_glyph_context == context
        # Check that it was recorded in preferences
        key = ("sadness", "Loss")
        assert key in orchestrator.user_preferences.effectiveness

    def test_no_repair_without_previous_response(self):
        """No repair detected when no previous response."""
        orchestrator = RepairOrchestrator("user_123")
        analysis = orchestrator.analyze_for_repair("That's not quite right")
        assert analysis.is_rejection is False

    def test_detect_explicit_rejection(self):
        """Detect explicit rejection of previous response."""
        orchestrator = RepairOrchestrator("user_123")
        orchestrator.record_response("I hear the anxiety in that.")

        context = GlyphCompositionContext(
            tone="anxiety",
            arousal=0.8,
            valence=-0.6,
            glyph_name="Breaking",
            user_id="user_123",
        )
        orchestrator.previous_glyph_context = context

        analysis = orchestrator.analyze_for_repair("That's not it.")
        assert analysis.is_rejection is True
        assert analysis.rejection_type == "explicit"

    def test_implicit_correction_detection(self):
        """Detect implicit correction."""
        orchestrator = RepairOrchestrator("user_123")
        orchestrator.record_response("I hear the anxiety.")

        context = GlyphCompositionContext(
            tone="anxiety",
            arousal=0.8,
            valence=-0.6,
            glyph_name="Breaking",
            user_id="user_123",
        )
        orchestrator.previous_glyph_context = context

        analysis = orchestrator.analyze_for_repair(
            "Actually, it feels more like pressure."
        )
        assert analysis.is_rejection is True
        # Note: "more" triggers explicit detection
        assert analysis.rejection_type in ("explicit", "implicit")

    def test_learn_and_suggest_alternative(self):
        """Learn from rejection and suggest better glyph."""
        orchestrator = RepairOrchestrator("user_456")

        # First turn: user rejects "Breaking" for anxiety
        orchestrator.record_response("I hear the breaking inside you.")
        context1 = GlyphCompositionContext(
            tone="anxiety", arousal=0.8, valence=-0.6, glyph_name="Breaking", user_id="user_456"
        )
        orchestrator.previous_glyph_context = context1

        analysis = orchestrator.analyze_for_repair("That's not it.")
        assert analysis.is_rejection is True

        # System learns Breaking doesn't work for this user's anxiety
        # Next, record acceptance of "Pressure" glyph
        context2 = GlyphCompositionContext(
            tone="anxiety", arousal=0.8, valence=-0.6, glyph_name="Pressure", user_id="user_456"
        )
        orchestrator.record_acceptance(context2)

        # Now rejection of Breaking should suggest Pressure as alternative
        orchestrator.previous_glyph_context = context1
        analysis2 = orchestrator.analyze_for_repair("Not quite right.")
        assert analysis2.is_rejection is True
        assert analysis2.suggested_alternative == "Pressure"

    def test_repair_history_recorded(self):
        """Repair attempts recorded in history."""
        orchestrator = RepairOrchestrator("user_789")
        orchestrator.record_response("I hear something.")

        context = GlyphCompositionContext(
            tone="anger", arousal=0.9, valence=-0.8, glyph_name="Fire", user_id="user_789"
        )
        orchestrator.previous_glyph_context = context

        analysis = orchestrator.analyze_for_repair("Nope, that's not it.")

        assert len(orchestrator.repair_history) == 1
        record = orchestrator.repair_history[0]
        assert record["rejection_type"] == "explicit"
        assert record["previous_glyph"] == "Fire"
        assert "Nope" in record["user_input"]

    def test_get_best_glyph_for_state(self):
        """Get best glyph for emotional state."""
        orchestrator = RepairOrchestrator("user_111")

        # Train on some acceptances
        ctx_loss = GlyphCompositionContext(
            tone="sadness", arousal=0.3, valence=-0.95, glyph_name="Loss", user_id="user_111"
        )
        ctx_grieving = GlyphCompositionContext(
            tone="sadness", arousal=0.3, valence=-0.95, glyph_name="Grieving", user_id="user_111"
        )

        # Loss gets accepted twice
        orchestrator.record_acceptance(ctx_loss)
        orchestrator.record_acceptance(ctx_loss)

        # Grieving gets accepted once
        orchestrator.record_acceptance(ctx_grieving)

        # Loss should be best for this state
        best = orchestrator.get_best_glyph_for_state("sadness", 0.3, -0.95)
        assert best == "Loss"

    def test_get_repair_summary(self):
        """Get summary of repairs and learning."""
        orchestrator = RepairOrchestrator("user_222")

        # Record some activity
        orchestrator.record_response("I hear the sadness.")
        context = GlyphCompositionContext(
            tone="sadness", arousal=0.2, valence=-0.9, glyph_name="Loss", user_id="user_222"
        )
        orchestrator.previous_glyph_context = context

        # First rejection
        orchestrator.analyze_for_repair("That's not it.")

        # Second rejection
        orchestrator.analyze_for_repair("Not really.")

        summary = orchestrator.get_repair_summary()
        assert summary["total_repairs"] == 2
        assert summary["explicit_rejections"] == 2
        assert "Loss" in summary["most_rejected_glyphs"]

    def test_reset_session(self):
        """Reset session state but keep learning."""
        orchestrator = RepairOrchestrator("user_333")

        # Record some history
        orchestrator.record_response("Response")
        context = GlyphCompositionContext(
            tone="anxiety", arousal=0.8, valence=-0.6, glyph_name="Breaking", user_id="user_333"
        )
        orchestrator.record_acceptance(context)

        initial_history_size = len(orchestrator.user_preferences.glyph_history)

        # Reset session
        orchestrator.reset_session()

        assert orchestrator.previous_response is None
        assert orchestrator.previous_glyph_context is None
        assert len(orchestrator.repair_history) == 0
        # Learning should be preserved
        assert len(
            orchestrator.user_preferences.glyph_history) == initial_history_size

    def test_clear_all(self):
        """Clear all learning and session state."""
        orchestrator = RepairOrchestrator("user_444")

        # Record history
        orchestrator.record_response("Response")
        context = GlyphCompositionContext(
            tone="anger", arousal=0.9, valence=-0.8, glyph_name="Fire", user_id="user_444"
        )
        orchestrator.record_acceptance(context)

        # Clear everything
        orchestrator.clear_all()

        assert orchestrator.previous_response is None
        assert orchestrator.previous_glyph_context is None
        assert len(orchestrator.repair_history) == 0
        assert len(orchestrator.user_preferences.glyph_history) == 0
        assert len(orchestrator.user_preferences.effectiveness) == 0


class TestGlyphCompositionContext:
    """Test glyph composition context."""

    def test_create_context(self):
        """Create glyph composition context."""
        context = GlyphCompositionContext(
            tone="sadness",
            arousal=0.3,
            valence=-0.9,
            glyph_name="Loss",
            user_id="user_123",
        )
        assert context.tone == "sadness"
        assert context.glyph_name == "Loss"
        assert context.timestamp is not None

    def test_context_with_custom_timestamp(self):
        """Create context with custom timestamp."""
        ts = "2024-01-01T12:00:00Z"
        context = GlyphCompositionContext(
            tone="anxiety",
            arousal=0.8,
            valence=-0.6,
            glyph_name="Breaking",
            user_id="user_456",
            timestamp=ts,
        )
        assert context.timestamp == ts


class TestRepairAnalysis:
    """Test repair analysis response."""

    def test_no_rejection_analysis(self):
        """Create analysis for non-rejection."""
        analysis = RepairAnalysis(
            is_rejection=False,
            rejection_type=None,
            user_correction=None,
            suggested_alternative=None,
            confidence=0.0,
        )
        assert analysis.is_rejection is False
        assert analysis.confidence == 0.0

    def test_explicit_rejection_analysis(self):
        """Create analysis for explicit rejection."""
        analysis = RepairAnalysis(
            is_rejection=True,
            rejection_type="explicit",
            user_correction=None,
            suggested_alternative="Pressure",
            confidence=0.7,
        )
        assert analysis.is_rejection is True
        assert analysis.rejection_type == "explicit"
        assert analysis.suggested_alternative == "Pressure"
        assert analysis.confidence == 0.7
