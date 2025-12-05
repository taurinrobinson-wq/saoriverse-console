"""
Sidebar UI Component.

Renders sidebar with authentication, conversation list, settings,
preferences, and consent controls.
"""

import os
import uuid
import datetime
import streamlit as st
import logging
from ..utils import load_svg, inject_sidebar_constraints

logger = logging.getLogger(__name__)


def render_sidebar():
    """Render the complete sidebar with all controls."""
    with st.sidebar:
        # Constrain sidebar width
        try:
            inject_sidebar_constraints()
        except Exception:
            pass

        # Render based on authentication status
        if not st.session_state.get("authenticated"):
            _render_demo_sidebar()
        else:
            _render_authenticated_sidebar()


def _render_demo_sidebar():
    """Render sidebar for unauthenticated demo users."""
    try:
        # Account panel
        try:
            svg_markup = load_svg("FirstPerson-Logo-black-cropped_notext.svg")
            st.markdown(
                f'<div style="border:1px solid rgba(0,0,0,0.06); padding:12px; '
                f'border-radius:12px; background: rgba(250,250,250,0.02); text-align:center;">\n'
                f'<div style="width:96px; margin:0 auto;">{svg_markup}</div>\n'
                f'<p style="margin:8px 0 6px 0; font-weight:600;">Demo mode</p>\n'
                f'</div>',
                unsafe_allow_html=True,
            )
        except Exception:
            st.markdown("### Account")

        st.markdown("<div style='margin-top:16px;'></div>",
                    unsafe_allow_html=True)
        st.markdown(
            "**Create an Account** or **Sign In** to keep your conversations and enable full features.")

        # Auth buttons
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Sign in", key="sidebar_toggle_sign_in"):
                st.session_state["sidebar_show_login"] = not st.session_state.get(
                    "sidebar_show_login", False
                )
                if st.session_state["sidebar_show_login"]:
                    st.session_state["sidebar_show_register"] = False

        with col_b:
            if st.button("Create an Account", key="sidebar_toggle_register"):
                st.session_state["sidebar_show_register"] = not st.session_state.get(
                    "sidebar_show_register", False
                )
                if st.session_state["sidebar_show_register"]:
                    st.session_state["sidebar_show_login"] = False

        # Quick demo entry if available
        try:
            from ..auth import SaoynxAuthentication
            auth = SaoynxAuthentication()
            if hasattr(auth, "quick_login_bypass"):
                if st.button("Continue in demo", key="sidebar_continue_demo"):
                    try:
                        auth.quick_login_bypass()
                    except Exception:
                        st.session_state.authenticated = False
                        st.rerun()
        except Exception:
            pass

        st.markdown("---")

        # Render auth expanders
        _render_auth_expanders()

    except Exception as e:
        logger.debug(f"Error rendering demo sidebar: {e}")


def _render_authenticated_sidebar():
    """Render sidebar for authenticated users."""
    try:
        # Display logo at top of sidebar
        try:
            logo_file = "FirstPerson-Logo_cropped.svg"
            pkg_path = os.path.join(os.path.dirname(__file__), "..", "static", "graphics", logo_file)
            repo_path = os.path.join("static", "graphics", logo_file)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if os.path.exists(pkg_path):
                    st.image(pkg_path, width=120)
                elif os.path.exists(repo_path):
                    st.image(repo_path, width=120)
        except Exception as e:
            logger.debug(f"Error rendering sidebar logo: {e}")
        
        st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
        
        st.markdown("### Settings")

        # Persist history toggle
        persist_default = st.session_state.get("persist_history", True)
        st.session_state["persist_history"] = st.checkbox(
            "💾 Save my chats",
            value=persist_default,
            help="Automatically save conversations for later retrieval",
        )

        # Save preference to server
        try:
            mgr = st.session_state.get("conversation_manager")
            if mgr:
                mgr.save_user_preferences({
                    "persist_history": bool(st.session_state.get("persist_history", False)),
                    "persist_confirmed": bool(st.session_state.get("persist_confirmed", False)),
                })
        except Exception as e:
            logger.debug(f"Error saving preferences: {e}")

        # Consent settings
        try:
            from ..consent_ui import render_consent_settings_panel
            render_consent_settings_panel()
        except ImportError:
            pass
        except Exception as e:
            st.warning(f"Consent settings error: {e}")

        st.markdown("---")

        # Conversation management
        _render_conversation_list()

    except Exception as e:
        logger.debug(f"Error rendering authenticated sidebar: {e}")


