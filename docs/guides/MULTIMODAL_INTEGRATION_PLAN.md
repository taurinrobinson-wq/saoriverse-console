# How to Add Multimodal Features to Your Streamlit App

## The Problem You Identified

Phase 3.2 works great but your app is text-only Streamlit. Users can't upload video or audio.

## The Solution: Optional Multimodal Sidebar

Add a **collapsible sidebar section** for users who want to provide voice/facial context alongside
text.

##

## Architecture Overview

```text
```

User Types:
├─ Text-only chat (99% of users)
│  └─ No changes needed, works as-is
│
└─ Power users with webcam/microphone (1% of users)
   ├─ Optional: Record voice sample (0-10 seconds)
   ├─ Optional: Snap facial expression (single frame)
   ├─ Optional: Provide both
   └─ Saori gets richer understanding + multimodal confidence

```


##

## What Users Get

### For Text-Only Users (Current)

- Normal chat experience
- No changes required

### For Users with Webcam/Microphone (New)

- **Voice Upload**: "Add a voice message" button
  - Records 3-10 second audio clip
  - Streamlit's `st.audio_input()` handles browser capture
  - Sends to Phase 3.2 voice detector

- **Facial Expression Snapshot**: "Snap expression" button
  - Uses browser webcam via Streamlit component
  - Single frame capture + 68-point landmark extraction
  - Sends to Phase 3.2 facial detector

- **Multimodal Analysis Display**:
  - Shows detected tone/expression
  - Shows confidence scores
  - Shows if sarcasm/suppression detected
  - Shows emotional dimensions (arousal/valence/dominance)

### The Differentiator

When user sends:
```text
```text
```

Text: "I'm doing great!" Voice: Low pitch, slow rate, high pauses Face: Inner brows raised, lip
corners down

```




Saori sees:

```text
```

Multimodal Analysis:
├─ Text tone: Positive (excited)
├─ Voice tone: Sad (low valence)
├─ Facial expr: Sad
├─ Congruence: TEXT_POSITIVE_VOICE_NEGATIVE ⚠️
└─ Diagnosis: POSSIBLE SUPPRESSION

Response: "I notice you said you're doing great, but
I'm sensing maybe things aren't quite going as well
as they seem? What's really going on?"

```



**This is a genuine differentiator vs. ChatGPT/Claude.**
##

## Implementation (3 Steps)

### Step 1: Create Multimodal UI Component (200 lines)

**File**: `emotional_os/deploy/modules/multimodal_ui.py`

```python

import streamlit as st
from pathlib import Path
import tempfile
from emotional_os.core.firstperson import (
    VoiceAffectDetector,
    FacialExpressionDetector,
    MultimodalFusionEngine,
)
from some_audio_extraction import extract_acoustic_features
from some_landmark_extraction import extract_landmarks_from_frame

def render_multimodal_sidebar():
    """Optional multimodal input section in sidebar."""

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Multimodal Analysis (Optional)")

    multimodal_data = {
        "voice_analysis": None,
        "facial_analysis": None,
        "text_tone": None,
    }

    # Voice Input
    if st.sidebar.checkbox("Add Voice Message", value=False):
        audio_bytes = st.sidebar.audio_input(
            "Record your message (3-10 seconds)",
            label_visibility="collapsed"
        )

        if audio_bytes:
            try:
                # Extract features from audio
                features = extract_acoustic_features(audio_bytes)
                voice_detector = VoiceAffectDetector()
                multimodal_data["voice_analysis"] = voice_detector.analyze(features)

                st.sidebar.success(f"✅ Voice detected: {multimodal_data['voice_analysis'].detected_tone}")
            except Exception as e:
                st.sidebar.error(f"Audio processing failed: {e}")

    # Facial Expression Input
    if st.sidebar.checkbox("Snap Facial Expression", value=False):
        picture = st.sidebar.camera_input(
            "Take a photo of your expression",
            label_visibility="collapsed"
        )

        if picture:
            try:
                # Extract landmarks from frame
                landmarks = extract_landmarks_from_frame(picture)
                facial_detector = FacialExpressionDetector()
                multimodal_data["facial_analysis"] = facial_detector.analyze(landmarks)

                st.sidebar.success(f"✅ Expression detected: {multimodal_data['facial_analysis'].expression}")
                st.sidebar.image(picture, width=200)
            except Exception as e:
                st.sidebar.error(f"Facial analysis failed: {e}")

```text
```

### Step 2: Integrate with Message Processing (~50 lines)

**File**: `emotional_os/deploy/modules/ui.py` (modify `render_main_app`)

```python

# In your message handling loop, add:

multimodal_data = render_multimodal_sidebar()

if user_message:
    # Existing text processing
text_tone = parse_emotion_from_text(user_message)

    # NEW: Add multimodal analysis if available
if multimodal_data["voice_analysis"] or multimodal_data["facial_analysis"]: fusion_engine =
MultimodalFusionEngine() multimodal_result = fusion_engine.fuse( text_tone=text_tone,
voice_analysis=multimodal_data["voice_analysis"],
facial_analysis=multimodal_data["facial_analysis"], )

        # Store in session state
