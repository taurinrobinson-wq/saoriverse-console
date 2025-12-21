import sys
from pathlib import Path

# Prepend the repo `src/` directory to sys.path so pytest import collection
# resolves package imports to the project's source layout.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
    # If a stale top-level `parser` package was already imported earlier in
    # the process, remove it so subsequent imports resolve to `src/parser`.
    if "parser" in sys.modules:
        for key in list(sys.modules.keys()):
            if key == "parser" or key.startswith("parser."):
                del sys.modules[key]
