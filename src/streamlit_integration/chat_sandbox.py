"""Streamlit integration wrapper for the Learning Sandbox UI.

This module adapts the tools/streamlit_chat_ui sandbox into the
`src`/`emotional_os` runtime by attempting to reuse shared
session initialization (when available) and then delegating to the
sandbox implementation to avoid duplicating logic.
"""
from __future__ import annotations

import logging
import streamlit as st

try:
    # Prefer shared initialization when available to reduce duplication
    from emotional_os.deploy.modules.ui_components import initialize_session_state
except Exception:
    initialize_session_state = None

try:
    # Import the sandbox implementation (keeps the heavy UI code in one place)
    from tools import streamlit_chat_ui as sandbox
except Exception:
    sandbox = None

logger = logging.getLogger(__name__)


def main():
    """Adapter main entrypoint for Streamlit hosting in `src`.

    Behavior:
    - If `emotional_os` shared initializer exists, call it to align
      `st.session_state` keys with the rest of the FirstPerson app.
    - Delegate to the sandbox UI in `tools/streamlit_chat_ui.py` to
      render the learning sandbox interface.
    """
    if initialize_session_state:
        try:
            initialize_session_state()
        except Exception as e:
            logger.debug("Shared initialize_session_state failed: %s", e)

    if sandbox is None:
        st.error("Sandbox UI not available (tools.streamlit_chat_ui import failed).")
        return

    # Call sandbox main. The sandbox module already manages its own
    # st.session_state keys; the adapter ensures we tried to align with
    # shared session structures first.
    try:
        sandbox.main()
    except Exception as e:
        logger.exception("Error running sandbox UI: %s", e)
        st.error("Failed to start Learning Sandbox UI. See logs for details.")


if __name__ == "__main__":
    main()
