"""Speech-to-Text and Audio Pipeline

Handles audio input, transcription, and preprocessing for the voice interface.
All processing is local (Whisper.cpp) - no API calls for privacy and speed.
"""

import io
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, AsyncGenerator
import tempfile

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    # Using faster-whisper for local inference
    # Install: pip install faster-whisper
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class AudioProcessor:
    """Handles audio preprocessing and feature extraction."""

    @staticmethod
    def load_audio(audio_bytes: bytes, sr: int = 16000) -> Tuple[np.ndarray, int]:
        """
        Load audio from bytes.

        Args:
            audio_bytes: Audio file bytes (WAV, MP3, etc.)
            sr: Target sample rate (16kHz is optimal for Whisper)

        Returns:
            (audio_array, sample_rate)
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError(
                "librosa required for audio loading. Install: pip install librosa")

        try:
            # Load from bytes buffer
            audio_buffer = io.BytesIO(audio_bytes)
            y, sr_loaded = librosa.load(audio_buffer, sr=sr, mono=True)
            return y, sr
        except Exception as e:
            raise ValueError(f"Failed to load audio: {e}")

    @staticmethod
    def normalize_audio(audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normalize audio to target loudness level.

        Args:
            audio: Audio waveform
            target_db: Target loudness in dB

        Returns:
            Normalized audio array
        """
        # Calculate current RMS
        rms = np.sqrt(np.mean(audio ** 2))

        if rms == 0:
            return audio

        # Convert target_db to linear scale
        target_linear = 10 ** (target_db / 20.0)

        # Apply scaling
        normalized = audio * (target_linear / rms)

        # Soft clip to prevent distortion
        normalized = np.tanh(normalized)

        return normalized

    @staticmethod
    def extract_vad_mask(audio: np.ndarray, sr: int = 16000,
                         energy_threshold: float = 0.02) -> np.ndarray:
        """
        Simple Voice Activity Detection using energy thresholding.

        Args:
            audio: Audio waveform
            sr: Sample rate
            energy_threshold: Energy threshold for speech detection

        Returns:
            Boolean mask (True = voice activity, False = silence)
        """
        # Frame-based energy calculation
        frame_length = int(sr * 0.02)  # 20ms frames
        hop_length = frame_length // 2

        # Calculate frame energies
        energies = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            energy = np.sqrt(np.mean(frame ** 2))
            energies.append(energy)

        # Threshold
        mean_energy = np.mean(energies)
        threshold = mean_energy * energy_threshold

        vad_mask = np.array(energies) > threshold

        # Smooth with median filter
        from scipy import signal
        vad_mask = signal.medfilt(vad_mask.astype(float), kernel_size=3)

        return vad_mask > 0.5

    @staticmethod
    def trim_silence(audio: np.ndarray, sr: int = 16000,
                     threshold_db: float = -40.0) -> np.ndarray:
        """
        Trim leading and trailing silence from audio.

        Args:
            audio: Audio waveform
            sr: Sample rate
            threshold_db: Threshold in dB below maximum

        Returns:
            Trimmed audio
        """
        if not LIBROSA_AVAILABLE:
            return audio

        try:
            trimmed, _ = librosa.effects.trim(
                audio,
                top_db=-threshold_db,
                ref=np.max
            )
            return trimmed
        except Exception:
            return audio


