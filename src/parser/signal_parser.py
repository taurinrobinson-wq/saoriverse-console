"""Bridge module to provide `parser.signal_parser` API from the
emotional_os implementation.
"""
from emotional_os.core.signal_parser import load_signal_map, parse_signals

__all__ = ["load_signal_map", "parse_signals"]
