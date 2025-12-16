# Phase 3.2 Integration Guide

**Target**: Integrating voice and facial affect detection into the full Saoriverse pipeline.

## Quick Start

### 1. Basic Multimodal Analysis

```python
from emotional_os.core.firstperson import (
    VoiceAffectDetector,
    FacialExpressionDetector,
    MultimodalFusionEngine,
    AcousticFeatures,
    FaceLandmarks,
)

# Initialize detectors
voice_detector = VoiceAffectDetector()
facial_detector = FacialExpressionDetector()
fusion_engine = MultimodalFusionEngine()

# Extract features (from audio and video)
voice_features = extract_acoustic_features(audio_data)  # Your extraction code
facial_landmarks = extract_facial_landmarks(video_frame)  # Your extraction code

# Analyze each modality
voice_analysis = voice_detector.analyze(voice_features)
facial_analysis = facial_detector.analyze(facial_landmarks)
text_tone = "excited"  # From Phase 1-2 analysis

# Fuse all modalities
multimodal_result = fusion_engine.fuse(
    text_tone=text_tone,
    voice_analysis=voice_analysis,
    facial_analysis=facial_analysis,
)

# Use result
print(f"Detected emotion: {multimodal_result.primary_emotion}")
print(f"Confidence: {multimodal_result.confidence.overall_confidence:.2f}")
if multimodal_result.incongruences:
```text
```



### 2. Feeding into Phase 3.1 Emotional Profiles

```python
from emotional_os.core.firstperson import EmotionalProfileManager

profile_manager = EmotionalProfileManager()

# Update profile with Phase 3.2 data
profile_manager.update_profile(
    emotion_tone=multimodal_result.primary_emotion,
    confidence=multimodal_result.confidence.overall_confidence,
    arousal=multimodal_result.dimensions.arousal,
    valence=multimodal_result.dimensions.valence,
    dominance=multimodal_result.dimensions.dominance,
    stress_level=multimodal_result.dimensions.stress_level,
    authenticity=multimodal_result.authenticity if hasattr(multimodal_result, 'authenticity') else None,
    incongruences=multimodal_result.incongruences,
)

# Profile now tracks multimodal data
```text
```



### 3. Audio Feature Extraction Reference

```python
import librosa
import numpy as np
from emotional_os.core.firstperson import AcousticFeatures

def extract_acoustic_features(audio_path, sr=22050):
    """Extract acoustic features from audio file."""
    y, sr = librosa.load(audio_path, sr=sr)

    # Pitch (fundamental frequency)
    f0 = librosa.yin(y, fmin=50, fmax=500)
    fundamental_frequency = np.nanmean(f0)

    # Intensity
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    intensity = np.mean(librosa.power_to_db(S))

    # Speech rate (frames per second with speech)
    hop_length = 512
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env)
    speech_rate = len(onset_frames) * sr / hop_length / (len(y) / sr) * 100

    # Pauses
    silence_threshold = np.mean(librosa.power_to_db(S)) - 20
    silent_frames = librosa.power_to_db(S) < silence_threshold
    pause_frames = np.sum(silent_frames, axis=1) / silent_frames.shape[1]
    pause_frequency = np.sum(pause_frames > 0.5) / len(pause_frames)
    pause_duration = np.mean(np.diff(np.where(pause_frames > 0.5)))

    # Variance
    pitch_variance = np.nanvar(f0)
    energy = np.sum(librosa.feature.melspectrogram(y=y, sr=sr), axis=0)
    energy_variance = np.var(energy)

    # Formants (approximate from spectral peaks)
    spec = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    formants = []
    for band in [1000, 3000, 5000]:
        idx = np.argmin(np.abs(freqs - band))
        formants.append(freqs[idx])

    # MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)

    # Duration
    duration = len(y) / sr

    return AcousticFeatures(
        fundamental_frequency=fundamental_frequency,
        intensity=intensity,
        speech_rate=speech_rate,
        pause_frequency=pause_frequency,
        pause_duration_avg=pause_duration,
        pitch_variance=pitch_variance,
        energy_variance=energy_variance,
        formant_frequencies=formants,
        mel_frequency_coefficients=mfcc_mean.tolist(),
        duration=duration,
```text
```



### 4. Facial Landmarks Extraction Reference

```python
import mediapipe as mp
import numpy as np
from emotional_os.core.firstperson import FaceLandmarks

