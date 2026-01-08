"""Speech Interface Package

Handles all voice I/O including STT, TTS, and prosody planning.
"""

from .audio_pipeline import (
    AudioPipeline,
    SpeechToText,
    AudioProcessor,
)

from .audio_input import (
    render_audio_input_widget,
    render_audio_visualization,
    render_transcription_status,
    render_audio_settings,
    render_voice_message_preview,
    render_audio_errors,
    AudioStreamHandler,
)

__all__ = [
    "AudioPipeline",
    "SpeechToText",
    "AudioProcessor",
    "render_audio_input_widget",
    "render_audio_visualization",
    "render_transcription_status",
    "render_audio_settings",
    "render_voice_message_preview",
    "render_audio_errors",
    "AudioStreamHandler",
]
