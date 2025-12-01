"""Package marker for scripts to avoid top-level module name collisions.

This file intentionally left minimal — presence ensures imports within
`scripts` are treated as package imports (e.g., `scripts.utilities.*`).
"""

__all__ = []
