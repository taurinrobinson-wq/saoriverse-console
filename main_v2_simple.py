"""
Simplified Streamlit app - temporary bypass for broken modularization.
This provides a minimal working UI until the modular imports are fixed.
"""

import streamlit as st
import os
import uuid
import datetime
import json
import base64

st.set_page_config(
    page_title="FirstPerson - Personal AI Companion",
    page_icon="🧠",
    layout="wide",
)

# ============================================================================
# DEMO MODE - BYPASS BROKEN MODULARIZATION
# ============================================================================

def init_session():
    """Initialize session state."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.conversations = {}
        st.session_state.current_conversation_id = None
        st.session_state.conversation_history = []
        st.session_state.show_login = False
        st.session_state.show_register = False

def render_splash():
    """Render splash screen."""
    st.markdown("<h1 style='text-align:center'>FirstPerson</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>A private space for emotional processing and growth</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Sign In", use_container_width=True, key="signin"):
            st.session_state.show_login = True
            st.rerun()
    with col2:
        if st.button("Create Account", use_container_width=True, key="signup"):
            st.session_state.show_register = True
            st.rerun()
    with col3:
        if st.button("📋 Demo Mode", use_container_width=True, key="demo"):
            user_id = str(uuid.uuid4())
            st.session_state.authenticated = True
            st.session_state.user_id = user_id
            st.session_state.username = "demo_user"
            st.session_state.show_login = False
            st.session_state.show_register = False
            st.rerun()

    st.divider()
    
    if st.session_state.get("show_login"):
        st.markdown("## Sign In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # Demo: accept any credentials
            user_id = str(uuid.uuid4())
            st.session_state.authenticated = True
            st.session_state.user_id = user_id
            st.session_state.username = username
            st.session_state.show_login = False
            st.rerun()
        if st.button("Back"):
            st.session_state.show_login = False
            st.rerun()
    
    elif st.session_state.get("show_register"):
        st.markdown("## Create An Account")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Create Account"):
            if first_name and last_name and email and username and password:
                user_id = str(uuid.uuid4())
                st.session_state.authenticated = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.session_state.show_register = False
                st.rerun()
            else:
                st.error("Please fill in all fields")
        if st.button("Back"):
            st.session_state.show_register = False
            st.rerun()

def render_app():
    """Render main application."""
    col1, col2, col3 = st.columns([1, 10, 1])
    with col1:
        if st.button("⚙️ Settings"):
            st.session_state.show_settings = True
    with col2:
        st.markdown("<h2 style='text-align:center'>FirstPerson Chat</h2>", unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    st.divider()
    
    # Sidebar - Conversations
    with st.sidebar:
        st.markdown("### Conversations")
        if st.button("+ New Conversation", use_container_width=True):
            conv_id = str(uuid.uuid4())
            st.session_state.current_conversation_id = conv_id
            st.session_state.conversation_history = []
            st.session_state.conversations[conv_id] = {
                "id": conv_id,
                "title": "New Conversation",
                "messages": [],
                "created": datetime.datetime.now().isoformat(),
            }
            st.rerun()
        
        st.markdown("---")
        for conv_id, conv in st.session_state.conversations.items():
            if st.button(f"💬 {conv['title']}", use_container_width=True, key=f"conv_{conv_id}"):
                st.session_state.current_conversation_id = conv_id
                st.session_state.conversation_history = conv.get("messages", [])
                st.rerun()
    
    # Main chat area
    st.markdown("### Chat")
    
    # Display conversation history
    for msg in st.session_state.conversation_history:
        with st.chat_message(msg.get("role", "user")):
            st.write(msg.get("content", ""))
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # Add user message
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.datetime.now().isoformat(),
        })
        
        # Generate response (demo)
        response = f"Thank you for sharing that. I'm listening. You said: '{user_input[:50]}...'"
        
        # Add assistant message
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.datetime.now().isoformat(),
        })
        
        # Update conversation
        if st.session_state.current_conversation_id:
            conv_id = st.session_state.current_conversation_id
            if conv_id in st.session_state.conversations:
                st.session_state.conversations[conv_id]["messages"] = st.session_state.conversation_history
                # Auto-name on first message
                if len(st.session_state.conversation_history) == 2:
                    st.session_state.conversations[conv_id]["title"] = user_input[:35].strip()
        
        st.rerun()

# ============================================================================
# MAIN
# ============================================================================

def main():
    init_session()
    
    if not st.session_state.authenticated:
        render_splash()
    else:
        render_app()

if __name__ == "__main__":
    main()
