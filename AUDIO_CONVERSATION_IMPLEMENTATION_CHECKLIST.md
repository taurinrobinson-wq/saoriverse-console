"""
Audio Conversation System - Implementation Checklist

Steps to fully integrate audio conversation into FirstPerson Streamlit app.
Check off each item as you complete it.

Created: 2025-12-11
Status: Ready for implementation
"""

# ============================================================================
# PHASE 1: DEPENDENCIES & INFRASTRUCTURE
# ============================================================================

PHASE_1_DEPENDENCIES = """
[✓] 1. System Dependencies (Dockerfile already includes):
    • portaudio19-dev (for sounddevice audio I/O)
    • libsndfile1 (for sound file handling)
    • ffmpeg (for audio format conversion)
    • gcc (for compilation)

[✓] 2. Python Packages (requirements.txt already includes):
    • sounddevice>=0.4.5         (audio recording/playback)
    • faster-whisper>=0.10.0     (speech-to-text)
    • pyttsx3>=2.90              (text-to-speech, local)
    • scipy>=1.11.0              (audio processing, silence detection)
    • numpy>=1.24.0              (audio data handling)
    • asyncio                    (built-in, async orchestration)

[✓] 3. Docker Image Rebuild:
    Command: docker compose -f docker-compose.local.yml build --no-cache streamlit
    
    Verification:
    • docker exec firstperson_streamlit python -c "import sounddevice; print('✓ sounddevice')"
    • docker exec firstperson_streamlit python -c "import faster_whisper; print('✓ faster-whisper')"
    • docker exec firstperson_streamlit python -c "import pyttsx3; print('✓ pyttsx3')"
"""

# ============================================================================
# PHASE 2: CORE MODULE SETUP
# ============================================================================

PHASE_2_MODULES = """
[✓] 1. prosody_planner.py (CREATED):
    Location: src/emotional_os/deploy/modules/prosody_planner.py
    Purpose: Convert glyph signals to SSML prosody tags
    Key Classes:
    • ProsodyPlanner: Maps voltage/tone/certainty to speech characteristics
    
    Test: python -c "from src.emotional_os.deploy.modules.prosody_planner import ProsodyPlanner; p = ProsodyPlanner(); print(p.get_prosody_summary({'voltage': 'high'}))"

[✓] 2. audio_conversation_orchestrator.py (UPDATED):
    Location: src/emotional_os/deploy/modules/audio_conversation_orchestrator.py
    Improvements Made:
    • Non-blocking playback with overlap buffer
    • Glyph intent support in TTS streaming
    • ProsodyPlanner integration
    • Response processor now returns (text, glyph_intent) tuples
    • 250ms initial playback buffer for smoother start
    
    Key Classes:
    • AudioRecorder: Captures speech with silence detection
    • TextToSpeechStreamer: Chunks text & synthesizes audio
    • AudioConversationOrchestrator: Main coordination loop
    • ProsodyPlanner: (imported) Prosody control

[  ] 3. UI Integration (NEXT):
    Location: src/emotional_os/deploy/modules/ui_refactored.py (or new module)
    Task: Add audio conversation UI to Streamlit
    
    What to Add:
    • "🎤 Start Audio Conversation" button
    • State indicator (live status display)
    • Pause/Resume/Stop controls
    • Conversation transcript display (expandable turns)
    • Real-time state callbacks to update UI
    
    Example Integration:
    from audio_conversation_orchestrator import AudioConversationOrchestrator
    from prosody_planner import ProsodyPlanner
    
    orchestrator = AudioConversationOrchestrator(
        response_processor=your_response_processor,
        max_turns=50
    )
    
    orchestrator.register_state_callback(st.session_state["update_state"])
    
    if st.button("🎤 Start"):
        turns = asyncio.run(orchestrator.run_conversation_loop())
"""

# ============================================================================
# PHASE 3: FIRSTPERSON INTEGRATION
# ============================================================================

