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


def render_main_header():
    """Render the main page header with logo and title."""
    if st.session_state.get("header_rendered"):
        return

    try:
        col1, col2, col3 = st.columns([0.5, 8, 2], gap="small")

        with col1:
            _render_header_logo()

        with col2:
            st.markdown(
                '<h1 style="margin: 0; margin-left: -35px; padding-top: 10px; '
                'color: #2E2E2E; font-weight: 300; letter-spacing: 2px; font-size: 2.2rem;">'
                "FirstPerson - Personal AI Companion"
                "</h1>",
                unsafe_allow_html=True,
            )

        with col3:
            # Show NLP warmup status
            nlp_status = st.session_state.get("nlp_status_message", "")
            if nlp_status:
                st.caption(nlp_status)

        st.session_state["header_rendered"] = True

    except Exception as e:
        logger.debug(f"Error rendering header: {e}")


def _render_header_logo():
    """Render logo in header (package-local or fallback)."""
    try:
        logo_file = "FirstPerson-Logo-normalized.svg"
        pkg_path = os.path.join(os.path.dirname(
            __file__), "..", "static", "graphics", logo_file)
        repo_path = os.path.join("static", "graphics", logo_file)

        if os.path.exists(pkg_path):
            st.image(pkg_path, width=24)
        elif os.path.exists(repo_path):
            st.image(repo_path, width=24)
        else:
            raise FileNotFoundError

    except Exception:
        # Fallback to emoji
        try:
            st.markdown(
                '<div style="font-size: 2.5rem; margin: 0; line-height: 1;">🧠</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            logger.debug(f"Error rendering header logo fallback: {e}")


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
