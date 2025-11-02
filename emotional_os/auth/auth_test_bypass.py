"""
Temporary Authentication Bypass for Testing
This allows you to test the authenticated UI while backend functions are being deployed
"""

import uuid
from datetime import datetime, timedelta

import streamlit as st


def create_test_session():
    """Create a temporary test session for UI testing"""
    # Set up test user session
    st.session_state.authenticated = True
    st.session_state.user_id = str(uuid.uuid4())
    st.session_state.username = "test_user"
    st.session_state.session_token = "test_token_" + str(uuid.uuid4())[:8]
    st.session_state.session_expires = datetime.now() + timedelta(hours=8)

    return True

def bypass_authentication():
    """Temporary function to bypass auth for testing"""
    st.info("🔧 **Testing Mode**: Authentication backend is being deployed. Using temporary session.")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("Continue with Test Session", type="primary", use_container_width=True):
            if create_test_session():
                st.success("✅ Test session created! Reloading...")
                st.rerun()

    with st.expander("ℹ️ About Test Mode"):
        st.write("""
        **What this does:**
        - Creates a temporary user session for testing the authenticated UI
        - All conversations will be local to this browser session
        - Data won't persist after browser refresh (until backend is deployed)
        
        **To enable full authentication:**
        1. Deploy the database schema in Supabase SQL Editor
        2. Deploy the auth-manager edge function  
        3. Deploy the authenticated-saori edge function
        4. Remove this test bypass
        """)

# Add this to your emotional_os_ui.py to enable test mode
