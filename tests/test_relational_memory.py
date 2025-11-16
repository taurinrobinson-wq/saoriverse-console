import os
import tempfile

from relational_memory import RelationalMemoryCapsule, store_capsule, list_recent, save_store, load_store


def test_store_and_list():
    # ensure store is usable
    c = RelationalMemoryCapsule(
        ["initiatory_signal"], "initiatory", "ΔV↑↑", "hi", "summary")
    store_capsule(c)
    recent = list_recent(1)
    assert recent and recent[0].response_summary == "summary"


def test_save_and_load(tmp_path):
    path = tmp_path / "capsules.json"
    c = RelationalMemoryCapsule(
        ["anchoring_signal"], "archetypal", "ΔV↔", "hello", "sum")
    store_capsule(c)
    save_store(str(path))
    # clear in-memory store by reloading module-level variable via loading twice
    load_store(str(path))
    assert path.exists()
