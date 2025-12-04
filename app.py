"""
FirstPerson - Personal AI Companion
Minimal working Streamlit entry point
"""

import sys
import os
from pathlib import Path

import streamlit as st

# Page config
try:
    logo_path = Path("static/graphics/FirstPerson-Logo-invert-cropped_notext.svg")
    page_icon = None
    if logo_path.exists():
        try:
            page_icon = logo_path.read_bytes()
        except Exception:
            page_icon = None
    
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon=page_icon if page_icon is not None else "🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def render_logo():
    """Display FirstPerson logo"""
    try:
        logo_path = Path("static/graphics/FirstPerson-Logo-invert-cropped_notext.svg")
        if logo_path.exists():
            with open(logo_path, "r") as f:
                svg_content = f.read()
                st.image(str(logo_path), width=150)
                return
    except Exception:
        pass
    st.markdown("# 🧠 FirstPerson")


def render_splash():
    """Render authentication splash"""
    st.markdown("# FirstPerson - Personal AI Companion")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_logo()
    
    with col2:
        st.markdown("""
        An advanced emotional AI system designed to understand, respond to, and learn from your unique emotional landscape.
        
        ### Features
        - 🎯 Emotional signal detection
        - 💭 Context-aware responses  
        - 🧬 Adaptive learning
        - 🔒 Privacy-first design
        """)
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Login", "Demo Mode"])
    
    with tab1:
        st.subheader("Sign In")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Sign In", key="login_btn"):
            if username and password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_id = f"user_{username}"
                st.session_state.demo_mode = False
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Please enter both username and password")
    
    with tab2:
        st.info("Try FirstPerson in demo mode with pre-loaded examples")
        if st.button("Enter Demo Mode", key="demo_btn", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.username = "Demo User"
            st.session_state.user_id = "demo_user"
            st.session_state.demo_mode = True
            st.session_state.conversation_history = [
                {"role": "user", "content": "I've been feeling overwhelmed lately"},
                {"role": "assistant", "content": "I hear you. Overwhelm is a signal that something needs attention. Let's explore what's happening beneath that feeling. What's taking the most bandwidth right now?", "metadata": "demo"},
            ]
            st.success("Entering demo mode...")
            st.rerun()


def render_main_app():
    """Render the main authenticated application"""
    
    # Sidebar
    with st.sidebar:
        render_logo()
        st.markdown("---")
        
        if st.session_state.demo_mode:
            st.info("📌 Demo Mode")
        else:
            st.success(f"✅ {st.session_state.username}")
        
        st.markdown("---")
        
        page = st.radio(
            "Navigate:",
            ["Chat", "Glyphs", "Journal", "Settings"],
            key="main_nav"
        )
        
        st.markdown("---")
        
        if st.button("Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.session_state.conversation_history = []
            st.session_state.demo_mode = False
            st.rerun()
    
    # Main content
    if page == "Chat":
        st.markdown("# 💬 Chat")
        
        # Display conversation
        for msg in st.session_state.conversation_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if "metadata" in msg:
                    st.caption(msg["metadata"])
        
        # Chat input
        user_input = st.chat_input("What's on your mind?")
        
        if user_input:
            # Add user message
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate response (try to use real pipeline if available)
            response = None
            metadata = ""
            
            try:
                from src.response_generator import process_user_input
                result = process_user_input(user_input)
                if result:
                    response = result
                    metadata = "AI-generated"
            except Exception as e:
                response = None
            
            # Fallback response
            if not response:
                response = f"I hear you: '{user_input}'. I'm processing this emotionally and will respond more fully as the system initializes."
                metadata = "system initializing"
            
            # Add assistant message
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": response,
                "metadata": metadata
            })
            
            st.rerun()
    
    elif page == "Glyphs":
        st.markdown("# ✨ Emotional Glyphs")
        st.info("Glyphs are emotional signatures detected in your messages")
        
        if st.session_state.conversation_history:
            st.markdown("### Detected Patterns")
            st.write("Glyph detection system initializing...")
    
    elif page == "Journal":
        st.markdown("# 📓 Journal")
        
        entry = st.text_area(
            "Write your reflection:",
            placeholder="Share what's emerging for you...",
            height=200,
            key="journal_entry"
        )
        
        if st.button("Save Entry"):
            if entry:
                st.session_state.conversation_history.append({
                    "role": "journal",
                    "content": entry,
                    "metadata": "journal entry"
                })
                st.success("Entry saved")
            else:
                st.error("Please write something")
    
    else:  # Settings
        st.markdown("# ⚙️ Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Preferences")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], key="theme_pref")
            tone = st.selectbox("Tone", ["Warm", "Professional", "Playful", "Meditative"], key="tone_pref")
        
        with col2:
            st.subheader("Processing")
            mode = st.selectbox("Mode", ["Local", "Hybrid", "Cloud"], key="mode_pref")
            save_history = st.checkbox("Save History", value=True, key="save_hist")
        
        st.markdown("---")
        if st.button("Clear History"):
            st.session_state.conversation_history = []
            st.success("History cleared")


def main():
    """Main entry point"""
    if not st.session_state.authenticated:
        render_splash()
    else:
        render_main_app()


if __name__ == "__main__":
    main()
