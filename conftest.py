import sys
from pathlib import Path

# Prepend the repo root and `src/` directories to sys.path so pytest import
# collection resolves package imports to the project's source layout.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# Ensure the repository root is first so top-level loaders (e.g., `parser`)
# execute and can preload submodules into `sys.modules` if needed.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Then add `src/` so `src` packages are importable as top-level modules.
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(1, str(SRC))

# If a stale `parser` entry exists, clear it so imports are deterministic.
if "parser" in sys.modules:
    for key in list(sys.modules.keys()):
        if key == "parser" or key.startswith("parser."):
            del sys.modules[key]

# Attempt to import the top-level `parser` package so its loader runs and
# registers `parser.<submodule>` entries (the loader maps to `src/parser`).
try:
    import parser as _parser  # noqa: F401
except Exception:
    # If importing fails, allow pytest to continue and fail with clearer
    # import errors later during test collection.
    pass
