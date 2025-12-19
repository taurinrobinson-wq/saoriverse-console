"""DraftShift package - legal tone analysis and transformations.

This package contains the DraftShift implementation (formerly `litone`).
Import modules from this package directly, e.g. `from DraftShift import core`.
"""

try:
    from .core import (
        detect_tone,
        shift_tone,
        split_sentences,
        classify_sentence_structure,
        assess_overall_message,
        get_tool_status,
    )
    __all__ = [
        "detect_tone",
        "shift_tone",
        "split_sentences",
        "classify_sentence_structure",
        "assess_overall_message",
        "get_tool_status",
    ]
except ImportError:
    __all__ = []

# Make submodules available for explicit import
from . import (
    constants,
    enhanced_affect_parser,
    tone_analysis_composer,
    tone_signal_parser,
)

__version__ = "1.1.0"
__author__ = "DraftShift Team"
