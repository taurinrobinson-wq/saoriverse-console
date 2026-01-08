""" Audio Conversation System - Integration Guide & Architecture

This document outlines the complete audio conversation pipeline for FirstPerson, including the
orchestrator, prosody planning, and Streamlit integration.

Table of Contents:

1. Architecture Overview 2. Components & Responsibilities 3. Data Flow 4. Integration with
FirstPerson Pipeline 5. Usage Examples 6. Troubleshooting """

# ============================================================================

# 1. ARCHITECTURE OVERVIEW

# ============================================================================

""" ┌─────────────────────────────────────────────────────────────────────────┐
│                     AUDIO CONVERSATION PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   RECORD     │ --> │ TRANSCRIBE   │ --> │   PROCESS    │ --> │ PLAN PROSODY │
│   (Audio)    │     │  (Whisper)   │     │(FirstPerson) │     │  (Glyphs)    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                ^                      |
                                                |                      v
context:              ┌──────────────┐ • history               │ SYNTHESIZE   │ • turn count
│   & STREAM   │ • settings              │   (TTS)      │
                                                                 └──────────────┘
                                                                      |
v ┌──────────────┐
                                                                 │   PLAYBACK   │
                                                                 │(Non-blocking)│
                                                                 └──────────────┘
                                                                      |
v [Loop back or Stop]

KEY FEATURES: • Glyph Intent → Prosody: voltage/tone/certainty control speech characteristics •
Non-blocking Playback: synthesis overlaps with playback (minimal latency) • Streaming TTS: text
chunked intelligently at sentence/phrase boundaries • Auto-silence Detection: recording stops after
1.5s of quiet • Pause/Resume/Stop: user controls at any time • State Machine: UI always knows
current conversation state """

# ============================================================================

# 2. COMPONENTS & RESPONSIBILITIES

# ============================================================================

""" ┌─ AudioRecorder ──────────────────────────────────────────────────────────┐
│ Captures user speech with automatic silence detection                    │
│ • Records 16kHz mono audio                                               │
│ • Auto-stops after 1.5s silence                                          │
│ • Thread-safe with stop event support                                    │
│ • Returns: np.ndarray of audio samples                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─ ProsodyPlanner ─────────────────────────────────────────────────────────┐
│ Converts glyph signals to SSML prosody tags                              │
│                                                                            │
│ Glyph Intent Inputs:                                                     │
│ • voltage: "low" | "medium" | "high"                                    │
│   → Affects: rate (slow/normal/fast), volume (soft/normal/loud)         │
│                                                                            │
│ • tone: "negative" | "neutral" | "positive"                             │
│   → Affects: pitch (low/medium/high)                                     │
│                                                                            │
│ • certainty: "low" | "neutral" | "high"                                 │
│   → Affects: intonation contour (rising/neutral/falling)                 │
│                                                                            │
│ • energy: 0.0-1.0 (float)                                                │
│   → Affects: overall intensity modulation                                │
│                                                                            │
│ • hesitation: bool                                                        │
│   → Adds strategic pauses for natural speech                             │
│                                                                            │
│ Output: SSML-marked text ready for TTS                                   │
│ Example: "<prosody rate='fast' pitch='high' volume='loud'>Text</prosody>"│
└─────────────────────────────────────────────────────────────────────────┘

┌─ TextToSpeechStreamer ───────────────────────────────────────────────────┐
│ Converts text chunks to audio and queues for playback                    │
│                                                                            │
│ Features:                                                                 │
│ • Smart chunking: splits at sentence/phrase boundaries                   │
│ • Applies ProsodyPlanner before synthesis                                │
│ • Uses pyttsx3 for local, offline TTS                                    │
│ • Non-blocking async synthesis                                           │
│ • Callback-driven playback coordination                                  │
│                                                                            │
│ Returns: AudioChunk objects with metadata (sequence, duration, is_final) │
└─────────────────────────────────────────────────────────────────────────┘

┌─ AudioConversationOrchestrator ──────────────────────────────────────────┐
│ Main coordinator managing full conversation cycle                        │
│                                                                            │
│ State Machine:                                                            │
│ • IDLE         → Waiting for user input                                  │
│ • RECORDING    → Capturing audio                                         │
│ • TRANSCRIBING → Converting speech to text (Whisper)                     │
│ • PROCESSING   → Running through FirstPerson pipeline                    │
│ • SPEAKING     → Playing back response audio                             │
│ • PAUSED       → User paused conversation                                │
│ • STOPPED      → User stopped or max turns reached                       │
│                                                                            │
│ Control Methods:                                                          │
│ • run_conversation_loop()  → Main async loop                             │
│ • pause()  → Pause at next safe point                                    │
│ • resume() → Resume from pause                                           │
│ • stop()   → Stop immediately                                            │
│ • reset()  → Clear history for new conversation                          │
│                                                                            │
│ Callbacks:                                                                │
│ • register_state_callback(fn) → Called on state changes                  │
│                                                                            │
│ Returns: List of ConversationTurn objects with full transcript           │
└─────────────────────────────────────────────────────────────────────────┘
"""

