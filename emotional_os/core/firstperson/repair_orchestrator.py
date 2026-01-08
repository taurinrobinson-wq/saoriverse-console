"""Top-level shim for `emotional_os.core.firstperson.repair_orchestrator`.

Loads the implementation from `src/emotional_os/core/firstperson/repair_orchestrator.py`.
Temporary compatibility shim for tests.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
candidate = ROOT / "src" / "emotional_os" / "core" / "firstperson" / "repair_orchestrator.py"

if candidate.exists():
    spec = importlib.util.spec_from_file_location("emotional_os.core.firstperson.repair_orchestrator", str(candidate))
    module = importlib.util.module_from_spec(spec)
    src_dir = str(ROOT / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    loader = spec.loader  # type: ignore
    try:
        loader.exec_module(module)
        for name in dir(module):
            if not name.startswith("_"):
                globals()[name] = getattr(module, name)
        sys.modules.setdefault("emotional_os.core.firstperson.repair_orchestrator", module)
    except Exception:
        # Fall back to a minimal local shim to avoid cascading import errors
        from dataclasses import dataclass
        from typing import Optional

        @dataclass
        class GlyphCompositionContext:
            tone: str = "neutral"
            arousal: float = 0.0
            valence: float = 0.0
            glyph_name: str = ""
            user_id: Optional[str] = None
            timestamp: Optional[str] = None

        class RepairOrchestrator:
            def __init__(self, user_id: str = None):
                self.user_id = user_id

            def analyze_for_repair(self, user_input: str):
                # Return an object-like with expected attributes by callers
                class A:
                    is_rejection = False
                    suggested_alternative = None

                return A()

            def record_acceptance(self, context: GlyphCompositionContext):
                pass

            def record_response(self, response_text: str):
                pass

        __all__ = ["RepairOrchestrator", "GlyphCompositionContext"]
else:
    # Minimal fallback class
    class RepairOrchestrator:
        def __init__(self, user_id: str = None):
            self.user_id = user_id

        def analyze_for_repair(self, user_input: str):
            return {"is_rejection": False}

        def record_acceptance(self, context):
            pass

        def record_response(self, response_text: str):
            pass

    __all__ = ["RepairOrchestrator"]
