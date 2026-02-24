"""
Response Processing Pipeline.

Decomposed into three clean phases:
1. parse_phase - Extract signals, emotions, glyphs from user input
2. interpret_phase - Analyze context and orchestrate FirstPerson
3. generate_phase - Apply tiers, safety, synthesis, and generate final response

Each phase is independently testable and failures don't cascade.
"""

from .parse_phase import parse_input_signals
from .interpret_phase import interpret_emotional_context
from .generate_phase import generate_enhanced_response

__all__ = [
    "parse_input_signals",
    "interpret_emotional_context",
    "generate_enhanced_response",
]
