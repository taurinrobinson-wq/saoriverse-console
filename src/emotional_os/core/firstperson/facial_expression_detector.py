"""Facial Expression Analysis for Phase 3.2.

Detects emotional expression from facial features using:
- Action Units (Ekman's FACS - Facial Action Coding System)
- Face landmarks (68-point face mesh)
- Eye region analysis (gaze, pupil dilation, blink rate)
- Mouth region analysis (smile intensity, lip tension)

Maps facial expressions to 7 basic emotions + neutral.
Integrates with voice and text analysis for multimodal fusion.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class FacialExpression(Enum):
    """Seven basic emotions from Ekman research + neutral."""
    HAPPY = "happy"        # Smile, crow's feet, raised cheeks
    ANGRY = "angry"        # Lowered brows, tensed lips, flared nostrils
    SAD = "sad"            # Lowered mouth corners, raised inner brows
    FEARFUL = "fearful"    # Raised upper lids, lower lid tension, open mouth
    SURPRISED = "surprised"  # Raised brows, dropped jaw, wide eyes
    DISGUSTED = "disgusted"  # Wrinkled nose, raised upper lip, raised chin
    CONTEMPTUOUS = "contemptuous"  # One-sided smile, raised cheek
    NEUTRAL = "neutral"    # Minimal muscle activation


class ActionUnit(Enum):
    """Facial Action Units from Facial Action Coding System (FACS)."""
    # Brow lowerer
    AU4 = "AU4_brow_lowerer"
    # Inner brow raiser
    AU1 = "AU1_inner_brow_raiser"
    # Outer brow raiser
    AU2 = "AU2_outer_brow_raiser"
    # Upper lid raiser
    AU5 = "AU5_upper_lid_raiser"
    # Cheek raiser / Crow's feet
    AU6 = "AU6_cheek_raiser"
    # Lid tightener
    AU7 = "AU7_lid_tightener"
    # Lips toward teeth
    AU23 = "AU23_lips_toward_teeth"
    # Lip corner depressor
    AU15 = "AU15_lip_corner_depressor"
    # Dimpler
    AU14 = "AU14_dimpler"
    # Lip corner puller (smile)
    AU12 = "AU12_lip_corner_puller"
    # Nose wrinkler
    AU9 = "AU9_nose_wrinkler"
    # Upper lip raiser
    AU10 = "AU10_upper_lip_raiser"
    # Jaw drop
    AU26 = "AU26_jaw_drop"


@dataclass
class FaceLandmarks:
    """68-point face landmark positions (normalized 0-1)."""
    # Face outline (0-16): chin to ears
    contour: List[Tuple[float, float]]

    # Right eyebrow (17-21)
    right_eyebrow: List[Tuple[float, float]]

    # Left eyebrow (22-26)
    left_eyebrow: List[Tuple[float, float]]

    # Nose (27-35)
    nose: List[Tuple[float, float]]

    # Right eye (36-41)
    right_eye: List[Tuple[float, float]]

    # Left eye (42-47)
    left_eye: List[Tuple[float, float]]

    # Mouth (48-67)
    mouth: List[Tuple[float, float]]


@dataclass
class EyeMetrics:
    """Eye region measurements."""
    left_eye_openness: float         # 0-1 (closed to wide open)
    right_eye_openness: float        # 0-1
    left_pupil_dilation: float       # 0-1 (normal to dilated)
    right_pupil_dilation: float      # 0-1
    left_blink_rate: float           # blinks per second
    right_blink_rate: float          # blinks per second
    # normalized (x, y) where (0.5, 0.5) = center
    gaze_direction: Tuple[float, float]
    fixation_duration: float         # seconds (how long looking at one point)


@dataclass
class MouthMetrics:
    """Mouth region measurements."""
    smile_intensity: float           # 0-1 (not smiling to full smile)
    mouth_openness: float            # 0-1 (closed to wide open)
    lip_tension: float               # 0-1 (relaxed to very tense)
    mouth_asymmetry: float           # 0-1 (symmetric to highly asymmetric)
    # pixels (height difference between corners)
    lip_corner_height_diff: float


@dataclass
class ActionUnitIntensities:
    """Intensity (0-1) of each facial action unit."""
    intensities: Dict[str, float]


@dataclass
class FacialAnalysis:
    """Complete facial expression analysis."""
    timestamp: float
    landmarks: FaceLandmarks
    expression: FacialExpression
    expression_confidence: float     # 0-1
    action_units: ActionUnitIntensities
    eye_metrics: EyeMetrics
    mouth_metrics: MouthMetrics

    # Emotional dimensions
    arousal: float                   # 0-1 (calm to excited)
    valence: float                   # 0-1 (negative to positive)
    dominance: float                 # 0-1 (submissive to dominant)

    # Engagement metrics
    attention: float                 # 0-1 (not attending to fully engaged)
    authenticity: float              # 0-1 (forced/fake to genuine)


class FacialExpressionDetector:
    """Detects emotional expression from facial landmarks and action units.

    Based on Ekman's 7 basic emotions and Facial Action Coding System (FACS).
    Analyzes:
    1. Eyebrow position and shape
    2. Eye openness and gaze
    3. Mouth shape and smile
    4. Overall face tension and wrinkles
    """

    def __init__(self):
        """Initialize facial expression detector."""
        self.action_unit_thresholds = {
            ActionUnit.AU1.value: 0.3,  # Inner brow raise threshold
            ActionUnit.AU2.value: 0.3,  # Outer brow raise threshold
            ActionUnit.AU4.value: 0.3,  # Brow lower threshold
            ActionUnit.AU5.value: 0.3,  # Upper lid raise threshold
            ActionUnit.AU6.value: 0.3,  # Cheek raise threshold
            ActionUnit.AU7.value: 0.3,  # Lid tighten threshold
            ActionUnit.AU12.value: 0.3,  # Smile threshold
            ActionUnit.AU15.value: 0.3,  # Lip corner depress threshold
            ActionUnit.AU26.value: 0.3,  # Jaw drop threshold
        }

    def analyze(self, landmarks: FaceLandmarks) -> FacialAnalysis:
        """Analyze facial landmarks to detect expression and emotion.

        Args:
            landmarks: 68-point face landmark positions

        Returns:
            FacialAnalysis with detected expression and metrics
        """
        # Extract action unit intensities
        action_units = self._detect_action_units(landmarks)

        # Extract eye metrics
        eye_metrics = self._analyze_eyes(landmarks)

        # Extract mouth metrics
        mouth_metrics = self._analyze_mouth(landmarks)

        # Detect primary expression
        expression, confidence = self._detect_expression(
            action_units, eye_metrics, mouth_metrics
        )

        # Calculate emotional dimensions
        arousal, valence, dominance = self._calculate_dimensions(
            action_units, eye_metrics, mouth_metrics
        )

        # Calculate engagement and authenticity
        attention = self._calculate_attention(eye_metrics)
        authenticity = self._calculate_authenticity(
            action_units, eye_metrics, mouth_metrics)

        analysis = FacialAnalysis(
            timestamp=0.0,  # Placeholder
            landmarks=landmarks,
            expression=expression,
            expression_confidence=confidence,
            action_units=action_units,
            eye_metrics=eye_metrics,
            mouth_metrics=mouth_metrics,
            arousal=arousal,
            valence=valence,
            dominance=dominance,
            attention=attention,
            authenticity=authenticity,
        )

        return analysis

    def _detect_action_units(self, landmarks: FaceLandmarks) -> ActionUnitIntensities:
        """Detect intensity of each facial action unit.

        Args:
            landmarks: Face landmarks

        Returns:
            ActionUnitIntensities with each AU intensity
        """
        intensities = {}

        # AU1: Inner Brow Raiser (sadness, surprise, fear)
        intensities[ActionUnit.AU1.value] = self._measure_inner_brow_raise(
            landmarks)

        # AU2: Outer Brow Raiser (surprise, fear)
        intensities[ActionUnit.AU2.value] = self._measure_outer_brow_raise(
            landmarks)

        # AU4: Brow Lowerer (anger, sadness, concentration)
        intensities[ActionUnit.AU4.value] = self._measure_brow_lower(landmarks)

        # AU5: Upper Lid Raiser (surprise, fear)
        intensities[ActionUnit.AU5.value] = self._measure_upper_lid_raise(
            landmarks)

        # AU6: Cheek Raiser / Crow's Feet (happiness, genuine smile)
        intensities[ActionUnit.AU6.value] = self._measure_cheek_raise(
            landmarks)

        # AU7: Lid Tightener (anger, disgust, concentration)
        intensities[ActionUnit.AU7.value] = self._measure_lid_tighten(
            landmarks)

        # AU9: Nose Wrinkler (disgust, contempt)
        intensities[ActionUnit.AU9.value] = self._measure_nose_wrinkle(
            landmarks)

        # AU10: Upper Lip Raiser (disgust, sadness)
        intensities[ActionUnit.AU10.value] = self._measure_upper_lip_raise(
            landmarks)

        # AU12: Lip Corner Puller (smile/happiness)
        intensities[ActionUnit.AU12.value] = self._measure_lip_corner_puller(
            landmarks)

        # AU15: Lip Corner Depressor (sadness)
        intensities[ActionUnit.AU15.value] = self._measure_lip_corner_depressor(
            landmarks)

        # AU26: Jaw Drop (surprise, fear, sadness)
        intensities[ActionUnit.AU26.value] = self._measure_jaw_drop(landmarks)

        return ActionUnitIntensities(intensities=intensities)

    def _measure_inner_brow_raise(self, landmarks: FaceLandmarks) -> float:
        """Measure AU1: Inner brow position (vertical distance)."""
        if len(landmarks.left_eyebrow) < 1 or len(landmarks.right_eyebrow) < 1:
            return 0.0
        # Inner eyebrows are points 0 and 4 of each eyebrow
        left_inner_y = landmarks.left_eyebrow[0][1]
        right_inner_y = landmarks.right_eyebrow[4][1]
        # Lower y = raised brow (normalize to 0-1)
        return max(0.0, min(1.0, 1.0 - ((left_inner_y + right_inner_y) / 2)))

    def _measure_outer_brow_raise(self, landmarks: FaceLandmarks) -> float:
        """Measure AU2: Outer brow position (vertical distance)."""
        if len(landmarks.left_eyebrow) < 1 or len(landmarks.right_eyebrow) < 1:
            return 0.0
        # Outer eyebrows are points 4 and 0 of each eyebrow
        left_outer_y = landmarks.left_eyebrow[4][1]
        right_outer_y = landmarks.right_eyebrow[0][1]
        # Lower y = raised brow
        return max(0.0, min(1.0, 1.0 - ((left_outer_y + right_outer_y) / 2)))

    def _measure_brow_lower(self, landmarks: FaceLandmarks) -> float:
        """Measure AU4: Brow position (lowering indicates anger/concentration)."""
        if len(landmarks.left_eyebrow) < 1 or len(landmarks.right_eyebrow) < 1:
            return 0.0
        # Higher y = lowered brow
        left_center_y = landmarks.left_eyebrow[2][1]
        right_center_y = landmarks.right_eyebrow[2][1]
        return max(0.0, min(1.0, (left_center_y + right_center_y) / 2))

    def _measure_upper_lid_raise(self, landmarks: FaceLandmarks) -> float:
        """Measure AU5: Upper eyelid opening."""
        if len(landmarks.left_eye) < 2 or len(landmarks.right_eye) < 2:
            return 0.0
        # Upper lids are points 1 and 2 of eye landmark
        left_lid_y = landmarks.left_eye[1][1]
        right_lid_y = landmarks.right_eye[1][1]
        # Lower y = more open
        return max(0.0, min(1.0, 1.0 - ((left_lid_y + right_lid_y) / 2)))

    def _measure_cheek_raise(self, landmarks: FaceLandmarks) -> float:
        """Measure AU6: Cheek position (raising indicates smile/happiness)."""
        if len(landmarks.left_eye) < 1 or len(landmarks.right_eye) < 1:
            return 0.0
        # Cheeks are at side of eyes (points 0 and 3)
        left_cheek_y = landmarks.left_eye[3][1]
        right_cheek_y = landmarks.right_eye[0][1]
        # Lower y = raised cheek
        return max(0.0, min(1.0, 1.0 - ((left_cheek_y + right_cheek_y) / 2)))

    def _measure_lid_tighten(self, landmarks: FaceLandmarks) -> float:
        """Measure AU7: Eye lid tension (narrowing of eyes)."""
        if len(landmarks.left_eye) < 2 or len(landmarks.right_eye) < 2:
            return 0.0
        # Narrowing is when upper and lower lids get closer
        left_upper_y = landmarks.left_eye[1][1]
        left_lower_y = landmarks.left_eye[4][1]
        right_upper_y = landmarks.right_eye[1][1]
        right_lower_y = landmarks.right_eye[4][1]

        left_gap = left_lower_y - left_upper_y
        right_gap = right_lower_y - right_upper_y
        avg_gap = (left_gap + right_gap) / 2

        # Narrower gap = higher intensity (inverted)
        return max(0.0, min(1.0, 1.0 - (avg_gap * 2)))

    def _measure_nose_wrinkle(self, landmarks: FaceLandmarks) -> float:
        """Measure AU9: Nose wrinkles (indicates disgust)."""
        if len(landmarks.nose) < 5:
            return 0.0
        # Nose wrinkles are indicated by nose bridge narrowing
        # This is a simplified measure based on nose width
        nose_width = abs(landmarks.nose[0][0] - landmarks.nose[4][0])
        # Narrower nose = more wrinkles
        return max(0.0, min(1.0, 1.0 - (nose_width * 2)))

    def _measure_upper_lip_raise(self, landmarks: FaceLandmarks) -> float:
        """Measure AU10: Upper lip raising (indicates disgust/sadness)."""
        if len(landmarks.mouth) < 7:
            return 0.0
        # Upper lip is around point 2
        upper_lip_y = landmarks.mouth[2][1]
        # Lower y = more raised
        return max(0.0, min(1.0, 1.0 - (upper_lip_y * 2)))

    def _measure_lip_corner_puller(self, landmarks: FaceLandmarks) -> float:
        """Measure AU12: Lip corners pulled up (smile/happiness)."""
        if len(landmarks.mouth) < 10:
            return 0.0
        # Lip corners are points 0 and 6 of mouth
        left_corner_y = landmarks.mouth[0][1]
        right_corner_y = landmarks.mouth[6][1]
        # Lower y = pulled up (smile)
        return max(0.0, min(1.0, 1.0 - ((left_corner_y + right_corner_y) / 2)))

    def _measure_lip_corner_depressor(self, landmarks: FaceLandmarks) -> float:
        """Measure AU15: Lip corners pulled down (sadness)."""
        if len(landmarks.mouth) < 10:
            return 0.0
        # Lip corners are points 0 and 6 of mouth
        left_corner_y = landmarks.mouth[0][1]
        right_corner_y = landmarks.mouth[6][1]
        # Higher y = pulled down (sadness)
        return max(0.0, min(1.0, (left_corner_y + right_corner_y) / 2))

    def _measure_jaw_drop(self, landmarks: FaceLandmarks) -> float:
        """Measure AU26: Jaw drop (indicates surprise, fear, or sadness)."""
        if len(landmarks.mouth) < 10:
            return 0.0
        # Jaw drop is indicated by mouth openness
        # Mouth corners (0, 6) stay relatively fixed while chin moves
        mouth_height = max(landmarks.mouth[9][1] - landmarks.mouth[3][1], 0)
        # Larger mouth opening = higher AU26
        return max(0.0, min(1.0, mouth_height * 3))

    def _analyze_eyes(self, landmarks: FaceLandmarks) -> EyeMetrics:
        """Analyze eye region metrics."""
        # Simplified eye metrics - would use pupil tracking in full implementation
        return EyeMetrics(
            left_eye_openness=self._measure_upper_lid_raise(landmarks),
            right_eye_openness=self._measure_upper_lid_raise(landmarks),
            left_pupil_dilation=0.5,  # Placeholder
            right_pupil_dilation=0.5,  # Placeholder
            left_blink_rate=0.0,  # Would need temporal data
            right_blink_rate=0.0,  # Would need temporal data
            gaze_direction=(0.5, 0.5),  # Placeholder (centered)
            fixation_duration=0.0,  # Would need temporal data
        )

    def _analyze_mouth(self, landmarks: FaceLandmarks) -> MouthMetrics:
        """Analyze mouth region metrics."""
        smile_intensity = self._measure_lip_corner_puller(landmarks)
        mouth_openness = self._measure_jaw_drop(landmarks)

        if len(landmarks.mouth) >= 10:
            left_corner_y = landmarks.mouth[0][1]
            right_corner_y = landmarks.mouth[6][1]
            asymmetry = abs(left_corner_y - right_corner_y)
        else:
            asymmetry = 0.0

        return MouthMetrics(
            smile_intensity=smile_intensity,
            mouth_openness=mouth_openness,
            lip_tension=0.5,  # Placeholder
            mouth_asymmetry=max(0.0, min(1.0, asymmetry * 2)),
            lip_corner_height_diff=abs(left_corner_y - right_corner_y) * 100,
        )

    def _detect_expression(
        self,
        action_units: ActionUnitIntensities,
        eye_metrics: EyeMetrics,
        mouth_metrics: MouthMetrics,
    ) -> Tuple[FacialExpression, float]:
        """Detect primary facial expression from action units.

        Args:
            action_units: Detected action unit intensities
            eye_metrics: Eye region metrics
            mouth_metrics: Mouth region metrics

        Returns:
            Tuple of (expression, confidence)
        """
        au = action_units.intensities

        # Happy: AU12 (smile) + AU6 (cheek raise) = genuine Duchenne smile
        if au[ActionUnit.AU12.value] > 0.5 and au[ActionUnit.AU6.value] > 0.4:
            return FacialExpression.HAPPY, 0.9

        # Angry: AU4 (brow lower) + AU7 (lid tighten) + AU23 (lip tension)
        if au[ActionUnit.AU4.value] > 0.5 and au[ActionUnit.AU7.value] > 0.4:
            return FacialExpression.ANGRY, 0.85

        # Sad: AU1 (inner brow raise) + AU15 (lip corner depress) + AU26 (jaw drop)
        if au[ActionUnit.AU1.value] > 0.4 and au[ActionUnit.AU15.value] > 0.5:
            return FacialExpression.SAD, 0.85

        # Fearful: AU1 (inner brow raise) + AU2 (outer brow raise) + AU5 (upper lid raise) + AU26 (jaw drop)
        if au[ActionUnit.AU1.value] > 0.4 and au[ActionUnit.AU5.value] > 0.5 and au[ActionUnit.AU26.value] > 0.4:
            return FacialExpression.FEARFUL, 0.85

        # Surprised: AU1 (inner brow raise) + AU2 (outer brow raise) + AU5 (upper lid raise) + AU26 (jaw drop)
        if (au[ActionUnit.AU1.value] > 0.3 and au[ActionUnit.AU2.value] > 0.3 and
                au[ActionUnit.AU5.value] > 0.4 and au[ActionUnit.AU26.value] > 0.4):
            return FacialExpression.SURPRISED, 0.85

        # Disgusted: AU9 (nose wrinkle) + AU10 (upper lip raise) + AU15 (lip corner depress)
        if au[ActionUnit.AU9.value] > 0.4 and au[ActionUnit.AU10.value] > 0.4:
            return FacialExpression.DISGUSTED, 0.8

        # Contemptuous: AU12 (one-sided smile) + asymmetry
        if au[ActionUnit.AU12.value] > 0.3 and mouth_metrics.mouth_asymmetry > 0.4:
            return FacialExpression.CONTEMPTUOUS, 0.75

        # Neutral: all AU intensities low
        if all(v < 0.2 for v in au.values()):
            return FacialExpression.NEUTRAL, 0.9

        # Default to neutral if no strong match
        return FacialExpression.NEUTRAL, 0.5

    def _calculate_dimensions(
        self,
        action_units: ActionUnitIntensities,
        eye_metrics: EyeMetrics,
        mouth_metrics: MouthMetrics,
    ) -> Tuple[float, float, float]:
        """Calculate arousal, valence, dominance dimensions.

        Returns:
            Tuple of (arousal, valence, dominance) each 0-1
        """
        au = action_units.intensities

        # Arousal: high with surprised, fearful, or angry expressions
        arousal = (
            au[ActionUnit.AU5.value] * 0.3 +  # Eye widening
            au[ActionUnit.AU26.value] * 0.3 +  # Jaw drop
            (1.0 - eye_metrics.left_eye_openness) * 0.2 +  # Eye tension
            (au[ActionUnit.AU4.value] + au[ActionUnit.AU7.value]) /
            2 * 0.2  # Brow/lid tension
        )
        arousal = max(0.0, min(1.0, arousal))

        # Valence: high with happy, low with sad/disgusted/angry
        valence = (
            mouth_metrics.smile_intensity * 0.4 +  # Smile
            (1.0 - au[ActionUnit.AU15.value]) * 0.2 +  # No lip corner depress
            (1.0 - au[ActionUnit.AU9.value]) * 0.2 +  # No nose wrinkle
            (1.0 - au[ActionUnit.AU4.value]) * 0.2  # No brow lower
        )
        valence = max(0.0, min(1.0, valence))

        # Dominance: high with wide eyes, low brow, high jaw prominence
        dominance = (
            au[ActionUnit.AU4.value] * 0.3 +  # Brow lower (dominance)
            # No inner brow raise (fear)
            (1.0 - au[ActionUnit.AU1.value]) * 0.2 +
            # No excessive eye widening
            (1.0 - au[ActionUnit.AU5.value]) * 0.2 +
            mouth_metrics.mouth_asymmetry * 0.3  # Asymmetric smile (contempt)
        )
        dominance = max(0.0, min(1.0, dominance))

        return arousal, valence, dominance

    def _calculate_attention(self, eye_metrics: EyeMetrics) -> float:
        """Calculate attention/engagement level (0-1)."""
        # Attention is high with open eyes and steady gaze
        attention = (
            eye_metrics.left_eye_openness * 0.4 +
            eye_metrics.right_eye_openness * 0.4 +
            (1.0 - (eye_metrics.left_blink_rate +
             eye_metrics.right_blink_rate) / 2) * 0.2
        )
        return max(0.0, min(1.0, attention))

    def _calculate_authenticity(
        self,
        action_units: ActionUnitIntensities,
        eye_metrics: EyeMetrics,
        mouth_metrics: MouthMetrics,
    ) -> float:
        """Calculate authenticity/genuineness of expression (0-1).

        Genuine expressions involve multiple consistent AUs (Duchenne smile = AU12+AU6).
        Fake expressions often have asymmetry or inconsistency.
        """
        au = action_units.intensities

        # Genuine happiness has both smile (AU12) and cheek raise (AU6)
        genuine_smile = (au[ActionUnit.AU12.value] >
                         0.4 and au[ActionUnit.AU6.value] > 0.3)

        # Consistency across face is a sign of authenticity
        consistency = 1.0 - mouth_metrics.mouth_asymmetry

        # Low asymmetry is more authentic
        authenticity = (
            (1.0 if genuine_smile else 0.5) * 0.5 +
            consistency * 0.3 +
            (1.0 - (1.0 if mouth_metrics.lip_tension > 0.7 else 0.0)) * 0.2
        )

        return max(0.0, min(1.0, authenticity))