PHASE_3_INTEGRATION = """
[  ] 1. Update response_processor signature:
    Current: handle_response_pipeline(user_text, context) → (text, time)
    
    New wrapper needed:
    def firstperson_audio_response_processor(user_text, context):
        response, processing_time = handle_response_pipeline(user_text, context)
        
        # Extract glyph-based intent (CRITICAL)
        glyph_intent = extract_glyph_intent(response, context)
        
        return response, glyph_intent
    
    Where glyph_intent dict contains:
    {
        "voltage": "low" | "medium" | "high",
        "tone": "negative" | "neutral" | "positive",
        "certainty": "low" | "neutral" | "high",
        "energy": 0.0-1.0 (float),
        "hesitation": bool,
        "phoneme_stretch": 1.0 (float, 1.0=normal)
    }

[  ] 2. Extract glyph signals for prosody:
    Suggested locations to extract signals:
    
    • Tier 1 Foundation (base emotional state):
      - valence (negative-positive) → tone mapping
      - arousal (low-high) → voltage mapping
    
    • Tier 2 Aliveness (presence intensity):
      - energy level → energy parameter
      - presence strength → volume scaling
    
    • Tier 3 Poetic Consciousness (complexity):
      - certainty metric → certainty parameter
      - introspection depth → hesitation/pauses
    
    Example extraction:
    def extract_glyph_intent(response_text, context):
        # Get latest glyph signals from Tier 2/3
        glyph_state = get_glyph_state()  # Your method
        
        return {
            "voltage": map_arousal_to_voltage(glyph_state.arousal),
            "tone": map_valence_to_tone(glyph_state.valence),
            "certainty": map_confidence_to_certainty(glyph_state.confidence),
            "energy": glyph_state.energy_level,
            "hesitation": glyph_state.introspection_depth > 0.7,
            "phoneme_stretch": 1.0,
        }

[  ] 3. Test integrated pipeline:
    Step-by-step test:
    
    a) Start Streamlit app:
       streamlit run app.py
    
    b) Navigate to audio conversation section
    
    c) Click "🎤 Start Audio Conversation"
    
    d) Speak test input: "How are you?"
    
    e) Verify:
       ✓ Audio recorded (waveform captured)
       ✓ Transcribed correctly (text appears)
       ✓ Response generated (FirstPerson response appears)
       ✓ Glyph intent extracted (logged)
       ✓ Prosody applied (speech sounds natural)
       ✓ Audio plays back (hear system response)
       ✓ State updates (UI shows: RECORDING → TRANSCRIBING → PROCESSING → SPEAKING → IDLE)
    
    f) Check logs:
       docker logs firstperson_streamlit | grep -i "audio\|prosody\|glyph"
"""

# ============================================================================
# PHASE 4: OPTIMIZATION & TUNING
# ============================================================================

PHASE_4_OPTIMIZATION = """
[  ] 1. Latency Profiling:
    Measure where time is spent:
    
    • Recording latency:
      - Start recording
      - Check time to first audio frame
      - Should be <100ms
    
    • Transcription latency:
      - Measure Whisper model inference time
      - Tune: use "tiny" for speed, "base" for accuracy
    
    • Processing latency:
      - Profile FirstPerson response pipeline
      - Check Tier 1/2/3 execution times
    
    • TTS latency:
      - Measure pyttsx3 synthesis time per chunk
      - Goal: synthesis faster than playback (9/10 of chunk duration)
    
    • Playback latency:
      - Measure time from playback start to first audio output
      - Should be <50ms (sounddevice overhead)
    
    Total Target: <2 seconds from speech end to response audio start

[  ] 2. Prosody Tuning:
    Fine-tune ProsodyPlanner mappings:
    
    • Voltage calibration:
      - Test different "rate" values (slow/medium/fast)
      - Match to arousal levels in your domain
    
    • Tone calibration:
      - Test different "pitch" values (low/medium/high)
      - Ensure negative→low, positive→high makes sense
    
    • Certainty calibration:
      - Test intonation contours (rising/neutral/falling)
      - Verify falling sounds confident, rising sounds questioning
    
    • Energy modulation:
      - Adjust volume scaling based on energy value
      - Test 0.0-1.0 range with different response texts
    
    Create test cases:
    glyph_intent_confident = {"voltage": "high", "tone": "positive", "certainty": "high"}
    glyph_intent_uncertain = {"voltage": "low", "tone": "negative", "certainty": "low"}
    
    Test both with same text to hear prosody differences

[  ] 3. Audio Quality Tuning:
    • Silence detection:
      - Current: 1.5 seconds of <0.02 RMS amplitude
      - Tune silence_threshold if too sensitive/insensitive
      - Tune silence_duration if recordings cut off too early/late
    
    • Sample rate:
      - Current: 16kHz (good balance of quality/size)
      - Increase to 48kHz for higher quality if CPU allows
    
    • Chunk size:
      - Current: ~100 characters per chunk
      - Increase for longer phrases (less switching)
      - Decrease for punchier delivery
    
    • Playback buffer:
      - Current: 0.25 seconds (250ms) before playback
      - Increase if synthesis can't keep up
      - Decrease if latency is priority

[  ] 4. Error Handling & Fallbacks:
    Test failure scenarios:
    
    • No audio input:
      - Microphone disconnected
      - Proper error message to user
    
    • Transcription failure:
      - Audio too noisy
      - Offer to re-record or type instead
    
    • TTS synthesis failure:
      - pyttsx3 engine crash
      - Fall back to text-only response
    
    • Processing timeout:
      - FirstPerson takes >30 seconds
      - Show "Still thinking..." message
      - Allow user to cancel and continue typing

[  ] 5. Performance Monitoring:
    Add to logs:
    
    • Per-turn metrics:
      - User speech duration (seconds)
      - Transcription confidence (0-1)
      - Processing time (seconds)
      - Total response duration (seconds)
      - Turn completion time (end-to-end)
    
    • Session metrics:
      - Total turns completed
      - Average processing time per turn
      - Error rate (failed transcriptions, etc.)
      - Total session duration
    
    Example logging:
    logger.info(f"Turn {turn_num}: "
               f"speech={recording_time:.1f}s, "
               f"transcribe={transcribe_time:.1f}s, "
               f"process={process_time:.1f}s, "
               f"tts={tts_time:.1f}s, "
               f"total={total_time:.1f}s")
"""

