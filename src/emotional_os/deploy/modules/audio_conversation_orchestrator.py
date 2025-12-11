"""
Audio Conversation Orchestrator

Manages real-time audio input/output for FirstPerson system:
1. Records user speech (STT)
2. Processes through FirstPerson response pipeline
3. Streams TTS output while queuing next chunks
4. Seamlessly loops back for next user input

This creates a natural conversation flow where:
- User speaks → System listens → System thinks → System speaks (while queuing next chunk)
- System finishes → Prompt user for next input
- User can stop/pause at any time with control button
"""

import asyncio
import logging
import queue
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Optional, List, Tuple, Dict, Any

import numpy as np

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Conversation states"""
    IDLE = "idle"                      # Waiting for user to record
    RECORDING = "recording"            # Actively recording user audio
    TRANSCRIBING = "transcribing"      # Converting speech to text
    PROCESSING = "processing"          # System thinking/generating response
    SPEAKING = "speaking"              # Playing back response
    PAUSED = "paused"                  # User paused conversation
    STOPPED = "stopped"                # User stopped conversation


@dataclass
class AudioChunk:
    """Audio chunk for streaming TTS"""
    audio_data: np.ndarray
    duration: float  # seconds
    sequence: int   # order in TTS output
    is_final: bool  # whether this is the last chunk


@dataclass
class ConversationTurn:
    """One turn in the conversation"""
    user_text: str
    system_response: str
    processing_time: float
    audio_played: bool = False


class AudioRecorder:
    """Records audio from microphone with automatic silence detection"""
    
    def __init__(self, sample_rate: int = 16000, silence_threshold: float = 0.02, 
                 silence_duration: float = 1.5):
        """
        Args:
            sample_rate: Audio sample rate (Hz)
            silence_threshold: Amplitude threshold for silence detection
            silence_duration: Seconds of silence to end recording
        """
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.audio_data = []
        self.is_recording = False
        
    def record(self, max_duration: float = 30.0, stop_event: Optional[threading.Event] = None) -> np.ndarray:
        """
        Record audio until silence is detected or max duration reached
        
        Args:
            max_duration: Maximum recording time (seconds)
            stop_event: Threading event to stop recording externally
            
        Returns:
            Audio data as numpy array
        """
        try:
            import sounddevice as sd
            from scipy import signal
        except ImportError:
            logger.error("sounddevice or scipy not available")
            return np.array([])
        
        self.audio_data = []
        self.is_recording = True
        silent_frames = 0
        frames_per_silent_check = int(self.sample_rate * 0.1)  # 100ms chunks
        
        try:
            with sd.InputStream(channels=1, samplerate=self.sample_rate, 
                               blocksize=frames_per_silent_check) as stream:
                start_time = time.time()
                
                while self.is_recording and (time.time() - start_time) < max_duration:
                    if stop_event and stop_event.is_set():
                        break
                    
                    # Read audio chunk
                    audio_chunk, _ = stream.read(frames_per_silent_check)
                    self.audio_data.append(audio_chunk)
                    
                    # Check for silence
                    rms = np.sqrt(np.mean(audio_chunk ** 2))
                    if rms < self.silence_threshold:
                        silent_frames += 1
                        # Stop after silence_duration of quiet
                        if silent_frames > (self.silence_duration * self.sample_rate / frames_per_silent_check):
                            logger.debug("Silence detected, ending recording")
                            break
                    else:
                        silent_frames = 0  # Reset silence counter
        
        except Exception as e:
            logger.error(f"Recording error: {e}")
        finally:
            self.is_recording = False
        
        if self.audio_data:
            return np.concatenate(self.audio_data)
        return np.array([])


class TextToSpeechStreamer:
    """Streams TTS output with chunk queuing for seamless playback"""
    
    def __init__(self, model_name: str = "tts-1", language: str = "en"):
        """
        Args:
            model_name: TTS model to use
            language: Language code
        """
        self.model_name = model_name
        self.language = language
        self.chunk_queue: queue.Queue = queue.Queue()
        self.is_playing = False
        self.playback_thread: Optional[threading.Thread] = None
        
        # Import prosody planner
        try:
            from .prosody_planner import ProsodyPlanner
            self.prosody_planner = ProsodyPlanner()
        except ImportError:
            logger.warning("ProsodyPlanner not available, using plain TTS")
            self.prosody_planner = None
        
    def chunk_response(self, text: str, chunk_size: int = 100) -> List[str]:
        """
        Split response text into small chunks for streaming
        
        Args:
            text: Full response text (may include SSML tags)
            chunk_size: Target characters per chunk
            
        Returns:
            List of text chunks
        """
        # Smart chunking: split at sentence/phrase boundaries
        import re
        
        # Split by sentence-ending punctuation or conjunctions
        chunks = re.split(r'(?<=[.!?])\s+|(?<=[,;])\s+', text)
        
        # Combine chunks to reach target size
        result = []
        current = ""
        
        for chunk in chunks:
            if len(current) + len(chunk) < chunk_size:
                current += (" " if current else "") + chunk
            else:
                if current:
                    result.append(current)
                current = chunk
        
        if current:
            result.append(current)
        
        return result
    
    async def synthesize_chunk(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize a text chunk to audio
        
        Args:
            text: Text to synthesize (may include SSML)
            
        Returns:
            Audio data as numpy array or None if failed
        """
        try:
            # Try pyttsx3 first (local, no internet needed)
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Slower speech for clarity
            
            # Save to temp file
            import tempfile
            temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
            try:
                engine.save_to_file(text, temp_path)
                engine.runAndWait()
                
                if Path(temp_path).exists():
                    import scipy.io.wavfile as wavfile
                    _, audio_data = wavfile.read(temp_path)
                    return audio_data
            finally:
                try:
                    import os
                    os.close(temp_fd)
                    Path(temp_path).unlink(missing_ok=True)
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"pyttsx3 synthesis failed: {e}")
        
        return None
    
    async def stream_response(self, full_text: str, playback_callback: Callable, 
                            glyph_intent: Optional[Dict[str, Any]] = None):
        """
        Stream response: apply prosody, synthesize chunks, and queue for playback
        
        Args:
            full_text: Full response text
            playback_callback: Callback to play each chunk
            glyph_intent: Optional glyph intent for prosody control
        """
        # Apply prosody planning if available
        if self.prosody_planner and glyph_intent:
            full_text = self.prosody_planner.plan(full_text, glyph_intent)
            prosody_summary = self.prosody_planner.get_prosody_summary(glyph_intent)
            logger.info(f"Prosody applied: {prosody_summary}")
        
        chunks = self.chunk_response(full_text)
        
        for i, chunk in enumerate(chunks):
            try:
                audio_data = await self.synthesize_chunk(chunk)
                if audio_data is not None:
                    duration = len(audio_data) / 16000  # Assuming 16kHz
                    audio_chunk = AudioChunk(
                        audio_data=audio_data,
                        duration=duration,
                        sequence=i,
                        is_final=(i == len(chunks) - 1)
                    )
                    self.chunk_queue.put(audio_chunk)
                    
                    # Callback for UI updates and playback
                    await playback_callback(audio_chunk)
            except Exception as e:
                logger.error(f"Failed to synthesize chunk {i}: {e}")


