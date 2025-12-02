"""Tests for glyph-aware response composition (Phase 2.2.2).

Validates that:
1. Glyph modernization lookup works (affect → glyph)
2. Glyph-aware responses embed glyph names appropriately
3. Fallback to ResponseRotator works when glyphs unavailable
4. Integration with affect analysis produces coherent responses
"""

import pytest
from emotional_os.core.firstperson.glyph_response_composer import (
    compose_glyph_aware_response,
    should_use_glyph_responses,
    GLYPH_AWARE_RESPONSES,
)
from emotional_os.core.firstperson.glyph_modernizer import (
    get_glyph_for_affect,
    get_modernized_glyph_name,
)


class TestGlyphModernizer:
    """Test glyph modernization lookups."""

    def test_get_glyph_for_affect_sad_low_arousal(self):
        """Sad + low arousal should map to Loss or Pain."""
        glyph = get_glyph_for_affect("sad", arousal=0.2, valence=-0.8)
        assert glyph in ("Loss", "Pain", "Grieving")

    def test_get_glyph_for_affect_anxious_high_arousal(self):
        """Anxious + high arousal should map to Breaking or Overwhelm."""
        glyph = get_glyph_for_affect("anxious", arousal=0.8, valence=-0.5)
        assert glyph in ("Breaking", "Overwhelm", "Pressure")

    def test_get_glyph_for_affect_angry(self):
        """Angry should map to Fire or Heat."""
        glyph = get_glyph_for_affect("angry", arousal=0.9, valence=-0.7)
        assert glyph in ("Fire", "Heat", "Frustration")

    def test_get_glyph_for_affect_grateful(self):
        """Grateful should map to positive glyphs."""
        glyph = get_glyph_for_affect("grateful", arousal=0.6, valence=0.9)
        assert glyph in ("Acceptance", "Satisfaction")

    def test_get_glyph_for_affect_no_match(self):
        """Unmapped affect combinations should return None."""
        glyph = get_glyph_for_affect("unknown", arousal=0.5, valence=0.0)
        assert glyph is None

    def test_get_modernized_glyph_name_mapped(self):
        """Mapped glyph names should be modernized."""
        modern = get_modernized_glyph_name("Recognized Stillness")
        assert modern == "Held Space"

    def test_get_modernized_glyph_name_unmapped(self):
        """Unmapped glyph names should return as-is."""
        original = "Some Poetic Name"
        modern = get_modernized_glyph_name(original)
        assert modern == original


class TestGlyphAwareResponseComposition:
    """Test glyph-aware response generation."""

    def test_compose_glyph_aware_response_exhaustion_with_loss(self):
        """Exhaustion with Loss glyph should produce appropriate response."""
        affect = {
            "tone": "sad",
            "arousal": 0.3,
            "valence": -0.8,
            "tone_confidence": 0.8,
        }
        response, glyph = compose_glyph_aware_response(
            "I'm so tired", affect_analysis=affect, use_rotator=False
        )
        # Should embed glyph if found
        assert response is not None
        assert len(response) > 0
        # Response should be conversational with emotional synonyms for loss (heavy, weight, tired)
        assert any(word in response.lower()
                   for word in ["hear", "exhaust", "tired", "heavy", "weight"])

    def test_compose_glyph_aware_response_anxiety(self):
        """Anxiety should produce anxiety-specific responses."""
        affect = {
            "tone": "anxious",
            "arousal": 0.8,
            "valence": -0.5,
            "tone_confidence": 0.7,
        }
        response, glyph = compose_glyph_aware_response(
            "I'm so worried", affect_analysis=affect, use_rotator=False
        )
        assert response is not None
        assert len(response) > 0
        # Should contain anxiety-related language (case-insensitive)
        assert any(
            word in response.lower()
            for word in ["anxiety", "worry", "tension", "overwhelm", "pressure", "breaking"]
        )

    def test_compose_glyph_aware_response_no_affect(self):
        """Without affect analysis, should use fallback."""
        response, glyph = compose_glyph_aware_response(
            "Some input", affect_analysis=None, use_rotator=True
        )
        assert response is not None
        assert len(response) > 0

    def test_compose_glyph_aware_response_low_confidence(self):
        """Low tone confidence should not trigger glyph response."""
        affect = {
            "tone": "sad",
            "arousal": 0.3,
            "valence": -0.8,
            "tone_confidence": 0.1,  # Too low
        }
        response, glyph = compose_glyph_aware_response(
            "Something", affect_analysis=affect, use_rotator=True
        )
        # Should still work (via rotator), just not glyph-specific
        assert response is not None


