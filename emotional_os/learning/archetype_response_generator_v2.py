import importlib
import importlib.util
import os
import sys

__all__ = []

try:
    # Preferred: import the package if available on sys.path
    mod = importlib.import_module("emotional_os_learning.archetype_response_generator_v2")
except Exception:
    # Fallback: load directly from src path relative to repo root
    repo_root = os.getcwd()
    candidate = os.path.join(repo_root, "src", "emotional_os_learning", "archetype_response_generator_v2.py")
    if os.path.exists(candidate):
        spec = importlib.util.spec_from_file_location("emotional_os_learning.archetype_response_generator_v2", candidate)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
    else:
        # Last resort: try plain module name
        mod = importlib.import_module("emotional_os_learning.archetype_response_generator_v2")

# Re-export public names from the implementation module
for name, val in vars(mod).items():
    if not name.startswith("_"):
        globals()[name] = val
        __all__.append(name)
