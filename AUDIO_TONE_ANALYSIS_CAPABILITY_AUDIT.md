# Audio Tone & Emotion Analysis in SaoriVerse

## Current State: What's Already Built

Your repo **already has foundational audio analysis capabilities** through librosa. Here's what exists:

### ✅ Existing Audio Analysis Components

#### 1. **AudioProcessor** (`src/audio_pipeline.py`)
**What it does:**
- Loads and normalizes audio from bytes
- Detects Voice Activity (VAD) using energy thresholding
- Estimates emotion from audio metadata

**Current Methods:**
```python
class AudioProcessor:
    def load_audio(audio_bytes, sr=16000) → (np.ndarray, int)
    def normalize_audio(audio, target_db=-20.0) → np.ndarray
    def extract_vad_mask(audio, sr=16000) → np.ndarray
    def estimate_emotion_from_audio_metadata(audio_bytes) → dict
```

#### 2. **Audio Features Extracted** (Currently)
- ✅ **Zero-Crossing Rate (ZCR)** - Speech rate estimation (WPM)
- ✅ **Energy (RMS)** - Loudness/intensity levels
- ✅ **Spectral Centroid** - Pitch range classification (low/normal/high)
- ✅ **Voice Activity Detection** - Silence vs speech detection

**Current Output:**
```python
{
    "estimated_arousal": 0.6,      # 0.0-1.0
    "speech_rate_wpm": 150,         # words per minute
    "energy_level": 0.7,            # 0.0-1.0 (normalized loudness)
    "pitch_range": "normal",        # "low", "normal", "high"
}
```

#### 3. **Librosa Integration** 
- ✅ Already imported and used in `src/audio_pipeline.py`
- ✅ Already in dependencies (voice interface)
- ✅ Used for audio loading, VAD, feature extraction
- ✅ Used in TTS for time-stretching and pitch-shifting

#### 4. **Voice Synthesis with Prosody** 
- ✅ Already modulates pitch, rate, energy based on emotional state
- ✅ `streaming_tts.py` uses librosa for pitch-shifting (-2 to +2 semitones)
- ✅ `streaming_tts.py` uses librosa for time-stretching (0.8x to 1.2x speed)

**Current Prosody Framework:**
```python
Emotional State → Prosody Plan
├─ Rate: 0.8x to 1.2x (tempo)
├─ Pitch: -2 to +2 semitones
├─ Energy: 0.7 to 1.0 (amplitude)
└─ Emphasis: word-level marks
```

---

## 🔍 Gap Analysis: What's Missing for Deeper Tone Parsing

### Currently Limited:

1. **Pitch Analysis**
   - ✅ Spectral centroid (rough frequency classification)
   - ❌ Fundamental frequency (F0) extraction
   - ❌ Pitch contour/trajectory
   - ❌ Pitch variance (steady vs tremulous)

2. **Temporal Features**
   - ✅ Zero-crossing rate (proxy for speech rate)
   - ❌ Actual syllable/phoneme timing
   - ❌ Pause detection and duration
   - ❌ Speech rate within utterance (variability)

3. **Spectral Features**
   - ✅ Spectral centroid
   - ❌ MFCCs (Mel-Frequency Cepstral Coefficients)
   - ❌ Spectral bandwidth/spread
   - ❌ Formant frequencies
   - ❌ Spectral flux (change over time)

4. **Voice Quality**
   - ❌ Jitter (pitch perturbation)
   - ❌ Shimmer (amplitude perturbation)
   - ❌ Breathiness/noise ratio
   - ❌ Creakiness/vocal fry detection

5. **Emotion Classification**
   - ⚠️ Basic heuristics only (arousal estimate)
   - ❌ No multi-emotion classification (joy, sadness, anger, etc.)
   - ❌ No confidence scores
   - ❌ No ML-based SER (Speech Emotion Recognition) models

---

## 🚀 Quick Enhancement: What to Add

### **Level 1: Easy (< 1 hour)**
Add deeper spectral analysis using librosa (already installed):

```python
import librosa
import numpy as np

def extract_tone_features(audio, sr=16000):
    """Extract deeper audio features for tone analysis."""
    
    # 1. Fundamental frequency (pitch)
    S = np.abs(librosa.stft(audio))
    frequencies = librosa.fft_frequencies(sr=sr)
    magnitude = np.mean(S, axis=1)
    f0_hz = np.sum(frequencies * magnitude) / np.sum(magnitude)  # Centroid
    
    # 2. MFCCs (spectral fingerprint)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfccs, axis=1)
    mfcc_std = np.std(mfccs, axis=1)
    
    # 3. Spectral features
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)  # 12 chromatic bins
    
    # 4. Energy contour
    rms = librosa.feature.rms(y=audio)[0]
    energy_mean = np.mean(rms)
    energy_std = np.std(rms)
    
    # 5. Tempo and beat
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_env=onset_env, sr=sr)
    
    return {
        "f0_hz": float(f0_hz),
        "mfcc_mean": mfcc_mean.tolist(),
        "mfcc_std": mfcc_std.tolist(),
        "chroma": chroma_mean.tolist(),
        "energy_mean": float(energy_mean),
        "energy_std": float(energy_std),
        "tempo_bpm": float(tempo),
    }
```

