"""Compatibility shim exposing `detect_phase` at `core.phase_modulator`.

This module forwards to `src.phase_modulator` which itself re-exports the
implementation from the archive location.
"""

from src.phase_modulator import detect_phase  # noqa: F401

__all__ = ["detect_phase"]
