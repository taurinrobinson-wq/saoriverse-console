"""Feedback persistence adapter.

Expose `append_feedback` and `append_conversation` functions that use a
shared persistence implementation when available, otherwise fall back to
the local `tools.feedback_store` implementation.
"""
from __future__ import annotations

import logging
logger = logging.getLogger(__name__)


def _import_shared():
    try:
        from emotional_os.persistence import append_feedback as af, append_conversation as ac
        return af, ac
    except Exception:
        return None, None


def _import_tools():
    try:
        from tools.feedback_store import append_feedback as af, append_conversation as ac
        return af, ac
    except Exception:
        # older path: tools folder may be on sys.path so try relative import
        try:
            from feedback_store import append_feedback as af2, append_conversation as ac2
            return af2, ac2
        except Exception:
            return None, None


_shared_af, _shared_ac = _import_shared()
_tools_af, _tools_ac = _import_tools()


def append_feedback(entry: dict):
    """Persist feedback entry via preferred backend."""
    if _shared_af:
        try:
            return _shared_af(entry)
        except Exception as e:
            logger.debug("Shared append_feedback failed: %s", e)
    if _tools_af:
        try:
            return _tools_af(entry)
        except Exception as e:
            logger.debug("Tools append_feedback failed: %s", e)
    # last-resort: write nothing but avoid raising
    logger.debug("No feedback persistence available; dropping feedback entry.")


def append_conversation(entry: dict):
    """Persist conversation entry via preferred backend."""
    if _shared_ac:
        try:
            return _shared_ac(entry)
        except Exception as e:
            logger.debug("Shared append_conversation failed: %s", e)
    if _tools_ac:
        try:
            return _tools_ac(entry)
        except Exception as e:
            logger.debug("Tools append_conversation failed: %s", e)
    logger.debug("No conversation persistence available; dropping conversation entry.")
