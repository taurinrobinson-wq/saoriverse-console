"""Audio module - STT, TTS, and voice UI components.

This module provides:
- Audio input pipeline (speech-to-text)
- Audio output pipeline (text-to-speech)
- UI components for voice interaction
"""

from .audio_pipeline import AudioProcessor, SpeechToText, AudioPipeline
from .streaming_tts import (
    StreamingTTSEngine,
    StreamingTTSPipeline,
    ProsodyApplier,
    TTSConfig,
)

__all__ = [
    "AudioProcessor",
    "SpeechToText",
    "AudioPipeline",
    "StreamingTTSEngine",
    "StreamingTTSPipeline",
    "ProsodyApplier",
    "TTSConfig",
]
