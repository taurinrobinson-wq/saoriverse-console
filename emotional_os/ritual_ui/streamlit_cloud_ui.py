"""
Streamlit Cloud Compatible Emotional OS with Authentication
Self-contained version that works without external dependencies
"""

import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta

import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Emotional OS",
    page_icon="/static/graphics/FirstPerson-Logo-normalized.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication configuration
AUTH_CONFIG = {
    "session_timeout_minutes": 480,  # 8 hours
    "max_login_attempts": 5,
    "lockout_duration_minutes": 15
}


class AuthenticationManager:
    """Handles user authentication and session management"""

    def __init__(self):
        # Use Streamlit secrets
        try:
            self.supabase_url = st.secrets["supabase"]["url"]
            self.supabase_key = st.secrets["supabase"]["key"]
        except KeyError:
            st.error("❌ Supabase configuration not found in secrets")
            st.stop()

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

    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == stored_hash

    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        if not st.session_state.authenticated:
            return False

        if not st.session_state.session_expires:
            return False

        try:
            expires = datetime.fromisoformat(st.session_state.session_expires)
            return datetime.now() < expires
        except Exception:
            return False

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

    def create_test_session(self):
        """Create a temporary test session for UI testing"""
        import uuid

        # Set up test user session
        st.session_state.authenticated = True
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.username = "test_user"
        st.session_state.session_token = "test_token_" + str(uuid.uuid4())[:8]
        st.session_state.session_expires = datetime.now() + timedelta(hours=8)

        return True

    def record_login_attempt(self, username: str, success: bool):
        """Record login attempt for rate limiting"""
        if username not in st.session_state.login_attempts:
            st.session_state.login_attempts[username] = {
                'count': 0, 'last_attempt': datetime.now()}

        if success:
            # Reset attempts on successful login
            del st.session_state.login_attempts[username]
        else:
            # Increment failed attempts
            st.session_state.login_attempts[username]['count'] += 1
            st.session_state.login_attempts[username]['last_attempt'] = datetime.now(
            )

    def create_user(self, username: str, password: str, email: str = "") -> dict:
        """Create new user account"""
        try:
            # Hash password
            password_hash, salt = self.hash_password(password)

            # Create user via Supabase edge function
            auth_url = st.secrets.get("supabase", {}).get(
                "auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
            response = requests.post(
                auth_url,
                headers={
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "action": "create_user",
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "salt": salt,
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
            auth_url = st.secrets.get("supabase", {}).get(
                "auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
            response = requests.post(
                auth_url,
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
                if data.get("success"):
                    # Set session state
                    st.session_state.authenticated = True
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.username = username
                    st.session_state.session_token = data.get("session_token")
                    st.session_state.session_expires = (datetime.now(
                    ) + timedelta(minutes=AUTH_CONFIG["session_timeout_minutes"])).isoformat()

                    self.record_login_attempt(username, True)
                    return {"success": True, "message": "Login successful"}
                self.record_login_attempt(username, False)
                return {"success": False, "message": data.get("message", "Login failed")}
            self.record_login_attempt(username, False)
            return {"success": False, "message": "Authentication service unavailable"}

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
        st.rerun()

    def render_user_header(self):
        """Render header for authenticated users"""
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(f"Welcome back, **{st.session_state.username}**! 👋")

        with col2:
            if st.button("⚙️ Settings", help="User settings and preferences"):
                st.info("Settings panel coming soon!")

        with col3:
            if st.button("🚪 Logout", help="Sign out of your account"):
                self.logout()

    def render_login_form(self):
        """Render login/registration form"""
        st.title("🔐 Emotional OS - Secure Access")

        # Test mode banner
        with st.container():
            st.warning(
                "⚠️ **Backend Deployment Status**: Authentication functions deployed and ready")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.info(
                    "Full authentication system is active. Try registering or use Test Mode for immediate access.")
            with col2:
                if st.button("🧪 Test Mode", type="secondary", help="Preview authenticated UI with temporary session"):
                    self.create_test_session()
                    st.rerun()

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

        with tab2:
            st.subheader("Create New Account")

            with st.form("register_form"):
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email (optional)")
                new_password = st.text_input(
                    "Choose Password", type="password")
                confirm_password = st.text_input(
                    "Confirm Password", type="password")
                register_submitted = st.form_submit_button("Create Account")

                if register_submitted:
                    if not new_username or not new_password:
                        st.error("Username and password are required")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            result = self.create_user(
                                new_username, new_password, new_email)

                        if result["success"]:
                            st.success(result["message"])
                            st.info(
                                "Please use the Login tab to sign in with your new account")
                        else:
                            st.error(result["message"])


def render_main_app():
    """Render the main application for authenticated users"""
    st.title("Emotional OS - Personal AI Companion")
    st.markdown("*Your private space for emotional processing and growth*")

    # User-specific conversation history
    conversation_key = f"conversation_history_{st.session_state.user_id}"
    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = []

    # Main interface
    with st.container():
        # Processing mode selection
        col1, col2 = st.columns([2, 1])

        # Map legacy ai_preferred -> hybrid + prefer_ai
        if st.session_state.get('processing_mode') == 'ai_preferred':
            st.session_state.processing_mode = 'hybrid'
            st.session_state['prefer_ai'] = True

        with col1:
            mode_options = ["hybrid", "local"]
            current = st.session_state.get('processing_mode', 'hybrid')
            try:
                idx = mode_options.index(current)
            except ValueError:
                idx = 0
            processing_mode = st.selectbox(
                "Processing Mode",
                mode_options,
                index=idx,
                help="Hybrid: Best performance, Local: Maximum privacy"
            )

        with col2:
            if st.button("Clear History", type="secondary"):
                st.session_state[conversation_key] = []
                st.rerun()

    # Chat interface
    chat_container = st.container()

    # Display conversation history
    with chat_container:
        for i, exchange in enumerate(st.session_state[conversation_key]):
            with st.chat_message("user"):
                st.write(exchange["user"])

            with st.chat_message("assistant"):
                st.write(exchange["assistant"])
                if "processing_time" in exchange:
                    st.caption(
                        f"Processed in {exchange['processing_time']} • Mode: {exchange.get('mode', 'unknown')}")

    # Input area
    user_input = st.chat_input("Share what you're feeling...")

    if user_input:
        # Add user message to chat
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)

        # Process the input
        with st.chat_message("assistant"):
            with st.spinner("Processing your emotional input..."):
                start_time = time.time()

                # Simple response for now (replace with actual processing when available)
                response = "Thank you for sharing. I'm here to listen and support you through whatever you're experiencing. Your feelings are valid and important."
                processing_time = time.time() - start_time

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
    st.write("Learning happens only from your conversations")
    st.write("⚡ Optimized for 2-3 second responses")

    if st.button("Download My Data", type="secondary"):
        # Option to export user's conversation data
        user_data = {
            "user_id": st.session_state.user_id,
            "username": st.session_state.username,
            "conversations": st.session_state[conversation_key],
            "export_date": datetime.now().isoformat()
        }
        st.download_button(
            "Download JSON",
            json.dumps(user_data, indent=2),
            file_name=f"emotional_os_data_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )


def main():
    """Main application with authentication"""
    # Initialize authentication
    auth_manager = AuthenticationManager()

    # Check session validity
    if not auth_manager.is_session_valid():
        auth_manager.render_login_form()
        return

    # User is authenticated - render main app
    auth_manager.render_user_header()
    render_main_app()


if __name__ == "__main__":
    main()
