"""
Theme Management Component.

Handles theme selection, application, and CSS injection.
Manages light/dark mode switching and preference persistence.
"""

import os
import logging
import streamlit as st
from ..utils import inject_svg_styling, inject_css

logger = logging.getLogger(__name__)


def apply_theme():
    """Apply current theme to the UI.

    Loads and injects theme CSS, logo styling, and ensures
    theme consistency across session.
    """
    try:
        # Ensure theme state exists
        current_theme = st.session_state.get("theme_select_row",
                                             st.session_state.get("theme", "Light"))

        # Only reload if needed
        if not st.session_state.get("theme_loaded"):
            _inject_theme_styles(current_theme)
            st.session_state["theme_loaded"] = True

    except Exception as e:
        logger.debug(f"Error applying theme: {e}")


def _inject_theme_styles(theme: str):
    """Inject theme-specific CSS.

    Args:
        theme: "Light" or "Dark"
    """
    try:
        if theme == "Dark":
            _inject_dark_theme()
        else:
            _inject_light_theme()

        # Always inject SVG styling
        try:
            inject_svg_styling()
        except Exception:
            pass

    except Exception as e:
        logger.debug(f"Error injecting theme styles: {e}")


def _inject_light_theme():
    """Inject light theme CSS."""
    try:
        st.markdown(
            """
            <style>
            :root { --accent-color: #5E60BA; }
            body, .main, .block-container {
                background: linear-gradient(180deg, #F5F5F5 0%, #FAFAFA 100%);
                color: #1F1F1F;
            }
            .stExpander, .stChatMessage, .stTextInput, .stSelectbox,
            .stTextArea, .stFileUploader {
                background-color: rgba(255, 255, 255, 0.9);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                border-radius: 8px;
            }
            .stButton>button {
                border-color: var(--accent-color);
            }
            .stButton>button:hover {
                background-color: var(--accent-color);
                color: #fff;
            }
            header[data-testid="stHeader"] {
                background: transparent !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.debug(f"Error injecting light theme: {e}")


def _inject_dark_theme():
    """Inject dark theme CSS."""
    try:
        st.markdown(
            """
            <style>
            :root { --accent-color: #A78BFA; }
            body, .main, .block-container {
                background: linear-gradient(180deg, #18191A 0%, #1F2023 100%);
                color: #E5E5E5;
            }
            .stExpander, .stChatMessage, .stTextInput, .stSelectbox,
            .stTextArea, .stFileUploader {
                background-color: rgba(35, 39, 47, 0.85);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(6px);
                border-radius: 8px;
                color: #EDEDED;
            }
            .stSelectbox>div>div, .stSelectbox>div>div>div,
            div[role="listbox"] {
                background: #000 !important;
                color: #fff !important;
                border-color: var(--accent-color) !important;
            }
            .stButton>button {
                border-color: var(--accent-color);
            }
            .stButton>button:hover {
                background-color: var(--accent-color);
                color: #18191A;
            }
            button[title*="Logout"], button[aria-label*="Logout"],
            button[title*="Log out"] {
                background-color: #fff;
                color: #000;
                border: 1px solid rgba(0,0,0,0.08);
            }
            header[data-testid="stHeader"] {
                background: #0F1113;
                color: #FFFFFF;
            }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
                font-weight: 500;
                color: #E5E5E5;
            }
            .brand-logo svg {
                filter: drop-shadow(0 0 6px #A78BFA);
            }
            .brand-logo svg path, .brand-logo svg circle {
                fill: #FFFFFF;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.debug(f"Error injecting dark theme: {e}")


def get_current_theme() -> str:
    """Get current theme selection.

    Returns:
        "Light" or "Dark"
    """
    return st.session_state.get("theme_select_row",
                                st.session_state.get("theme", "Light"))


def ensure_theme_consistency():
    """Ensure theme state is consistent across all keys."""
    current = get_current_theme()
    st.session_state["theme"] = current
    st.session_state["theme_select_row"] = current