def _render_conversation_list():
    """Render list of previous conversations."""
    try:
        from ..conversation_manager import (
            load_all_conversations_to_sidebar,
        )

        mgr = st.session_state.get("conversation_manager")
        if mgr:
            load_all_conversations_to_sidebar(mgr)

        # New conversation button
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state["current_conversation_id"] = str(uuid.uuid4())
            st.session_state["conversation_title"] = "New Conversation"
            st.session_state.pop("selected_conversation", None)

            # Initialize empty history
            from .session_manager import get_conversation_key
            key = get_conversation_key()
            st.session_state[key] = []

            # Cache new conversation
            try:
                cid = st.session_state["current_conversation_id"]
                cached = st.session_state.setdefault(
                    "session_cached_conversations", [])
                if not any(c.get("conversation_id") == cid for c in cached):
                    cached.insert(0, {
                        "conversation_id": cid,
                        "title": "New Conversation",
                        "updated_at": datetime.datetime.now().isoformat(),
                        "message_count": 0,
                        "processing_mode": st.session_state.get("processing_mode", "local"),
                    })
            except Exception:
                pass

            st.rerun()

    except Exception as e:
        logger.debug(f"Error rendering conversation list: {e}")


def _render_auth_expanders():
    """Render authentication form expanders in sidebar."""
    try:
        if st.session_state.get("sidebar_show_login"):
            with st.expander("Sign in", expanded=True):
                try:
                    from ..auth import SaoynxAuthentication
                    auth = SaoynxAuthentication()
                    auth.render_login_form(in_sidebar=True)
                except Exception as e:
                    logger.debug(f"Login form error: {e}")
                    st.error("Authentication subsystem unavailable")

        if st.session_state.get("sidebar_show_register"):
            with st.expander("", expanded=True):
                try:
                    st.markdown(
                        '<div style="text-align:center; font-weight:700; '
                        'font-size:1.02rem; margin-bottom:8px;">Create an Account</div>',
                        unsafe_allow_html=True,
                    )
                except Exception:
                    st.markdown("**Create an Account**")

                try:
                    from ..auth import SaoynxAuthentication
                    auth = SaoynxAuthentication()
                    auth.render_register_form(in_sidebar=True)
                except Exception as e:
                    logger.debug(f"Register form error: {e}")
                    st.error("Authentication subsystem unavailable")

    except Exception as e:
        logger.debug(f"Error rendering auth expanders: {e}")


def render_settings_sidebar():
    """Render Settings expander in sidebar (legacy - now in authenticated_sidebar)."""
    try:
        from .session_manager import ensure_processing_prefs

        try:
            ensure_processing_prefs()
        except Exception:
            pass

        with st.sidebar.expander("⚙️ Settings", expanded=False):
            st.markdown("**Interface & Processing**")

            # Processing mode is fixed to local
            try:
                st.markdown("**Processing:** Local-only (remote AI disabled)")
                st.session_state["processing_mode"] = "local"
            except Exception:
                st.session_state.setdefault("processing_mode", "local")

            # Theme selection
            current_theme = st.session_state.get(
                "theme_select_row",
                st.session_state.get("theme", "Light")
            )

            def _on_theme_change():
                st.session_state["theme"] = st.session_state.get(
                    "theme_select_row", current_theme
                )
                st.session_state["theme_loaded"] = False

            st.selectbox(
                "Theme",
                options=["Light", "Dark"],
                index=0 if current_theme == "Light" else 1,
                key="theme_select_row",
                help="Choose the UI theme (Light or Dark)",
                on_change=_on_theme_change,
            )

            # Mirror theme into older key
            st.session_state["theme"] = st.session_state.get(
                "theme_select_row", "Light"
            )
            st.session_state["theme_loaded"] = False

    except Exception as e:
        logger.debug(f"Error rendering settings sidebar: {e}")