class SpeechToText:
    """Local STT using Whisper (faster-whisper for speed)."""

    def __init__(self, model_size: str = "base",
                 device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize Whisper STT engine.

        Args:
            model_size: Model size ("tiny", "base", "small", "medium", "large")
                       Larger = better accuracy but slower
                       Recommend "base" for real-time (~100ms)
            device: "cpu" or "cuda"
            compute_type: "int8", "int16", "float16", "float32"
                         int8 = fastest, float32 = most accurate
        """
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "faster-whisper required for STT. "
                "Install: pip install faster-whisper"
            )

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        # Load model (downloaded on first use, ~140MB for base)
        try:
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                download_root=Path.home() / ".cache" / "whisper"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")

        self.audio_processor = AudioProcessor()

    def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> dict:
        """
        Transcribe audio to text.

        Args:
            audio_bytes: Audio file bytes
            language: Language code (e.g., "en", "es"). 
                     Auto-detect if None.

        Returns:
            {
                "text": "transcribed text",
                "language": "en",
                "confidence": 0.95,
                "duration": 5.2,
            }
        """
        try:
            # Load and preprocess audio
            audio, sr = self.audio_processor.load_audio(audio_bytes)
            audio = self.audio_processor.normalize_audio(audio)
            audio = self.audio_processor.trim_silence(audio)

            # Transcribe
            segments, info = self.model.transcribe(
                audio,
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0.0,  # Deterministic
            )

            # Collect all text
            full_text = " ".join([segment.text for segment in segments])

            # Calculate average confidence
            confidences = [segment.confidence for segment in segments]
            avg_confidence = np.mean(confidences) if confidences else 0.5

            return {
                "text": full_text.strip(),
                "language": info.language,
                "confidence": float(avg_confidence),
                "duration": info.duration,
                "segments": [
                    {
                        "text": seg.text,
                        "start": seg.start,
                        "end": seg.end,
                        "confidence": seg.confidence,
                    }
                    for seg in segments
                ]
            }

        except Exception as e:
            return {
                "text": "",
                "language": "unknown",
                "confidence": 0.0,
                "duration": 0.0,
                "error": str(e),
            }

    async def transcribe_streaming(self,
                                   audio_generator: AsyncGenerator[bytes, None],
                                   language: Optional[str] = None):
        """
        Transcribe streaming audio chunks.
        Useful for real-time transcription as user speaks.

        Args:
            audio_generator: Async generator yielding audio bytes
            language: Optional language code

        Yields:
            Partial transcription results as they become available
        """
        # Buffer audio chunks
        audio_buffer = io.BytesIO()
        chunk_count = 0

        try:
            async for chunk in audio_generator:
                audio_buffer.write(chunk)
                chunk_count += 1

                # Every N chunks (e.g., 10 chunks ≈ 1 second of audio at 16kHz)
                if chunk_count % 10 == 0:
                    audio_buffer.seek(0)
                    result = self.transcribe(audio_buffer.getvalue(), language)

                    if result.get("text"):
                        yield {
                            "partial": True,
                            "text": result["text"],
                            "confidence": result["confidence"],
                        }

                    # Don't clear buffer - Whisper needs context

        except Exception as e:
            yield {
                "error": str(e),
                "text": "",
            }

        # Final transcription
        audio_buffer.seek(0)
        result = self.transcribe(audio_buffer.getvalue(), language)
        yield {
            "partial": False,
            "text": result["text"],
            "confidence": result["confidence"],
            "duration": result["duration"],
        }


class AudioPipeline:
    """Complete audio input pipeline."""

    def __init__(self):
        """Initialize audio pipeline."""
        self.stt = SpeechToText(model_size="base")  # Fast + accurate balance
        self.audio_processor = AudioProcessor()

    def process_user_audio(self, audio_bytes: bytes) -> dict:
        """
        Full processing pipeline for user audio input.

        Args:
            audio_bytes: Raw audio bytes from user

        Returns:
            {
                "transcribed_text": "what user said",
                "confidence": 0.95,
                "duration": 5.2,
                "vad_mask": [T/F array of voice activity],
            }
        """
        try:
            # Load and preprocess
            audio, sr = self.audio_processor.load_audio(audio_bytes)
            audio = self.audio_processor.normalize_audio(audio)

            # Extract VAD for analysis
            vad_mask = self.audio_processor.extract_vad_mask(audio, sr)

            # Trim silence for cleaner input
            audio_trimmed = self.audio_processor.trim_silence(audio)

            # Convert back to bytes for transcription
            import soundfile as sf
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, audio_trimmed, sr, format='WAV')
            audio_buffer.seek(0)

            # Transcribe
            result = self.stt.transcribe(audio_buffer.getvalue())

            # Enrich with VAD data
            result["vad_mask"] = vad_mask.tolist()  # For visualization
            result["vad_ratio"] = float(
                np.sum(vad_mask) / len(vad_mask))  # % of audio with voice

            return result

        except Exception as e:
            return {
                "error": str(e),
                "transcribed_text": "",
                "confidence": 0.0,
            }

    def estimate_emotion_from_audio_metadata(self, audio_bytes: bytes) -> dict:
        """
        Quick emotion estimation from audio characteristics before full analysis.
        Useful for quick feedback to user.

        Args:
            audio_bytes: Raw audio bytes

        Returns:
            {
                "estimated_arousal": 0.6,  # Based on speech rate, energy
                "speech_rate": 150,  # words per minute estimate
                "energy_level": 0.7,  # normalized loudness
                "pitch_range": "normal",  # based on frequency spread
            }
        """
        try:
            audio, sr = self.audio_processor.load_audio(audio_bytes)

            # Estimate speech rate from zero-crossings
            # (quick proxy; not accurate but fast)
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio))
            estimated_wpm = int(100 + (zcr * 200))  # Rough estimate

            # Energy level
            rms = np.sqrt(np.mean(audio ** 2))
            energy_normalized = np.clip(rms * 10, 0, 1)  # Normalize to 0-1

            # Pitch range (frequency analysis)
            if LIBROSA_AVAILABLE:
                S = np.abs(librosa.stft(audio))
                freqs = librosa.fft_frequencies(sr=sr)
                magnitude = np.mean(S, axis=1)
                centroid = np.sum(freqs * magnitude) / np.sum(magnitude)

                if centroid < 150:
                    pitch_range = "low"
                elif centroid > 250:
                    pitch_range = "high"
                else:
                    pitch_range = "normal"
            else:
                pitch_range = "unknown"

            # Arousal estimate
            arousal = (estimated_wpm / 200) * 0.5 + (energy_normalized * 0.5)
            arousal = np.clip(arousal, 0, 1)

            return {
                "estimated_arousal": float(arousal),
                "speech_rate_wpm": estimated_wpm,
                "energy_level": float(energy_normalized),
                "pitch_range": pitch_range,
            }

        except Exception as e:
            return {
                "error": str(e),
                "estimated_arousal": 0.5,
            }