def extract_facial_landmarks(video_frame):
    """Extract 68-point face landmarks from video frame."""
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        min_detection_confidence=0.5,
    ) as face_mesh:
        results = face_mesh.process(video_frame)

        if not results.multi_face_landmarks:
            return None

        landmarks_list = results.multi_face_landmarks[0].landmark

        # 68-point mapping (approximated from MediaPipe's 468 landmarks)
        # MediaPipe → Dlib 68-point conversion
        contour = [landmarks_list[i] for i in range(10)]
        right_eyebrow = [landmarks_list[i] for i in range(10, 15)]
        left_eyebrow = [landmarks_list[i] for i in range(15, 20)]
        nose = [landmarks_list[i] for i in range(20, 30)]
        right_eye = [landmarks_list[i] for i in range(30, 36)]
        left_eye = [landmarks_list[i] for i in range(36, 42)]
        mouth = [landmarks_list[i] for i in range(42, 68)]

        # Normalize to (0, 1) range
        def normalize(lm):
            return (lm.x, lm.y)

        return FaceLandmarks(
            contour=[normalize(lm) for lm in contour],
            right_eyebrow=[normalize(lm) for lm in right_eyebrow],
            left_eyebrow=[normalize(lm) for lm in left_eyebrow],
            nose=[normalize(lm) for lm in nose],
            right_eye=[normalize(lm) for lm in right_eye],
            left_eye=[normalize(lm) for lm in left_eye],
            mouth=[normalize(lm) for lm in mouth],
```text
```



## Integration Checkpoints

### Checkpoint 1: Voice Analysis Only

```python

# Test voice detection independently
voice_detector = VoiceAffectDetector()
voice_analysis = voice_detector.analyze(acoustic_features)

assert voice_analysis.detected_tone in [
    "Calm", "Energetic", "Hesitant", "Angry", "Sad", "Excited", "Anxious", "Confident"
]
assert 0 <= voice_analysis.arousal <= 1
assert 0 <= voice_analysis.valence <= 1
```text
```



### Checkpoint 2: Facial Analysis Only

```python

# Test facial detection independently
facial_detector = FacialExpressionDetector()
facial_analysis = facial_detector.analyze(landmarks)

assert facial_analysis.expression in [
    "Happy", "Sad", "Angry", "Fearful", "Surprised", "Disgusted", "Contemptuous", "Neutral"
]
assert 0 <= facial_analysis.authenticity <= 1
assert 0 <= facial_analysis.attention <= 1
```text
```



### Checkpoint 3: Multimodal Fusion

```python

# Test fusion of all three modalities
engine = MultimodalFusionEngine()
result = engine.fuse(text_tone, voice_analysis, facial_analysis)

assert result.primary_emotion is not None
assert 0 <= result.modality_agreement <= 1
assert result.congruence_type in [
    "Full_Agreement", "Partial_Agreement", "Modality_Conflict",
    "Text_Positive_Voice_Negative", "Suppression", "Consistent_Fake"
]
assert result.confidence.overall_confidence >= result.confidence.text_confidence

```text
```



### Checkpoint 4: Phase 3.1 Integration

```python

# Test integration with emotional profiles
profile_manager = EmotionalProfileManager()

# Before update
profile_before = profile_manager.get_current_profile()

# After multimodal analysis
profile_manager.update_profile(
    emotion_tone=result.primary_emotion,
    confidence=result.confidence.overall_confidence,
    arousal=result.dimensions.arousal,
    valence=result.dimensions.valence,
    dominance=result.dimensions.dominance,
    stress_level=result.dimensions.stress_level,
)

profile_after = profile_manager.get_current_profile()

assert profile_after.current_emotion != profile_before.current_emotion or \
```text
```



## Common Patterns

### Pattern 1: Real-time Voice Streaming

```python
import queue
import threading

class VoiceStreamAnalyzer:
    def __init__(self):
        self.detector = VoiceAffectDetector()
        self.audio_queue = queue.Queue()
        self.results = []

    def process_chunk(self, audio_chunk, sr=22050):
        """Process audio chunk (e.g., 0.5 seconds)."""
        features = self._extract_features(audio_chunk, sr)
        analysis = self.detector.analyze(features)
        self.results.append(analysis)
        return analysis

    def _extract_features(self, audio_chunk, sr):
        # ... feature extraction code ...
        pass

    def get_trend(self, window_size=5):
        """Get emotion trend over recent chunks."""
        if not self.results:
            return None
        recent = self.results[-window_size:]
        avg_arousal = np.mean([r.arousal for r in recent])
        avg_valence = np.mean([r.valence for r in recent])
        return {
            "arousal_trend": "increasing" if avg_arousal > recent[0].arousal else "decreasing",
            "valence_trend": "increasing" if avg_valence > recent[0].valence else "decreasing",
```text
```



### Pattern 2: Video Frame Batch Processing

```python
import cv2

class FacialExpressionBatchAnalyzer:
    def __init__(self):
        self.detector = FacialExpressionDetector()
        self.results = []

    def process_video(self, video_path, fps=10):
        """Process video file, sampling every 1/fps second."""
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Sample at desired fps
            if frame_count % int(cap.get(cv2.CAP_PROP_FPS) / fps) == 0:
                landmarks = extract_facial_landmarks(frame)
                if landmarks:
                    analysis = self.detector.analyze(landmarks)
                    self.results.append(analysis)

            frame_count += 1

        cap.release()
        return self.results

    def get_dominant_expression(self):
        """Get most common expression across video."""
        if not self.results:
            return None
        expressions = [r.expression for r in self.results]
```text
```



### Pattern 3: Sarcasm Detection Workflow

```python
def detect_sarcasm(text, voice_analysis, facial_analysis):
    """Detect sarcasm using text positivity and voice/facial negativity."""

    # Text sentiment (from Phase 1)
    text_positive = is_positive_text(text)  # your text analysis

    # Voice indicators (negative)
    voice_negative = (
        voice_analysis.valence < 0.4 or
        voice_analysis.detected_tone in ["Sad", "Angry", "Anxious"]
    )

    # Facial indicators (negative)
    facial_negative = (
        facial_analysis.expression in ["Sad", "Angry", "Contemptuous"] or
        facial_analysis.authenticity < 0.5
    )

    # Sarcasm: text positive, voice and/or facial negative
    is_sarcasm = text_positive and (voice_negative or facial_negative)

    return {
        "is_sarcasm": is_sarcasm,
        "text_positive": text_positive,
        "voice_negative": voice_negative,
        "facial_negative": facial_negative,
```text
```



## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import hashlib

class OptimizedMultimodalAnalyzer:
    def __init__(self):
        self.voice_detector = VoiceAffectDetector()
        self.facial_detector = FacialExpressionDetector()
        self.fusion_engine = MultimodalFusionEngine()
        self.cache = {}

    def _get_feature_hash(self, features):
        """Create hash of acoustic features for caching."""
        key_values = [
            features.fundamental_frequency,
            features.intensity,
            features.speech_rate,
        ]
        return hashlib.md5(str(key_values).encode()).hexdigest()

    def analyze_with_cache(self, voice_features, landmarks, text_tone):
        """Analyze with caching for repeated inputs."""
        voice_hash = self._get_feature_hash(voice_features)

        if voice_hash in self.cache:
            voice_analysis = self.cache[voice_hash]
        else:
            voice_analysis = self.voice_detector.analyze(voice_features)
            self.cache[voice_hash] = voice_analysis

        facial_analysis = self.facial_detector.analyze(landmarks)

```text
```



### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

class ParallelMultimodalAnalyzer:
    def __init__(self):
        self.voice_detector = VoiceAffectDetector()
        self.facial_detector = FacialExpressionDetector()
        self.fusion_engine = MultimodalFusionEngine()

    def analyze_parallel(self, voice_features, landmarks, text_tone):
        """Analyze voice and facial in parallel."""
        with ThreadPoolExecutor(max_workers=2) as executor:
            voice_future = executor.submit(
                self.voice_detector.analyze, voice_features
            )
            facial_future = executor.submit(
                self.facial_detector.analyze, landmarks
            )

            voice_analysis = voice_future.result()
            facial_analysis = facial_future.result()

```text
```



## Troubleshooting

### Issue: Low Voice Confidence

**Symptoms**: `voice_analysis.confidence < 0.5`

**Causes**:

- Poor audio quality (background noise)
- Very short audio sample (< 1 second)
- Unusual voice characteristics

**Solution**:

```python
if voice_analysis.confidence < 0.5:
    # Fall back to facial analysis or request clearer audio
```text
```



### Issue: Unrecognized Facial Expression

**Symptoms**: `facial_analysis.expression == "Neutral"` but clearly emotional

**Causes**:

- Landmark extraction failure
- Micro-expression (too brief to detect)
- Non-standard facial features

**Solution**:

```python
if facial_analysis.authenticity < 0.3:
    # Request clearer video or manual input
    print("Unable to reliably detect expression")
```text
```



### Issue: Multimodal Conflict

**Symptoms**: `result.congruence_type == "Modality_Conflict"`

**Diagnosis**:

```python
if result.congruence_type == "Modality_Conflict":
    print(f"Text: {text_tone}")
    print(f"Voice: {result.comparison.voice_details}")
    print(f"Facial: {result.comparison.facial_details}")
```text
```



## Testing Utilities

### Mock Generators for Testing

```python
from emotional_os.core.firstperson import (
    AcousticFeatures,
    FaceLandmarks,
    VoiceAnalysis,
    FacialAnalysis,
)

def create_mock_calm_voice():
    return AcousticFeatures(
        fundamental_frequency=130,  # Low pitch
        intensity=70,
        speech_rate=100,
        pause_frequency=0.2,
        pause_duration_avg=200,
        pitch_variance=10,
        energy_variance=5,
        formant_frequencies=[700, 1200, 2600],
        mel_frequency_coefficients=[0.5] * 13,
        duration=5.0,
    )

def create_mock_happy_face():
    # Smiling face landmarks (AU12 + AU6 active)
    return FaceLandmarks(
        contour=[(i/20, 0.5) for i in range(17)],
        right_eyebrow=[(0.3, 0.3), (0.35, 0.25), (0.4, 0.3), (0.45, 0.35), (0.5, 0.3)],
        left_eyebrow=[(0.5, 0.3), (0.55, 0.35), (0.6, 0.3), (0.65, 0.25), (0.7, 0.3)],
        nose=[(0.5, 0.4), (0.5, 0.5), (0.5, 0.6), (0.48, 0.65), (0.52, 0.65)],
        right_eye=[(0.35, 0.3), (0.35, 0.22), (0.45, 0.2), (0.45, 0.28)],
        left_eye=[(0.55, 0.3), (0.55, 0.22), (0.65, 0.2), (0.65, 0.28)],
        mouth=[(0.4, 0.65), (0.5, 0.62), (0.6, 0.65), (0.5, 0.72)],
    )
```


##

**Version**: 1.0
**Last Updated**: Phase 3.2 completion
**Next Integration**: Phase 3.5.2 (LoRA fine-tuning) or Phase 3.2.1 (streaming)
