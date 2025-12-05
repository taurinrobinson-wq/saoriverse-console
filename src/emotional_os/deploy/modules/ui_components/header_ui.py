"""
Header UI Component.

Renders main header including logo, title, and welcome banner.
Handles both authenticated and demo mode displays.
"""

import os
import streamlit as st
import logging
from ..utils import load_svg

logger = logging.getLogger(__name__)


def render_demo_banner():
    """Render informational banner for demo mode users."""
    try:
        pkg_logo = os.path.join(
            os.path.dirname(__file__),
            "..",
            "static",
            "graphics",
            "FirstPerson-Logo-invert-cropped_notext.svg",
        )

        if os.path.exists(pkg_logo):
            c1, c2, c3 = st.columns([1, 0.6, 1])
            with c2:
                try:
                    st.image(pkg_logo, width=64)
                except Exception:
                    svg_markup = load_svg(
                        "FirstPerson-Logo-invert-cropped_notext.svg")
                    st.markdown(
                        f"<div style='width:64px;margin:0 auto'>{svg_markup}</div>",
                        unsafe_allow_html=True,
                    )
        else:
            svg_markup = load_svg("FirstPerson-Logo-invert-cropped_notext.svg")
            st.markdown(
                f"<div style='width:64px;margin:0 auto'>{svg_markup}</div>",
                unsafe_allow_html=True,
            )

        st.info(
            "Running in demo mode, register or sign in in the sidebar to enable "
            "persistence and full features."
        )

    except Exception as e:
        try:
            st.info(
                "Running in demo mode, register or sign in in the sidebar to enable "
                "persistence and full features."
            )
        except Exception:
            logger.debug(f"Error rendering demo banner: {e}")


def render_welcome_message():
    """Render welcome message for authenticated users."""
    try:
        display_name = st.session_state.get(
            "first_name") or st.session_state.get("username")
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(f"Welcome back, **{display_name}**! 👋")

    except Exception as e:
        logger.debug(f"Error rendering welcome message: {e}")


def render_post_login_confirmation():
    """Render confirmation card after successful login."""
    try:
        if not (st.session_state.get("authenticated") and
                st.session_state.get("post_login_transition")):
            return

        msg = st.session_state.get(
            "post_login_message", "Signed in successfully")
        c1, c2, c3 = st.columns([1, 2, 1])

        with c2:
            st.markdown(
                f"<div style='padding:16px;border-radius:10px;background:#f0fff4;"
                f"border:1px solid #d1f7d8;text-align:center;font-weight:600;'>"
                f"✅ {msg}</div>",
                unsafe_allow_html=True,
            )

        # Small pause
        import time
        try:
            time.sleep(1.0)
        except Exception:
            pass

        # Clear flags and rerun
        st.session_state.pop("post_login_transition", None)
        st.session_state.pop("post_login_message", None)
        st.rerun()

    except Exception as e:
        logger.debug(f"Error rendering post-login confirmation: {e}")
