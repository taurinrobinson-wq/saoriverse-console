"""Compatibility shim for legacy phase module imports.

Tests and other modules may import from phase_modulator. This shim ensures
backward compatibility by re-exporting from the archive location.
"""

from archive.phase_infrastructure.phase_modulator import detect_phase  # noqa: F401

__all__ = ["detect_phase"]
