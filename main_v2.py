"""
Streamlit app entry point (root directory shim).

This file serves as the entry point for Streamlit, which expects main_v2.py
to be in the root directory. It simply imports and runs the actual application
from core/main_v2.py.

This wrapper was created to maintain backward compatibility with the existing
Streamlit deployment while reorganizing the codebase into a modular structure
(Phase 8-11 reorganization).
"""

import sys
from pathlib import Path

# Ensure parent directory is in path for imports
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Import and run the actual app
from core.main_v2 import *  # noqa: F401, F403
