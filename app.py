"""FirstPerson - Personal AI Companion - Main Entry Point"""
import os
import sys
from pathlib import Path

import streamlit as st

# Add workspace root to path for imports
_workspace_root = str(Path(__file__).parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# Page config with FirstPerson logo
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

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Authentication
with st.sidebar:
    st.markdown("---")
    st.markdown("## FirstPerson")
    st.markdown("*Your Personal AI Companion*")
    st.markdown("---")
    
    if not st.session_state.logged_in:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if username and password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Please enter both username and password")
    else:
        st.success(f"✅ Logged in as **{st.session_state.username}**")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        st.subheader("Navigation")
        page = st.radio("Select:", ["Chat", "Settings", "About"], key="nav_radio")
        st.markdown("---")
        st.markdown("**v1.0.0** | Streamlit Cloud")

# Main content
if not st.session_state.logged_in:
    st.markdown("# 🧠 FirstPerson")
    st.markdown("## Personal AI Companion")
    st.info("Please log in using the sidebar to continue.")
    st.markdown("""
    ### Features
    - 🎯 Emotional AI processing
    - 💭 Personalized responses
    - 🧬 Adaptive learning
    - 🔒 Privacy-first design
    """)
else:
    if page == "Chat":
        st.markdown("# 💬 Chat with FirstPerson")
        
        # Chat display
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.write(f"**You:** {message['content']}")
                else:
                    st.write(f"**FirstPerson:** {message['content']}")
        
        # Chat input
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            user_input = st.text_input(
                "Your message:",
                key="chat_input",
                placeholder="Type your message here..."
            )
        with col2:
            send_button = st.button("Send", key="send_btn")
        
        if send_button and user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Simulate AI response (placeholder)
            response = f"I understand you said: '{user_input}'. This is a placeholder response. Full AI integration coming soon."
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            st.rerun()
    
    elif page == "Settings":
        st.markdown("# ⚙️ Settings")
        st.write(f"**Current User:** {st.session_state.username}")
        
        st.subheader("Preferences")
        tone = st.selectbox("Tone", ["Warm", "Professional", "Playful", "Neutral"])
        response_length = st.slider("Response Length", 1, 5, 3)
        
        if st.button("Save Settings"):
            st.success("Settings saved!")
    
    else:  # About
        st.markdown("# ℹ️ About FirstPerson")
        st.markdown("""
        **FirstPerson** is an advanced emotional AI system designed to provide:
        
        - **Personalized Responses** - Adapts to your emotional state and preferences
        - **Privacy-First Design** - Your data stays with you
        - **Emotional Intelligence** - Understands context and nuance
        - **Local-First Processing** - Minimal data transmission
        
        ### Technology
        Built with Streamlit, powered by advanced emotional processing algorithms.
        
        ### Contact
        Questions? Feedback? Reach out to support.
        """)
