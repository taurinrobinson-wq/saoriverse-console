"""Legacy `core.phase_modulator` compatibility shim.

This small adapter re-exports `detect_phase` from the top-level
`src.phase_modulator` module so older imports like
`from core.phase_modulator import detect_phase` continue to work.
"""

from ..phase_modulator import detect_phase  # noqa: F401

__all__ = ["detect_phase"]
