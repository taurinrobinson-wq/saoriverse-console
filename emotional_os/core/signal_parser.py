"""Top-level shim for `emotional_os.core.signal_parser`.

This minimal shim provides `parse_input` and a few helpers so tests
can import the symbol during collection. It intentionally avoids
pulling in the full implementation to prevent circular imports.
"""
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Signal:
    keyword: str
    signal: str


def parse_input(text: str, **kwargs) -> Dict[str, Any]:
    return {"input_text": text, "signals": [], "glyphs": []}


def parse_signals(text: str) -> List[Signal]:
    return []


def load_signal_map(*a, **k):
    return {}


def fetch_glyphs(*a, **k):
    return []


def evaluate_gates(*a, **k):
    return {}


__all__ = [
    "parse_input",
    "parse_signals",
    "load_signal_map",
    "fetch_glyphs",
    "evaluate_gates",
]
