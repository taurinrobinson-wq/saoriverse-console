"""Compatibility shim

This module exists for backward compatibility. It delegates all public
symbols to the canonical implementation in
`emotional_os.core.signal_parser` so legacy imports use the full-featured
parser (fuzzy matching, NRC hooks, learned lexicon, DB-backed glyph lookup).

Keep this thin: re-export the canonical parser's public API.
"""

# keep module reference
from emotional_os.core import signal_parser as _core_signal_parser
from emotional_os.core.signal_parser import *  # noqa: F401, F403


# Backwards-compatible wrapper for `parse_signals`.
# The canonical parser returns a list of dicts with keys like
# {'keyword':..., 'signal':..., 'voltage':..., 'tone':...}.
# Older callers historically expected a list of signal identifiers
# (simple, hashable values). Provide a thin adapter preserving both
# behaviours: if the canonical returns dicts, map to the `'signal'`
# values; otherwise, return the canonical output unchanged.
def parse_signals_compat(input_text: str, signal_map):
    """Compatibility wrapper for parse_signals.

    Returns a list of signal identifiers (strings) when possible so
    legacy callers that expect hashable items (e.g., using `set()`)
    continue to work.
    """
    # Call canonical implementation from the core module directly
    raw = _core_signal_parser.parse_signals(input_text, signal_map)

    # If canonical returned dicts, extract 'signal' values
    out = []
    for item in raw:
        if isinstance(item, dict):
            sig = item.get("signal")
            if sig is not None:
                out.append(sig)
        else:
            # assume hashable scalar (string)
            out.append(item)

    return out


# Rebind the name `parse_signals` in this module to the compatibility wrapper
# so legacy imports like `from parser.signal_parser import parse_signals`
# will receive the adapted behaviour.
parse_signals = parse_signals_compat
