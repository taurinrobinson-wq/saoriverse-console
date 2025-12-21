"""Compatibility shim exposing relational memory helpers at `core.relational_memory`.

For legacy imports, forward to the authoritative top-level `relational_memory`
module so callers and tests share a single in-memory store instance.
"""

from relational_memory import (
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
