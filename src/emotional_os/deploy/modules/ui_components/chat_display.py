"""
Chat Display Component.

Renders message history, empty state, and chat input interface.
Handles message rendering with processing metadata.
"""

import os
import streamlit as st
import logging

logger = logging.getLogger(__name__)


def render_chat_container(conversation_key: str):
    """Render the main chat display container.

    Shows message history or empty state. Used as container for
    displaying user/assistant exchanges.

    Args:
        conversation_key: Session state key for conversation history
    """
    # Center the chat area
    cols_center = st.columns([1, 6, 1])
    chat_container = cols_center[1].container()

    with chat_container:
        # Show empty state if no messages yet
        if not st.session_state.get(conversation_key):
            _render_empty_state()
        else:
            # Display all message exchanges
            for exchange in st.session_state.get(conversation_key, []):
                if isinstance(exchange, dict):
                    with st.chat_message("user"):
                        st.write(exchange.get("user", ""))

                    with st.chat_message("assistant"):
                        st.write(exchange.get("assistant", ""))

                        # Show processing metadata if available
                        if "processing_time" in exchange:
                            _show_processing_info(exchange)

    return chat_container


def _render_empty_state():
    """Render placeholder when no messages exist yet."""
    try:
        st.markdown(
            "<div style='color:var(--jp-ui-font-color2, #6b7280); padding:12px; "
            "border-radius:8px; background: rgba(0,0,0,0.02);'>"
            "Your conversation will appear here after you send your first message."
            "</div>",
            unsafe_allow_html=True,
        )
    except Exception:
        try:
            st.info(
                "Your conversation will appear here after you send your first message.")
        except Exception as e:
            logger.debug(f"Error rendering empty state: {e}")


def _show_processing_info(exchange: dict):
    """Show processing time and mode caption for exchange.

    Args:
        exchange: Message exchange dict with metadata
    """
    try:
        processing_time = exchange.get("processing_time", "0.00s")
        mode = exchange.get("mode", "unknown")

        show_mode = (
            os.environ.get("FP_SHOW_PROCESSING_MODE") == "1" or
            st.session_state.get("show_processing_mode", False)
        )

        caption_text = f"Processed in {processing_time}"
        if show_mode:
            caption_text += f" • Mode: {mode}"

        st.caption(caption_text)

    except Exception as e:
        logger.debug(f"Error showing processing info: {e}")


def render_chat_input() -> tuple:
    """Render chat input area with file uploader.

    Returns:
        Tuple of (user_input, uploaded_file) or (None, None) if no input
    """
    try:
        left_col, input_col, right_col = st.columns([1, 6, 1])

        # File uploader
        uploaded_file = None
        with left_col:
            try:
                st.markdown(
                    """
                    <style>
                    [data-testid="stFileUploaderDropzone"] {
                        border: none !important;
                        background: none !important;
                        padding: 0 !important;
                    }
                    [data-testid="stFileUploaderDropzoneInstructions"] {
                        display: none !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                uploaded_file = st.file_uploader(
                    "Browse Files",
                    label_visibility="collapsed",
                    type=["txt", "docx", "pdf", "md", "html",
                          "htm", "csv", "xlsx", "xls", "json"],
                    key="inline_uploader",
                )
            except Exception as e:
                logger.debug(f"Error rendering file uploader: {e}")

        # Chat input
        with input_col:
            user_input = st.chat_input("Share what you're feeling...")

        return user_input, uploaded_file

    except Exception as e:
        logger.debug(f"Error rendering chat input: {e}")
        # Fallback to simple input
        return st.chat_input("Share what you're feeling..."), None


def display_user_message(user_input: str):
    """Display user message in chat.

    Args:
        user_input: User's message text
    """
    with st.chat_message("user"):
        st.write(user_input)


def display_assistant_message(response: str) -> st.container:
    """Display assistant message in chat.

    Args:
        response: Assistant's response text

    Returns:
        Container for additional content (loading spinner, etc.)
    """
    container = st.chat_message("assistant")
    with container:
        st.write(response)
        
        # Synthesize audio if voice mode is enabled
        if st.session_state.get("voice_mode_enabled"):
            try:
                from .audio_ui import synthesize_response_audio, render_audio_playback
                from .glyph_handler import get_best_glyph
                from .response_handler import get_debug_info
                
                # Get glyph info for prosody guidance
                debug_info = get_debug_info()
                glyphs = debug_info.get("glyphs", [])
                best_glyph = get_best_glyph(glyphs) if glyphs else None
                glyph_name = best_glyph.get("glyph_name", "") if best_glyph else ""
                
                # Synthesize audio
                audio_bytes = synthesize_response_audio(
                    response,
                    glyph_name=glyph_name,
                    voice="Default",
                    speed=1.0
                )
                
                if audio_bytes:
                    render_audio_playback(audio_bytes, label="🔊 Listen to response")
                    st.session_state["last_audio_output"] = audio_bytes
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Audio synthesis error: {e}")
    
    return container


def show_processing_spinner():
    """Show loading spinner during response processing."""
    return st.spinner("Processing your emotional input...")
