"""
SaoriVerse Console - Emotional OS Core

This module exports all public APIs for use by UI layers (Streamlit, etc.)
"""

# Core emotional processing
try:
    from src.response_generator import process_user_input
except Exception:
    process_user_input = None

# Signal parsing
try:
    from src.signal_parser import parse_input, extract_themes
except Exception:
    parse_input = None
    extract_themes = None

# Response generation and composition
try:
    from src.enhanced_response_composer import DynamicResponseComposer
except Exception:
    DynamicResponseComposer = None

# Voice interface
try:
    from src.voice_interface import VoiceInterface
except Exception:
    VoiceInterface = None

# TTS/STT
try:
    from src.streaming_tts import StreamingTTS
except Exception:
    StreamingTTS = None

try:
    from src.audio_pipeline import AudioPipeline
except Exception:
    AudioPipeline = None

# Prosody and audio
try:
    from src.prosody_planner import ProsodyPlanner
except Exception:
    ProsodyPlanner = None

# Learning systems
try:
    from src.lexicon_learner import LexiconLearner
except Exception:
    LexiconLearner = None

# Memory and persistence
try:
    from src.relational_memory import RelationalMemoryCapsule, store_capsule
except Exception:
    RelationalMemoryCapsule = None
    store_capsule = None

__all__ = [
    "process_user_input",
    "parse_input",
    "extract_themes",
    "DynamicResponseComposer",
    "VoiceInterface",
    "StreamingTTS",
    "AudioPipeline",
    "ProsodyPlanner",
    "LexiconLearner",
    "RelationalMemoryCapsule",
    "store_capsule",
]
