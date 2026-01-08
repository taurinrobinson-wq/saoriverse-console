"""Sprint 3: Streaming Text-to-Speech Integration

Convert glyph-driven prosody plans to streaming audio with minimal latency.
Uses Coqui TTS for high-quality synthesis with emotional control.
"""

import io
import numpy as np
from typing import Generator, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import time

try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False


class StreamingTTSError(Exception):
    """Raised when TTS streaming fails."""
    pass


@dataclass
class TTSConfig:
    """TTS synthesis configuration."""

    model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"
    """Coqui TTS model to use."""

    gpu: bool = False
    """Use GPU acceleration if available."""

    chunk_size_ms: int = 500
    """Generate audio in chunks of this duration."""

    sample_rate: int = 22050
    """Output sample rate in Hz."""

    language: str = "en"
    """Language code."""


@dataclass
class TTSAudioChunk:
    """A chunk of generated audio."""

    audio_data: np.ndarray
    """Audio samples (mono, float32)."""

    duration_ms: float
    """Duration of this chunk in milliseconds."""

    start_time_ms: float
    """Absolute start time in milliseconds."""

    is_final: bool = False
    """Whether this is the final chunk."""


class ProsodyApplier:
    """Applies prosody adjustments to synthesized audio."""

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def apply_rate_change(
        self,
        audio: np.ndarray,
        rate_multiplier: float,
    ) -> np.ndarray:
        """Change speaking rate by time-stretching audio.

        Args:
            audio: Input audio samples
            rate_multiplier: Speed factor (1.0 = normal, 1.5 = 50% faster)

        Returns:
            Time-stretched audio
        """
        if rate_multiplier <= 0:
            raise ValueError(
                f"Rate multiplier must be positive: {rate_multiplier}")

        if abs(rate_multiplier - 1.0) < 0.01:
            # No change needed
            return audio

        try:
            import librosa
            # Stretch time without changing pitch
            stretched = librosa.effects.time_stretch(
                audio, rate=rate_multiplier)
            return stretched
        except ImportError:
            # Fallback: simple resampling (changes pitch but maintains duration ratio)
            # This is less ideal but works without librosa
            target_length = int(len(audio) / rate_multiplier)
            return np.interp(
                np.linspace(0, len(audio) - 1, target_length),
                np.arange(len(audio)),
                audio
            )

    def apply_pitch_shift(
        self,
        audio: np.ndarray,
        semitone_shift: float,
    ) -> np.ndarray:
        """Shift pitch by semitones without changing speed.

        Args:
            audio: Input audio samples
            semitone_shift: Pitch shift in semitones (-12 to +12)

        Returns:
            Pitch-shifted audio
        """
        if abs(semitone_shift) < 0.1:
            return audio

        try:
            import librosa
            # Shift pitch without changing time
            shifted = librosa.effects.pitch_shift(
                audio,
                sr=self.sample_rate,
                n_steps=semitone_shift
            )
            return shifted
        except ImportError:
            # Fallback: frequency-domain pitch shifting approximation
            # FFT-based approach for quick estimation
            fft = np.fft.rfft(audio)
            # Shift bin indices
            # 120 semitones ≈ octave in bins
            shift_bins = int(len(fft) * semitone_shift / 120)
            if shift_bins > 0:
                fft_shifted = np.pad(fft, (shift_bins, 0))[:-shift_bins]
            else:
                fft_shifted = np.pad(fft, (0, -shift_bins))[-shift_bins:]
            return np.fft.irfft(fft_shifted, n=len(audio))

    def apply_energy_scaling(
        self,
        audio: np.ndarray,
        energy_multiplier: float,
    ) -> np.ndarray:
        """Scale audio energy (volume).

        Args:
            audio: Input audio samples
            energy_multiplier: Energy scale factor

        Returns:
            Scaled audio
        """
        # Clamp to prevent clipping
        scaled = audio * energy_multiplier
        scaled = np.clip(scaled, -0.95, 0.95)
        return scaled

    def apply_pause_emphasis(
        self,
        audio: np.ndarray,
        emphasis_tokens: list,
        word_boundaries: list,
    ) -> np.ndarray:
        """Add emphasis pauses around important words.

        Args:
            audio: Input audio samples
            emphasis_tokens: List of emphasized word indices
            word_boundaries: List of (start_sample, end_sample) for each word

        Returns:
            Audio with emphasis pauses
        """
        if not emphasis_tokens or not word_boundaries:
            return audio

        # Add short silence (100ms) after emphasized words
        silence_samples = int(0.1 * self.sample_rate)
        silence = np.zeros(silence_samples)

        # Build output by inserting pauses
        output = []
        sample_offset = 0

        for word_idx, (start, end) in enumerate(word_boundaries):
            # Add audio chunk
            output.append(audio[sample_offset:end])

            # Add pause if this word is emphasized
            if word_idx in emphasis_tokens:
                output.append(silence)

            sample_offset = end

        # Add remaining audio
        if sample_offset < len(audio):
            output.append(audio[sample_offset:])

        return np.concatenate(output) if output else audio


