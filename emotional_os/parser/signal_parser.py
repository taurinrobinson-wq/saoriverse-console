"""Compatibility shim: expose parser APIs under emotional_os.parser namespace.
This module re-exports the core parsing functions from the glyphs signal parser
so older imports (emotional_os.parser.signal_parser) continue to work.
"""

from emotional_os.glyphs.signal_parser import (
    evaluate_gates,
    fetch_glyphs,
    generate_contextual_response,
    load_signal_map,
    parse_input,
    parse_signals,
    select_best_glyph_and_response,
)

__all__ = [
    'parse_input', 'parse_signals', 'evaluate_gates', 'fetch_glyphs',
    'select_best_glyph_and_response', 'generate_contextual_response', 'load_signal_map'
]