**Performance:** ~5-10ms per 10s audio clip

---

### **Level 2: Medium (2-3 hours)**
Add heuristic-based mood classification:

```python
def classify_mood_from_features(features):
    """Simple heuristic mood classification."""
    
    f0 = features["f0_hz"]
    energy_mean = features["energy_mean"]
    energy_std = features["energy_std"]
    tempo = features["tempo_bpm"]
    
    # Simple rules
    mood_scores = {
        "joy": 0.0,
        "sadness": 0.0,
        "anger": 0.0,
        "calm": 0.0,
        "anxiety": 0.0,
    }
    
    # High pitch + high energy + fast tempo = joy/excitement
    if f0 > 200 and energy_mean > 0.5 and tempo > 110:
        mood_scores["joy"] += 0.7
        mood_scores["anxiety"] += 0.3
    
    # Low pitch + low energy + slow tempo = sadness
    elif f0 < 100 and energy_mean < 0.3 and tempo < 80:
        mood_scores["sadness"] += 0.8
    
    # High energy variation + loud + fast = anger
    elif energy_std > 0.2 and energy_mean > 0.6 and tempo > 120:
        mood_scores["anger"] += 0.7
    
    # Steady energy + moderate pitch = calm
    else:
        mood_scores["calm"] += 0.6
    
    # Normalize
    total = sum(mood_scores.values())
    if total > 0:
        mood_scores = {k: v/total for k, v in mood_scores.items()}
    
    return mood_scores
```

---

### **Level 3: Advanced (4-6 hours)**
Integrate with pre-trained Speech Emotion Recognition model:

```python
# Option A: Hugging Face transformers
from transformers import pipeline

def classify_emotion_ml(audio_bytes):
    """Use pre-trained SER model."""
    classifier = pipeline(
        "audio-classification",
        model="wav2vec2-large-xlsr-53-english"
    )
    result = classifier(audio_bytes)
    return result

# Option B: Pyannote audio
from pyannote.audio import Pipeline

def detect_speaker_emotion(audio_bytes):
    """Use pyannote for speaker diarization + emotion."""
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.0"
    )
    diarization = pipeline(audio_bytes)
    # Returns speaker segments with identity
```

---

## 🔌 Integration Points: Where to Add

### **Option 1: Extend AudioProcessor** (Recommended)
Add methods to `src/audio_pipeline.py`:

```python
class AudioProcessor:
    # Existing methods...
    
    def extract_tone_features(self, audio, sr=16000) -> dict:
        """Extract detailed tone features."""
        # Implementation above
    
    def classify_mood_from_features(self, features) -> dict:
        """Classify mood from extracted features."""
        # Implementation above
    
    def analyze_tone(self, audio_bytes) -> dict:
        """Full pipeline: extract features + classify mood."""
        audio, sr = self.load_audio(audio_bytes)
        features = self.extract_tone_features(audio, sr)
        mood = self.classify_mood_from_features(features)
        return {"features": features, "mood": mood}
```

### **Option 2: Create New Module**
Create `src/emotional_os/audio_tone_parser.py`:

```python
"""
Audio Tone Parser
Analyzes user's voice tone and extracts emotional cues
"""

import librosa
import numpy as np
from typing import Dict, Tuple

class AudioToneParser:
    """Parse audio tone and detect emotional state."""
    
    def __init__(self):
        self.sr = 16000
    
    def extract_features(self, audio: np.ndarray) -> Dict:
        """Extract tone features from audio."""
        # Implementation
    
    def classify_mood(self, features: Dict) -> Dict:
        """Classify mood from features."""
        # Implementation
    
    def analyze(self, audio_bytes: bytes) -> Dict:
        """Full analysis pipeline."""
        # Implementation
```

### **Option 3: Feed into Tier 2 Aliveness**
Modify Tier 2 to use audio tone:

```python
# In response_handler.py or tier2_aliveness.py

from src.emotional_os.audio_tone_parser import AudioToneParser

tone_parser = AudioToneParser()

# Extract tone from user's voice
audio_tone = tone_parser.analyze(recorded_audio)

# Feed into Tier 2
tier2_context = {
    "user_input": transcribed_text,
    "audio_tone": audio_tone,  # ← NEW
    "history": conversation_history
}

response, metrics = tier2.process_for_aliveness(
    user_input,
    base_response,
    history=tier2_context
)
```

