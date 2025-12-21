"""Compatibility shim exposing relational memory helpers at `core.relational_memory`.

For legacy imports, forward to the implementation in `src.relational_memory`.
"""

from src.relational_memory import (
    RelationalMemoryCapsule,
    store_capsule,
    retrieve_capsule_by_tag,
    list_recent,
    save_store,
    load_store,
)

__all__ = [
    "RelationalMemoryCapsule",
    "store_capsule",
    "retrieve_capsule_by_tag",
    "list_recent",
    "save_store",
    "load_store",
]
