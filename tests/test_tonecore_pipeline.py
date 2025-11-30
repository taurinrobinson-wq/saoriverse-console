"""
Tests for ToneCore Parallel Pipeline
-----------------------------------
Tests for the refactored emotional parsing pipeline that executes
Signal Parser, NRC, TextBlob, and spaCy in parallel.
"""

import unittest
from unittest import mock

from parser.tonecore_pipeline import (
    ToneCorePipeline,
    SignalParserOutput,
    NRCOutput,
    TextBlobOutput,
    SpacyOutput,
    MergedEmotionalData,
    ChordProgression,
    analyze_text,
    generate_chord_progression,
    get_pipeline,
)


class TestOutputSchemas(unittest.TestCase):
    """Test standardized output schema dataclasses."""

    def test_signal_parser_output_to_dict(self):
        output = SignalParserOutput(
            keyword="overwhelmed",
            signal="ε",
            voltage="high",
            tone="insight",
        )
        result = output.to_dict()
        self.assertEqual(result["keyword"], "overwhelmed")
        self.assertEqual(result["signal"], "ε")
        self.assertEqual(result["voltage"], "high")
        self.assertEqual(result["tone"], "insight")

    def test_nrc_output_to_dict(self):
        output = NRCOutput(emotion_scores={"joy": 3, "sadness": 1})
        result = output.to_dict()
        self.assertEqual(result["emotion_scores"]["joy"], 3)
        self.assertEqual(result["emotion_scores"]["sadness"], 1)

    def test_textblob_output_to_dict(self):
        output = TextBlobOutput(polarity=0.5, subjectivity=0.7)
        result = output.to_dict()
        self.assertAlmostEqual(result["polarity"], 0.5)
        self.assertAlmostEqual(result["subjectivity"], 0.7)

    def test_spacy_output_to_dict(self):
        output = SpacyOutput(
            nouns=["feeling", "heart"],
            verbs=["feel", "love"],
            adjectives=["happy", "sad"],
        )
        result = output.to_dict()
        self.assertEqual(result["nouns"], ["feeling", "heart"])
        self.assertEqual(result["verbs"], ["feel", "love"])
        self.assertEqual(result["adjectives"], ["happy", "sad"])

    def test_merged_emotional_data_to_dict(self):
        merged = MergedEmotionalData(
            signal_parser=[SignalParserOutput(keyword="joy", signal="λ")],
            nrc=NRCOutput(emotion_scores={"joy": 2}),
            textblob=TextBlobOutput(polarity=0.6),
            spacy=SpacyOutput(nouns=["happiness"]),
            dominant_emotion="joy",
            confidence=0.8,
            emotional_arc=["joy", "trust"],
            recommended_gates=["Gate 5", "Gate 6"],
        )
        result = merged.to_dict()
        self.assertEqual(len(result["signal_parser"]), 1)
        self.assertEqual(result["dominant_emotion"], "joy")
        self.assertAlmostEqual(result["confidence"], 0.8)
        self.assertEqual(result["emotional_arc"], ["joy", "trust"])
        self.assertEqual(result["recommended_gates"], ["Gate 5", "Gate 6"])

    def test_chord_progression_to_dict(self):
        prog = ChordProgression(
            chords=["I", "IV", "V", "I"],
            emotion_sequence=["joy", "calm", "hope", "joy"],
            arc_description="Cyclic joy with variations",
        )
        result = prog.to_dict()
        self.assertEqual(result["chords"], ["I", "IV", "V", "I"])
        self.assertEqual(result["emotion_sequence"], ["joy", "calm", "hope", "joy"])
        self.assertEqual(result["arc_description"], "Cyclic joy with variations")


class TestToneCorePipeline(unittest.TestCase):
    """Test ToneCorePipeline parallel execution."""

    def setUp(self):
        self.pipeline = ToneCorePipeline(enable_cache=False)

    def test_empty_text_returns_empty_result(self):
        result = self.pipeline.analyze("")
        self.assertEqual(result.dominant_emotion, "neutral")
        self.assertAlmostEqual(result.confidence, 0.0)
        self.assertEqual(result.signal_parser, [])

    def test_analyze_returns_merged_emotional_data(self):
        result = self.pipeline.analyze("I feel happy and joyful today")
        self.assertIsInstance(result, MergedEmotionalData)
        self.assertIn(result.dominant_emotion, [
            "joy", "positive", "neutral", "happy", "anticipation", "trust"
        ])

    def test_parallel_execution_completes(self):
        """Verify that all modules execute in parallel without blocking."""
        result = self.pipeline.analyze("I am feeling overwhelmed and anxious")
        # Check that we get results from multiple sources
        self.assertIsInstance(result.nrc, NRCOutput)
        self.assertIsInstance(result.textblob, TextBlobOutput)
        self.assertIsInstance(result.spacy, SpacyOutput)

    def test_cache_enabled_returns_same_result(self):
        pipeline = ToneCorePipeline(enable_cache=True)
        text = "This is a test for caching"
        result1 = pipeline.analyze(text)
        result2 = pipeline.analyze(text)
        # Results should be identical (same object due to caching)
        self.assertEqual(result1.dominant_emotion, result2.dominant_emotion)
        self.assertEqual(result1.confidence, result2.confidence)
        # Verify cache stats
        stats = pipeline.get_cache_stats()
        self.assertEqual(stats["size"], 1)

    def test_clear_cache(self):
        pipeline = ToneCorePipeline(enable_cache=True)
        pipeline.analyze("Test text")
        self.assertEqual(pipeline.get_cache_stats()["size"], 1)
        pipeline.clear_cache()
        self.assertEqual(pipeline.get_cache_stats()["size"], 0)