# ============================================================================

# 3. DATA FLOW

# ============================================================================

""" TURN-BY-TURN DATA FLOW:

1. USER SPEAKS
   ├─ AudioRecorder.record()
   └─ Returns: np.ndarray (16kHz mono audio)

2. TRANSCRIPTION
   ├─ WhisperModel.transcribe(audio_data)
   └─ Returns: str (user's text)

3. CONTEXT BUILDING
   ├─ conversation_history: List[ConversationTurn] (previous exchanges)
   ├─ turn_number: int (1-indexed)
   ├─ Any custom context (user preference, etc.)
   └─ Returns: Dict[str, Any]

4. FIRSTPERSON PROCESSING
   ├─ response_processor(user_text, context)
   ├─ Can return:
   │  • (response_text, glyph_intent)  → Full response with prosody
   │  • response_text                   → Plain text (no glyph prosody)
   └─ Returns: Tuple[str, Optional[Dict]] or str

5. PROSODY PLANNING (if glyph_intent provided)
   ├─ ProsodyPlanner.plan(response_text, glyph_intent)
   └─ Returns: SSML-marked text with prosody tags

6. TEXT CHUNKING
   ├─ Split at sentence boundaries (smart)
   ├─ Target ~100 characters per chunk
   └─ Returns: List[str]

7. TTS SYNTHESIS & STREAMING
   ├─ For each chunk:
   │  ├─ pyttsx3.synthesize_chunk(chunk)
   │  ├─ Save to temp WAV file
   │  ├─ Read audio data: np.ndarray
   │  └─ Create AudioChunk object
├─ Callback:_playback_callback(chunk)
   └─ Returns: None (async generator pattern)

8. NON-BLOCKING PLAYBACK
   ├─ sounddevice.play(audio_data, blocking=False)
   ├─ Sleep ~90% of chunk duration (overlap buffer)
   ├─ Next chunk starts synthesis while current plays
   └─ Continue until all chunks played

9. STORE CONVERSATION TURN
   ├─ ConversationTurn(user_text, system_response, processing_time)
   └─ Added to conversation_history

10. LOOP OR EXIT
    ├─ If stop_event set → Exit
    ├─ If pause_event set → Sleep until resumed
    ├─ If max_turns reached → Exit
    └─ Otherwise → Back to step 1 (USER SPEAKS)
"""

# ============================================================================

# 4. INTEGRATION WITH FIRSTPERSON PIPELINE

# ============================================================================

""" Your response_processor function MUST follow this signature:

def your_response_processor(user_text: str, context: dict) -> Union[str, Tuple[str, dict]]: '''
Args: user_text (str): User's spoken/typed input context (dict): Contains: • conversation_history
(List[ConversationTurn]) • turn_number (int) • Any other context you add

Returns: str: Plain response text OR Tuple[str, dict]: (response_text, glyph_intent) '''

    # Example: Call FirstPerson tier processing
from emotional_os.deploy.modules.response_handler import handle_response_pipeline

response_text, processing_time = handle_response_pipeline(user_text, context)

    # Example: Extract glyph intent from Glyph signals
glyph_intent = { "voltage": "high",        # User expressing high energy "tone": "positive",       #
Sentiment is positive "certainty": "high",      # Confident response "energy": 0.8,            # 80%
intensity "hesitation": False,      # No pauses }

return response_text, glyph_intent

# Then instantiate orchestrator

orchestrator = AudioConversationOrchestrator( response_processor=your_response_processor,
max_turns=50 )

# Run conversation (from Streamlit or elsewhere)

turns = asyncio.run(orchestrator.run_conversation_loop())

# Access results

for turn in turns: print(f"User: {turn.user_text}") print(f"System: {turn.system_response}")
print(f"Time: {turn.processing_time:.2f}s") print(f"Audio Played: {turn.audio_played}") """

# ============================================================================

# 5. USAGE EXAMPLES

# ============================================================================

