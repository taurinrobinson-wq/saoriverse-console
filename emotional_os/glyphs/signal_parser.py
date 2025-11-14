"""Backward compatibility stub - imports from canonical emotional_os.core

This module re-exports the public API from `emotional_os.core.signal_parser`.
Tests and some legacy code also reach into a few internal helpers (prefixed
with an underscore). Importing via `from ... import *` does not bring
underscore-prefixed names into the local module namespace, so re-export the
small set of internal helpers that tests rely on explicitly.
"""
from emotional_os.core.signal_parser import *  # noqa: F401, F403
# Re-export a few internal helpers for backward compatibility / tests
from emotional_os.core.signal_parser import _looks_like_artifact