class StreamingTTSEngine:
    """High-performance streaming TTS synthesis."""

    def __init__(self, config: Optional[TTSConfig] = None):
        """Initialize TTS engine.

        Args:
            config: TTS configuration

        Raises:
            StreamingTTSError: If TTS library not available
        """
        if not HAS_TTS:
            raise StreamingTTSError(
                "TTS not installed. Run: pip install TTS"
            )

        self.config = config or TTSConfig()
        self.sample_rate = self.config.sample_rate
        self.prosody_applier = ProsodyApplier(self.sample_rate)

        # Lazy load TTS model to avoid startup delay
        self._tts_model = None

    def _load_model(self):
        """Lazy-load TTS model on first use."""
        if self._tts_model is None:
            try:
                self._tts_model = TTS(
                    model_name=self.config.model_name,
                    gpu=self.config.gpu,
                    progress_bar=False,
                    verbose=False
                )
            except Exception as e:
                raise StreamingTTSError(f"Failed to load TTS model: {e}")

    def synthesize_with_prosody(
        self,
        text: str,
        prosody_plan: Any,  # ProsodyPlan from prosody_planner
    ) -> np.ndarray:
        """Synthesize audio with prosody characteristics.

        Args:
            text: Text to synthesize
            prosody_plan: ProsodyPlan from prosody_planner

        Returns:
            Audio samples as numpy array (mono, float32)
        """
        self._load_model()

        # Initial synthesis
        try:
            # Generate base audio
            wav = self._tts_model.tts(
                text=text,
                language=self.config.language,
            )

            # Convert to numpy if needed
            if not isinstance(wav, np.ndarray):
                wav = np.array(wav)

            # Normalize to float32 if needed
            if wav.dtype != np.float32:
                # Normalize from int16 or other format
                if np.issubdtype(wav.dtype, np.integer):
                    wav = wav.astype(np.float32) / 32768.0
                else:
                    wav = wav.astype(np.float32)
        except Exception as e:
            raise StreamingTTSError(f"TTS synthesis failed: {e}")

        # Apply prosody modifications
        wav = self.prosody_applier.apply_rate_change(
            wav,
            prosody_plan.speaking_rate
        )

        wav = self.prosody_applier.apply_pitch_shift(
            wav,
            prosody_plan.pitch_shift_semitones
        )

        wav = self.prosody_applier.apply_energy_scaling(
            wav,
            prosody_plan.energy_level
        )

        return wav

    def stream_synthesis(
        self,
        text: str,
        prosody_plan: Any,
        chunk_size_ms: Optional[int] = None,
    ) -> Generator[TTSAudioChunk, None, None]:
        """Stream synthesized audio in chunks.

        Args:
            text: Text to synthesize
            prosody_plan: ProsodyPlan from prosody_planner
            chunk_size_ms: Size of audio chunks (default from config)

        Yields:
            TTSAudioChunk objects
        """
        chunk_size_ms = chunk_size_ms or self.config.chunk_size_ms

        # Generate full audio
        audio = self.synthesize_with_prosody(text, prosody_plan)

        # Calculate chunk size in samples
        chunk_samples = int((chunk_size_ms / 1000.0) * self.sample_rate)

        # Stream chunks
        current_sample = 0
        chunk_start_ms = 0.0

        while current_sample < len(audio):
            # Extract chunk
            chunk_end = min(current_sample + chunk_samples, len(audio))
            chunk_audio = audio[current_sample:chunk_end]

            # Calculate duration
            chunk_duration_ms = (len(chunk_audio) / self.sample_rate) * 1000

            # Determine if final
            is_final = chunk_end >= len(audio)

            yield TTSAudioChunk(
                audio_data=chunk_audio,
                duration_ms=chunk_duration_ms,
                start_time_ms=chunk_start_ms,
                is_final=is_final
            )

            current_sample = chunk_end
            chunk_start_ms += chunk_duration_ms

    def get_tts_info(self) -> Dict[str, Any]:
        """Get TTS engine information.

        Returns:
            Dictionary with engine info
        """
        return {
            "model": self.config.model_name,
            "sample_rate": self.sample_rate,
            "gpu_enabled": self.config.gpu,
            "chunk_size_ms": self.config.chunk_size_ms,
        }