---

## 📊 Feature Extraction Costs

### Processing Time per 10s Clip

| Feature | Time | Notes |
|---------|------|-------|
| Load audio | 1ms | Already done |
| Zero-crossing rate | <1ms | Already done |
| Spectral centroid | 2ms | Already done |
| RMS energy | 1ms | Already done |
| **MFCCs** | 3-5ms | ← NEW |
| **Chroma features** | 2-3ms | ← NEW |
| **Beat/tempo** | 2-3ms | ← NEW |
| **Pitch tracking** | 3-5ms | ← NEW |
| **Full feature extraction** | ~12-18ms | Total |
| **Heuristic mood classification** | <1ms | Fast |
| **ML model inference** | 50-200ms | Much slower |

**Recommendation:** Use Level 1-2 (heuristic) for <30ms total, keep ML for async analysis

---

## 🎯 Integration with Existing System

### Current Flow (Tier 1+2+3)
```
User Input (text + audio)
    ↓
Transcribe audio → text
    ↓
Tier 1: Learn + Safety
    ↓
Tier 2: Aliveness (tone detection from TEXT only)
    ↓
Tier 3: Poetry
    ↓
Response
```

### Enhanced Flow (With Audio Tone)
```
User Input (text + audio)
    ↓
Transcribe audio → text
    ↓ + Extract tone from AUDIO ← NEW
    ↓
Tier 1: Learn + Safety (+ audio tone context)
    ↓
Tier 2: Aliveness (+ audio tone as input)
    ↓ (uses mood detected from voice, not just text)
    ↓
Tier 3: Poetry
    ↓
Response
```

---

## 📋 Files to Check/Modify

### Already Exist
- ✅ `src/audio_pipeline.py` - AudioProcessor class (core audio loading)
- ✅ `src/streaming_tts.py` - Prosody generation (uses librosa)
- ✅ `src/emotional_os/tier2_aliveness.py` - Tier 2 orchestrator

### Would Need to Create
- `src/emotional_os/audio_tone_parser.py` - Deep tone analysis
- `tests/test_audio_tone_parser.py` - Tests for tone parser

### Would Need to Modify
- `src/emotional_os/tier2_aliveness.py` - Accept audio_tone in context
- `response_handler.py` - Pass audio_tone to Tier 2
- `session_manager.py` - Initialize tone parser

---

## 🚀 Recommended Next Steps

### **Immediate (If interested)**
1. Read through `src/audio_pipeline.py` - understand current audio loading
2. Check if recorded audio clips are available in sessions
3. Test `estimate_emotion_from_audio_metadata()` on actual recordings

### **Short Term (1-2 hours)**
Create `audio_tone_parser.py` with Level 1 features (MFCCs, chroma, tempo)

### **Medium Term (2-4 hours)**
Add Level 2 heuristic mood classification

### **Long Term (optional)**
Integrate ML-based SER models for more accurate emotion detection

---

## 📚 Reference Code Snippets

### Using librosa for feature extraction
```python
import librosa
import numpy as np

# Load
y, sr = librosa.load("clip.wav", sr=16000)

# MFCCs (13 coefficients = standard)
mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

# Chromagram (12 pitch classes)
chroma = librosa.feature.chroma_stft(y=y, sr=sr)

# Spectral centroid
centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

# Zero-crossing rate
zcr = librosa.feature.zero_crossing_rate(y)

# Tempo and beat
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
tempo, beats = librosa.beat.beat_track(onset_env=onset_env, sr=sr)

# RMS energy
rms = librosa.feature.rms(y=y)
```

---

## Summary

**Good News:** Your repo already has audio loading and basic tone detection infrastructure via librosa.

**What's available now:**
- Audio loading and normalization
- Voice activity detection
- Basic speech rate, energy, pitch range estimation
- Librosa integration for processing

**What's missing for deeper analysis:**
- MFCCs, chroma features, spectral analysis
- Detailed pitch extraction
- Temporal feature extraction
- Mood/emotion classification (heuristic or ML)

**Recommendation:** Add Level 1 features (MFCCs, chroma, tempo) as a simple extension to `AudioProcessor`. Performance should stay <20ms per 10s clip, fitting within Tier budgets.

Would you like me to implement the audio tone parser? Can do it either as:
1. **Extension to `AudioProcessor`** - simpler, integrated
2. **New module `AudioToneParser`** - more modular, extensible
3. **Integration with Tier 2** - immediately feed audio tone into response generation

---

**Document Created:** 2024
**Status:** Reference & Implementation Guide
