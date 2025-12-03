"""
Streamlit app entry point (root directory shim).

This file serves as the entry point for Streamlit, which expects main_v2.py
to be in the root directory. It imports and executes the actual application
from core/main_v2.py.

This wrapper was created to maintain backward compatibility with the existing
Streamlit deployment while reorganizing the codebase into a modular structure
(Phase 8-11 reorganization).
"""

import core.main_v2 as _core_main
import sys
from pathlib import Path

# Ensure parent directory is in path for imports
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Import the core module

# Execute the main application
# This ensures the __name__ == "__main__" block in core/main_v2.py is executed
if __name__ == "__main__":
    _core_main.main()
