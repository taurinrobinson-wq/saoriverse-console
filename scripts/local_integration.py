"""Local-only integration helpers.

Provides small wrappers so the app can use local-only processing without
depending on remote AI services. This module is safe to import in tests.
"""

import os
import types
from typing import Dict, List


def get_processing_mode() -> str:
    """Return the processing mode to use by default.

    Priority: environment variable `PROCESSING_MODE`, otherwise `local`.
    """
    return os.environ.get("PROCESSING_MODE", "local")


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


def remote_ai_allowed() -> bool:
    """Return True when remote AI calls are allowed.

    Policy:
    - If `get_processing_mode()` is not 'local', allow remote AI.
    - Otherwise only allow if env var `ALLOW_REMOTE_AI` is set to '1'.
    """
    # Enforce local-only policy by default. Return False to indicate
    # remote AI calls are not allowed unless code explicitly opts in
    # via `ALLOW_REMOTE_AI` env var. This removes hybrid selection logic
    # and makes local-only behavior the default.
    return os.environ.get("ALLOW_REMOTE_AI", "0") == "1"


def remote_ai_error(msg: str = None):
    """Raise a RuntimeError describing that remote AI is disabled.

    This helper centralizes the error message so callers can raise a consistent
    error when an API that would call external services is invoked while the
    repository is configured to run local-only.
    """
    default = (
        "Remote AI calls are disabled (processing mode 'local'). "
        "Set PROCESSING_MODE to a non-local value or set ALLOW_REMOTE_AI=1 to opt in."
    )
    raise RuntimeError(msg or default)


def enforce_local_mode_guard():
    """Fail-fast guard: if running in local mode and an OpenAI key is present,
    raise a RuntimeError. This makes accidental use of remote AI loudly visible.

    Callers: executed at module import to enforce policy early.
    """
    try:
        mode = get_processing_mode()
    except Exception:
        mode = os.environ.get("PROCESSING_MODE", "local")

    if mode == "local" and os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY present while PROCESSING_MODE='local'. "
            "Remove the key or set PROCESSING_MODE to a non-local value to allow remote AI."
        )


# Enforce guard at import time so local-first violations are visible immediately.
enforce_local_mode_guard()


def create_local_integration():
    """Factory that returns a small local-only integration namespace.

    This provides the same basic helpers but makes it explicit that this
    integration is local-only. Callers can import this factory and use
    the returned object in place of a hybrid/local selector.
    """
    return types.SimpleNamespace(
        get_processing_mode=get_processing_mode,
        get_synonyms=get_synonyms,
        remote_ai_allowed=remote_ai_allowed,
        remote_ai_error=remote_ai_error,
    )
