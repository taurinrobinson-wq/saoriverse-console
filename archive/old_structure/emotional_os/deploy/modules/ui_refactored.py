"""
FirstPerson - Personal AI Companion

Main Streamlit UI entry point after modularization.

This is the refactored orchestration layer that delegates to modular components.
Previously this file was 3,068 lines with mixed responsibilities.
Now it's focused on high-level routing and orchestration.
"""

from emotional_os.deploy.modules.utils import inject_defensive_scripts
from emotional_os.deploy.modules.ui_components import (
    initialize_session_state,
    get_conversation_key,
    ensure_conversation_history,
    get_conversation_context,
    add_exchange_to_history,
    load_conversation_manager,
    migrate_demo_to_auth,
    render_main_header,
    render_demo_banner,
    render_welcome_message,
    render_sidebar,
    render_chat_container,
    render_chat_input,
    show_processing_spinner,
    handle_response_pipeline,
    strip_prosody_metadata,
    apply_theme,
    process_uploaded_file,
    display_document_info,
    render_journal_center,
    initialize_learning_system,
    handle_dynamic_evolution,
    display_learning_progress,
)
import os
import datetime
import time
import streamlit as st
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import modularized components


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def delete_user_history_from_supabase(user_id: str) -> tuple:
    """Delete all persisted conversation history for a user from Supabase.

    Args:
        user_id: The user ID whose history should be deleted.

    Returns:
        A tuple (success: bool, message: str) indicating whether the deletion succeeded.
    """
    try:
        if requests is None:
            return False, "Network requests not available in this environment."

        supabase_url = st.secrets.get("supabase", {}).get("url")
        supabase_key = st.secrets.get("supabase", {}).get("key")

        if not supabase_url or not supabase_key:
            return False, "Supabase not configured. Cannot delete server history."

        # Call a Supabase function or use the REST API to delete user history
        # For now, we'll attempt a direct REST API call to a hypothetical endpoint
        delete_url = f"{supabase_url}/rest/v1/conversations?user_id=eq.{user_id}"

        response = requests.delete(
            delete_url,
            headers={
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            timeout=10,
        )

        if response.status_code in [200, 204, 404]:
            return True, "Server-side history deleted successfully."
        else:
            return False, f"Failed to delete history (HTTP {response.status_code})."
    except Exception as e:
        return False, f"Error deleting history: {str(e)}"


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

def _configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# ============================================================================
# AUTHENTICATION & SPLASH SCREEN
# ============================================================================

def render_splash_interface():
    """Render the authentication/welcome splash screen."""
    try:
        from emotional_os.deploy.modules.auth import SaoynxAuthentication

        auth = SaoynxAuthentication()
        auth.render_splash_interface()

    except ImportError:
        st.error("Authentication module not available")
    except Exception as e:
        logger.error(f"Error rendering splash: {e}")
        st.error("Welcome to FirstPerson. Please refresh the page.")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def render_app():
    """Render the main authenticated application."""
    try:
        # Apply theme (light/dark mode)
        apply_theme()

        # Initialize session state
        initialize_session_state()

        # Load conversation manager
        try:
            load_conversation_manager()
        except Exception as e:
            logger.debug(f"ConversationManager load failed: {e}")

        # Handle demo->auth migration
        try:
            migrate_demo_to_auth()
        except Exception as e:
            logger.debug(f"Demo migration failed: {e}")

        # Defensive DOM patches
        try:
            inject_defensive_scripts()
        except Exception:
            pass

        # ====== HEADER ======
        render_main_header()

        # Render demo banner if not authenticated
        if not st.session_state.get("authenticated"):
            render_demo_banner()
        else:
            render_welcome_message()

        # ====== SIDEBAR ======
        render_sidebar()

        # ====== MAIN CHAT AREA ======
        conversation_key = get_conversation_key()
        ensure_conversation_history()

        chat_container = render_chat_container(conversation_key)

        # ====== CHAT INPUT ======
        user_input, uploaded_file = render_chat_input()

        # Handle file upload
        if uploaded_file:
            try:
                file_text = process_uploaded_file(uploaded_file)
                if isinstance(file_text, str) and not file_text.startswith("Error"):
                    display_document_info(uploaded_file.name, file_text)
            except Exception as e:
                st.error(f"File processing error: {e}")

        # ====== PROCESS USER INPUT ======
        if user_input:
            with chat_container:
                # Show user message
                with st.chat_message("user"):
                    st.write(user_input)

                # Process response
                with st.chat_message("assistant"):
                    processing_mode = st.session_state.get(
                        "processing_mode", "local")

                    with show_processing_spinner():
                        try:
                            conversation_context = get_conversation_context()
                            response, processing_time = handle_response_pipeline(
                                user_input,
                                conversation_context,
                            )

                            # Display response
                            st.write(response)
                            st.caption(
                                f"Processed in {processing_time:.2f}s • Mode: {processing_mode}"
                            )

                        except Exception as e:
                            logger.error(f"Response processing failed: {e}")
                            st.error(
                                "Failed to process your message. Please try again.")
                            response = "I'm having trouble processing that right now. Could you try again?"
                            processing_time = 0

                    # Store exchange
                    try:
                        add_exchange_to_history(
                            user_input,
                            response,
                            metadata={
                                "processing_time": f"{processing_time:.2f}s",
                                "mode": processing_mode,
                                "timestamp": datetime.datetime.now().isoformat(),
                            },
                        )
                    except Exception as e:
                        logger.debug(f"Failed to store exchange: {e}")

                    # Run learning system if available
                    try:
                        from emotional_os.deploy.modules.ui_components import (
                            extract_glyphs_from_analysis,
                            get_debug_info,
                        )

                        # Get glyphs from last analysis
                        debug_info = get_debug_info()
                        glyphs = debug_info.get("glyphs", [])

                        # Process through learning
                        if st.session_state.get("processing_mode") in ("local", "hybrid"):
                            handle_dynamic_evolution(
                                user_input, response, glyphs)
                            display_learning_progress()

                    except Exception as e:
                        logger.debug(f"Learning system failed: {e}")

                    # Persist conversation
                    try:
                        mgr = st.session_state.get("conversation_manager")
                        if mgr and st.session_state.get("persist_history"):
                            conversation_id = st.session_state.get(
                                "current_conversation_id")
                            title = st.session_state.get(
                                "conversation_title", "New Conversation"
                            )
                            messages = st.session_state.get(
                                conversation_key, [])
                            mgr.save_conversation(
                                conversation_id, title, messages)

                    except Exception as e:
                        logger.debug(f"Conversation persistence failed: {e}")

            st.rerun()

        # ====== JOURNAL CENTER (if active) ======
        try:
            render_journal_center()
        except Exception as e:
            logger.debug(f"Journal center error: {e}")

    except Exception as e:
        logger.error(f"Application render error: {e}")
        st.error("An error occurred. Please refresh the page.")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main application entry point."""
    _configure_page()

    # Check authentication status
    if not st.session_state.get("authenticated"):
        render_splash_interface()
    else:
        render_app()


def render_main_app():
    """Main app interface for authenticated users - Full Emotional OS"""
    render_app()


def render_main_app_safe(*args, **kwargs):
    """Runtime-safe wrapper around render_main_app.

    Catches exceptions raised during rendering, writes a full traceback to
    `debug_runtime.log`, attempts to display a minimal error to the user,
    and then re-raises the exception so host-level logs capture it as well.
    """
    try:
        return render_main_app(*args, **kwargs)
    except Exception as e:
        import traceback
        from pathlib import Path as _Path

        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        try:
            _Path("debug_runtime.log").write_text(tb, encoding="utf-8")
        except Exception:
            # best-effort write
            pass

        try:
            # If Streamlit is usable, show a short excerpt to the user
            st.error(
                "A runtime error occurred; details have been written to debug_runtime.log")
            excerpt = "\n".join(tb.splitlines()[-12:])
            st.markdown(
                f"<pre style='white-space:pre-wrap'>{excerpt}</pre>", unsafe_allow_html=True)
        except Exception:
            # If Streamlit can't render, print to stdout for host logs
            print(tb)

        # Re-raise so hosting environment also records the traceback
        raise


if __name__ == "__main__":
    main()
