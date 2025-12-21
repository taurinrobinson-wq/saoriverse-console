"""Parser package initializer.

Ensure `parser.tonecore_pipeline` is available from the package namespace
and expose its public symbols. Use a local relative import so the package
resolves to `src/parser` consistently.
"""
from .tonecore_pipeline import *  # noqa: F401,F403

__all__ = [
	"ToneCorePipeline",
	"SignalParserOutput",
	"NRCOutput",
	"TextBlobOutput",
	"SpacyOutput",
	"MergedEmotionalData",
	"ChordProgression",
	"get_pipeline",
	"analyze_text",
	"generate_chord_progression",
]
