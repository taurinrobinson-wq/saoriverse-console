"""Voice Affect Detection for Phase 3.2.

Analyzes acoustic features of speech to detect emotional tone:
- Pitch (fundamental frequency)
- Intensity (loudness/energy)
- Rate (speech speed)
- Pauses (hesitation, confidence)
- Timbre (voice quality)

Integrates with EmotionalProfileManager to enhance text-based detection.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class VoiceAffectTone(Enum):
    """Voice-based emotional tones detected from acoustic features."""
    CALM = "calm"              # Low pitch, steady rhythm, controlled
    ENERGETIC = "energetic"    # High pitch, fast rate, strong intensity
    HESITANT = "hesitant"      # Variable pitch, slow rate, frequent pauses
    ANGRY = "angry"            # Low-mid pitch, high intensity, fast rate
    SAD = "sad"                # Low pitch, slow rate, low intensity
    EXCITED = "excited"        # High pitch, fast rate, high intensity
    ANXIOUS = "anxious"        # Variable pitch, fast rate, nervous pauses
    CONFIDENT = "confident"    # Steady pitch, controlled rate, minimal pauses


@dataclass
class AcousticFeatures:
    """Raw acoustic features extracted from audio."""
    fundamental_frequency: float      # Hz (pitch)
    intensity: float                  # dB (loudness)
    speech_rate: float                # words per minute
    pause_frequency: int              # number of pauses
    pause_duration_avg: float         # average pause length (ms)
    pitch_variance: float             # std deviation of pitch
    energy_variance: float            # std deviation of intensity
    formant_frequencies: List[float]  # Hz (voice characteristics)
    mel_frequency_coefficients: List[float]  # MFCC for timbre
    duration: float                   # total duration (seconds)


@dataclass
class VoiceAnalysis:
    """Complete voice analysis result."""
    timestamp: float
    raw_features: AcousticFeatures
    detected_tone: VoiceAffectTone
    tone_confidence: float             # 0.0-1.0
    emotional_state: Dict[str, float]  # emotion -> intensity
    arousal: float                      # 0.0-1.0 (low->high energy)
    valence: float                      # 0.0-1.0 (negative->positive)
    dominance: float                    # 0.0-1.0 (submissive->dominant)
    stress_indicator: float             # 0.0-1.0 (low->high stress)


class VoiceAffectDetector:
    """Detects emotional affect from voice acoustic features.

    Based on:
    - Pitch patterns (fundamental frequency + variance)
    - Intensity dynamics (loudness + energy variance)
    - Temporal features (speech rate, pauses)
    - Voice quality (formants, MFCCs, timbre)

    Maps to VAD (Valence-Arousal-Dominance) model for continuous emotion space.
    """

    def __init__(self):
        """Initialize voice affect detector."""
        # Baseline thresholds for acoustic features
        self.pitch_low_threshold = 80      # Hz
        self.pitch_high_threshold = 250    # Hz
        self.intensity_low_threshold = 50  # dB
        self.intensity_high_threshold = 80  # dB
        self.rate_slow_threshold = 120     # wpm
        self.rate_fast_threshold = 180     # wpm
        self.pause_freq_threshold = 5      # pauses per minute

    def analyze(self, features: AcousticFeatures) -> VoiceAnalysis:
        """Analyze acoustic features to detect emotional tone.

        Args:
            features: Extracted acoustic features from audio

        Returns:
            VoiceAnalysis with detected tone and emotional dimensions
        """
        # Calculate VAD dimensions (continuous emotional space)
        arousal = self._calculate_arousal(features)
        valence = self._calculate_valence(features)
        dominance = self._calculate_dominance(features)

        # Detect primary tone
        tone, confidence = self._detect_primary_tone(
            features, arousal, valence, dominance)

        # Calculate emotional intensity for each tone
        emotional_state = self._estimate_emotional_state(
            features, arousal, valence, dominance)

        # Calculate stress indicator
        stress = self._calculate_stress(features)

        analysis = VoiceAnalysis(
            timestamp=features.duration,  # Use duration as proxy for timestamp
            raw_features=features,
            detected_tone=tone,
            tone_confidence=confidence,
            emotional_state=emotional_state,
            arousal=arousal,
            valence=valence,
            dominance=dominance,
            stress_indicator=stress,
        )

        return analysis

    def _calculate_arousal(self, features: AcousticFeatures) -> float:
        """Calculate arousal dimension (low energy -> high energy).

        High arousal: fast speech, high pitch, high intensity, high pitch variance
        Low arousal: slow speech, low pitch, low intensity, low pitch variance
        """
        components = []

        # Speech rate component (0-1)
        if features.speech_rate < self.rate_slow_threshold:
            rate_score = 0.2
        elif features.speech_rate > self.rate_fast_threshold:
            rate_score = 0.8
        else:
            rate_score = 0.5
        components.append(rate_score)

        # Pitch component (0-1)
        if features.fundamental_frequency < self.pitch_low_threshold:
            pitch_score = 0.2
        elif features.fundamental_frequency > self.pitch_high_threshold:
            pitch_score = 0.8
        else:
            pitch_score = 0.5
        components.append(pitch_score)

        # Intensity component (0-1)
        if features.intensity < self.intensity_low_threshold:
            intensity_score = 0.2
        elif features.intensity > self.intensity_high_threshold:
            intensity_score = 0.8
        else:
            intensity_score = 0.5
        components.append(intensity_score)

        # Pitch variance component (more variance = higher arousal)
        variance_score = min(1.0, features.pitch_variance / 50)
        components.append(variance_score)

        return sum(components) / len(components)

    def _calculate_valence(self, features: AcousticFeatures) -> float:
        """Calculate valence dimension (negative -> positive).

        Positive valence: higher pitch, higher intensity, faster rate, fewer pauses
        Negative valence: lower pitch, lower intensity, slower rate, more pauses
        """
        components = []

        # Pitch component (higher pitch = more positive)
        pitch_score = (features.fundamental_frequency - self.pitch_low_threshold) / (
            self.pitch_high_threshold - self.pitch_low_threshold
        )
        pitch_score = max(0.0, min(1.0, pitch_score))
        components.append(pitch_score)

        # Intensity component (higher intensity = more positive)
        intensity_score = (features.intensity - self.intensity_low_threshold) / (
            self.intensity_high_threshold - self.intensity_low_threshold
        )
        intensity_score = max(0.0, min(1.0, intensity_score))
        components.append(intensity_score)

        # Pause frequency component (fewer pauses = more positive)
        max_pauses_per_min = self.pause_freq_threshold * 2
        pause_score = 1.0 - \
            min(1.0, (features.pause_frequency /
                features.duration * 60) / max_pauses_per_min)
        components.append(pause_score)

        # Pitch variance (lower variance = more positive/stable)
        variance_score = 1.0 - min(1.0, features.pitch_variance / 50)
        components.append(variance_score)

        return sum(components) / len(components)

    def _calculate_dominance(self, features: AcousticFeatures) -> float:
        """Calculate dominance dimension (submissive -> dominant).

        High dominance: low pitch, high intensity, fast rate, minimal hesitation
        Low dominance: high pitch, low intensity, slow rate, frequent hesitation
        """
        components = []

        # Pitch component (lower pitch = more dominant)
        pitch_score = 1.0 - (features.fundamental_frequency - self.pitch_low_threshold) / (
            self.pitch_high_threshold - self.pitch_low_threshold
        )
        pitch_score = max(0.0, min(1.0, pitch_score))
        components.append(pitch_score)

        # Intensity component (higher intensity = more dominant)
        intensity_score = (features.intensity - self.intensity_low_threshold) / (
            self.intensity_high_threshold - self.intensity_low_threshold
        )
        intensity_score = max(0.0, min(1.0, intensity_score))
        components.append(intensity_score)

        # Speech rate component (faster = more dominant)
        if features.speech_rate < self.rate_slow_threshold:
            rate_score = 0.2
        elif features.speech_rate > self.rate_fast_threshold:
            rate_score = 0.8
        else:
            rate_score = 0.5
        components.append(rate_score)

        # Hesitation component (fewer pauses = more dominant)
        max_pauses_per_min = self.pause_freq_threshold * 2
        pause_score = 1.0 - \
            min(1.0, (features.pause_frequency /
                features.duration * 60) / max_pauses_per_min)
        components.append(pause_score)

        return sum(components) / len(components)

    def _detect_primary_tone(
        self,
        features: AcousticFeatures,
        arousal: float,
        valence: float,
        dominance: float,
    ) -> Tuple[VoiceAffectTone, float]:
        """Detect primary emotional tone from VAD dimensions.

        Args:
            features: Acoustic features
            arousal: Arousal score (0-1)
            valence: Valence score (0-1)
            dominance: Dominance score (0-1)

        Returns:
            Tuple of (detected_tone, confidence)
        """
        # High arousal + high valence + high dominance → Excited
        if arousal > 0.7 and valence > 0.6 and dominance > 0.6:
            return VoiceAffectTone.EXCITED, 0.9

        # High arousal + low valence + low dominance → Anxious
        if arousal > 0.7 and valence < 0.4 and dominance < 0.4:
            return VoiceAffectTone.ANXIOUS, 0.85

        # High arousal + low valence + high dominance → Angry
        if arousal > 0.7 and valence < 0.4 and dominance > 0.6:
            return VoiceAffectTone.ANGRY, 0.85

        # Low arousal + low valence → Sad
        if arousal < 0.3 and valence < 0.4:
            return VoiceAffectTone.SAD, 0.85

        # Low arousal + high valence → Calm
        if arousal < 0.3 and valence > 0.6:
            return VoiceAffectTone.CALM, 0.85

        # Variable pitch + pauses → Hesitant
        if features.pitch_variance > 30 and features.pause_frequency > 5:
            return VoiceAffectTone.HESITANT, 0.8

        # High intensity + fast rate → Energetic (default high arousal)
        if arousal > 0.6:
            return VoiceAffectTone.ENERGETIC, 0.75

        # Steady features → Confident (default low arousal positive)
        if valence > 0.5 and dominance > 0.5:
            return VoiceAffectTone.CONFIDENT, 0.75

        # Default: Calm
        return VoiceAffectTone.CALM, 0.5

    def _estimate_emotional_state(
        self,
        features: AcousticFeatures,
        arousal: float,
        valence: float,
        dominance: float,
    ) -> Dict[str, float]:
        """Estimate intensity of each emotional tone based on VAD.

        Args:
            features: Acoustic features
            arousal: Arousal score
            valence: Valence score
            dominance: Dominance score

        Returns:
            Dictionary mapping tone names to intensities (0-1)
        """
        emotions = {}

        # Excited: high arousal, high valence
        emotions[VoiceAffectTone.EXCITED.value] = (
            arousal + valence) / 2 if arousal > 0.6 else 0.0

        # Energetic: high arousal
        emotions[VoiceAffectTone.ENERGETIC.value] = arousal if arousal > 0.6 else 0.0

        # Anxious: high arousal, low valence, low dominance
        emotions[VoiceAffectTone.ANXIOUS.value] = (
            arousal * (1 - valence) * (1 - dominance)
        ) if arousal > 0.5 else 0.0

        # Angry: high arousal, low valence, high dominance
        emotions[VoiceAffectTone.ANGRY.value] = (
            arousal * (1 - valence) * dominance
        ) if arousal > 0.5 else 0.0

        # Sad: low arousal, low valence
        emotions[VoiceAffectTone.SAD.value] = (
            (1 - arousal) * (1 - valence)
        ) if arousal < 0.5 else 0.0

        # Calm: low arousal, high valence
        emotions[VoiceAffectTone.CALM.value] = (
            (1 - arousal) * valence
        ) if arousal < 0.5 else 0.0

        # Hesitant: variable pitch, pauses
        hesitancy = features.pitch_variance / \
            50 * (features.pause_frequency / 10)
        emotions[VoiceAffectTone.HESITANT.value] = min(1.0, hesitancy)

        # Confident: steady pitch, minimal pauses, high dominance
        confidence = (1 - features.pitch_variance / 50) * \
            (1 - features.pause_frequency / 10) * dominance
        emotions[VoiceAffectTone.CONFIDENT.value] = min(
            1.0, max(0.0, confidence))

        # Normalize so max is 1.0 (don't sum to 1.0, keep individual scores)
        max_emotion = max(emotions.values()) if emotions else 1.0
        if max_emotion > 1.0:
            emotions = {k: v / max_emotion for k, v in emotions.items()}

        return emotions

    def _calculate_stress(self, features: AcousticFeatures) -> float:
        """Calculate stress indicator from acoustic features.

        High stress indicators:
        - High pitch variance
        - Frequent pauses
        - High intensity variance
        - Fast speech with pauses (hesitation)
        - High overall arousal with low valence
        """
        components = []

        # Pitch variance component (high variance = stress)
        pitch_stress = min(1.0, features.pitch_variance / 50)
        components.append(pitch_stress)

        # Pause frequency component (many pauses = stress)
        max_pauses_per_min = self.pause_freq_threshold * 2
        pause_stress = min(1.0, (features.pause_frequency /
                           features.duration * 60) / max_pauses_per_min)
        components.append(pause_stress)

        # Intensity variance component (high variance = stress)
        intensity_stress = min(1.0, features.energy_variance / 10)
        components.append(intensity_stress)

        return sum(components) / len(components)

    def compare_with_text_emotion(
        self,
        text_tone: str,
        voice_analysis: VoiceAnalysis,
    ) -> Dict[str, any]:
        """Compare voice emotion with text emotion to detect inconsistencies.

        Useful for detecting:
        - Sarcasm (text positive, voice negative)
        - Suppressed emotion (voice anxious, text calm)
        - Deception (mismatch between expressed and vocal emotion)

        Args:
            text_tone: Emotional tone from text analysis
            voice_analysis: Emotional analysis from voice

        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "text_tone": text_tone,
            "voice_tone": voice_analysis.detected_tone.value,
            "match": text_tone.lower() == voice_analysis.detected_tone.value,
            "confidence_delta": voice_analysis.tone_confidence,
            "arousal": voice_analysis.arousal,
            "valence": voice_analysis.valence,
            "dominance": voice_analysis.dominance,
            "stress_level": voice_analysis.stress_indicator,
            "potential_sarcasm": False,
            "potential_suppression": False,
            "notes": [],
        }

        # Detect sarcasm (text positive, voice negative)
        if text_tone.lower() in ["excited", "happy", "joyful"] and voice_analysis.valence < 0.3:
            comparison["potential_sarcasm"] = True
            comparison["notes"].append(
                "Possible sarcasm detected (positive text, negative voice)")

        # Detect emotional suppression (voice stressed, text calm)
        if text_tone.lower() in ["calm", "grounded"] and voice_analysis.stress_indicator > 0.6:
            comparison["potential_suppression"] = True
            comparison["notes"].append(
                "Possible emotion suppression (calm text, stressed voice)")

        # Detect incongruence
        if not comparison["match"] and voice_analysis.tone_confidence > 0.7:
            comparison["notes"].append(
                f"Incongruence: text={text_tone}, voice={voice_analysis.detected_tone.value}")

        return comparison
