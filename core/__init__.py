"""Top-level compatibility package for legacy `core` imports.

This package re-exports key helpers from the `src` layout so older
imports like `from core.phase_modulator import detect_phase` work during
tests and local development.
"""

from .phase_modulator import detect_phase  # re-export for convenience

__all__ = ["detect_phase"]
