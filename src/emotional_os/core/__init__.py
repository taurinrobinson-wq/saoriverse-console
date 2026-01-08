"""Lightweight core package initializer.

Avoid importing heavy submodules at package-import time to prevent
cascading circular imports during test collection. Tests should import
submodules explicitly (e.g. `from emotional_os.core import signal_parser`).
"""

__all__ = []
