"""
Railway deployment entry point (root directory shim).

This file serves as the entry point for Railway deployment, which was
originally configured to run start.py from the root directory. It simply
imports and runs the actual application from core/start.py.

This wrapper was created to maintain backward compatibility with the existing
Railway deployment while reorganizing the codebase into a modular structure
(Phase 8-11 reorganization).
"""

import sys
from pathlib import Path

# Ensure parent directory is in path for imports
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Import and run the actual app
from core.start import *  # noqa: F401, F403