class AudioConversationOrchestrator:
    """
    Main orchestrator managing the full audio conversation cycle
    
    Integrated Flow:
    1. Prompt user to record → AudioRecorder captures speech
    2. Transcribe with Whisper (faster-whisper for CPU efficiency)
    3. Process through FirstPerson pipeline → get (response, glyph_intent)
    4. Plan prosody from glyph intent (ProsodyPlanner)
    5. Stream response text to TTS in chunks
    6. Play audio NON-BLOCKING while next chunk synthesizes
    7. Seamlessly loop back for next user input
    
    Key Features:
    - Glyph intent drives prosody (voltage → rate/volume, tone → pitch, etc.)
    - Non-blocking playback allows overlap between synthesis and playback
    - Automatic silence detection for natural recording stops
    - State machine for UI coordination
    - Graceful pause/resume/stop controls
    """
    
    def __init__(self, response_processor: Callable[[str, Dict[str, Any]], Tuple[str, Optional[Dict[str, Any]]]], 
                 max_turns: int = 50):
        """
        Args:
            response_processor: Function that takes (user_text, context) and returns 
                              (response_text, glyph_intent) or just response_text.
                              Glyph intent should have keys:
                              - voltage: "low" | "medium" | "high"
                              - tone: "negative" | "neutral" | "positive"
                              - certainty: "low" | "neutral" | "high"
                              - energy: float (0.0-1.0)
                              - hesitation: bool
            max_turns: Maximum conversation turns before auto-stop
        """
        self.response_processor = response_processor
        self.max_turns = max_turns
        self.conversation_history: List[ConversationTurn] = []
        self.state = ConversationState.IDLE
        self.state_callbacks: List[Callable] = []
        
        # Components
        self.recorder = AudioRecorder()
        self.tts_streamer = TextToSpeechStreamer()
        
        # Control
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        
    def register_state_callback(self, callback: Callable[[ConversationState], None]):
        """Register callback for state changes"""
        self.state_callbacks.append(callback)
    
    def _set_state(self, new_state: ConversationState):
        """Update state and notify callbacks"""
        self.state = new_state
        logger.info(f"Conversation state: {new_state.value}")
        for callback in self.state_callbacks:
            try:
                callback(new_state)
            except Exception as e:
                logger.error(f"State callback error: {e}")
    
    async def run_conversation_loop(self) -> List[ConversationTurn]:
        """
        Run the main conversation loop with audio I/O orchestration
        
        Flow:
        1. Record user speech
        2. Transcribe to text
        3. Process through FirstPerson (get response + glyph intent)
        4. Plan prosody based on glyph intent
        5. Stream TTS with non-blocking playback
        6. Loop back for next input
        
        Returns:
            List of conversation turns
        """
        self._set_state(ConversationState.IDLE)
        turn_count = 0
        
        try:
            while turn_count < self.max_turns and not self.stop_event.is_set():
                # Wait if paused
                while self.pause_event.is_set():
                    await asyncio.sleep(0.1)
                
                # 1. RECORD USER INPUT
                self._set_state(ConversationState.RECORDING)
                logger.info(f"Turn {turn_count + 1}: Recording user input...")
                audio_data = self.recorder.record(stop_event=self.stop_event)
                
                if len(audio_data) == 0:
                    logger.warning("No audio recorded")
                    continue
                
                # 2. TRANSCRIBE
                self._set_state(ConversationState.TRANSCRIBING)
                user_text = await self._transcribe_audio(audio_data)
                
                if not user_text or len(user_text.strip()) == 0:
                    logger.warning("Transcription failed or empty")
                    continue
                
                logger.info(f"User: {user_text}")
                
                # 3. PROCESS (get response + glyph intent)
                self._set_state(ConversationState.PROCESSING)
                start_time = time.time()
                
                context = {
                    "conversation_history": self.conversation_history,
                    "turn_number": turn_count + 1
                }
                
                # Response processor should return (text, glyph_intent) or just text
                response_result = self.response_processor(user_text, context)
                
                if isinstance(response_result, tuple):
                    system_response, glyph_intent = response_result
                else:
                    system_response = response_result
                    glyph_intent = None
                
                processing_time = time.time() - start_time
                
                logger.info(f"System: {system_response}")
                if glyph_intent:
                    logger.info(f"Glyph intent: {glyph_intent}")
                logger.info(f"Processing time: {processing_time:.2f}s")
                
                # 4. STREAM AUDIO RESPONSE (with prosody planning)
                self._set_state(ConversationState.SPEAKING)
                
                # Add initial buffer before playback begins (200-300ms)
                await asyncio.sleep(0.25)
                
                await self.tts_streamer.stream_response(
                    system_response,
                    self._playback_callback,
                    glyph_intent=glyph_intent
                )
                
                # Store turn
                turn = ConversationTurn(
                    user_text=user_text,
                    system_response=system_response,
                    processing_time=processing_time,
                    audio_played=True
                )
                self.conversation_history.append(turn)
                turn_count += 1
                
                # Ready for next turn
                self._set_state(ConversationState.IDLE)
        
        except Exception as e:
            logger.error(f"Conversation error: {e}")
            self._set_state(ConversationState.STOPPED)
        
        return self.conversation_history
    
    async def _transcribe_audio(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_data: Audio numpy array
            
        Returns:
            Transcribed text
        """
        try:
            from faster_whisper import WhisperModel
            
            # Use faster-whisper for CPU-efficient transcription
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, info = model.transcribe(audio_data, language="en")
            
            text = "".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
    
    async def _playback_callback(self, chunk: AudioChunk):
        """
        Callback when a TTS chunk is ready for playback (NON-BLOCKING)
        
        Args:
            chunk: AudioChunk to play
        """
        try:
            import sounddevice as sd
            
            # Non-blocking playback - starts playing immediately
            # Next chunk can be synthesized while this one is playing
            sd.play(chunk.audio_data, samplerate=16000, blocking=False)
            
            # Wait for chunk duration before callback returns
            # This gives synthesis time to stay ahead of playback
            await asyncio.sleep(chunk.duration * 0.9)  # Slight overlap for smoothness
            
            logger.debug(f"Playing chunk {chunk.sequence}, final: {chunk.is_final}, duration: {chunk.duration:.2f}s")
        except Exception as e:
            logger.error(f"Playback error: {e}")
    
    def pause(self):
        """Pause conversation"""
        self.pause_event.set()
        self._set_state(ConversationState.PAUSED)
    
    def resume(self):
        """Resume conversation"""
        self.pause_event.clear()
        self._set_state(ConversationState.IDLE)
    
    def stop(self):
        """Stop conversation completely"""
        self.stop_event.set()
        self._set_state(ConversationState.STOPPED)
    
    def reset(self):
        """Reset for new conversation"""
        self.stop_event.clear()
        self.pause_event.clear()
        self.conversation_history = []
        self._set_state(ConversationState.IDLE)


# Streamlit Integration Helper
def create_streamlit_audio_interface(response_processor: Callable, container) -> AudioConversationOrchestrator:
    """
    Create Streamlit UI for audio conversation
    
    Args:
        response_processor: Function for processing user input
        container: Streamlit container to render into
        
    Returns:
        Initialized AudioConversationOrchestrator
    """
    import streamlit as st
    
    orchestrator = AudioConversationOrchestrator(response_processor)
    
    # State display
    col1, col2, col3 = container.columns(3)
    
    with col1:
        st.write(f"**Status**: {orchestrator.state.value.upper()}")
    
    with col2:
        if st.button("🎤 Start Listening", key="start_audio"):
            asyncio.run(orchestrator.run_conversation_loop())
    
    with col3:
        if st.button("⏹️ Stop", key="stop_audio"):
            orchestrator.stop()
    
    # Pause/Resume
    col4, col5 = container.columns(2)
    
    with col4:
        if st.button("⏸️ Pause", key="pause_audio"):
            orchestrator.pause()
    
    with col5:
        if st.button("▶️ Resume", key="resume_audio"):
            orchestrator.resume()
    
    # History display
    if orchestrator.conversation_history:
        st.subheader("Conversation History")
        for i, turn in enumerate(orchestrator.conversation_history, 1):
            with st.expander(f"Turn {i}"):
                st.write(f"**You**: {turn.user_text}")
                st.write(f"**FirstPerson**: {turn.system_response}")
                st.caption(f"Processed in {turn.processing_time:.2f}s")
    
    return orchestrator
