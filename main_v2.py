"""Main entry point for the streamlit FirstPerson app."""

from emotional_os.deploy.modules.ui import render_main_app, render_splash_interface, delete_user_history_from_supabase
from emotional_os.deploy.modules.auth import SaoynxAuthentication
import streamlit as st
from pathlib import Path
import os
import base64

# Must be first Streamlit command
st.set_page_config(
    page_title="FirstPerson - Personal AI Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['theme'] = 'Light'
    st.session_state['theme_loaded'] = False

    # Initialize learning persistence
    st.session_state['learning_settings'] = {
        'processing_mode': 'hybrid',  # Default to hybrid mode
        'enable_learning': True,      # Enable learning by default
        'persist_learning': True      # Enable persistence by default
    }

    # Create learning directories if they don't exist
    os.makedirs('learning/user_signals', exist_ok=True)
    os.makedirs('learning/user_overrides', exist_ok=True)
    os.makedirs('learning/conversation_glyphs', exist_ok=True)


# Customize navigation text
st.markdown("""
    <style>
    div.st-emotion-cache-j7qwjs span.st-emotion-cache-6tkfeg {
        visibility: hidden;
        position: relative;
    }
    
    div.st-emotion-cache-j7qwjs span.st-emotion-cache-6tkfeg::before {
        visibility: visible;
        position: absolute;
        content: "FirstPerson - Emotional AI Companion";
        left: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Apply theme only if not already loaded for this session
if not st.session_state.get('theme_loaded'):
    if st.session_state.get('theme') == 'Dark':
        st.markdown("""
            <style>
            body, .stApp {background-color: #0E1117; color: #FAFAFA;}
            .stButton>button {
                background-color: #262730;
                color: #FAFAFA;
                border: 1px solid #555;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            body, .stApp {background-color: #FFFFFF; color: #31333F;}
            .stButton>button {
                background-color: #F0F2F6;
                color: #31333F;
                border: 1px solid #E0E0E0;
            }
            </style>
        """, unsafe_allow_html=True)
    st.session_state['theme_loaded'] = True

# Basic theme compatibility
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {color: inherit;}
    .stMarkdown {color: inherit;}
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

# Optional local preprocessor (privacy-first steward)
try:
    from local_inference.preprocessor import Preprocessor
    PREPROCESSOR_AVAILABLE = True
except Exception:
    Preprocessor = None
    PREPROCESSOR_AVAILABLE = False

# Optional limbic integration (safe import)
try:
    from emotional_os.glyphs.limbic_integration import LimbicIntegrationEngine
    HAS_LIMBIC = True
except Exception:
    LimbicIntegrationEngine = None
    HAS_LIMBIC = False


def main():
    """Main application entry point."""
    # Initialize authentication
    auth = SaoynxAuthentication()

    # Check if user is authenticated
    if st.session_state.get('authenticated', False):
        render_main_app()
    else:
        render_splash_interface(auth)


if __name__ == "__main__":
    main()