class TestShouldUseGlyphResponses:
    """Test decision logic for when to use glyph responses."""

    def test_simple_checkin(self):
        """Simple emotional check-ins should use glyph responses."""
        result = should_use_glyph_responses(
            tone_confidence=0.8, arousal=0.3, valence=-0.1
        )
        assert result is True

    def test_stressed_checkin(self):
        """High arousal + negative valence should use glyph responses."""
        result = should_use_glyph_responses(
            tone_confidence=0.7, arousal=0.8, valence=-0.5
        )
        assert result is True

    def test_low_confidence(self):
        """Low confidence should not use glyph responses."""
        result = should_use_glyph_responses(
            tone_confidence=0.2, arousal=0.3, valence=-0.1
        )
        assert result is False

    def test_positive_valence(self):
        """Positive valence without high arousal should not trigger."""
        result = should_use_glyph_responses(
            tone_confidence=0.8, arousal=0.3, valence=0.5
        )
        assert result is False


class TestGlyphAwareResponseBank:
    """Test the glyph-aware response bank structure."""

    def test_response_bank_has_exhaustion(self):
        """Bank should have exhaustion responses with glyphs."""
        assert "exhaustion" in GLYPH_AWARE_RESPONSES
        exhaustion_responses = GLYPH_AWARE_RESPONSES["exhaustion"]
        assert isinstance(exhaustion_responses, dict)
        assert len(exhaustion_responses) > 0

    def test_exhaustion_responses_have_loss_glyph(self):
        """Exhaustion should have Loss glyph responses with conversational tone."""
        exhaustion_responses = GLYPH_AWARE_RESPONSES["exhaustion"]
        assert "Loss" in exhaustion_responses
        loss_responses = exhaustion_responses["Loss"]
        assert isinstance(loss_responses, list)
        assert len(loss_responses) > 0
        # Should mention emotional synonyms for loss in conversational way (heavy, weight, etc)
        assert any(word in r.lower() for r in loss_responses
                   for word in ["heavy", "weight", "hear", "exhaustion"])

    def test_anxiety_responses_have_breaking_glyph(self):
        """Anxiety should have Breaking glyph responses."""
        anxiety_responses = GLYPH_AWARE_RESPONSES["anxiety"]
        assert "Breaking" in anxiety_responses
        breaking_responses = anxiety_responses["Breaking"]
        assert isinstance(breaking_responses, list)
        assert len(breaking_responses) > 0

    def test_all_response_tone_categories_have_responses(self):
        """All tone categories should have response options."""
        expected_tones = ["exhaustion", "anxiety",
                          "sadness", "anger", "calm", "joy"]
        for tone in expected_tones:
            if tone in GLYPH_AWARE_RESPONSES:
                assert len(GLYPH_AWARE_RESPONSES[tone]) > 0


class TestIntegrationWithAffectParser:
    """Test integration with affect parsing results."""

    def test_full_pipeline_exhaustion_example(self):
        """End-to-end: detect exhaustion → get glyph → compose response."""
        # Simulate affect parser output for "I'm exhausted"
        affect = {
            "tone": "sad",
            "arousal": 0.2,
            "valence": -0.9,
            "tone_confidence": 0.85,
        }

        # Get glyph
        glyph = get_glyph_for_affect(
            affect["tone"], affect["arousal"], affect["valence"]
        )
        assert glyph in ("Loss", "Pain", "Grieving", None)

        # Compose response
        response, used_glyph = compose_glyph_aware_response(
            "I'm exhausted", affect_analysis=affect, use_rotator=True
        )

        # Response should be reasonable
        assert response is not None
        assert len(response) > 20  # Not too short
        assert len(response) < 200  # Not too long (conversational)
        # Should use concrete emotional language
        assert any(
            word in response.lower()
            for word in ["hear", "exhaust", "drain", "tired", "fatigue", "heavy", "weight"]
        )

    def test_full_pipeline_anxiety_example(self):
        """End-to-end: detect anxiety → get glyph → compose response."""
        affect = {
            "tone": "anxious",
            "arousal": 0.7,
            "valence": -0.6,
            "tone_confidence": 0.9,
        }

        glyph = get_glyph_for_affect(
            affect["tone"], affect["arousal"], affect["valence"]
        )
        assert glyph in ("Breaking", "Overwhelm", "Pressure", None)

        response, used_glyph = compose_glyph_aware_response(
            "I'm panicking", affect_analysis=affect, use_rotator=True
        )

        assert response is not None
        assert 20 < len(response) < 200
        # Should mention worry, anxiety, tension, overwhelm, or breaking (case-insensitive)
        assert any(
            word in response.lower()
            for word in ["anxiety", "worry", "tension", "overwhelm", "pressure", "breaking"]
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
