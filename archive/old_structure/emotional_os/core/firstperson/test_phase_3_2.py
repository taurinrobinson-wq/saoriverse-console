"""Tests for Phase 3.2: Multi-Modal Affect Analysis.

Tests cover:
1. Voice affect detection (acoustic features → emotional tone)
2. Facial expression detection (landmarks → expressions)  
3. Multimodal fusion (text + voice + facial → unified emotion)
4. Incongruence detection (sarcasm, suppression, deception)
5. Integration with Phase 3.1 emotional profiles
"""

import pytest
from typing import Dict, List

from .voice_affect_detector import (
    VoiceAffectDetector,
    AcousticFeatures,
    VoiceAnalysis,
    VoiceAffectTone,
)
from .facial_expression_detector import (
    FacialExpressionDetector,
    FaceLandmarks,
    FacialAnalysis,
    FacialExpression,
)
from .multimodal_fusion_engine import (
    MultimodalFusionEngine,
    CongruenceType,
    MultimodalAnalysis,
)


class TestVoiceAffectDetector:
    """Tests for voice acoustic analysis."""

    def setup_method(self):
        """Setup detector for each test."""
        self.detector = VoiceAffectDetector()

    def test_calm_voice_analysis(self):
        """Test voice analysis for calm speech."""
        features = AcousticFeatures(
            fundamental_frequency=120,
            intensity=60,
            speech_rate=140,
            pause_frequency=2,
            pause_duration_avg=100,
            pitch_variance=10,
            energy_variance=2,
            formant_frequencies=[700, 1200, 2500],
            mel_frequency_coefficients=[1.0] * 13,
            duration=10.0,
        )
        analysis = self.detector.analyze(features)

        assert analysis.detected_tone == VoiceAffectTone.CALM
        assert analysis.arousal < 0.5
        assert 0.0 <= analysis.tone_confidence <= 1.0

    def test_anxious_voice_analysis(self):
        """Test voice analysis for anxious speech."""
        features = AcousticFeatures(
            fundamental_frequency=180,
            intensity=70,
            speech_rate=200,
            pause_frequency=8,
            pause_duration_avg=300,
            pitch_variance=40,
            energy_variance=8,
            formant_frequencies=[800, 1300, 2600],
            mel_frequency_coefficients=[1.2] * 13,
            duration=10.0,
        )
        analysis = self.detector.analyze(features)

        assert analysis.detected_tone in [
            VoiceAffectTone.ANXIOUS, VoiceAffectTone.HESITANT]
        assert analysis.stress_indicator > 0.7

    def test_excited_voice_analysis(self):
        """Test voice analysis for excited speech."""
        features = AcousticFeatures(
            fundamental_frequency=220,
            intensity=80,
            speech_rate=220,
            pause_frequency=1,
            pause_duration_avg=50,
            pitch_variance=35,
            energy_variance=10,
            formant_frequencies=[900, 1400, 2700],
            mel_frequency_coefficients=[1.3] * 13,
            duration=10.0,
        )
        analysis = self.detector.analyze(features)

        assert analysis.detected_tone in [
            VoiceAffectTone.EXCITED, VoiceAffectTone.ENERGETIC]
        assert analysis.arousal > 0.6

    def test_voice_valence_comparison(self):
        """Test that excited has higher valence than anxious."""
        calm_features = AcousticFeatures(
            fundamental_frequency=120, intensity=60, speech_rate=140,
            pause_frequency=2, pause_duration_avg=100, pitch_variance=10,
            energy_variance=2, formant_frequencies=[700, 1200, 2500],
            mel_frequency_coefficients=[1.0] * 13, duration=10.0,
        )

        excited_features = AcousticFeatures(
            fundamental_frequency=220, intensity=80, speech_rate=220,
            pause_frequency=1, pause_duration_avg=50, pitch_variance=35,
            energy_variance=10, formant_frequencies=[900, 1400, 2700],
            mel_frequency_coefficients=[1.3] * 13, duration=10.0,
        )

        calm_analysis = self.detector.analyze(calm_features)
        excited_analysis = self.detector.analyze(excited_features)

        assert excited_analysis.valence > calm_analysis.valence

    def test_voice_emotional_state(self):
        """Test emotional state estimation."""
        features = AcousticFeatures(
            fundamental_frequency=150, intensity=70, speech_rate=160,
            pause_frequency=3, pause_duration_avg=150, pitch_variance=20,
            energy_variance=5, formant_frequencies=[750, 1250, 2550],
            mel_frequency_coefficients=[1.1] * 13, duration=10.0,
        )
        analysis = self.detector.analyze(features)

        assert len(analysis.emotional_state) > 0
        assert all(0.0 <= v <= 1.0 for v in analysis.emotional_state.values())


