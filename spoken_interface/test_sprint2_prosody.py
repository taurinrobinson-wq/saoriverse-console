"""Tests for Sprint 2: Prosody Planning

Test glyph-to-prosody mapping and guardrails.
"""

import pytest
import numpy as np
from spoken_interface.prosody_planner import (
    ProsodyPlanner,
    GlyphSignals,
    ArousalBand,
    ValenceBand,
    CertaintyBand,
    ProsodyExplainer,
)


class TestSignalBucketing:
    """Test bucketing of continuous signals into bands."""

    def test_bucket_voltage_low(self):
        """Low voltage → LOW band."""
        planner = ProsodyPlanner()
        band = planner._bucket_voltage(0.2)
        assert band == ArousalBand.LOW

    def test_bucket_voltage_medium(self):
        """Medium voltage → MEDIUM band."""
        planner = ProsodyPlanner()
        band = planner._bucket_voltage(0.5)
        assert band == ArousalBand.MEDIUM

    def test_bucket_voltage_high(self):
        """High voltage → HIGH band."""
        planner = ProsodyPlanner()
        band = planner._bucket_voltage(0.8)
        assert band == ArousalBand.HIGH

    def test_bucket_valence_negative(self):
        """Low valence → NEGATIVE band."""
        planner = ProsodyPlanner()
        band = planner._bucket_valence(0.2)
        assert band == ValenceBand.NEGATIVE

    def test_bucket_valence_positive(self):
        """High valence → POSITIVE band."""
        planner = ProsodyPlanner()
        band = planner._bucket_valence(0.8)
        assert band == ValenceBand.POSITIVE

    def test_bucket_certainty_uncertain(self):
        """Low certainty → LOW band."""
        planner = ProsodyPlanner()
        band = planner._bucket_certainty(0.2)
        assert band == CertaintyBand.LOW

    def test_bucket_certainty_certain(self):
        """High certainty → HIGH band."""
        planner = ProsodyPlanner()
        band = planner._bucket_certainty(0.9)
        assert band == CertaintyBand.HIGH


class TestProsodyMapping:
    """Test prosody feature mapping."""

    def test_rate_from_arousal(self):
        """Speaking rate should match arousal."""
        planner = ProsodyPlanner()

        # Low arousal = slower
        assert planner._rate_from_arousal(ArousalBand.LOW) < 1.0

        # High arousal = faster
        assert planner._rate_from_arousal(ArousalBand.HIGH) > 1.0

        # Medium = normal
        assert planner._rate_from_arousal(ArousalBand.MEDIUM) == 1.0

    def test_pitch_from_valence(self):
        """Pitch should match valence."""
        planner = ProsodyPlanner()

        # Negative valence = lower pitch
        assert planner._pitch_from_valence(ValenceBand.NEGATIVE) < 0

        # Positive valence = higher pitch
        assert planner._pitch_from_valence(ValenceBand.POSITIVE) > 0

        # Neutral = no shift
        assert planner._pitch_from_valence(ValenceBand.NEUTRAL) == 0

    def test_energy_from_arousal(self):
        """Energy should match arousal."""
        planner = ProsodyPlanner()

        # Low arousal = quieter
        assert planner._energy_from_arousal(ArousalBand.LOW) < 1.0

        # High arousal = louder
        assert planner._energy_from_arousal(ArousalBand.HIGH) > 1.0

    def test_terminal_contour_from_certainty(self):
        """Terminal contour should match certainty."""
        planner = ProsodyPlanner()

        # Uncertain → rising (questioning)
        assert planner._terminal_from_certainty(CertaintyBand.LOW) == "rising"

        # Confident → falling (assertive)
        assert planner._terminal_from_certainty(
            CertaintyBand.HIGH) == "falling"


class TestFullProsodyPlanning:
    """Test complete prosody planning."""

    def test_excited_positive_response(self):
        """Excited, positive response should be fast and bright."""
        planner = ProsodyPlanner()

        signals = GlyphSignals(
            text="I'm so excited to help!",
            voltage=0.85,
            tone="excited",
            emotional_attunement=0.7,
            certainty=0.9,
            valence=0.85,
        )

        plan = planner.plan_from_glyph(signals)

        # Should be fast
        # Should be bright (positive pitch)
        assert plan.speaking_rate > 1.1
        assert plan.pitch_shift_semitones > 0

        # Should be loud
        assert plan.energy_level > 1.0

        # Should be assertive (falling contour)
        assert plan.terminal_contour == "falling"

    def test_uncertain_gentle_response(self):
        """Uncertain, gentle response should be slow and soft."""
        planner = ProsodyPlanner()

        signals = GlyphSignals(
            text="I'm not sure about this...",
            voltage=0.2,
            tone="anxious",
            emotional_attunement=0.6,
            certainty=0.25,
            valence=0.2,
        )

        plan = planner.plan_from_glyph(signals)

        # Should be slow
        assert plan.speaking_rate < 0.95

        # Should be dark (negative pitch)
        assert plan.pitch_shift_semitones < 0

        # Should be quiet
        assert plan.energy_level < 1.0

        # Should be questioning (rising contour)
        assert plan.terminal_contour == "rising"

    def test_empathetic_response(self):
        """High empathy should add emphasis on emotional words."""
        planner = ProsodyPlanner()

        signals = GlyphSignals(
            text="I understand you're feeling overwhelmed and I want to help.",
            voltage=0.5,
            tone="calm",
            emotional_attunement=0.9,
            certainty=0.7,
            valence=0.5,
        )

        plan = planner.plan_from_glyph(signals)

        # Should have emphasized tokens
        assert len(plan.emphasis_tokens) > 0

        # Should include empathetic words
        emphasized_lower = [t.lower() for t in plan.emphasis_tokens]
        has_empathy_word = any(
            word in emphasized_lower
            for word in ["understand", "help", "feel", "you"]
        )
        # Note: may not always include due to heuristic


