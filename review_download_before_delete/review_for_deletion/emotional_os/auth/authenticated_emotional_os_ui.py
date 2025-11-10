"""
Enhanced Emotional OS UI with User Authentication
Secure login system with user-isolated conversation data
"""

import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta

import requests
import streamlit as st

from emotional_os.deploy.config import SUPABASE_ANON_KEY, SUPABASE_URL
from emotional_os.supabase.supabase_integration import create_hybrid_processor
from emotional_os.deploy.modules.ui import render_settings_sidebar

# Authentication configuration
AUTH_CONFIG = {
    "session_timeout_minutes": 480,  # 8 hours
    "max_login_attempts": 5,
    "lockout_duration_minutes": 15
}


class AuthenticationManager:
    """Handles user authentication and session management"""

    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_ANON_KEY
        self.init_session_state()

    def init_session_state(self):
        """Initialize authentication session state"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'session_token' not in st.session_state:
            st.session_state.session_token = None
        if 'session_expires' not in st.session_state:
            st.session_state.session_expires = None
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = {}

    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)

        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )

        return password_hash.hex(), salt

    def verify_password(self, password: str, hash_hex: str, salt: str) -> bool:
        """Verify password against hash"""
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == hash_hex

    def generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(64)

    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        if not st.session_state.authenticated:
            return False

        if st.session_state.session_expires:
            if datetime.now() > st.session_state.session_expires:
                self.logout()
                return False

        return True

    def check_login_attempts(self, username: str) -> bool:
        """Check if user is locked out due to failed attempts"""
        if username not in st.session_state.login_attempts:
            return True

        attempts = st.session_state.login_attempts[username]
        if attempts['count'] >= AUTH_CONFIG['max_login_attempts']:
            lockout_time = attempts['last_attempt'] + \
                timedelta(minutes=AUTH_CONFIG['lockout_duration_minutes'])
            if datetime.now() < lockout_time:
                return False
            # Reset attempts after lockout period
            del st.session_state.login_attempts[username]

        return True

    def record_login_attempt(self, username: str, success: bool):
        """Record login attempt"""
        if username not in st.session_state.login_attempts:
            st.session_state.login_attempts[username] = {
                'count': 0, 'last_attempt': datetime.now()}

        if success:
            # Reset attempts on successful login
            if username in st.session_state.login_attempts:
                del st.session_state.login_attempts[username]
        else:
            # Increment failed attempts
            st.session_state.login_attempts[username]['count'] += 1
            st.session_state.login_attempts[username]['last_attempt'] = datetime.now(
            )

    def create_user(self, username: str, password: str, email: str = None) -> dict:
        """Create new user account"""
        try:
            # Hash password
            password_hash, salt = self.hash_password(password)

            # Create user via Supabase edge function
            response = requests.post(
                f"{self.supabase_url}/functions/v1/auth-manager",
                headers={
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "action": "create_user",
                    "username": username,
                    "password_hash": password_hash,
                    "salt": salt,
                    "email": email,
                    "created_at": datetime.now().isoformat()
                },
                timeout=10
            )

            if response.status_code == 200:
                return {"success": True, "message": "Account created successfully"}
            error_data = response.json() if response.headers.get(
                'content-type', '').startswith('application/json') else {}
            return {"success": False, "message": error_data.get("error", "Failed to create account")}

        except Exception as e:
            return {"success": False, "message": f"Registration error: {str(e)}"}

    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user login"""
        try:
            # Check if user is locked out
            if not self.check_login_attempts(username):
                return {"success": False, "message": "Account temporarily locked due to failed attempts"}

            # Authenticate via Supabase edge function
            response = requests.post(
                f"{self.supabase_url}/functions/v1/auth-manager",
                headers={
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "action": "authenticate",
                    "username": username,
                    "password": password
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("authenticated"):
                    # Successful login
                    self.record_login_attempt(username, True)

                    # Set session data
                    st.session_state.authenticated = True
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.username = username
                    st.session_state.session_token = self.generate_session_token()
                    st.session_state.session_expires = datetime.now(
                    ) + timedelta(minutes=AUTH_CONFIG['session_timeout_minutes'])

                    return {"success": True, "message": "Login successful", "user_id": data.get("user_id")}
                # Failed authentication
                self.record_login_attempt(username, False)
                return {"success": False, "message": "Invalid username or password"}
            self.record_login_attempt(username, False)
            return {"success": False, "message": "Authentication service error"}

        except Exception as e:
            self.record_login_attempt(username, False)
            return {"success": False, "message": f"Login error: {str(e)}"}

    def logout(self):
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.session_token = None
        st.session_state.session_expires = None

        # Clear conversation history
        if 'conversation_history' in st.session_state:
            del st.session_state.conversation_history

        st.rerun()

    def render_login_form(self):
        """Render login/registration form"""
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Login to Your Account")

            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_submitted = st.form_submit_button("Login")

                if login_submitted:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        with st.spinner("Authenticating..."):
                            result = self.authenticate_user(username, password)

                        if result["success"]:
                            st.success(result["message"])
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(result["message"])

                            # Show lockout warning if approaching limit
                            if username in st.session_state.login_attempts:
                                attempts = st.session_state.login_attempts[username]['count']
                                remaining = AUTH_CONFIG['max_login_attempts'] - attempts
                                if remaining <= 2:
                                    st.warning(
                                        f"Warning: {remaining} attempts remaining before temporary lockout")

        with tab2:
            st.subheader("Create New Account")

            with st.form("register_form"):
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email (optional)")
                new_password = st.text_input(
                    "Choose Password", type="password")
                confirm_password = st.text_input(
                    "Confirm Password", type="password")
                register_submitted = st.form_submit_button("Register")

                if register_submitted:
                    if not new_username or not new_password:
                        st.error("Username and password are required")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters long")
                    else:
                        with st.spinner("Creating account..."):
                            result = self.create_user(
                                new_username, new_password, new_email)

                        if result["success"]:
                            st.success(result["message"])
                            st.info("You can now login with your new account")
                        else:
                            st.error(result["message"])

        # Privacy notice
        with st.expander("🔒 Privacy & Security"):
            st.write("""
            **Your Privacy Matters:**
            - All conversations are encrypted and isolated by user account
            - Emotional data is never shared between users
            - Sessions expire automatically for security
            - Failed login attempts are rate-limited
            - Local processing options available for maximum privacy
            """)

    def render_user_header(self):
        """Render header with user info and logout"""
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(f"Welcome back, **{st.session_state.username}**")

        with col2:
            # Session info
            if st.session_state.session_expires:
                time_left = st.session_state.session_expires - datetime.now()
                hours_left = int(time_left.total_seconds() // 3600)
                st.write(f"Session: {hours_left}h left")

        with col3:
            if st.button("Logout", type="secondary"):
                self.logout()


def main():
    """Main application with authentication"""
    st.set_page_config(
        page_title="Emotional OS",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize authentication
    auth_manager = AuthenticationManager()

    # Check session validity
    if not auth_manager.is_session_valid():
        auth_manager.render_login_form()
        return

    # User is authenticated - render main app
    auth_manager.render_user_header()

    st.title("🧠 Emotional OS - Personal AI Companion")
    st.markdown("*Your private space for emotional processing and growth*")

    # Initialize conversation processor with user context
    if 'processor' not in st.session_state:
        st.session_state.processor = create_hybrid_processor(
            limbic_engine=st.session_state.get('limbic_engine'))

    # User-specific conversation history
    conversation_key = f"conversation_history_{st.session_state.user_id}"
    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = []

    # Main interface
    # Render shared Settings expander in the sidebar for Processing Mode and Theme
    render_settings_sidebar()

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            # Read the processing mode selected from Settings
            processing_mode = st.session_state.get('processing_mode', 'hybrid')

        with col2:
            if st.button("Clear History", type="secondary"):
                st.session_state[conversation_key] = []
                st.rerun()

    # Chat interface
    chat_container = st.container()

    # Display conversation history
    with chat_container:
        for exchange in st.session_state[conversation_key]:
            with st.chat_message("user"):
                st.write(exchange["user"])
            with st.chat_message("assistant"):
                st.write(exchange["assistant"])
                if "processing_time" in exchange:
                    st.caption(f"Processed in {exchange['processing_time']}")

    # User input
    user_input = st.chat_input("Share what's on your mind...")

    if user_input:
        # Add user message to history
        with st.chat_message("user"):
            st.write(user_input)

        # Process response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                start_time = time.time()

                # Pass user context and session A/B metadata to processor
                session_meta = {
                    'user_id': st.session_state.user_id,
                    'ab_participate': st.session_state.get('ab_participate', False),
                    'ab_group': st.session_state.get('ab_group', 'not_participating')
                }

                # Lightweight small-talk filter: short-circuit some common social queries
                # to avoid long self-descriptive replies from upstream processors.
                smalltalk_triggers = [
                    "how are you",
                    "how're you",
                    "how are you doing",
                    "tell me about yourself",
                    "what do you do",
                    "who are you",
                    "tell me more about yourself",
                ]

                lowered = user_input.lower().strip()
                is_smalltalk = any(
                    trigger in lowered for trigger in smalltalk_triggers)

                if is_smalltalk:
                    # Short, friendly canned replies for brief social prompts
                    canned = [
                        "I'm here and present with you. That's what matters — how are you doing?",
                        "Thanks for asking — I'm here to listen. What's on your mind?",
                        "I'm steady and ready to listen. Tell me about you."
                    ]
                    # Choose deterministic canned reply (first) to keep behavior predictable in tests
                    response = canned[0]
                    processing_time = time.time() - start_time
                    st.write(response)
                    st.caption(
                        f"Processed in {processing_time:.2f}s (small-talk)")
                else:
                    result = st.session_state.processor.process_emotional_input(
                        user_input,
                        prefer_ai=st.session_state.get('prefer_ai', True),
                        privacy_mode=(processing_mode == "local"),
                        session_metadata=session_meta
                    )

                    processing_time = time.time() - start_time

                    # Prefer normalized 'response' key; provide safe fallbacks
                    response = result.get("response") or result.get(
                        "voltage_response") or "I'm here to listen."
                    st.write(response)
                    st.caption(f"Processed in {processing_time:.2f}s")

        # Add to conversation history
        st.session_state[conversation_key].append({
            "user": user_input,
            "assistant": response,
            "processing_time": f"{processing_time:.2f}s",
            "mode": processing_mode,
            "timestamp": datetime.now().isoformat()
        })

        st.rerun()

    # Sidebar with user stats and settings
    with st.sidebar:
        st.subheader("Your Emotional Journey")

        # User-specific stats
        conversation_count = len(st.session_state[conversation_key])
        st.metric("Conversations", conversation_count)

        if conversation_count > 0:
            recent_conversation = st.session_state[conversation_key][-1]
            st.metric("Last Session", recent_conversation["timestamp"][:10])

        st.subheader("Privacy Settings")
        st.write("🔒 Your data is completely isolated")
        st.write("🧠 Learning happens only from your conversations")
        st.write("⚡ Optimized for 2-3 second responses")

        # NOTE: The export/download control has been removed from this sidebar
        # to avoid duplication. Use the "Privacy & Consent" sidebar expander
        # (provided by `render_consent_settings_panel`) to export user data.


if __name__ == "__main__":
    main()
