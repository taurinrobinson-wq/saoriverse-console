"""Local-only integration helpers.

Provides small wrappers so the app can use local-only processing without
depending on remote AI services. This module is safe to import in tests.
"""
import os
from typing import List, Dict


def get_processing_mode() -> str:
    """Return the processing mode to use by default.

    Priority: environment variable `PROCESSING_MODE`, otherwise `local`.
    """
    return os.environ.get('PROCESSING_MODE', 'local')


def get_synonyms(seed: str, top_k: int = 5) -> List[Dict]:
    """Return top synonyms for `seed` from local SQLite DB if available.

    Falls back to an empty list if the DB or query helper is not present.
    Each item is a dict: {'word': str, 'score': float|None, 'source': str}
    """
    try:
        from scripts.synonym_db import query_synonyms
    except Exception:
        return []

    try:
        return query_synonyms(seed, top_k)
    except Exception:
        return []