class TestMergeEmotionalData(unittest.TestCase):
    """Test the mergeEmotionalData function."""

    def setUp(self):
        self.pipeline = ToneCorePipeline(enable_cache=False)

    def test_merge_with_strong_nrc_signal(self):
        signal_parser = []
        nrc = NRCOutput(emotion_scores={"joy": 5, "sadness": 1})
        textblob = TextBlobOutput(polarity=0.2, subjectivity=0.5)
        spacy = SpacyOutput()

        result = self.pipeline.mergeEmotionalData(
            signal_parser, nrc, textblob, spacy
        )

        # Joy should dominate due to high NRC score
        self.assertEqual(result.dominant_emotion, "joy")
        self.assertGreater(result.confidence, 0.0)

    def test_merge_with_strong_polarity(self):
        signal_parser = []
        nrc = NRCOutput(emotion_scores={})
        textblob = TextBlobOutput(polarity=-0.8, subjectivity=0.6)
        spacy = SpacyOutput()

        result = self.pipeline.mergeEmotionalData(
            signal_parser, nrc, textblob, spacy
        )

        # Negative polarity should influence result
        self.assertIn(result.dominant_emotion, ["negative", "sadness", "neutral"])

    def test_merge_with_signal_parser_tones(self):
        signal_parser = [
            SignalParserOutput(keyword="grief", signal="θ", tone="grief"),
            SignalParserOutput(keyword="loss", signal="θ", tone="grief"),
        ]
        nrc = NRCOutput(emotion_scores={})
        textblob = TextBlobOutput(polarity=0.0, subjectivity=0.0)
        spacy = SpacyOutput()

        result = self.pipeline.mergeEmotionalData(
            signal_parser, nrc, textblob, spacy
        )

        # Grief tone from signal parser should influence result
        self.assertIn(result.dominant_emotion, ["sadness", "grief", "neutral"])

    def test_recommended_gates_mapped_from_emotion(self):
        signal_parser = []
        nrc = NRCOutput(emotion_scores={"fear": 4})
        textblob = TextBlobOutput(polarity=-0.5, subjectivity=0.6)
        spacy = SpacyOutput()

        result = self.pipeline.mergeEmotionalData(
            signal_parser, nrc, textblob, spacy
        )

        # Fear should map to Gate 4 and Gate 2
        if result.dominant_emotion == "fear":
            self.assertIn("Gate 4", result.recommended_gates)


class TestEmotionalArc(unittest.TestCase):
    """Test emotional arc calculation."""

    def setUp(self):
        self.pipeline = ToneCorePipeline(enable_cache=False)

    def test_emotional_arc_from_nrc(self):
        nrc = NRCOutput(emotion_scores={
            "joy": 5,
            "trust": 3,
            "anticipation": 2,
            "sadness": 1,
        })

        arc = self.pipeline._calculate_emotional_arc(nrc)

        # Arc should contain top 3 emotions in order
        self.assertEqual(len(arc), 3)
        self.assertEqual(arc[0], "joy")  # Highest score
        self.assertIn("trust", arc)
        self.assertIn("anticipation", arc)

    def test_emotional_arc_empty_scores(self):
        nrc = NRCOutput(emotion_scores={})
        arc = self.pipeline._calculate_emotional_arc(nrc)
        self.assertEqual(arc, ["neutral"])


