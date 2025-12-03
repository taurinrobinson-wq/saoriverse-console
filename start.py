"""
Railway deployment entry point (root directory shim).

This file serves as the entry point for Railway deployment, which was
originally configured to run start.py from the root directory. It imports
and executes the actual application from core/start.py.

This wrapper was created to maintain backward compatibility with the existing
Railway deployment while reorganizing the codebase into a modular structure
(Phase 8-11 reorganization).
"""

import core.start as _core_start
import sys
from pathlib import Path

# Ensure parent directory is in path for imports
root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Re-export the main function for imports
main = _core_start.main

# Execute the main application
# This ensures the __name__ == "__main__" block in core/start.py is executed
if __name__ == "__main__":
    main()
