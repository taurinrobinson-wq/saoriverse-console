"""TheVillage package.

Standalone experimental architecture for a persistent internal model with
state, goals, subsystems, vocabulary learning, embodiment, and narrative.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from TheVillage.core.mind import TheVillageEngine, get_or_create_engine, reset_engine


__all__ = ["TheVillageEngine", "get_or_create_engine", "reset_engine"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module("TheVillage.core.mind")
        return getattr(module, name)
    raise AttributeError(f"module 'TheVillage' has no attribute {name!r}")