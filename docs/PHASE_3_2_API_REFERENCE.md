# Phase 3.2 API Reference

## Table of Contents

1. [Voice Affect Detector](#voice-affect-detector) 2. [Facial Expression
Detector](#facial-expression-detector) 3. [Multimodal Fusion Engine](#multimodal-fusion-engine) 4.
[Data Classes](#data-classes) 5. [Enums](#enums)

##

## Voice Affect Detector

**Module**: `emotional_os/core/firstperson/voice_affect_detector.py`

### Class: `VoiceAffectDetector`

Main class for analyzing vocal emotion from acoustic features.

#### Methods

##### `__init__()`

```python
```text
```text
```

Initializes the voice affect detector with no parameters.

##### `analyze(features: AcousticFeatures) -> VoiceAnalysis`

Analyzes acoustic features to determine vocal emotion.

**Parameters**:

- `features` (`AcousticFeatures`): Extracted acoustic properties of speech

**Returns**: `VoiceAnalysis` object containing detected tone, dimensions, and confidence

**Example**:

```python

features = AcousticFeatures(
    fundamental_frequency=150,
    intensity=75,
    speech_rate=120,
    pause_frequency=0.1,
    pause_duration_avg=100,
    pitch_variance=20,
    energy_variance=8,
    formant_frequencies=[900, 1400, 2700],
    mel_frequency_coefficients=[1.0] * 13,
    duration=5.0,
)

```text
```

**Output Fields**:

- `detected_tone` (VoiceAffectTone): Primary emotional tone
- `arousal` (float): 0-1 scale, calmness to excitement
- `valence` (float): 0-1 scale, negativity to positivity
- `dominance` (float): 0-1 scale, submissiveness to assertiveness
- `stress_indicator` (float): 0-1 scale, relaxation to stress
- `emotional_state` (dict): All 8 tones with confidence scores
- `confidence` (float): Overall confidence in analysis (0-1)

##### `compare_with_text_emotion(text_tone: str, voice_analysis: VoiceAnalysis) -> dict`

Compares voice emotion against text emotion to detect incongruences.

**Parameters**:

- `text_tone` (str): Text-derived emotional tone (e.g., "excited", "calm")
- `voice_analysis` (VoiceAnalysis): Result from previous `analyze()` call

**Returns**: Dictionary with comparison results

```python
{ "text_tone": "excited", "voice_tone": "anxious", "match_score": 0.4,  # 0-1, higher = more similar
"incongruence_type": "possible_suppression",  # or "sarcasm", "conflict", "alignment" "is_sarcasm":
False, "is_suppression": True, "explanation": "Calm/hesitant voice with excited text suggests
suppression",
```text
```text
```

##

### Class: `VoiceAffectTone` (Enum)

**Values**:

- `CALM`: Low arousal, positive valence, controlled
- `ENERGETIC`: High arousal, variable valence
- `HESITANT`: Uncertain, questioning tone (pitch variance, pauses)
- `ANGRY`: High arousal, negative valence, high dominance
- `SAD`: Low arousal, negative valence
- `EXCITED`: High arousal, positive valence, rapid speech
- `ANXIOUS`: High arousal, negative valence, low dominance
- `CONFIDENT`: Steady, controlled, high dominance

##

### Class: `AcousticFeatures` (Dataclass)

Input data for voice analysis.

**Fields**:

```python

@dataclass class AcousticFeatures: fundamental_frequency: float      # Hz, typically 80-250 Hz
intensity: float                  # dB, typically 50-100 dB speech_rate: float                #
words per minute, typically 100-200 pause_frequency: float            # pauses per second, 0-1
pause_duration_avg: float         # milliseconds, 50-500 pitch_variance: float             # Hz^2,
measure of pitch fluctuation energy_variance: float            # dB^2, measure of intensity
fluctuation formant_frequencies: List[float]  # Hz, typically 3 values [F1, F2, F3]
mel_frequency_coefficients: List[float]  # 13 MFCCs

```text
```

**Typical Ranges**:

- `fundamental_frequency`: 80-300 Hz (male lower, female higher)
- `intensity`: 50-100 dB
- `speech_rate`: 80-250 wpm
- `pitch_variance`: 10-100 Hz²
- `energy_variance`: 1-30 dB²
- `formant_frequencies`: [700-1000, 1200-2500, 2500-4000] Hz

##

### Class: `VoiceAnalysis` (Dataclass)

Output data from voice analysis.

**Fields**:

```python
@dataclass
class VoiceAnalysis:
    detected_tone: VoiceAffectTone
    arousal: float                           # 0-1
    valence: float                           # 0-1
    dominance: float                         # 0-1
    stress_indicator: float                  # 0-1
    emotional_state: Dict[str, float]        # All 8 tones with confidences
```text
```text
```

##

## Facial Expression Detector

**Module**: `emotional_os/core/firstperson/facial_expression_detector.py`

### Class: `FacialExpressionDetector`

Main class for analyzing facial emotion from landmarks.

#### Methods

##### `__init__()`

```python

```text
```

Initializes the facial expression detector.

##### `analyze(landmarks: FaceLandmarks) -> FacialAnalysis`

Analyzes facial landmarks to determine expression and emotional state.

**Parameters**:

- `landmarks` (`FaceLandmarks`): 68-point face landmark coordinates

**Returns**: `FacialAnalysis` object containing expression, action units, and dimensions

**Example**:

```python
landmarks = FaceLandmarks( contour=[(x, y) for x, y in ...], right_eyebrow=[...],
left_eyebrow=[...], nose=[...], right_eye=[...], left_eye=[...], mouth=[...], ) analysis =
detector.analyze(landmarks) print(f"Expression: {analysis.expression}")
```text
```text
```

##

### Class: `FacialExpression` (Enum)

**Values** (Ekman's 7 basic emotions):

- `HAPPY`: Smile, raised cheeks (AU6 + AU12)
- `SAD`: Lowered mouth corners, inner brows raised (AU1 + AU15)
- `FEARFUL`: Raised brows, wide eyes, jaw drop (AU1 + AU2 + AU5 + AU26)
- `SURPRISED`: Similar to fearful, more jaw drop
- `ANGRY`: Lowered brows, narrowed eyes (AU4 + AU7)
- `DISGUSTED`: Nose wrinkle, upper lip raise (AU9 + AU10)
- `CONTEMPTUOUS`: One-sided smile + asymmetry
- `NEUTRAL`: Minimal AU activation

##

### Class: `ActionUnit` (Enum)

FACS (Facial Action Coding System) units tracked.

**Values**:

- `AU1`: Inner brow raiser (sadness, surprise)
- `AU2`: Outer brow raiser (surprise)
- `AU4`: Brow lowerer (anger, sadness)
- `AU5`: Upper lid raiser (surprise, fear)
- `AU6`: Cheek raiser (genuine smile indicator)
- `AU7`: Lid tightener (anger, disgust)
- `AU9`: Nose wrinkler (disgust)
- `AU10`: Upper lip raiser (disgust)
- `AU12`: Lip corner puller (smile)
- `AU15`: Lip corner depressor (sadness)
- `AU26`: Jaw drop (surprise, fear)

##

### Class: `FaceLandmarks` (Dataclass)

Input data for facial analysis (68 points normalized to 0-1 range).

**Fields**:

```python

@dataclass class FaceLandmarks: contour: List[Tuple[float, float]]              # 17 points
right_eyebrow: List[Tuple[float, float]]        # 5 points left_eyebrow: List[Tuple[float, float]]
# 5 points nose: List[Tuple[float, float]]                 # 9 points right_eye: List[Tuple[float,
float]]            # 6 points left_eye: List[Tuple[float, float]]             # 6 points

```text
```

**Total**: 68 landmarks, all normalized to (0, 1) range

##

### Class: `EyeMetrics` (Dataclass)

Eye-related measurements from facial landmarks.

**Fields**:

```python
@dataclass
class EyeMetrics:
    eye_openness: float                 # 0-1, closed to wide open
    pupil_dilation: float               # 0-1, constricted to dilated
    blink_rate: float                   # blinks per minute (0-30 typical)
    gaze_direction: str                 # "left", "center", "right"
```text
```text
```

##

### Class: `MouthMetrics` (Dataclass)

Mouth-related measurements from facial landmarks.

**Fields**:

```python

@dataclass
class MouthMetrics:
    smile_intensity: float              # 0-1, no smile to full smile
    mouth_openness: float               # 0-1, closed to wide open
    lip_tension: float                  # 0-1, relaxed to tense

```text
```

##

### Class: `FacialAnalysis` (Dataclass)

Output data from facial expression analysis.

**Fields**:

```python
@dataclass class FacialAnalysis: landmarks: FaceLandmarks expression: FacialExpression confidence:
float                            # 0-1 action_units: ActionUnitIntensities          # AU
measurements eye_metrics: EyeMetrics mouth_metrics: MouthMetrics arousal: float
# 0-1, sleepy to alert valence: float                               # 0-1, negative to positive
dominance: float                             # 0-1, submissive to assertive attention: float
# 0-1, distracted to focused
```text
```text
```

##

## Multimodal Fusion Engine

**Module**: `emotional_os/core/firstperson/multimodal_fusion_engine.py`

### Class: `MultimodalFusionEngine`

Fuses text, voice, and facial data into unified emotional understanding.

#### Methods

##### `__init__()`

```python

```text
```

Initializes the fusion engine.

##### `fuse(text_tone: str, voice_analysis: VoiceAnalysis, facial_analysis: FacialAnalysis) -> MultimodalAnalysis`

Combines all three modalities into unified analysis.

**Parameters**:

- `text_tone` (str): Text emotion (e.g., "excited", "calm", "angry")
- `voice_analysis` (VoiceAnalysis): Output from VoiceAffectDetector
- `facial_analysis` (FacialAnalysis): Output from FacialExpressionDetector

**Returns**: `MultimodalAnalysis` object with complete fusion results

**Example**:

```python
result = engine.fuse(
    text_tone="excited",
    voice_analysis=voice_result,
    facial_analysis=facial_result,
)

print(f"Primary emotion: {result.primary_emotion}")
print(f"Agreement: {result.modality_agreement:.2f}")
print(f"Congruence: {result.congruence_type}")

if result.incongruences:
    for inc in result.incongruences:
```text
```text
```

##

### Class: `CongruenceType` (Enum)

**Values**:

- `FULL_AGREEMENT`: All 3 modalities agree (rare)
- `PARTIAL_AGREEMENT`: 2/3 modalities aligned
- `MODALITY_CONFLICT`: All modalities disagree
- `TEXT_POSITIVE_VOICE_NEGATIVE`: Sarcasm indicator
- `SUPPRESSION`: Stressed voice/face with calm text
- `CONSISTENT_FAKE`: Low authenticity across modalities

##

### Class: `ModularityConfidence` (Dataclass)

Confidence scores for each modality and combined result.

**Fields**:

```python

@dataclass
class ModularityConfidence:
    text_confidence: float               # 0-1
    voice_confidence: float              # 0-1
    facial_confidence: float             # 0-1

```text
```

##

### Class: `EmotionalDimensions` (Dataclass)

Fused dimensional emotion representation with source attribution.

**Fields**:

```python
@dataclass class EmotionalDimensions: arousal: float                       # 0-1, fused arousal
valence: float                       # 0-1, fused valence dominance: float                     #
0-1, fused dominance arousal_source: str                  # "text", "voice", "facial"
valence_source: str                  # "text", "voice", "facial" dominance_source: str
# "text", "voice", "facial"
```text
```text
```

##

### Class: `MultimodalAnalysis` (Dataclass)

Complete output of multimodal fusion.

**Fields**:

```python

@dataclass class MultimodalAnalysis: primary_emotion: str                        # Dominant emotion
congruence_type: CongruenceType modality_agreement: float                   # 0-1, how much
agreement incongruences: List[str]                    # List of detected issues dimensions:
EmotionalDimensions confidence: ModularityConfidence comparison: ModularityComparison            #
Detailed modality breakdown

```text
```

##

## Data Classes

### `ActionUnitIntensities` (Dataclass)

Container for all 11 Action Unit measurements.

**Fields**:

```python
@dataclass
class ActionUnitIntensities:
    intensities: Dict[str, float]  # Keys: "AU1_inner_brow_raiser", "AU2_outer_brow_raiser", etc.
```text
```text
```

**Keys** (11 total):

- `AU1_inner_brow_raiser`
- `AU2_outer_brow_raiser`
- `AU4_brow_lowerer`
- `AU5_upper_lid_raiser`
- `AU6_cheek_raiser`
- `AU7_lid_tightener`
- `AU9_nose_wrinkler`
- `AU10_upper_lip_raiser`
- `AU12_lip_corner_puller`
- `AU15_lip_corner_depressor`
- `AU26_jaw_drop`

##

### `ModularityComparison` (Dataclass)

Detailed comparison of each modality's analysis.

**Fields**:

```python

@dataclass
class ModularityComparison:
    text_details: str           # Summary of text emotion
    voice_details: str          # Summary of voice tone
    facial_details: str         # Summary of facial expression
    text_voice_alignment: float # 0-1
    voice_facial_alignment: float # 0-1

```text
```

##

## Enums

### VoiceAffectTone

```python
```text
```text
```

### FacialExpression

```python

```text
```

### ActionUnit

```python
```text
```text
```

### CongruenceType

```python

FULL_AGREEMENT, PARTIAL_AGREEMENT, MODALITY_CONFLICT,

```text
```

##

## Common Usage Patterns

### Pattern 1: Simple Voice Analysis

```python
from emotional_os.core.firstperson import VoiceAffectDetector, AcousticFeatures

detector = VoiceAffectDetector() features = AcousticFeatures(...) analysis =
detector.analyze(features)
```text
```text
```

### Pattern 2: Facial Expression with Authenticity

```python

from emotional_os.core.firstperson import FacialExpressionDetector, FaceLandmarks

detector = FacialExpressionDetector() landmarks = FaceLandmarks(...) analysis =
detector.analyze(landmarks)

if analysis.authenticity > 0.7: print("Genuine expression") else:

```text
```

### Pattern 3: Full Multimodal Analysis

```python
from emotional_os.core.firstperson import MultimodalFusionEngine

engine = MultimodalFusionEngine()
result = engine.fuse(text_tone, voice_analysis, facial_analysis)

print(f"Emotion: {result.primary_emotion}")
print(f"Confidence: {result.confidence.overall_confidence:.2%}")
```text
```text
```

### Pattern 4: Sarcasm Detection

```python

if result.congruence_type == "TEXT_POSITIVE_VOICE_NEGATIVE":
    print("⚠️  Possible sarcasm detected")

```text
```

### Pattern 5: Suppression Detection

```python
if result.congruence_type == "SUPPRESSION": print("⚠️  Possible emotion suppression") print(f"Stress
level: {result.dimensions.stress_level:.2%}")
```

##

**Version**: 1.0
**Last Updated**: Phase 3.2 completion
**API Status**: Stable
