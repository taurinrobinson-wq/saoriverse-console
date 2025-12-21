"""Top-level `parser` package loader that exposes submodules from
the authoritative `src/parser` implementation.

This loader preloads a small set of submodules used during test
collection so imports like `parser.tonecore_pipeline` resolve to the
files under `src/parser` rather than any top-level copies.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src" / "parser"

# Prefer the src/parser directory as the package path
__path__ = [str(SRC_DIR)]

def _load_src_submodule(module_name: str):
    path = SRC_DIR / f"{module_name}.py"
    if not path.exists():
        raise ImportError(f"No module named parser.{module_name}")
    spec = importlib.util.spec_from_file_location(f"parser.{module_name}", str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    sys.modules[f"parser.{module_name}"] = module
    return module

# Preload commonly-imported submodules so pytest collection finds them.
for _m in ("tonecore_pipeline", "signal_parser"):
    _load_src_submodule(_m)