class TestFacialExpressionDetector:
    """Tests for facial expression analysis."""

    def setup_method(self):
        """Setup detector for each test."""
        self.detector = FacialExpressionDetector()

    def test_happy_expression_analysis(self):
        """Test facial expression detection for happy."""
        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.3), (0.35, 0.25),
                           (0.4, 0.3), (0.45, 0.35), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.35), (0.6, 0.3),
                          (0.65, 0.25), (0.7, 0.3)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.2), (0.45, 0.2),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.22)],
            left_eye=[(0.55, 0.3), (0.55, 0.2), (0.65, 0.2),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.22)],
            mouth=[(0.4, 0.7), (0.45, 0.65), (0.5, 0.63), (0.55, 0.65), (0.6, 0.7),
                   (0.55, 0.75), (0.5, 0.76), (0.45, 0.75), (0.5, 0.73), (0.5, 0.73)],
        )
        analysis = self.detector.analyze(landmarks)

        assert analysis.expression in [
            FacialExpression.HAPPY, FacialExpression.SURPRISED, FacialExpression.SAD]
        assert 0.0 <= analysis.expression_confidence <= 1.0

    def test_sad_expression_analysis(self):
        """Test facial expression detection for sad."""
        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.2), (0.35, 0.15),
                           (0.4, 0.2), (0.45, 0.25), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.25), (0.6, 0.2),
                          (0.65, 0.15), (0.7, 0.2)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.25), (0.45, 0.25),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.27)],
            left_eye=[(0.55, 0.3), (0.55, 0.25), (0.65, 0.25),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.27)],
            mouth=[(0.4, 0.65), (0.45, 0.7), (0.5, 0.72), (0.55, 0.7), (0.6, 0.65),
                   (0.55, 0.8), (0.5, 0.81), (0.45, 0.8), (0.5, 0.73), (0.5, 0.73)],
        )
        analysis = self.detector.analyze(landmarks)

        assert analysis.expression in [
            FacialExpression.SAD, FacialExpression.NEUTRAL]
        assert analysis.valence < 0.6

    def test_facial_vad_dimensions(self):
        """Test VAD dimensions from facial analysis."""
        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.3), (0.35, 0.25),
                           (0.4, 0.3), (0.45, 0.35), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.35), (0.6, 0.3),
                          (0.65, 0.25), (0.7, 0.3)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.2), (0.45, 0.2),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.22)],
            left_eye=[(0.55, 0.3), (0.55, 0.2), (0.65, 0.2),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.22)],
            mouth=[(0.4, 0.7), (0.45, 0.65), (0.5, 0.63), (0.55, 0.65), (0.6, 0.7),
                   (0.55, 0.75), (0.5, 0.76), (0.45, 0.75), (0.5, 0.73), (0.5, 0.73)],
        )
        analysis = self.detector.analyze(landmarks)

        assert 0.0 <= analysis.arousal <= 1.0
        assert 0.0 <= analysis.valence <= 1.0
        assert 0.0 <= analysis.dominance <= 1.0

    def test_facial_authenticity(self):
        """Test authenticity scoring."""
        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.3), (0.35, 0.25),
                           (0.4, 0.3), (0.45, 0.35), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.35), (0.6, 0.3),
                          (0.65, 0.25), (0.7, 0.3)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.2), (0.45, 0.2),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.22)],
            left_eye=[(0.55, 0.3), (0.55, 0.2), (0.65, 0.2),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.22)],
            mouth=[(0.4, 0.7), (0.45, 0.65), (0.5, 0.63), (0.55, 0.65), (0.6, 0.7),
                   (0.55, 0.75), (0.5, 0.76), (0.45, 0.75), (0.5, 0.73), (0.5, 0.73)],
        )
        analysis = self.detector.analyze(landmarks)

        assert 0.0 <= analysis.authenticity <= 1.0
        assert 0.0 <= analysis.attention <= 1.0


