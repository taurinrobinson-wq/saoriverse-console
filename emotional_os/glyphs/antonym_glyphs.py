"""Top-level shim to expose `emotional_os.glyphs.antonym_glyphs` during tests.

Loads the implementation from `src/emotional_os_glyphs/antonym_glyphs.py`.
This is a temporary compatibility shim to unblock pytest collection.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
candidate = ROOT / "src" / "emotional_os_glyphs" / "antonym_glyphs.py"

if candidate.exists():
    spec = importlib.util.spec_from_file_location("emotional_os_glyphs.antonym_glyphs", str(candidate))
    module = importlib.util.module_from_spec(spec)
    src_dir = str(ROOT / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    loader = spec.loader  # type: ignore
    loader.exec_module(module)
    for name in dir(module):
        if not name.startswith("_"):
            globals()[name] = getattr(module, name)
    sys.modules.setdefault("emotional_os_glyphs.antonym_glyphs", module)
else:
    # Minimal fallback
    def get_all_antonym_glyphs():
        return []

    def find_antonym_by_emotion(name):
        return None

    __all__ = ["get_all_antonym_glyphs", "find_antonym_by_emotion"]
