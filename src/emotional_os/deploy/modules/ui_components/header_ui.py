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
    """Render the main page header with logo only."""
    if st.session_state.get("header_rendered"):
        return

    try:
        # Center the logo
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            _render_header_logo()
        
        # Reduce spacing within divider
        st.markdown(
            "<style>div[data-testid='stVerticalBlockContainer'] { gap: 0.5rem; }</style>",
            unsafe_allow_html=True,
        )

        st.session_state["header_rendered"] = True

    except Exception as e:
        logger.debug(f"Error rendering header: {e}")


def _render_header_logo():
    """Render logo in header from FirstPerson-Logo_cropped.svg."""
    try:
        logo_file = "FirstPerson-Logo_cropped.svg"
        pkg_path = os.path.join(os.path.dirname(
            __file__), "..", "static", "graphics", logo_file)
        repo_path = os.path.join("static", "graphics", logo_file)

        if os.path.exists(pkg_path):
            st.image(pkg_path, width=140)
        elif os.path.exists(repo_path):
            st.image(repo_path, width=140)
        else:
            raise FileNotFoundError

    except Exception:
        # Fallback to emoji
        try:
            st.markdown(
                '<div style="font-size: 3rem; margin: 0 auto; text-align: center; line-height: 1;">🧠</div>',
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
    """Render welcome message for authenticated users with logo header."""
    try:
        display_name = st.session_state.get(
            "first_name") or st.session_state.get("username")
        
        # Display logo at top
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            _render_welcome_logo()
        st.markdown("---")
        
        # Welcome message below logo
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(f"Welcome back, **{display_name}**! 👋")

    except Exception as e:
        logger.debug(f"Error rendering welcome message: {e}")


def _render_welcome_logo():
    """Render FirstPerson logo in welcome section."""
    try:
        # Try to load logo from the expected location
        logo_path = os.path.join(
            os.path.dirname(__file__),
            "../../../deploy_modules/static/graphics/FirstPerson-Logo_cropped.svg"
        )
        
        # Normalize the path
        logo_path = os.path.normpath(logo_path)
        
        if os.path.exists(logo_path):
            with open(logo_path, 'r') as f:
                svg_content = f.read()
            st.markdown(
                f"<div style='text-align:center;margin:20px 0;'>"
                f"<img src='data:image/svg+xml;base64,{__get_base64_svg(svg_content)}' "
                f"style='height:120px;'/></div>",
                unsafe_allow_html=True,
            )
        else:
            # Fallback: just show the text
            logger.debug(f"Logo not found at {logo_path}")
            
    except Exception as e:
        logger.debug(f"Error rendering welcome logo: {e}")


def __get_base64_svg(svg_content: str) -> str:
    """Convert SVG content to base64 for embedding."""
    import base64
    return base64.b64encode(svg_content.encode()).decode()


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