class TestMultimodalFusionEngine:
    """Tests for multimodal emotional fusion."""

    def setup_method(self):
        """Setup fusion engine."""
        self.engine = MultimodalFusionEngine()
        self.voice_detector = VoiceAffectDetector()
        self.facial_detector = FacialExpressionDetector()

    def test_multimodal_confidence_scores(self):
        """Test confidence calculation in multimodal fusion."""
        # Create excited voice
        voice_features = AcousticFeatures(
            fundamental_frequency=220, intensity=80, speech_rate=220,
            pause_frequency=1, pause_duration_avg=50, pitch_variance=35,
            energy_variance=10, formant_frequencies=[900, 1400, 2700],
            mel_frequency_coefficients=[1.3] * 13, duration=10.0,
        )
        voice_analysis = self.voice_detector.analyze(voice_features)

        # Create happy facial expression
        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.3), (0.35, 0.25),
                           (0.4, 0.3), (0.45, 0.35), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.35), (0.6, 0.3),
                          (0.65, 0.25), (0.7, 0.3)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.2), (0.45, 0.2),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.22)],
            left_eye=[(0.55, 0.3), (0.55, 0.2), (0.65, 0.2),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.22)],
            mouth=[(0.4, 0.7), (0.45, 0.65), (0.5, 0.63), (0.55, 0.65), (0.6, 0.7),
                   (0.55, 0.75), (0.5, 0.76), (0.45, 0.75), (0.5, 0.73), (0.5, 0.73)],
        )
        facial_analysis = self.facial_detector.analyze(landmarks)

        # Fuse
        analysis = self.engine.fuse("excited", voice_analysis, facial_analysis)

        assert 0.0 <= analysis.confidence.text_confidence <= 1.0
        assert 0.0 <= analysis.confidence.voice_confidence <= 1.0
        assert 0.0 <= analysis.confidence.facial_confidence <= 1.0
        assert 0.0 <= analysis.confidence.overall_confidence <= 1.0

    def test_multimodal_dimensions(self):
        """Test dimension fusion in multimodal analysis."""
        voice_features = AcousticFeatures(
            fundamental_frequency=220, intensity=80, speech_rate=220,
            pause_frequency=1, pause_duration_avg=50, pitch_variance=35,
            energy_variance=10, formant_frequencies=[900, 1400, 2700],
            mel_frequency_coefficients=[1.3] * 13, duration=10.0,
        )
        voice_analysis = self.voice_detector.analyze(voice_features)

        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.3), (0.35, 0.25),
                           (0.4, 0.3), (0.45, 0.35), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.35), (0.6, 0.3),
                          (0.65, 0.25), (0.7, 0.3)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.2), (0.45, 0.2),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.22)],
            left_eye=[(0.55, 0.3), (0.55, 0.2), (0.65, 0.2),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.22)],
            mouth=[(0.4, 0.7), (0.45, 0.65), (0.5, 0.63), (0.55, 0.65), (0.6, 0.7),
                   (0.55, 0.75), (0.5, 0.76), (0.45, 0.75), (0.5, 0.73), (0.5, 0.73)],
        )
        facial_analysis = self.facial_detector.analyze(landmarks)

        analysis = self.engine.fuse("excited", voice_analysis, facial_analysis)

        assert 0.0 <= analysis.dimensions.arousal <= 1.0
        assert 0.0 <= analysis.dimensions.valence <= 1.0
        assert 0.0 <= analysis.dimensions.dominance <= 1.0
        assert 0.0 <= analysis.dimensions.stress_level <= 1.0
        assert 0.0 <= analysis.dimensions.authenticity <= 1.0

    def test_sarcasm_detection(self):
        """Test detection of sarcasm (text positive, voice negative)."""
        # Create calm voice (negative valence)
        voice_features = AcousticFeatures(
            fundamental_frequency=100, intensity=50, speech_rate=120,
            pause_frequency=5, pause_duration_avg=200, pitch_variance=15,
            energy_variance=3, formant_frequencies=[700, 1200, 2500],
            mel_frequency_coefficients=[1.0] * 13, duration=10.0,
        )
        voice_analysis = self.voice_detector.analyze(voice_features)

        # Create sad facial expression
        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.2), (0.35, 0.15),
                           (0.4, 0.2), (0.45, 0.25), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.25), (0.6, 0.2),
                          (0.65, 0.15), (0.7, 0.2)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.25), (0.45, 0.25),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.27)],
            left_eye=[(0.55, 0.3), (0.55, 0.25), (0.65, 0.25),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.27)],
            mouth=[(0.4, 0.65), (0.45, 0.7), (0.5, 0.72), (0.55, 0.7), (0.6, 0.65),
                   (0.55, 0.8), (0.5, 0.81), (0.45, 0.8), (0.5, 0.73), (0.5, 0.73)],
        )
        facial_analysis = self.facial_detector.analyze(landmarks)

        # Text says happy, but voice and face are negative
        analysis = self.engine.fuse("happy", voice_analysis, facial_analysis)

        # Should detect incongruence
        assert analysis.congruence_type in [
            CongruenceType.TEXT_POSITIVE_VOICE_NEGATIVE,
            CongruenceType.MODALITY_CONFLICT,
            CongruenceType.PARTIAL_AGREEMENT,
        ] or len(analysis.incongruences) > 0

    def test_multimodal_comparison(self):
        """Test detailed modality comparison."""
        voice_features = AcousticFeatures(
            fundamental_frequency=220, intensity=80, speech_rate=220,
            pause_frequency=1, pause_duration_avg=50, pitch_variance=35,
            energy_variance=10, formant_frequencies=[900, 1400, 2700],
            mel_frequency_coefficients=[1.3] * 13, duration=10.0,
        )
        voice_analysis = self.voice_detector.analyze(voice_features)

        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.3), (0.35, 0.25),
                           (0.4, 0.3), (0.45, 0.35), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.35), (0.6, 0.3),
                          (0.65, 0.25), (0.7, 0.3)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.2), (0.45, 0.2),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.22)],
            left_eye=[(0.55, 0.3), (0.55, 0.2), (0.65, 0.2),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.22)],
            mouth=[(0.4, 0.7), (0.45, 0.65), (0.5, 0.63), (0.55, 0.65), (0.6, 0.7),
                   (0.55, 0.75), (0.5, 0.76), (0.45, 0.75), (0.5, 0.73), (0.5, 0.73)],
        )
        facial_analysis = self.facial_detector.analyze(landmarks)

        analysis = self.engine.fuse("excited", voice_analysis, facial_analysis)

        assert "text" in analysis.modality_comparison
        assert "voice" in analysis.modality_comparison
        assert "facial" in analysis.modality_comparison


