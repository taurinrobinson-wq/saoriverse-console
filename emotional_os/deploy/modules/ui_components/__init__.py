"""
UI Components Module.

High-level orchestration of UI components including session management,
response handling, and display rendering.
"""

# Session management
from .session_manager import (
    initialize_session_state,
    load_conversation_manager,
    migrate_demo_to_auth,
    get_conversation_key,
    ensure_conversation_history,
    get_conversation_context,
    add_exchange_to_history,
    get_session_summary,
)

# Header and branding
from .header_ui import (
    render_demo_banner,
    render_welcome_message,
)

# Sidebar
from .sidebar_ui import (
    render_sidebar,
    render_settings_sidebar,
)

# Chat display
from .chat_display import (
    render_chat_container,
    render_chat_input,
    display_user_message,
    display_assistant_message,
    show_processing_spinner,
)

# Response processing
from .response_handler import (
    handle_response_pipeline,
    strip_prosody_metadata,
    get_debug_info,
)

# Glyph handling
from .glyph_handler import (
    extract_glyphs_from_analysis,
    get_best_glyph,
    display_glyph_info,
    display_activated_glyphs,
    display_debug_panel,
)

# Theme management
from .theme_manager import (
    apply_theme,
    get_current_theme,
)

# Document processing
from .document_processor import (
    process_uploaded_file,
    display_document_info,
    store_document_in_session,
)

# Learning and evolution
from .learning_tracker import (
    initialize_learning_system,
    process_learning_exchange,
    display_learning_progress,
    handle_dynamic_evolution,
)

# Journal
from .journal_center import (
    render_journal_center,
)

# Audio (voice input/output)
try:
    from .audio_ui import (
        render_voice_mode_toggle,
        render_audio_recorder,
        render_audio_playback,
        render_voice_chat_interface,
        process_audio_input,
        synthesize_response_audio,
        initialize_voice_session,
    )
except (ImportError, OSError) as e:
    # Audio libraries not available (e.g., PortAudio)
    # Provide dummy functions that warn users
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Audio components disabled: {e}")
    
    def render_voice_mode_toggle():
        import streamlit as st
        st.warning("⚠️ Audio features not available in this environment")
    
    def render_audio_recorder():
        return None
    
    def render_audio_playback(audio_data=None):
        pass
    
    def render_voice_chat_interface():
        import streamlit as st
        st.info("💬 Voice chat requires audio libraries (not installed)")
    
    def process_audio_input(audio_data):
        return None
    
    def synthesize_response_audio(text):
        return None
    
    def initialize_voice_session():
        pass

__all__ = [
    # Session
    "initialize_session_state",
    "load_conversation_manager",
    "migrate_demo_to_auth",
    "get_conversation_key",
    "ensure_conversation_history",
    "get_conversation_context",
    "add_exchange_to_history",
    "get_session_summary",
    # Header
    "render_demo_banner",
    "render_welcome_message",
    # Sidebar
    "render_sidebar",
    "render_settings_sidebar",
    # Chat
    "render_chat_container",
    "render_chat_input",
    "display_user_message",
    "display_assistant_message",
    "show_processing_spinner",
    # Response
    "handle_response_pipeline",
    "strip_prosody_metadata",
    "get_debug_info",
    # Glyphs
    "extract_glyphs_from_analysis",
    "get_best_glyph",
    "display_glyph_info",
    "display_activated_glyphs",
    "display_debug_panel",
    # Theme
    "apply_theme",
    "get_current_theme",
    # Documents
    "process_uploaded_file",
    "display_document_info",
    "store_document_in_session",
    # Learning
    "initialize_learning_system",
    "process_learning_exchange",
    "display_learning_progress",
    "handle_dynamic_evolution",
    # Journal
    "render_journal_center",
    # Audio/Voice
    "render_voice_mode_toggle",
    "render_audio_recorder",
    "render_audio_playback",
    "render_voice_chat_interface",
    "process_audio_input",
    "synthesize_response_audio",
    "initialize_voice_session",
]