# ============================================================================
# PHASE 5: USER EXPERIENCE
# ============================================================================

PHASE_5_UX = """
[  ] 1. Visual Feedback:
    Create clear UI indicators:
    
    • State indicator (animated):
      - IDLE: "🟢 Ready to listen"
      - RECORDING: "🔴 Listening..." (with waveform animation)
      - TRANSCRIBING: "🔵 Processing speech..."
      - PROCESSING: "🟠 FirstPerson thinking..."
      - SPEAKING: "🟡 Speaking response..." (with audio waveform)
      - PAUSED: "⚪ Paused"
      - STOPPED: "⚫ Stopped"
    
    • Real-time waveform visualization:
      - Show incoming audio during recording
      - Show playback waveform during response
    
    • Transcript display:
      - Show user's transcription immediately
      - Show system response as it's generated/played

[  ] 2. Control Buttons:
    Place clearly above/below waveform:
    
    • 🎤 Start Audio Conversation (primary)
    • ⏸️ Pause (during SPEAKING)
    • ▶️ Resume (during PAUSED)
    • ⏹️ Stop (anytime)
    • 📝 Switch to Text (stop audio, fallback to typing)

[  ] 3. Accessibility:
    • Add transcription display (for deaf users)
    • Volume control for playback
    • Speed control for playback (1.0x / 0.8x / 1.2x)
    • Haptic feedback option (if device supports)
    • Keyboard shortcuts (Space=start, P=pause, S=stop)

[  ] 4. Settings/Configuration:
    Allow users to customize:
    
    • Audio sensitivity (silence threshold)
    • Maximum recording duration (default 30s)
    • Response voice (pitch, rate)
    • Prosody intensity (how much glyph signals affect speech)
    • Transcript visibility (show/hide)
    • Auto-play next turn (loop until user stops)
"""

# ============================================================================
# PHASE 6: DEPLOYMENT & MONITORING
# ============================================================================