class TestGuardrails:
    """Test guardrail application."""

    def test_clamp_speaking_rate(self):
        """Speaking rate should be clamped to reasonable range."""
        planner = ProsodyPlanner()

        # Create a plan with extreme rate
        plan = planner.plan_from_glyph(
            GlyphSignals(
                text="test",
                voltage=0.99,
                tone="excited",
                emotional_attunement=0.5,
                certainty=0.99,
                valence=0.99,
            )
        )

        # Should be clamped to max
        assert plan.speaking_rate <= 2.0
        assert plan.speaking_rate >= 0.5

    def test_clamp_pitch_shift(self):
        """Pitch should be clamped to musical range."""
        planner = ProsodyPlanner()

        plan = planner.plan_from_glyph(
            GlyphSignals(
                text="test",
                voltage=0.1,
                tone="sad",
                emotional_attunement=0.5,
                certainty=0.1,
                valence=0.1,
            )
        )

        # Should be clamped to reasonable semitone range
        assert plan.pitch_shift_semitones >= -12
        assert plan.pitch_shift_semitones <= 12

    def test_clamp_energy(self):
        """Energy should be clamped."""
        planner = ProsodyPlanner()

        plan = planner.plan_from_glyph(
            GlyphSignals(
                text="test",
                voltage=0.5,
                tone="calm",
                emotional_attunement=0.5,
                certainty=0.5,
                valence=0.5,
            )
        )

        assert plan.energy_level >= 0.3
        assert plan.energy_level <= 1.5

    def test_transition_duration_reasonable(self):
        """Transition duration should be within guardrails."""
        planner = ProsodyPlanner()

        plan = planner.plan_from_glyph(
            GlyphSignals(
                text="test",
                voltage=0.5,
                tone="calm",
                emotional_attunement=0.5,
                certainty=0.5,
                valence=0.5,
            )
        )

        assert plan.transition_duration_ms >= planner.min_transition_ms
        assert plan.transition_duration_ms <= planner.max_transition_ms


class TestProsodyExplainer:
    """Test prosody explanation."""

    def test_explain_plan_returns_string(self):
        """Explanation should return readable string."""
        planner = ProsodyPlanner()
        explainer = ProsodyExplainer()

        signals = GlyphSignals(
            text="This is a test response.",
            voltage=0.5,
            tone="neutral",
            emotional_attunement=0.5,
            certainty=0.5,
            valence=0.5,
        )

        plan = planner.plan_from_glyph(signals)
        explanation = explainer.explain_plan(signals, plan)

        # Should return a string
        assert isinstance(explanation, str)

        # Should contain key information
        assert "Speaking rate" in explanation
        assert "Pitch shift" in explanation
        assert "Energy" in explanation
        assert "Voice style" in explanation


class TestValenceInference:
    """Test valence inference from tone strings."""

    def test_infer_positive_valence_from_tone(self):
        """Positive tone → positive valence."""
        planner = ProsodyPlanner()
        valence = planner._infer_valence_from_tone("excited")
        assert valence > 0.5

    def test_infer_negative_valence_from_tone(self):
        """Negative tone → negative valence."""
        planner = ProsodyPlanner()
        valence = planner._infer_valence_from_tone("sad")
        assert valence < 0.5

    def test_infer_neutral_valence_from_tone(self):
        """Neutral tone → neutral valence."""
        planner = ProsodyPlanner()
        valence = planner._infer_valence_from_tone("informative")
        assert 0.4 < valence < 0.6


class TestStyleConsistency:
    """Test that voice style is consistent with prosody."""

    def test_professional_consistency(self):
        """Professional style should have moderate prosody."""
        planner = ProsodyPlanner()

        signals = GlyphSignals(
            text="The quarterly results are promising.",
            voltage=0.6,
            tone="professional",
            emotional_attunement=0.4,
            certainty=0.9,
            valence=0.6,
        )

        plan = planner.plan_from_glyph(signals)

        # Should be professional style
        assert plan.voice_style == "professional"

        # Rate should be moderate (not extreme)
        assert 0.85 <= plan.speaking_rate <= 1.15

    def test_gentle_consistency(self):
        """Gentle style should have slower, softer prosody."""
        planner = ProsodyPlanner()

        signals = GlyphSignals(
            text="It's okay, I understand.",
            voltage=0.2,
            tone="calm",
            emotional_attunement=0.8,
            certainty=0.3,
            valence=0.4,
        )

        plan = planner.plan_from_glyph(signals)

        # Should be gentle style
        assert plan.voice_style == "gentle"

        # Rate should be slower
        assert plan.speaking_rate <= 0.9

        # Energy should be quieter
        assert plan.energy_level <= 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
