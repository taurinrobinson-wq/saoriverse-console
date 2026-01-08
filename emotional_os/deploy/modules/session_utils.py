"""Session utilities for service and Streamlit contexts.

Provide a small helper so service callers (FastAPI) can pass a
lightweight `session_override` dict-like object while Streamlit code
continues to use `st.session_state` as before.

Functions:
- get_session_value(session_override, key, default=None)

The helper is deliberately defensive and import-local to avoid
introducing Streamlit as a hard dependency for service processes.
"""
from typing import Any


def get_session_value(session_override: Any, key: str, default: Any = None) -> Any:
    """Return `key` from `session_override` if present, otherwise
    fall back to `streamlit.session_state` when available.

    This function never raises; on any error it returns `default`.
    """
    try:
        # Prefer explicit override (dict-like or object with attributes)
        if session_override is not None:
            try:
                return session_override.get(key, default)
            except Exception:
                try:
                    return getattr(session_override, key, default)
                except Exception:
                    return default

        # Avoid importing Streamlit at module import time in service
        # processes; import lazily and protect against missing/disabled
        # runtime.
        try:
            import streamlit as st
        except Exception:
            return default

        try:
            return st.session_state.get(key, default)
        except Exception:
            try:
                return getattr(st.session_state, key, default)
            except Exception:
                return default
    except Exception:
        return default