PHASE_6_DEPLOYMENT = """
[✓] 1. Docker Deployment (Already configured):
    • Dockerfile.streamlit includes all audio dependencies
    • docker-compose.local.yml configured with Ollama
    • Both services running and healthy
    
    Verify:
    docker compose -f docker-compose.local.yml ps

[  ] 2. Environment Configuration:
    Set in docker-compose.local.yml or .env:
    
    • WHISPER_MODEL_SIZE: "tiny" | "base" | "small"
                         (tiny=fastest, small=best quality)
    • TTS_ENGINE: "pyttsx3" (or future: "elevenlabs", "google", etc.)
    • AUDIO_SAMPLE_RATE: 16000 (Hz)
    • AUDIO_SILENCE_THRESHOLD: 0.02 (RMS amplitude)
    • AUDIO_SILENCE_DURATION: 1.5 (seconds)
    • MAX_RECORDING_DURATION: 30 (seconds)
    • MAX_CONVERSATION_TURNS: 50 (per session)

[  ] 3. Production Checklist:
    Before deploying to production:
    
    • [ ] Load testing: 10+ concurrent audio conversations
    • [ ] Stress testing: 100+ turns in one session
    • [ ] Error recovery: all failure modes handled gracefully
    • [ ] Security: no audio data logged/stored without consent
    • [ ] Privacy: GDPR compliance for audio data
    • [ ] Licensing: verify pyttsx3 license compatible
    • [ ] Performance: <2s latency for 95th percentile
    • [ ] Monitoring: all metrics logged and dashboarded

[  ] 4. Scaling Considerations:
    For high-concurrency deployment:
    
    • Whisper model: Consider TensorRT optimization
    • TTS: Consider cloud TTS (Google, Azure) for parallelism
    • Audio storage: Use object storage (S3, etc.) if archiving
    • Load balancing: Distribute across multiple Streamlit instances
    • Database: Store conversations persistently for analytics
"""

# ============================================================================
# TESTING CHECKLIST
# ============================================================================

TESTING_CHECKLIST = """
[  ] Unit Tests:
    • AudioRecorder: silence detection, max duration
    • TextToSpeechStreamer: chunking logic, prosody application
    • ProsodyPlanner: all mappings, SSML generation
    • AudioConversationOrchestrator: state transitions, callbacks

[  ] Integration Tests:
    • End-to-end audio conversation (mock FirstPerson response)
    • Pause/resume functionality
    • Stop during playback
    • Multiple consecutive turns
    • Error handling (no audio, bad transcription, synthesis failure)

[  ] UI Tests (Manual):
    • Button responsiveness
    • State display accuracy
    • Transcript appearance
    • Audio playback (verify sound)
    • Mobile responsiveness (if deployed to mobile)

[  ] Performance Tests:
    • Latency profiling (record each stage)
    • Memory usage during long sessions
    • CPU usage during playback
    • GPU utilization (if using GPU-accelerated Whisper)
"""

# ============================================================================
# QUICK START GUIDE (For Next Session)
# ============================================================================

QUICK_START = """
To resume work on audio integration:

1. Start Docker:
   docker compose -f docker-compose.local.yml up -d

2. Start Streamlit:
   streamlit run app.py

3. Test audio components:
   python -c "from src.emotional_os.deploy.modules.audio_conversation_orchestrator import AudioConversationOrchestrator; print('✓ Import successful')"

4. Check logs:
   docker logs firstperson_streamlit | tail -50

5. Access Streamlit:
   Open http://localhost:8501 in browser

6. Begin PHASE 3 (UI Integration) from checklist above

7. For debugging:
   docker exec -it firstperson_streamlit bash
   cd /app && python -m pytest tests/ -v
"""

# ============================================================================
# CURRENT STATUS: 2025-12-11
# ============================================================================

STATUS = """
✓ COMPLETED:
  - ProsodyPlanner class (prosody_planner.py)
  - AudioRecorder with silence detection
  - TextToSpeechStreamer with chunk queuing
  - AudioConversationOrchestrator with state machine
  - Non-blocking playback integration
  - Glyph intent support throughout pipeline
  - Docker dependencies (PortAudio, ffmpeg, etc.)
  - Documentation (this file + AUDIO_CONVERSATION_INTEGRATION_GUIDE.md)

⏳ NEXT (PRIORITY ORDER):
  1. Update response_processor to extract glyph intent
  2. Integrate audio UI into ui_refactored.py
  3. Test full end-to-end pipeline
  4. Prosody tuning based on FirstPerson glyph signals
  5. Performance optimization & latency reduction
  6. Error handling & fallback paths
  7. Production monitoring & deployment

🎯 GOAL:
  Users can have natural, prosodically-expressive conversations with FirstPerson
  using spoken audio, with glyph signals driving speech characteristics in real time.
"""
