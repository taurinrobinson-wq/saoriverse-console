"""Comprehensive tests for Phase 3.5: Local LLM with Glyph Control.

Tests glyph schema, gate enforcement, post-processing, and curriculum building.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from glyph_lm_control import (
    Glyph, GlyphAttributes, GlyphMovement, GlyphRituality,
    GlyphRegistry, GatePolicy, StyleDirective, ControlTagRenderer,
    GLYPH_REGISTRY,
)
from safety_post_processor import (
    RecognitionRiskDetector, UncannynessEnforcer, RhythmEnforcer,
    MetaphorDensityMeter, SafetyPostProcessor, create_safe_response,
)
from training_corpus import (
    TrainingExample, TrainingCorpusBuilder,
    create_baseline_curriculum, create_safe_gate_schedule,
)


# ============================================================================
# GLYPH SCHEMA TESTS
# ============================================================================

class TestGlyphAttributes:
    """Test glyph attribute definitions."""

    def test_glyph_attributes_creation(self):
        """Test creating glyph attributes."""
        attrs = GlyphAttributes(
            valence=-0.6,
            intensity=0.7,
            rituality=0.8,
            movement=GlyphMovement.RECURSIVE,
            primary_family="Ache",
        )

        assert attrs.valence == -0.6
        assert attrs.intensity == 0.7
        assert attrs.movement == GlyphMovement.RECURSIVE

    def test_glyph_attributes_emotion_tags(self):
        """Test emotional tags in attributes."""
        attrs = GlyphAttributes(
            valence=0.5,
            intensity=0.6,
            rituality=0.7,
            movement=GlyphMovement.FLOWING,
            primary_family="Joy",
            related_emotions=["Aspiration", "Connection"],
        )

        assert "Aspiration" in attrs.related_emotions


class TestGlyphRegistry:
    """Test glyph registry and lookup."""

    def test_registry_loads_base_glyphs(self):
        """Test that registry loads base glyphs on init."""
        registry = GlyphRegistry()

        assert len(registry.glyphs) > 0
        assert registry.get("Recursive Ache") is not None
        assert registry.get("Grounded Joy") is not None

    def test_glyph_registration(self):
        """Test adding glyphs to registry."""
        registry = GlyphRegistry()
        initial_count = len(registry.glyphs)

        new_glyph = Glyph(
            name="Test Glyph",
            component_formula="X × Y",
            description="A test glyph",
            attributes=GlyphAttributes(
                valence=0.0,
                intensity=0.5,
                rituality=0.5,
                movement=GlyphMovement.FLOWING,
                primary_family="Test",
            ),
        )

        registry.register(new_glyph)

        assert len(registry.glyphs) == initial_count + 1
        assert registry.get("Test Glyph") is not None

    def test_list_glyphs_by_family(self):
        """Test filtering glyphs by family."""
        registry = GlyphRegistry()

        ache_glyphs = registry.list_by_family("Ache")
        joy_glyphs = registry.list_by_family("Joy")

        assert len(ache_glyphs) > 0
        assert len(joy_glyphs) > 0
        assert all(g.attributes.primary_family == "Ache" for g in ache_glyphs)

    def test_list_safe_for_uncanny_gate(self):
        """Test filtering glyphs by uncanny_ok gate."""
        registry = GlyphRegistry()

        # When uncanny_ok=False, should exclude safe_uncanny_ok glyphs
        safe_glyphs = registry.list_safe_for_uncanny(uncanny_ok=False)

        # All returned glyphs should have safe_uncanny_ok=False
        assert all(not g.safe_uncanny_ok for g in safe_glyphs)

        # When uncanny_ok=True, should include everything
        all_glyphs = registry.list_safe_for_uncanny(uncanny_ok=True)
        assert len(all_glyphs) >= len(safe_glyphs)


# ============================================================================
# GATE ENFORCEMENT TESTS
# ============================================================================

class TestGatePolicy:
    """Test gate policy validation."""

    def test_gate_validates_safe_glyph(self):
        """Test gate allows safe glyphs."""
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.8)
        safe_glyph = GLYPH_REGISTRY.get("Grounded Joy")

        assert gate.validates_glyph(safe_glyph)

    def test_gate_blocks_uncanny_when_disabled(self):
        """Test gate blocks uncanny glyphs when uncanny_ok=False."""
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.8)
        uncanny_glyph = GLYPH_REGISTRY.get("Dissolving Edge")

        assert not gate.validates_glyph(uncanny_glyph)

    def test_gate_allows_uncanny_when_enabled(self):
        """Test gate allows uncanny glyphs when uncanny_ok=True."""
        gate = GatePolicy(uncanny_ok=True, safety_bias=0.8)
        uncanny_glyph = GLYPH_REGISTRY.get("Dissolving Edge")

        assert gate.validates_glyph(uncanny_glyph)


# ============================================================================
# CONTROL TAG RENDERING TESTS
# ============================================================================

class TestControlTagRenderer:
    """Test rendering control tags for LLM prompts."""

    def test_render_glyphs(self):
        """Test rendering glyph control tags."""
        glyph = GLYPH_REGISTRY.get("Recursive Ache")
        gate = GatePolicy()

        tags = ControlTagRenderer.render_glyphs([(glyph, 0.8)], gate)

        assert "<GLYPH:" in tags
        assert "Recursive Ache" in tags
        assert "0.80" in tags

    def test_render_gates(self):
        """Test rendering gate control tags."""
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.85, directness=0.6)

        tags = ControlTagRenderer.render_gates(gate)

        assert "<GATE:" in tags
        assert "uncanny_ok:false" in tags
        assert "safety_bias:0.85" in tags

    def test_render_control_prefix(self):
        """Test rendering complete control prefix."""
        glyph = GLYPH_REGISTRY.get("Grounded Joy")
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.9)
        style = StyleDirective(
            register="warm", rhythm="slow", metaphor_density=0.5)

        prefix = ControlTagRenderer.render_control_prefix(
            [(glyph, 0.7)], gate, style)

        assert "<SYS>" in prefix
        assert "</SYS>" in prefix
        assert "<GLYPH:" in prefix
        assert "<GATE:" in prefix
        assert "<STYLE:" in prefix


# ============================================================================
# RECOGNITION RISK DETECTION TESTS
# ============================================================================

class TestRecognitionRiskDetector:
    """Test detection and removal of recognition-risk phrases."""

    def test_detect_recognition_phrases(self):
        """Test detecting 'I remember you' type phrases."""
        text = "I remember your face from before when we met"

        matches = RecognitionRiskDetector.detect(text)

        assert len(matches) > 0
        assert any("remember" in m[0].lower() for m in matches)

    def test_remove_risk_phrases(self):
        """Test removing recognition phrases."""
        text = "I remember you from before. This is important."

        cleaned, removed = RecognitionRiskDetector.remove_risk_phrases(text)

        assert len(removed) > 0
        assert "remember" not in cleaned.lower()

    def test_no_risk_in_safe_text(self):
        """Test that safe text has no recognition risk."""
        text = "I can sense a pattern in what you're expressing."

        matches = RecognitionRiskDetector.detect(text)

        assert len(matches) == 0


# ============================================================================
# UNCANNINESS ENFORCEMENT TESTS
# ============================================================================

class TestUncannynessEnforcer:
    """Test uncanny content detection and removal."""

    def test_flag_uncanny_content(self):
        """Test detecting uncanny phrases."""
        text = "The boundary dissolves and edges soften into blur."

        flagged = UncannynessEnforcer.flag_uncanny_content(text)

        assert len(flagged) > 0

    def test_remove_uncanny_content(self):
        """Test removing uncanny phrases."""
        text = "The boundary dissolves. This remains important."

        cleaned, count = UncannynessEnforcer.remove_uncanny_content(text)

        assert count > 0
        assert "dissolves" not in cleaned.lower()


# ============================================================================
# RHYTHM ENFORCEMENT TESTS
# ============================================================================

class TestRhythmEnforcer:
    """Test rhythm analysis and enforcement."""

    def test_analyze_rhythm(self):
        """Test analyzing sentence rhythm."""
        text = "Short. This is a medium sentence here. This is a very long sentence that contains many more words."

        metrics = RhythmEnforcer.analyze_rhythm(text)

        assert "avg_length" in metrics
        assert "short_count" in metrics
        assert metrics["short_count"] > 0

    def test_suggest_rhythm_improvements(self):
        """Test suggesting rhythm adjustments."""
        # All short sentences, but target is slow/contemplative
        text = "Short. Very short. Quick."

        suggestions = RhythmEnforcer.suggest_rhythm_improvements(text, "slow")

        assert len(suggestions) > 0


# ============================================================================
# METAPHOR DENSITY TESTS
# ============================================================================

class TestMetaphorDensityMeter:
    """Test metaphor density measurement."""

    def test_measure_density_literal(self):
        """Test measuring low metaphor density."""
        text = "The temperature is 72 degrees. The sky is blue."

        density = MetaphorDensityMeter.measure_density(text)

        assert density < 0.3

    def test_measure_density_metaphorical(self):
        """Test measuring high metaphor density."""
        text = "Like water flowing, your emotions echo through the ground of being."

        density = MetaphorDensityMeter.measure_density(text)

        assert density > 0.3


# ============================================================================
# SAFETY POST-PROCESSOR TESTS
# ============================================================================

class TestSafetyPostProcessor:
    """Test comprehensive post-processing."""

    def test_process_removes_recognition_risk(self):
        """Test that processor removes recognition-risk content."""
        text = "I remember your face from our last meeting."
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.9)
        style = StyleDirective()

        processor = SafetyPostProcessor(gate, style)
        result = processor.process(text)

        assert "remember" not in result.processed_text.lower()
        assert result.safety_violations_fixed > 0

    def test_process_enforces_uncanny_gate(self):
        """Test that processor enforces uncanny gate."""
        text = "The boundary dissolves and edges soften."
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.9)
        style = StyleDirective()

        processor = SafetyPostProcessor(gate, style)
        result = processor.process(text)

        assert "dissolves" not in result.processed_text.lower()

    def test_process_preserves_safe_content(self):
        """Test that processor preserves safe content."""
        text = "Here and enough. The ground holds you."
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.9)
        style = StyleDirective()

        processor = SafetyPostProcessor(gate, style)
        result = processor.process(text)

        assert len(result.processed_text) > 0
        assert "ground" in result.processed_text.lower()


# ============================================================================
# TRAINING CORPUS TESTS
# ============================================================================

class TestTrainingExample:
    """Test training example structure."""

    def test_example_creation(self):
        """Test creating a training example."""
        example = TrainingExample(
            id="test_001",
            context="Test context",
            prompt="Test prompt",
            response="Test response",
            glyphs=[{"name": "Grounded Joy", "intensity": 0.7}],
            gates={"uncanny_ok": False, "safety_bias": 0.8, "directness": 0.5},
            style={"register": "warm", "rhythm": "mixed",
                   "metaphor_density": 0.5},
            lexicon_tags=["test", "example"],
        )

        assert example.id == "test_001"
        assert "Grounded Joy" in str(example.glyphs)

    def test_example_to_jsonl(self):
        """Test serializing example to JSONL."""
        example = TrainingExample(
            id="test_001",
            context="Test",
            prompt="Prompt",
            response="Response",
            glyphs=[],
            gates={},
            style={},
            lexicon_tags=[],
        )

        jsonl_line = example.to_jsonl_line()

        assert jsonl_line.endswith("\n")
        assert "test_001" in jsonl_line


class TestTrainingCorpusBuilder:
    """Test corpus building."""

    def test_add_from_interaction(self):
        """Test adding training example from interaction."""
        builder = TrainingCorpusBuilder()
        glyph = GLYPH_REGISTRY.get("Grounded Joy")
        gate = GatePolicy()
        style = StyleDirective()

        example = builder.add_from_interaction(
            user_input="How are you feeling?",
            response="Here and enough.",
            glyphs=[(glyph, 0.8)],
            gates=gate,
            style=style,
            user_satisfaction=0.9,
        )

        assert len(builder.examples) == 1
        assert example.user_satisfaction == 0.9

    def test_get_statistics(self):
        """Test getting corpus statistics."""
        builder = TrainingCorpusBuilder()
        glyph = GLYPH_REGISTRY.get("Grounded Joy")
        gate = GatePolicy()
        style = StyleDirective()

        builder.add_from_interaction(
            user_input="Test",
            response="Response text here",
            glyphs=[(glyph, 0.8)],
            gates=gate,
            style=style,
            user_satisfaction=0.85,
        )

        stats = builder.get_statistics()

        assert stats["total_examples"] == 1
        assert stats["avg_user_satisfaction"] == 0.85

    def test_curriculum_progression(self):
        """Test curriculum learning progression."""
        builder = TrainingCorpusBuilder()
        curriculum = create_baseline_curriculum()
        gates_schedule = create_safe_gate_schedule()

        examples = builder.add_curriculum_progression(
            curriculum, gates_schedule)

        assert len(examples) == len(curriculum)
        assert len(builder.examples) == len(curriculum)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase35Integration:
    """Test integration of glyph control system."""

    def test_end_to_end_safe_response_generation(self):
        """Test complete pipeline from glyphs to safe response."""
        glyph = GLYPH_REGISTRY.get("Grounded Joy")
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.9)
        style = StyleDirective(register="warm", rhythm="slow")

        # Simulate LLM output with potential issues
        raw_response = (
            "I remember you from before. The boundaries dissolve here. "
            "But here and enough, the ground holds you."
        )

        safe_response, result = create_safe_response(
            raw_response,
            [glyph],
            gate,
            style,
        )

        assert "remember" not in safe_response.lower()
        assert "dissolves" not in safe_response.lower()
        assert result.safety_violations_fixed > 0

    def test_glyph_control_flow(self):
        """Test complete glyph control flow."""
        glyphs = [
            (GLYPH_REGISTRY.get("Recursive Ache"), 0.8),
            (GLYPH_REGISTRY.get("Grounded Joy"), 0.3),
        ]
        gate = GatePolicy(uncanny_ok=False, safety_bias=0.85, directness=0.5)
        style = StyleDirective(
            register="poetic", rhythm="mixed", metaphor_density=0.7)

        # Render control prefix
        prefix = ControlTagRenderer.render_control_prefix(glyphs, gate, style)

        # Verify structure
        assert "<SYS>" in prefix
        assert "<GLYPH:" in prefix
        assert "Recursive Ache" in prefix
        assert "Grounded Joy" in prefix
        assert "<GATE:" in prefix


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
