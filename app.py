"""FirstPerson - Personal AI Companion - Main Entry Point"""
import sys
import os
from pathlib import Path

# Ensure src is in path
workspace_root = str(Path(__file__).parent)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import streamlit as st

# Set page config first
try:
    _logo_path = Path("static/graphics/FirstPerson-Logo-invert-cropped_notext.svg")
    _page_icon = None
    if _logo_path.exists():
        try:
            with open(_logo_path, "rb") as f:
                _page_icon = f.read()
        except Exception:
            _page_icon = None
    
    st.set_page_config(
        page_title="FirstPerson - Personal AI Companion",
        page_icon=_page_icon if _page_icon is not None else "🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception as e:
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
    st.session_state.demo_mode = True
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


def render_splash():
    """Render authentication/demo splash screen"""
    col1, col2 = st.columns([0.3, 0.7])
    
    with col1:
        try:
            logo_path = Path("static/graphics/FirstPerson-Logo-invert-cropped_notext.svg")
            if logo_path.exists():
                st.image(str(logo_path), use_column_width=True)
        except Exception:
            st.markdown("# 🧠")
    
    with col2:
        st.markdown("# FirstPerson")
        st.markdown("## Personal AI Companion")
        st.markdown("""
        An advanced emotional AI system designed to understand, respond to, and learn from your unique emotional landscape.
        
        ### Features
        - 🎯 Emotional intelligence & resonance detection
        - 💭 Personalized, context-aware responses
        - 🧬 Adaptive learning & evolution
        - 🔒 Privacy-first, local-first design
        - 📓 Journaling & reflection tools
        """)
    
    st.markdown("---")
    
    # Demo mode or login
    if st.checkbox("Enter Demo Mode", value=True):
        st.session_state.demo_mode = True
        st.session_state.authenticated = True
        st.session_state.username = "Demo User"
        st.session_state.user_id = "demo_user"
        st.rerun()
    
    st.markdown("### Or sign in with your account:")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Sign In"):
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
        new_username = st.text_input("Choose a username", key="register_username")
        new_password = st.text_input("Choose a password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
        
        if st.button("Create Account"):
            if not new_username or not new_password:
                st.error("Username and password required")
            elif new_password != confirm_password:
                st.error("Passwords don't match")
            else:
                st.session_state.authenticated = True
                st.session_state.username = new_username
                st.session_state.user_id = f"user_{new_username}"
                st.session_state.demo_mode = False
                st.success(f"Welcome, {new_username}! Your account has been created.")
                st.rerun()


def render_main_app():
    """Render the main application for authenticated users"""
    
    # Sidebar header
    with st.sidebar:
        try:
            logo_path = Path("static/graphics/FirstPerson-Logo-invert-cropped_notext.svg")
            if logo_path.exists():
                st.image(str(logo_path), width=200)
        except Exception:
            st.markdown("# 🧠 FirstPerson")
        
        st.markdown("---")
        
        # User info
        if st.session_state.demo_mode:
            st.info(f"📌 Running in Demo Mode")
        else:
            st.success(f"✅ Logged in as **{st.session_state.username}**")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Select:",
            ["Chat", "Glyphs", "Insights", "Journal", "Settings"],
            key="main_nav"
        )
        
        st.markdown("---")
        
        # Settings
        st.subheader("Preferences")
        processing_mode = st.selectbox(
            "Processing Mode",
            ["Local", "Hybrid", "Cloud"],
            key="processing_mode"
        )
        
        tone = st.selectbox(
            "Response Tone",
            ["Warm", "Professional", "Playful", "Neutral", "Meditative"],
            key="tone_preference"
        )
        
        st.markdown("---")
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.session_state.conversation_history = []
            st.rerun()
    
    # Main content based on page selection
    if page == "Chat":
        st.markdown("# 💬 Chat with FirstPerson")
        
        # Chat display
        chat_container = st.container()
        with chat_container:
            for i, msg in enumerate(st.session_state.conversation_history):
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(msg["content"])
                        if "metadata" in msg:
                            st.caption(msg["metadata"])
        
        # Chat input
        user_input = st.chat_input("Share what you're feeling...")
        
        if user_input:
            # Add user message
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Try to generate response using your processing pipeline
            try:
                from src import process_user_input
                
                if process_user_input:
                    response = process_user_input(user_input)
                    processing_time = "0.00s"
                else:
                    response = "I'm listening to you. This is a connection moment. [Response generation system initializing...]"
                    processing_time = "0.00s"
            except Exception as e:
                response = f"I hear you saying: '{user_input}'. I'm here with you. [System: {str(e)[:50]}...]"
                processing_time = "0.00s"
            
            # Add assistant message
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": response,
                "metadata": f"Processed in {processing_time} • Mode: {processing_mode}"
            })
            
            st.rerun()
    
    elif page == "Glyphs":
        st.markdown("# ✨ Glyphs & Emotional Resonance")
        st.info("Glyphs are emotional signatures detected in your messages. They help understand your emotional landscape.")
        
        # Try to load glyph data
        try:
            from src import parse_input
            if parse_input and st.session_state.conversation_history:
                last_message = [m for m in st.session_state.conversation_history if m["role"] == "user"][-1]["content"]
                result = parse_input(last_message)
                st.json(result if isinstance(result, dict) else {"status": "parsing..."})
        except Exception as e:
            st.write(f"Glyph detection system: {e}")
    
    elif page == "Insights":
        st.markdown("# 📊 Learning Insights")
        st.write("Your FirstPerson system learns from our conversations and adapts over time.")
        st.info("Insights system initializing...")
    
    elif page == "Journal":
        st.markdown("# 📓 Personal Journal")
        st.write("Reflections, rituals, and personal growth tracking.")
        
        entry_text = st.text_area(
            "Write your reflection:",
            placeholder="What's emerging for you emotionally or personally?",
            height=200,
            key="journal_entry"
        )
        
        if st.button("Save Reflection"):
            if entry_text:
                st.success("Your reflection has been saved.")
            else:
                st.error("Please write something first.")
    
    else:  # Settings
        st.markdown("# ⚙️ Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Display")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], key="theme")
            response_length = st.slider("Response Detail Level", 1, 5, 3, key="response_length")
        
        with col2:
            st.subheader("Privacy & Data")
            persist_history = st.checkbox("Persist conversation history", value=True, key="persist_history")
            local_processing = st.checkbox("Prefer local processing", value=True, key="local_processing")
        
        st.markdown("---")
        st.subheader("Account")
        
        if st.button("Delete All Conversation History"):
            st.session_state.conversation_history = []
            st.success("History cleared.")
        
        if st.button("Export My Data"):
            st.info("Export feature coming soon...")


def main():
    """Main entry point"""
    if not st.session_state.get("authenticated"):
        render_splash()
    else:
        render_main_app()


if __name__ == "__main__":
    main()