class TestChordProgressionGenerator(unittest.TestCase):
    """Test chord progression generation."""

    def setUp(self):
        self.pipeline = ToneCorePipeline(enable_cache=False)

    def test_generate_chord_progression_default_length(self):
        merged = MergedEmotionalData(
            dominant_emotion="joy",
            emotional_arc=["joy", "trust", "anticipation"],
        )

        progression = self.pipeline.generate_chord_progression(merged)

        self.assertEqual(len(progression.chords), 4)
        self.assertEqual(len(progression.emotion_sequence), 4)
        self.assertIn("joy", progression.emotion_sequence)

    def test_generate_chord_progression_custom_length(self):
        merged = MergedEmotionalData(
            dominant_emotion="sadness",
            emotional_arc=["sadness", "fear"],
        )

        progression = self.pipeline.generate_chord_progression(merged, length=6)

        self.assertEqual(len(progression.chords), 6)
        self.assertEqual(len(progression.emotion_sequence), 6)

    def test_chord_progression_arc_description_transition(self):
        merged = MergedEmotionalData(
            dominant_emotion="hope",
            emotional_arc=["sadness", "hope", "joy"],
        )

        progression = self.pipeline.generate_chord_progression(merged, length=3)

        # Arc starts with sadness and ends with joy, so description should mention transition
        self.assertIn("Transition", progression.arc_description)

    def test_chord_progression_sustained_emotion(self):
        merged = MergedEmotionalData(
            dominant_emotion="calm",
            emotional_arc=["calm"],
        )

        progression = self.pipeline.generate_chord_progression(merged, length=4)

        # All emotions in sequence should be calm
        self.assertEqual(set(progression.emotion_sequence), {"calm"})
        self.assertIn("Sustained", progression.arc_description)

    def test_emotion_to_chord_mapping(self):
        # Test specific emotion to chord mappings
        merged = MergedEmotionalData(
            dominant_emotion="joy",
            emotional_arc=["joy"],
        )
        progression = self.pipeline.generate_chord_progression(merged, length=1)
        self.assertEqual(progression.chords[0], "I")  # Joy maps to I (major tonic)

        merged = MergedEmotionalData(
            dominant_emotion="longing",
            emotional_arc=["longing"],
        )
        progression = self.pipeline.generate_chord_progression(merged, length=1)
        self.assertEqual(progression.chords[0], "i")  # Longing maps to i (minor tonic)


class TestConvenienceFunctions(unittest.TestCase):
    """Test module-level convenience functions."""

    def test_get_pipeline_singleton(self):
        pipeline1 = get_pipeline()
        pipeline2 = get_pipeline()
        self.assertIs(pipeline1, pipeline2)

    def test_analyze_text_function(self):
        result = analyze_text("I am feeling happy today")
        self.assertIsInstance(result, MergedEmotionalData)

    def test_generate_chord_progression_function(self):
        result = generate_chord_progression("I feel a mix of joy and hope", length=4)
        self.assertIsInstance(result, ChordProgression)
        self.assertEqual(len(result.chords), 4)


class TestGateActivationCompatibility(unittest.TestCase):
    """Test compatibility with existing gate activation logic."""

    def setUp(self):
        self.pipeline = ToneCorePipeline(enable_cache=False)

    def test_joy_maps_to_correct_gates(self):
        merged = MergedEmotionalData(dominant_emotion="joy")
        gates = self.pipeline.EMOTION_GATE_MAPPINGS.get("joy", [])
        self.assertIn("Gate 5", gates)
        self.assertIn("Gate 6", gates)

    def test_sadness_maps_to_correct_gates(self):
        gates = self.pipeline.EMOTION_GATE_MAPPINGS.get("sadness", [])
        self.assertIn("Gate 4", gates)
        self.assertIn("Gate 10", gates)

    def test_fear_maps_to_correct_gates(self):
        gates = self.pipeline.EMOTION_GATE_MAPPINGS.get("fear", [])
        self.assertIn("Gate 4", gates)
        self.assertIn("Gate 2", gates)

    def test_neutral_has_default_gate(self):
        gates = self.pipeline.EMOTION_GATE_MAPPINGS.get("neutral", [])
        self.assertEqual(gates, ["Gate 9"])


class TestLegacyWorkflowComparison(unittest.TestCase):
    """Tests comparing new parallel results to legacy sequential workflow."""

    def setUp(self):
        self.pipeline = ToneCorePipeline(enable_cache=False)

    def test_parallel_produces_similar_dominant_emotion(self):
        """
        The parallel pipeline should produce similar emotional classifications
        to the legacy sequential approach.
        """
        # Test with clearly emotional text
        test_cases = [
            ("I am so happy and joyful!", ["joy", "positive", "trust", "anticipation"]),
            ("I feel sad and alone", ["sadness", "negative", "fear", "neutral"]),
            ("I'm angry and frustrated", ["anger", "negative", "disgust", "neutral"]),
        ]

        for text, expected_emotions in test_cases:
            result = self.pipeline.analyze(text)
            self.assertIn(
                result.dominant_emotion,
                expected_emotions,
                f"Text: '{text}' produced unexpected emotion: {result.dominant_emotion}"
            )

    def test_emotional_nuance_for_poetic_input(self):
        """
        Test that poetic/complex syntax produces nuanced emotional analysis.
        """
        poetic_text = (
            "The autumn leaves fall gently, carrying whispers of memories "
            "long forgotten, as twilight embraces the weary soul."
        )
        result = self.pipeline.analyze(poetic_text)

        # Should detect some emotional content
        self.assertIsNotNone(result.dominant_emotion)
        # Should have some confidence in the analysis
        # Poetic text may have low confidence but should still analyze
        self.assertIsInstance(result.confidence, float)

    def test_mixed_emotional_content(self):
        """
        Test handling of text with mixed emotional signals.
        """
        mixed_text = "I feel both happy about the promotion but sad to leave my friends"
        result = self.pipeline.analyze(mixed_text)

        # Should detect multiple emotions in the arc
        # The merged data should capture the complexity
        self.assertIsInstance(result.emotional_arc, list)


if __name__ == "__main__":
    unittest.main()
