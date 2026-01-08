"""Bridge for `emotional_os.learning.archetype_response_generator_v2`.

Re-exports the implementation from `emotional_os_learning.archetype_response_generator_v2`
when available; provides a minimal fallback otherwise.
"""
from importlib import import_module

try:
    mod = import_module("emotional_os_learning.archetype_response_generator_v2")
    ArchetypeResponseGeneratorV2 = getattr(mod, "ArchetypeResponseGeneratorV2")
    __all__ = ["ArchetypeResponseGeneratorV2"]
except Exception as exc:  # pragma: no cover - fail loudly for tests
    raise ImportError(
        "Missing required implementation: emotional_os_learning.archetype_response_generator_v2"
    ) from exc
