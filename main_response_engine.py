"""
Compatibility shim for main_response_engine.

After modularization (Phase 8), main_response_engine.py was moved from root to core/.
This shim maintains backward compatibility for imports.

Use: from main_response_engine import process_user_input
or:  from core.main_response_engine import process_user_input
"""

from core.main_response_engine import *

__all__ = [
    "process_user_input",
    "ResponseEngine",
    "generate_response",
    "extract_emotional_context",
]
