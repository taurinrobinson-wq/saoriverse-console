import pytest
from scripts import local_integration


def test_get_processing_mode():
    mode = local_integration.get_processing_mode()
    assert isinstance(mode, str)
    # Expect local by default; tests should allow explicit local-only mode
    assert mode == "local" or mode.isidentifier()


def test_get_synonyms_no_error():
    # Should not raise even if DB isn't present; returns a list
    res = local_integration.get_synonyms("joy", top_k=3)
    assert isinstance(res, list)
    for item in res:
        assert isinstance(item, dict)
        assert 'word' in item
        assert 'source' in item