class AudioBufferQueue:
    """Thread-safe audio buffer for streaming playback."""

    def __init__(self, max_chunks: int = 10):
        """Initialize audio buffer.

        Args:
            max_chunks: Maximum chunks to buffer
        """
        self.queue: queue.Queue = queue.Queue(maxsize=max_chunks)
        self.lock = threading.Lock()

    def put_chunk(self, chunk: TTSAudioChunk, timeout: float = 5.0):
        """Add audio chunk to buffer.

        Args:
            chunk: Audio chunk to buffer
            timeout: Timeout in seconds

        Raises:
            queue.Full: If buffer full
        """
        try:
            self.queue.put(chunk, timeout=timeout)
        except queue.Full:
            raise StreamingTTSError("Audio buffer full - playback too slow")

    def get_chunk(self, timeout: float = 2.0) -> Optional[TTSAudioChunk]:
        """Retrieve next audio chunk.

        Args:
            timeout: Timeout in seconds

        Returns:
            Audio chunk or None if timeout
        """
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def clear(self):
        """Clear all buffered chunks."""
        with self.lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except queue.Empty:
                    break

    def size(self) -> int:
        """Get number of chunks in buffer."""
        return self.queue.qsize()


class StreamingTTSPipeline:
    """Complete streaming TTS pipeline with buffering and timing."""

    def __init__(self, config: Optional[TTSConfig] = None):
        """Initialize pipeline.

        Args:
            config: TTS configuration
        """
        self.engine = StreamingTTSEngine(config)
        self.buffer = AudioBufferQueue()
        self._synthesis_thread = None
        self._is_running = False

    def synthesize_to_buffer(
        self,
        text: str,
        prosody_plan: Any,
    ) -> None:
        """Synthesize audio in background thread, buffering chunks.

        Args:
            text: Text to synthesize
            prosody_plan: Prosody plan from prosody_planner
        """
        def _synthesize():
            try:
                for chunk in self.engine.stream_synthesis(text, prosody_plan):
                    self.buffer.put_chunk(chunk)
            except Exception as e:
                # Put error marker
                self.buffer.put_chunk(
                    TTSAudioChunk(
                        audio_data=np.array([]),
                        duration_ms=0,
                        start_time_ms=0,
                        is_final=True
                    )
                )

        # Start synthesis in background
        self._is_running = True
        self._synthesis_thread = threading.Thread(
            target=_synthesize, daemon=True)
        self._synthesis_thread.start()

    def get_audio_stream(self) -> Generator[TTSAudioChunk, None, None]:
        """Get streaming audio chunks.

        Yields:
            Audio chunks as they become available
        """
        while self._is_running:
            chunk = self.buffer.get_chunk(timeout=3.0)

            if chunk is None:
                # Timeout - synthesis may have stalled
                break

            yield chunk

            if chunk.is_final:
                self._is_running = False
                break

    def wait_completion(self, timeout: float = 30.0) -> bool:
        """Wait for synthesis to complete.

        Args:
            timeout: Timeout in seconds

        Returns:
            True if completed, False if timeout
        """
        if self._synthesis_thread:
            self._synthesis_thread.join(timeout=timeout)
            return not self._synthesis_thread.is_alive()
        return True

    def get_info(self) -> Dict[str, Any]:
        """Get pipeline information."""
        return {
            "engine": self.engine.get_tts_info(),
            "buffer_size": self.buffer.size(),
            "running": self._is_running,
        }


def export_audio_chunks_to_bytes(
    chunks: list,
    sample_rate: int = 22050,
) -> bytes:
    """Combine audio chunks into WAV format bytes.

    Args:
        chunks: List of TTSAudioChunk objects
        sample_rate: Sample rate in Hz

    Returns:
        WAV file as bytes
    """
    if not HAS_SOUNDFILE:
        raise StreamingTTSError(
            "soundfile not installed. Run: pip install soundfile"
        )

    # Concatenate all audio
    audio_parts = [chunk.audio_data for chunk in chunks if len(
        chunk.audio_data) > 0]

    if not audio_parts:
        raise StreamingTTSError("No audio chunks to export")

    audio = np.concatenate(audio_parts)

    # Write to bytes buffer
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format='WAV')
    buffer.seek(0)
    return buffer.read()


if __name__ == "__main__":
    # Example usage
    print("Streaming TTS module loaded successfully")

    if HAS_TTS:
        print("✓ TTS library available")

        # Create a test prosody plan (mock)
        class MockProsodyPlan:
            speaking_rate = 1.1
            pitch_shift_semitones = 1
            energy_level = 1.0

        engine = StreamingTTSEngine()
        print(f"✓ TTS engine initialized: {engine.get_tts_info()}")
    else:
        print("✗ TTS library not available (install with: pip install TTS)")
