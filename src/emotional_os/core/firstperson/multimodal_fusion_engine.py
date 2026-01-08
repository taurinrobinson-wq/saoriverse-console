"""Multimodal Affect Fusion for Phase 3.2.

Combines:
- Text emotional tone (from Phase 1-2)
- Voice acoustic features (VoiceAffectDetector)
- Facial expressions (FacialExpressionDetector)

Into unified emotional understanding with:
- Confidence scores for each modality
- Modality agreement/disagreement detection
- Incongruence indicators (sarcasm, suppression, deception)
- Dominant/primary emotion across modalities
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .voice_affect_detector import VoiceAnalysis, VoiceAffectTone
from .facial_expression_detector import FacialAnalysis, FacialExpression


class CongruenceType(Enum):
    """Types of congruence between modalities."""
    FULL_AGREEMENT = "full_agreement"       # All modalities agree on emotion
    PARTIAL_AGREEMENT = "partial_agreement"  # 2/3 modalities agree
    MODALITY_CONFLICT = "conflict"           # Each modality shows different emotion
    TEXT_POSITIVE_VOICE_NEGATIVE = "sarcasm"  # Likely sarcasm
    SUPPRESSION = "suppression"              # Voice/face show stress, text is calm
    CONSISTENT_FAKE = "consistent_fake"      # All modalities show low authenticity


@dataclass
class ModularityConfidence:
    """Confidence scores for each modality."""
    text_confidence: float         # 0-1 (from text analyzer)
    voice_confidence: float        # 0-1 (from voice analyzer)
    facial_confidence: float       # 0-1 (from facial analyzer)
    overall_confidence: float      # 0-1 (weighted average)


@dataclass
class EmotionalDimensions:
    """Continuous emotional dimensions across modalities."""
    # VAD model (Valence-Arousal-Dominance)
    arousal: float                 # 0-1 (calm to excited)
    arousal_source: str            # which modality contributes most

    valence: float                 # 0-1 (negative to positive)
    valence_source: str

    dominance: float               # 0-1 (submissive to dominant)
    dominance_source: str

    # Stress and authenticity
    stress_level: float            # 0-1 (relaxed to high stress)
    authenticity: float            # 0-1 (fake/forced to genuine)


@dataclass
class MultimodalAnalysis:
    """Complete multimodal emotional analysis."""
    text_tone: str                 # Text emotion
    voice_analysis: VoiceAnalysis
    facial_analysis: FacialAnalysis

    # Unified emotion
    primary_emotion: str           # Name of primary emotion across modalities
    primary_confidence: float      # 0-1

    # Congruence analysis
    congruence_type: CongruenceType
    modality_agreement: float      # 0-1 (how well do modalities agree)

    # Continuous dimensions
    dimensions: EmotionalDimensions

    # Confidence in each modality
    confidence: ModularityConfidence

    # Detailed comparison
    modality_comparison: Dict[str, any]

    # Incongruence details
    incongruences: List[str] = field(default_factory=list)


class MultimodalFusionEngine:
    """Fuses multimodal emotional data into unified understanding.

    Approach:
    1. Extract emotion and confidence from each modality
    2. Compare for agreement/disagreement
    3. Detect incongruences (sarcasm, suppression, etc.)
    4. Calculate unified emotional dimensions
    5. Determine primary emotion and authenticity
    """

    def __init__(self):
        """Initialize multimodal fusion engine."""
        # Emotion mapping between modalities for comparison
        self.emotion_mapping = {
            # Text tones -> Voice tones
            "anxious": [VoiceAffectTone.ANXIOUS.value, VoiceAffectTone.HESITANT.value],
            "overwhelmed": [VoiceAffectTone.ANXIOUS.value, VoiceAffectTone.ENERGETIC.value],
            "reflective": [VoiceAffectTone.CALM.value, VoiceAffectTone.CONFIDENT.value],
            "protective": [VoiceAffectTone.CONFIDENT.value, VoiceAffectTone.ENERGETIC.value],
            "connecting": [VoiceAffectTone.ENERGETIC.value, VoiceAffectTone.CALM.value],
            "vulnerable": [VoiceAffectTone.HESITANT.value, VoiceAffectTone.SAD.value],
            "resilient": [VoiceAffectTone.CONFIDENT.value, VoiceAffectTone.ENERGETIC.value],
            "grounded": [VoiceAffectTone.CALM.value, VoiceAffectTone.CONFIDENT.value],

            # Text tones -> Facial expressions
            "happy": [FacialExpression.HAPPY.value, FacialExpression.SURPRISED.value],
            "sad": [FacialExpression.SAD.value, FacialExpression.FEARFUL.value],
            "angry": [FacialExpression.ANGRY.value, FacialExpression.CONTEMPTUOUS.value],
            "fearful": [FacialExpression.FEARFUL.value, FacialExpression.SURPRISED.value],
            "disgusted": [FacialExpression.DISGUSTED.value, FacialExpression.ANGRY.value],
        }

    def fuse(
        self,
        text_tone: str,
        voice_analysis: VoiceAnalysis,
        facial_analysis: FacialAnalysis,
    ) -> MultimodalAnalysis:
        """Fuse multimodal data into unified analysis.

        Args:
            text_tone: Detected text emotion tone
            voice_analysis: Voice acoustic analysis
            facial_analysis: Facial expression analysis

        Returns:
            MultimodalAnalysis with fused result
        """
        # Compare modalities
        congruence_type, agreement_score = self._assess_congruence(
            text_tone, voice_analysis, facial_analysis
        )

        # Detect specific incongruences
        incongruences = self._detect_incongruences(
            text_tone, voice_analysis, facial_analysis
        )

        # Calculate unified dimensions
        dimensions = self._fuse_dimensions(
            text_tone, voice_analysis, facial_analysis
        )

        # Calculate confidence scores
        confidence = self._calculate_confidence(
            voice_analysis, facial_analysis
        )

        # Determine primary emotion
        primary_emotion, primary_confidence = self._determine_primary_emotion(
            text_tone, voice_analysis, facial_analysis, agreement_score
        )

        # Build comparison details
        comparison = self._build_comparison(
            text_tone, voice_analysis, facial_analysis
        )

        analysis = MultimodalAnalysis(
            text_tone=text_tone,
            voice_analysis=voice_analysis,
            facial_analysis=facial_analysis,
            primary_emotion=primary_emotion,
            primary_confidence=primary_confidence,
            congruence_type=congruence_type,
            modality_agreement=agreement_score,
            dimensions=dimensions,
            confidence=confidence,
            modality_comparison=comparison,
            incongruences=incongruences,
        )

        return analysis

    def _assess_congruence(
        self,
        text_tone: str,
        voice_analysis: VoiceAnalysis,
        facial_analysis: FacialAnalysis,
    ) -> Tuple[CongruenceType, float]:
        """Assess congruence between modalities.

        Returns:
            Tuple of (CongruenceType, agreement_score 0-1)
        """
        # Check for text positive but voice negative (sarcasm)
        if text_tone.lower() in ["happy", "excited", "joyful"]:
            if voice_analysis.valence < 0.3 and facial_analysis.valence < 0.3:
                return CongruenceType.TEXT_POSITIVE_VOICE_NEGATIVE, 0.7

        # Check for emotional suppression
        if text_tone.lower() in ["calm", "grounded", "reflective"]:
            if voice_analysis.stress_indicator > 0.7 and facial_analysis.attention < 0.4:
                return CongruenceType.SUPPRESSION, 0.6

        # Check for consistent fake expression
        if (voice_analysis.tone_confidence < 0.5 and
            facial_analysis.authenticity < 0.4 and
                facial_analysis.expression_confidence > 0.7):
            return CongruenceType.CONSISTENT_FAKE, 0.65

        # Calculate raw agreement between text and voice
        text_matches_voice = self._emotion_matches(
            text_tone, voice_analysis.detected_tone.value
        )

        # Calculate raw agreement between voice and facial
        voice_matches_facial = self._emotion_matches(
            voice_analysis.detected_tone.value, facial_analysis.expression.value
        )

        # Count agreements
        agreements = sum([text_matches_voice, voice_matches_facial])

        if agreements == 2:
            return CongruenceType.FULL_AGREEMENT, 0.9
        elif agreements == 1:
            return CongruenceType.PARTIAL_AGREEMENT, 0.7
        else:
            return CongruenceType.MODALITY_CONFLICT, 0.4

    def _emotion_matches(self, emotion1: str, emotion2: str) -> bool:
        """Check if two emotions are similar/matching."""
        emotion1 = emotion1.lower()
        emotion2 = emotion2.lower()

        if emotion1 == emotion2:
            return True

        # Define emotion similarity groups
        similar_emotions = {
            "happy": ["excited", "joyful", "content", "euphoric"],
            "sad": ["depressed", "sorrowful", "grief", "unhappy"],
            "angry": ["frustrated", "irritated", "rage", "hostile"],
            "fearful": ["scared", "terrified", "anxious", "hesitant"],
            "calm": ["relaxed", "peaceful", "serene", "grounded"],
            "surprised": ["shocked", "startled", "amazed"],
        }

        for group in similar_emotions.values():
            if emotion1 in group and emotion2 in group:
                return True
            if emotion1 in group and emotion1 in group:
                return True

        return False

    def _detect_incongruences(
        self,
        text_tone: str,
        voice_analysis: VoiceAnalysis,
        facial_analysis: FacialAnalysis,
    ) -> List[str]:
        """Detect specific incongruences between modalities."""
        incongruences = []

        # Sarcasm detection
        if text_tone.lower() in ["happy", "excited"]:
            if voice_analysis.valence < 0.3:
                incongruences.append(
                    f"Possible sarcasm: text says {text_tone} but voice is {voice_analysis.detected_tone.value}"
                )

        # Emotional suppression
        if voice_analysis.stress_indicator > 0.7 and facial_analysis.attention < 0.3:
            incongruences.append(
                f"Possible suppression: high vocal stress but low facial engagement"
            )

        # Mismatch between voice and facial
        if (voice_analysis.tone_confidence > 0.7 and
            facial_analysis.expression_confidence > 0.7 and
                not self._emotion_matches(voice_analysis.detected_tone.value, facial_analysis.expression.value)):
            incongruences.append(
                f"Voice-facial mismatch: voice={voice_analysis.detected_tone.value}, face={facial_analysis.expression.value}"
            )

        # Authenticity concerns
        if facial_analysis.authenticity < 0.4 and voice_analysis.tone_confidence > 0.6:
            incongruences.append(
                "Facial expression appears forced or inauthentic")

        return incongruences

    def _fuse_dimensions(
        self,
        text_tone: str,
        voice_analysis: VoiceAnalysis,
        facial_analysis: FacialAnalysis,
    ) -> EmotionalDimensions:
        """Fuse continuous emotional dimensions from all modalities."""
        # Weight contributions by confidence
        voice_weight = voice_analysis.tone_confidence
        facial_weight = facial_analysis.expression_confidence
        total_weight = voice_weight + facial_weight

        if total_weight == 0:
            voice_weight = facial_weight = 0.5
        else:
            voice_weight = voice_weight / total_weight
            facial_weight = facial_weight / total_weight

        # Fuse arousal
        arousal = voice_weight * voice_analysis.arousal + \
            facial_weight * facial_analysis.arousal
        arousal_source = "voice" if voice_analysis.arousal > facial_analysis.arousal else "facial"

        # Fuse valence
        valence = voice_weight * voice_analysis.valence + \
            facial_weight * facial_analysis.valence
        valence_source = "voice" if voice_analysis.valence > facial_analysis.valence else "facial"

        # Fuse dominance
        dominance = voice_weight * voice_analysis.dominance + \
            facial_weight * facial_analysis.dominance
        dominance_source = "voice" if voice_analysis.dominance > facial_analysis.dominance else "facial"

        # Calculate stress and authenticity
        stress_level = (voice_analysis.stress_indicator +
                        (1.0 - facial_analysis.attention)) / 2
        authenticity = facial_analysis.authenticity

        return EmotionalDimensions(
            arousal=max(0.0, min(1.0, arousal)),
            arousal_source=arousal_source,
            valence=max(0.0, min(1.0, valence)),
            valence_source=valence_source,
            dominance=max(0.0, min(1.0, dominance)),
            dominance_source=dominance_source,
            stress_level=stress_level,
            authenticity=authenticity,
        )

    def _calculate_confidence(
        self,
        voice_analysis: VoiceAnalysis,
        facial_analysis: FacialAnalysis,
    ) -> ModularityConfidence:
        """Calculate confidence scores for each modality."""
        # Text confidence comes from prior analysis (assume 0.7 as baseline)
        text_confidence = 0.7

        overall_confidence = (
            text_confidence * 0.2 +
            voice_analysis.tone_confidence * 0.4 +
            facial_analysis.expression_confidence * 0.4
        )

        return ModularityConfidence(
            text_confidence=text_confidence,
            voice_confidence=voice_analysis.tone_confidence,
            facial_confidence=facial_analysis.expression_confidence,
            overall_confidence=max(0.0, min(1.0, overall_confidence)),
        )

    def _determine_primary_emotion(
        self,
        text_tone: str,
        voice_analysis: VoiceAnalysis,
        facial_analysis: FacialAnalysis,
        agreement_score: float,
    ) -> Tuple[str, float]:
        """Determine primary emotion across modalities.

        Returns:
            Tuple of (primary_emotion_name, confidence_0_1)
        """
        # If modalities agree, use that emotion
        if agreement_score > 0.8:
            # Voice and facial agree (more reliable than text alone)
            if (voice_analysis.tone_confidence > 0.6 and
                    facial_analysis.expression_confidence > 0.6):
                if self._emotion_matches(
                    voice_analysis.detected_tone.value,
                    facial_analysis.expression.value
                ):
                    emotion = voice_analysis.detected_tone.value
                    confidence = (voice_analysis.tone_confidence +
                                  facial_analysis.expression_confidence) / 2
                    return emotion, confidence

        # If voice is very confident, use voice
        if voice_analysis.tone_confidence > 0.75:
            return voice_analysis.detected_tone.value, voice_analysis.tone_confidence

        # If facial is very confident, use facial
        if facial_analysis.expression_confidence > 0.75:
            return facial_analysis.expression.value, facial_analysis.expression_confidence

        # Fall back to text with lower confidence
        return text_tone, 0.5

    def _build_comparison(
        self,
        text_tone: str,
        voice_analysis: VoiceAnalysis,
        facial_analysis: FacialAnalysis,
    ) -> Dict[str, any]:
        """Build detailed modality comparison."""
        return {
            "text": {
                "tone": text_tone,
                "confidence": 0.7,  # Baseline
            },
            "voice": {
                "tone": voice_analysis.detected_tone.value,
                "confidence": voice_analysis.tone_confidence,
                "arousal": voice_analysis.arousal,
                "valence": voice_analysis.valence,
                "dominance": voice_analysis.dominance,
                "stress": voice_analysis.stress_indicator,
            },
            "facial": {
                "expression": facial_analysis.expression.value,
                "confidence": facial_analysis.expression_confidence,
                "arousal": facial_analysis.arousal,
                "valence": facial_analysis.valence,
                "dominance": facial_analysis.dominance,
                "authenticity": facial_analysis.authenticity,
                "attention": facial_analysis.attention,
            },
        }