""" EXAMPLE 1: Standalone Python Script ────────────────────────────────────

import asyncio from src.emotional_os.deploy.modules.audio_conversation_orchestrator import (
AudioConversationOrchestrator ) from emotional_os.deploy.modules.response_handler import
handle_response_pipeline

def my_response_processor(user_text, context): response,_ = handle_response_pipeline(user_text,
context)

    # Extract glyph-based intent (from your Glyph signals)
glyph_intent = { "voltage": "medium", "tone": "neutral", "certainty": "high", "energy": 0.5, }

return response, glyph_intent

orchestrator = AudioConversationOrchestrator(my_response_processor, max_turns=10)

# Add state callback for logging

def on_state_change(state): print(f"[State] {state.value.upper()}")

orchestrator.register_state_callback(on_state_change)

# Run conversation

turns = asyncio.run(orchestrator.run_conversation_loop())

# Print transcript

for i, turn in enumerate(turns, 1): print(f"\\n=== Turn {i} ===") print(f"You: {turn.user_text}")
print(f"FirstPerson: {turn.system_response}") print(f"Processing: {turn.processing_time:.2f}s")

─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

EXAMPLE 2: Streamlit Integration ──────────────────────────────────

import streamlit as st import asyncio from
src.emotional_os.deploy.modules.audio_conversation_orchestrator import (
AudioConversationOrchestrator, ConversationState ) from emotional_os.deploy.modules.response_handler
import handle_response_pipeline

st.title("FirstPerson Audio Conversation")

def response_processor(user_text, context):
    # Your FirstPerson processing here
response, _= handle_response_pipeline(user_text, context)

    # Build glyph intent based on response analysis
glyph_intent = { "voltage": "high" if len(response) > 200 else "medium", "tone": "positive",  # or
extract from sentiment analysis "certainty": "high", "energy": 0.7, "hesitation": False, } return
response, glyph_intent

# Initialize session state

if "orchestrator" not in st.session_state: st.session_state.orchestrator =
AudioConversationOrchestrator( response_processor, max_turns=50 )

orchestrator = st.session_state.orchestrator

# UI Layout

col1, col2, col3 = st.columns(3)

with col1: if st.button("🎤 Start Audio Conversation"): st.session_state.conversation_running = True

with col2: if st.button("⏸️ Pause"): orchestrator.pause()

with col3: if st.button("⏹️ Stop"): orchestrator.stop()

# State display

state_colors = { "idle": "🟢", "recording": "🔴", "transcribing": "🔵", "processing": "🟠", "speaking":
"🟡", "paused": "⚪", "stopped": "⚫", }

col_status = st.empty() col_status.write(f"{state_colors.get(orchestrator.state.value, '❓')} " +
f"**State**: {orchestrator.state.value.upper()}")

# Run conversation if active

if st.session_state.get("conversation_running", False): with st.spinner("Listening..."): turns =
asyncio.run(orchestrator.run_conversation_loop()) st.session_state.conversation_running = False

# Display history

if orchestrator.conversation_history: st.subheader("Conversation Transcript") for i, turn in
enumerate(orchestrator.conversation_history, 1): with st.expander(f"Turn {i}:
{turn.user_text[:50]}..."): st.write(f"**You:** {turn.user_text}") st.write(f"**FirstPerson:**
{turn.system_response}")
            st.caption(f"⏱️ {turn.processing_time:.2f}s | 🔊 Audio played: {turn.audio_played}")

─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

EXAMPLE 3: Pause/Resume During Conversation ──────────────────────────────────────────────

# In a background thread or event handler

import time

def monitor_user_input(): while not stop_event.is_set(): user_input = input("Command (p=pause,
r=resume, s=stop): ")

if user_input.lower() == "p": orchestrator.pause() print("⏸️ Paused") elif user_input.lower() ==
"r": orchestrator.resume() print("▶️ Resumed") elif user_input.lower() == "s": orchestrator.stop()
print("⏹️ Stopped")

time.sleep(0.1)

# Run in separate thread

import threading monitor_thread = threading.Thread(target=monitor_user_input, daemon=True)
monitor_thread.start()

turns = asyncio.run(orchestrator.run_conversation_loop()) """

# ============================================================================

# 6. TROUBLESHOOTING

# ============================================================================

""" ISSUE: "sounddevice unavailable: PortAudio library not found"
────────────────────────────────────────────────────────────── Cause: PortAudio development headers
not installed Fix: • Linux: apt-get install portaudio19-dev • macOS: brew install portaudio •
Windows: Already in Dockerfile.streamlit

ISSUE: spaCy model not found during warmup ──────────────────────────────────────────── Cause: NLP
initialization before Docker build completes Fix: • Ensure nlp_init.py runs successfully in
container • Check Dockerfile installs spaCy: python -m spacy download en_core_web_sm
  • Verify container logs: docker logs firstperson_streamlit | grep -i spacy

ISSUE: Transcription fails (WhisperModel issues) ─────────────────────────────────────────────────
Cause: faster-whisper not installed or audio quality poor Fix: • Ensure faster-whisper in
requirements.txt • Check audio levels: confirm AudioRecorder recording properly • Try shorter
recording duration (max_duration param in recorder.record)

ISSUE: TTS chunks not playing seamlessly ────────────────────────────────────────── Cause: Blocking
playback or synthesis latency Fix: • Verify playback is non-blocking: sd.play(..., blocking=False) •
Increase chunk duration (reduce chunk_size in TextToSpeechStreamer) • Check pyttsx3 engine state
between chunks

ISSUE: High latency between user input and response
─────────────────────────────────────────────────── Cause: Processing time, transcription delay, or
synthesis bottleneck Fix: • Profile response_processor timing • Use Whisper "tiny" or "base" for
faster transcription • Pre-warm TTS engine on startup • Consider chunking earlier (split text while
still processing)

ISSUE: Glyph intent not affecting prosody ────────────────────────────────────────── Cause:
response_processor not returning glyph_intent tuple Fix: • Ensure response_processor returns (text,
glyph_intent) not just text • Check ProsodyPlanner mapping matches your glyph schema • Verify
pyttsx3 supports SSML (some platforms don't fully support it) """

# ============================================================================

# END OF GUIDE

# ============================================================================