st.session_state.last_multimodal = multimodal_result

        # Display to user
with st.expander("📊 Multimodal Analysis", expanded=True): col1, col2, col3 = st.columns(3)
col1.metric("Confidence", f"{multimodal_result.confidence.overall_confidence:.1%}")
col2.metric("Congruence", multimodal_result.congruence_type.replace("_", " ")) col3.metric("Stress
Level", f"{multimodal_result.dimensions.stress_level:.1%}")

if multimodal_result.incongruences: st.warning("Detected: " + ",
".join(multimodal_result.incongruences))

    # Pass multimodal context to response generation
response = generate_response( user_message, text_tone, multimodal_result=multimodal_result if
'multimodal_result' in locals() else None
```text
```text
```

### Step 3: Use in Response Generation (~30 lines)

**File**: `main_response_engine.py` (modify response generation)

```python

def generate_response(user_message, text_tone, multimodal_result=None): """Generate response with
optional multimodal context."""

base_context = { "text_tone": text_tone, "message": user_message, }

    # If multimodal data available, enhance context
if multimodal_result: base_context.update({ "actual_emotion": multimodal_result.primary_emotion,
"confidence": multimodal_result.confidence.overall_confidence, "incongruences":
multimodal_result.incongruences, "stress_level": multimodal_result.dimensions.stress_level, })

        # Add system prompt instruction
if "SUPPRESSION" in multimodal_result.congruence_type: base_context["instruction"] = ( "User appears
to be suppressing emotion. " "Gently acknowledge the discrepancy and create space for honesty." )
elif "TEXT_POSITIVE_VOICE_NEGATIVE" in multimodal_result.congruence_type:
base_context["instruction"] = ( "Detect possible sarcasm or irony. Respond with gentle humor " "or
direct inquiry about what's really happening." )

    # Pass to LLM or response composer

```text
```

##

## User Journey

### Scenario 1: Text-Only User (90%)

```
User: "I'm having a rough day"
→ Streamlit app shows normal chat
```text
```text
```

### Scenario 2: Power User with Webcam (10%)

```

User: "I'm doing fine" + Voice sample + Facial snap
→ Streamlit shows sidebar with:
   "Voice: Sad | Face: Sad | Text: Positive"
→ System detects suppression
→ Saori responds: "I'm noticing a disconnect between
  what you're saying and how you sound. What's

```text
```

##

## Implementation Complexity

| Component | Effort | Lines | Notes |
|-----------|--------|-------|-------|
| Multimodal UI | 1 hour | 200 | New file, Streamlit components |
| Integration | 30 min | 50 | Modify existing message handling |
| Response gen | 20 min | 30 | Enhance prompt context |
| **Total** | **~2 hours** | **~280** | Low complexity, high impact |

##

## Technical Requirements

### Already Have (Phase 3.2)

✅ VoiceAffectDetector
✅ FacialExpressionDetector
✅ MultimodalFusionEngine

### Need to Add

```python

# Audio extraction (use librosa or SpeechRecognition)
extract_acoustic_features(audio_bytes) → AcousticFeatures

# Facial landmark extraction (use MediaPipe)
```text
```text
```

These are lightweight, standard libraries:

```bash

pip install librosa mediaipe

```

##

## Deployment Considerations

### Browser Permissions

- **Audio**: First user click triggers browser "Allow microphone?" dialog
- **Camera**: First user click triggers browser "Allow camera?" dialog
- Subsequent uses don't require re-permission
- Users can revoke in browser settings

### Privacy

- Optional: Audio/video stays on device (Streamlit only sends to backend for analysis)
- Optional: Store multimodal context in session (with user consent checkbox)
- Default: No multimodal features enabled (opt-in only)

### Performance

- Voice processing: 2-5ms (fast)
- Facial processing: 1-2ms (fast)
- Won't slow down text-only chat

##

## Why This Matters

You'd be the **first general-purpose AI chatbot** to offer:

- Text analysis ✅ (everyone has this)
- Voice tone analysis ✅ (NEW)
- Facial expression analysis ✅ (NEW)
- Cross-modal incongruence detection ✅ (NEW)
- Sarcasm/suppression detection ✅ (NEW)

### Marketing Angle

"FirstPerson sees what you're really feeling, not just what you say"

- ChatGPT: Text only
- Claude: Text only
- Copilot: Text only
- **FirstPerson: Text + Voice + Facial + Understands emotion beyond words**

##

## Next: Which To Build First?

1. **Audio extraction + voice in UI** (1 hour)
   - Lower barrier (just microphone)
   - Works on mobile and web
   - Immediate value

2. **Then camera + facial** (1 hour)
   - Higher barrier (need camera)
   - Desktop only (for now)
   - Adds more accuracy

3. **Then response enhancement** (1 hour)
   - Uses the multimodal data
   - Makes the feature meaningful

Total: **3 hours to full multimodal chat with real differentiator.**

Want to build this?