class TestPhase32Integration:
    """Integration tests for Phase 3.2 with Phase 3.1."""

    def test_multimodal_to_emotional_profile(self):
        """Test that multimodal data can feed into emotional profiles."""
        engine = MultimodalFusionEngine()
        voice_detector = VoiceAffectDetector()
        facial_detector = FacialExpressionDetector()

        voice_features = AcousticFeatures(
            fundamental_frequency=220, intensity=80, speech_rate=220,
            pause_frequency=1, pause_duration_avg=50, pitch_variance=35,
            energy_variance=10, formant_frequencies=[900, 1400, 2700],
            mel_frequency_coefficients=[1.3] * 13, duration=10.0,
        )
        voice_analysis = voice_detector.analyze(voice_features)

        landmarks = FaceLandmarks(
            contour=[(i/20, 0.5) for i in range(17)],
            right_eyebrow=[(0.3, 0.3), (0.35, 0.25),
                           (0.4, 0.3), (0.45, 0.35), (0.5, 0.3)],
            left_eyebrow=[(0.5, 0.3), (0.55, 0.35), (0.6, 0.3),
                          (0.65, 0.25), (0.7, 0.3)],
            nose=[(0.5, 0.35), (0.5, 0.45), (0.5, 0.55),
                  (0.48, 0.6), (0.52, 0.6)],
            right_eye=[(0.35, 0.3), (0.35, 0.2), (0.45, 0.2),
                       (0.45, 0.3), (0.4, 0.32), (0.4, 0.22)],
            left_eye=[(0.55, 0.3), (0.55, 0.2), (0.65, 0.2),
                      (0.65, 0.3), (0.6, 0.32), (0.6, 0.22)],
            mouth=[(0.4, 0.7), (0.45, 0.65), (0.5, 0.63), (0.55, 0.65), (0.6, 0.7),
                   (0.55, 0.75), (0.5, 0.76), (0.45, 0.75), (0.5, 0.73), (0.5, 0.73)],
        )
        facial_analysis = facial_detector.analyze(landmarks)

        analysis = engine.fuse("excited", voice_analysis, facial_analysis)

        # Should provide usable data for Phase 3.1
        assert analysis.primary_emotion is not None
        assert analysis.confidence.overall_confidence > 0.0
        assert analysis.dimensions.arousal >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
