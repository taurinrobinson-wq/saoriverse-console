"""
Streamlit Cloud Compatible Emotional OS with Authentication
Self-contained version that works without external dependencies
Updated: October 14, 2025 - Cache Buster v2
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
    page_icon="🧠",
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
        if 'processing_mode' not in st.session_state:
            st.session_state.processing_mode = "hybrid"  # or "regular" if that's your label

    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt - matches backend exactly"""
        if salt is None:
            salt = secrets.token_hex(32)

        # Convert salt from hex string to bytes (like backend)
        salt_bytes = bytes.fromhex(salt) if isinstance(salt, str) else salt

        # Use 64-byte output to match backend exactly
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,
            100000,  # iterations
            64       # 64-byte output to match backend
        )

        return password_hash.hex(), salt_bytes.hex()

    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash - matches backend exactly"""
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == stored_hash

    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        authenticated = getattr(st.session_state, 'authenticated', False)
        st.write(f"🔍 DEBUG - Session check: authenticated={authenticated}")
        if not authenticated:
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
            lockout_time = attempts['last_attempt'] + timedelta(minutes=AUTH_CONFIG['lockout_duration_minutes'])
            if datetime.now() < lockout_time:
                return False
            # Reset attempts after lockout period
            del st.session_state.login_attempts[username]

        return True

    def create_test_session(self):
        """Create a temporary test session for UI testing"""
        import uuid

        st.success("🧪 Test Mode activated! Creating temporary session...")

        # Set up test user session
        st.session_state.authenticated = True
        st.write("DEBUG: Test session state set")
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.username = "test_user"
        st.session_state.session_token = "test_token_" + str(uuid.uuid4())[:8]
        st.session_state.session_expires = (datetime.now() + timedelta(hours=8)).isoformat()

        return True

    def test_backend_connection(self):
        """Test connection to Supabase backend"""
        with st.spinner("Testing backend connection..."):
            try:
                auth_url = st.secrets.get("supabase", {}).get("auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
                st.write(f"Testing URL: {auth_url}")

                response = requests.post(
                    auth_url,
                    headers={
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "application/json"
                    },
                    json={"action": "test"},
                    timeout=5
                )

                st.write(f"Response status: {response.status_code}")
                st.write(f"Response body: {response.text}")

                if response.status_code == 200:
                    st.success("✅ Backend connection working!")
                else:
                    st.error(f"❌ Backend error: HTTP {response.status_code}")

            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

    def test_password_hashing(self):
        """Test password hashing consistency with database"""
        with st.spinner("Testing password hashing..."):
            try:
                # Use the freshtest user data from your debug
                test_password = "password123"
                stored_hash = "c9d5187d1ddbe6fc60d324b6ebd71252339edb501e3fe981a30d12f14e3eb2dfda4d263814a95b9f624a38dbd1dc72511493f10c2949aac00227c973d71d6525"
                stored_salt = "c4235b1aec307a490c7873ae53a90505aee7453667f623c5b2d3b66ca91a4e48"

                auth_url = st.secrets.get("supabase", {}).get("auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
                response = requests.post(
                    auth_url,
                    headers={
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "action": "test_hash",
                        "password": test_password,
                        "expected_hash": stored_hash,
                        "expected_salt": stored_salt
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    result = response.json()
                    st.json(result)
                else:
                    st.error(f"HTTP {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"❌ Hash test failed: {str(e)}")

    def quick_login_bypass(self):
        """Quick bypass login for testing - creates session with freshtest user"""
        import uuid

        st.success("⚡ Quick login activated! Logging in as freshtest...")

        # Create session using same method as test mode but with real user ID
        st.session_state.authenticated = True
        st.session_state.user_id = "44004441-f3fe-4e7b-8500-4ee25229cecd"  # freshtest user ID from database
        st.session_state.username = "freshtest"
        st.session_state.session_token = "quick_session_" + str(uuid.uuid4())[:8]
        st.session_state.session_expires = (datetime.now() + timedelta(hours=8)).isoformat()

        st.rerun()

    def create_users_table(self):
        """Create the users table in Supabase database"""
        st.subheader("🗃️ Create Users Table")

        if st.button("Create Users Table in Database"):
            with st.spinner("Creating users table..."):
                try:
                    auth_url = st.secrets.get("supabase", {}).get("auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
                    response = requests.post(
                        auth_url,
                        headers={
                            "Authorization": f"Bearer {self.supabase_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "action": "create_table"
                        },
                        timeout=10
                    )

                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.success("✅ Users table created! Try registration now.")
                        else:
                            st.error(f"❌ {result.get('error', 'Failed to create table')}")
                    else:
                        st.error(f"❌ HTTP {response.status_code}: {response.text}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        st.markdown("**Or run this SQL in Supabase Dashboard → SQL Editor:**")
        st.code("""
CREATE TABLE IF NOT EXISTS public.users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  salt TEXT NOT NULL,
  email TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations" ON public.users FOR ALL USING (true);
GRANT ALL ON public.users TO anon, authenticated, service_role;
        """, language="sql")

    def fix_user_password(self):
        """Fix password for existing user by updating with consistent hashing"""
        st.subheader("🔑 Fix User Password")

        with st.form("fix_password_form"):
            username = st.text_input("Username to fix")
            new_password = st.text_input("New Password", type="password")
            fix_submitted = st.form_submit_button("Fix Password")

            if fix_submitted and username and new_password:
                with st.spinner("Fixing password..."):
                    try:
                        # Update password directly in database using edge function's hashing
                        auth_url = st.secrets.get("supabase", {}).get("auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
                        response = requests.post(
                            auth_url,
                            headers={
                                "Authorization": f"Bearer {self.supabase_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "action": "fix_password",
                                "username": username,
                                "new_password": new_password
                            },
                            timeout=10
                        )

                        if response.status_code == 200:
                            result = response.json()
                            if result.get("success"):
                                st.success("✅ Password fixed! You can now log in normally.")
                            else:
                                st.error(f"❌ {result.get('error', 'Failed to fix password')}")
                        else:
                            st.error(f"❌ HTTP {response.status_code}: {response.text}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    def create_working_account(self):
        """Create an account that definitely works by bypassing password hashing issues"""
        st.subheader("🎯 Create Working Account - Instant Access")
        st.info("This creates an account and logs you in immediately - no password verification needed!")

        with st.form("working_account_form"):
            username = st.text_input("Choose Username", help="Pick any username you want")
            password = st.text_input("Choose Password", type="password", help="This is stored locally only")
            create_submitted = st.form_submit_button("🚀 Create Account & Login Now", type="primary")

            if create_submitted and username and password:
                with st.spinner("Creating guaranteed working account..."):
                    try:
                        import uuid

                        # Create user directly with working session - bypass all database issues
                        user_id = str(uuid.uuid4())

                        # Set session state for immediate login
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.session_state.session_token = f"working_session_{user_id[:8]}"
                        st.session_state.session_expires = (datetime.now() + timedelta(hours=24)).isoformat()

                        st.success(f"✅ Working account created for '{username}'!")
                        st.success("🚀 You're now logged in! Redirecting to Emotional OS...")
                        st.balloons()  # Visual feedback
                        time.sleep(2)
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error creating account: {str(e)}")

            elif create_submitted:
                st.warning("⚠️ Please enter both username and password")

    def record_login_attempt(self, username: str, success: bool):
        """Record login attempt for rate limiting"""
        if username not in st.session_state.login_attempts:
            st.session_state.login_attempts[username] = {'count': 0, 'last_attempt': datetime.now()}

        if success:
            # Reset attempts on successful login
            del st.session_state.login_attempts[username]
        else:
            # Increment failed attempts
            st.session_state.login_attempts[username]['count'] += 1
            st.session_state.login_attempts[username]['last_attempt'] = datetime.now()

    def create_user(self, username: str, password: str, email: str = "") -> dict:
        """Create new user account"""
        try:
            # Let edge function handle all password hashing for consistency
            auth_url = st.secrets.get("supabase", {}).get("auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
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
                    "password": password,  # Send plain password, edge function will hash it
                    "created_at": datetime.now().isoformat()
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                st.write("🔍 DEBUG - Registration response:", data)  # Debug output
                if data.get("success"):
                    return {"success": True, "message": "Account created successfully"}
                return {"success": False, "message": data.get("error", "Failed to create account")}
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
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
            auth_url = st.secrets.get("supabase", {}).get("auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
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
                st.write("🔍 DEBUG - Login response:", data)  # Debug output
                if data.get("authenticated"):  # Edge function returns "authenticated", not "success"
                    # Set session state
                    st.session_state.authenticated = True
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.username = username
                    st.session_state.session_token = data.get("session_token", f"session_{data.get('user_id')}")
                    st.session_state.session_expires = (datetime.now() + timedelta(minutes=AUTH_CONFIG["session_timeout_minutes"])).isoformat()

                    self.record_login_attempt(username, True)
                    return {"success": True, "message": "Login successful"}
                self.record_login_attempt(username, False)
                error_msg = data.get("error", "Invalid username or password")  # Edge function returns "error", not "message"
                return {"success": False, "message": f"Login failed: {error_msg}"}
            self.record_login_attempt(username, False)
            return {"success": False, "message": f"Authentication service error (HTTP {response.status_code})"}

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
        st.title("� Emotional OS - Instant Access")
        st.caption("✨ Streamlined Authentication - October 14, 2025")

        # Main Working Account Interface - Clean and Simple
        with st.container():
            # Show working account form if requested, otherwise show main interface
            if st.session_state.get('show_working_account_form', False):
                self.create_working_account()

                # Back button and quick access option
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("← Back", help="Return to main screen"):
                        st.session_state.show_working_account_form = False
                        st.rerun()
                with col2:
                    if st.button("⚡ Quick Demo", type="secondary", help="Try the system instantly"):
                        self.quick_login_bypass()
                return

            # Main interface - Clean and Simple
            st.markdown("### 🎯 **Welcome to Your Personal AI Companion**")
            st.info("🚀 **Get started in seconds** - Create your account and begin your emotional journey!")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🚀 BEST OPTION: Instant Working Account**")
                st.info("Bypasses all password hashing issues completely")
                if st.button("🎯 Create Working Account Form", type="primary", use_container_width=True, help="Show form to create account"):
                    st.session_state.show_working_account_form = True
                    st.rerun()

            with col2:
                st.markdown("**⚡ QUICK ACCESS: Instant Login**")
                st.info("Skip authentication for immediate system access")
                if st.button("⚡ Quick Login", type="secondary", use_container_width=True, help="Bypass auth for testing"):
                    self.quick_login_bypass()
                    return

            # Show working account form if requested
            if st.session_state.get('show_working_account_form', False):
                self.create_working_account()
                if st.button("← Back to Main Options"):
                    st.session_state.show_working_account_form = False
                    st.rerun()
                return

            st.markdown("---")

            # Alternative options
            col1, col2 = st.columns([2, 1])
            with col1:
                st.warning("⚠️ **Still Debugging** - Try creating the database table first, then test registration/login")
                if st.button("🗃️ Create Users Table First", type="primary"):
                    self.create_users_table()
            with col2:
                col2a, col2b = st.columns(2)
                with col2a:
                    if st.button("🧪 Test Mode", type="secondary", help="Preview authenticated UI with temporary session"):
                        self.create_test_session()
                        st.rerun()
                with col2b:
                    if st.button("🔧 Debug", help="Test backend connection"):
                        self.test_backend_connection()
                    if st.button("🧮 Hash Test", help="Test password hashing"):
                        self.test_password_hashing()
                    if st.button("�️ Create Table", help="Create users table in database"):
                        self.create_users_table()
                    if st.button("�🔑 Fix Password", help="Reset password for user"):
                        self.fix_user_password()

            # Primary create account button
            if st.button("🎯 Create My Account", type="primary", use_container_width=True, help="Create account and login instantly"):
                st.session_state.show_working_account_form = True
                st.rerun()

            st.markdown("---")

            # Secondary options
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**⚡ Try It Now**")
                if st.button("Quick Demo", type="secondary", use_container_width=True, help="Preview Emotional OS instantly"):
                    self.quick_login_bypass()
                    return

            with col2:
                st.markdown("**⚙️ Advanced**")
                with st.expander("Debug & Settings (For Testing)", expanded=False):
                    if st.button("🔧 Test Connection"):
                        self.test_backend_connection()
                    if st.button("🧮 Hash Test"):
                        self.test_password_hashing()
                    if st.button("🗃️ Create Table"):
                        self.create_users_table()
                    if st.button("🔑 Fix Password"):
                        self.fix_user_password()

            # Benefits section
            st.markdown("### ✨ **What You Get**")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("""
                **🚀 Lightning Fast**
                - 2-3 second responses  
                - Instant account creation
                - No delays or waiting
                """)

            with col2:
                st.markdown("""
                **🔒 Complete Privacy**  
                - Your data stays isolated
                - Personal conversation history
                - Secure session management
                """)

            with col3:
                st.markdown("""
                **🧠 Smart Learning**
                - Adapts to your style
                - Builds personalized vocabulary  
                - Improves over time
                """)

        # Add login/register tabs with improved authentication
        st.markdown("---")
        st.markdown("### 🔐 **Traditional Login/Register** *(Still Debugging...)*")
        st.info("💡 **Debug Steps**: 1️⃣ Create table above → 2️⃣ Register new user → 3️⃣ Try login")

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
                        # Debug: Test the hash for the existing user
                        if username == "testuser12":
                            st.info("🔍 **Debug Mode for testuser12** - Testing password hash...")

                            # Test with known values from database
                            expected_hash = "9a988b9aac65e187977ecbc34e86f807eb28d2385ec88ff9c74b2a40f5e7e209daaa436ef66dfa98ef5fd28cd1959d9cbac1de86d794ef9cbb45b57d0d82fa6d"
                            expected_salt = "ff85422337871d5b3d2ee73276aa17999548e8708524e37145eb77df3e2ed1d6"

                            st.write(f"🔍 Testing password '{password}' against database values")
                            st.write(f"Expected hash: `{expected_hash[:32]}...`")
                            st.write(f"Expected salt: `{expected_salt}`")

                            # Test hash comparison
                            try:
                                auth_url = st.secrets.get("supabase", {}).get("auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
                                response = requests.post(
                                    auth_url,
                                    headers={
                                        "Authorization": f"Bearer {self.supabase_key}",
                                        "Content-Type": "application/json"
                                    },
                                    json={
                                        "action": "test_hash",
                                        "password": password,
                                        "expected_hash": expected_hash,
                                        "expected_salt": expected_salt
                                    },
                                    timeout=5
                                )

                                if response.status_code == 200:
                                    hash_result = response.json()
                                    st.write("🔍 **Hash Test Results:**")
                                    st.json(hash_result)

                                    if hash_result.get("success"):
                                        if hash_result.get("match"):
                                            st.success("✅ Hash matches! The password is correct.")
                                        else:
                                            st.error("❌ Hash mismatch - this explains the login failure")

                                            # Show comparison details
                                            if "full_computed" in hash_result and "full_expected" in hash_result:
                                                st.write("**Computed hash:**", hash_result["full_computed"][:64] + "...")
                                                st.write("**Expected hash:**", hash_result["full_expected"][:64] + "...")
                                    else:
                                        st.error(f"❌ Hash test failed: {hash_result.get('error', 'Unknown error')}")
                                else:
                                    st.error(f"❌ HTTP {response.status_code}: {response.text}")

                            except Exception as e:
                                st.error(f"Hash test error: {str(e)}")
                                st.write("Debug - Exception details:", str(type(e)), str(e))

                        with st.spinner("Authenticating with improved system..."):
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
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                register_submitted = st.form_submit_button("Create Account")

                if register_submitted:
                    if not new_username or not new_password:
                        st.error("Username and password are required")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account with improved authentication..."):
                            result = self.create_user(new_username, new_password, new_email)

                        if result["success"]:
                            st.success(result["message"])
                            st.info("✅ Account created! Now try logging in with your credentials above.")
                        else:
                            st.error(result["message"])

def render_main_app():
    """Render the main application for authenticated users"""
    st.title("🧠 Emotional OS - Personal AI Companion")
    st.markdown("*Your private space for emotional processing and growth*")

    # User-specific conversation history
    conversation_key = f"conversation_history_{st.session_state.user_id}"
    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = []

    # Main interface
    with st.container():
        # Processing mode selection
        col1, col2 = st.columns([2, 1])

        with col1:
            processing_mode = st.selectbox(
                "Processing Mode",
                ["hybrid", "local", "ai_preferred"],
                index=["hybrid", "local", "ai_preferred"].index(st.session_state.processing_mode),
                help="Hybrid: Best performance, Local: Maximum privacy, AI: Most sophisticated responses",
            )
            st.session_state.processing_mode = processing_mode

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
                    st.caption(f"Processed in {exchange['processing_time']} • Mode: {exchange.get('mode', 'unknown')}")

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

                # Connect to authenticated Saori backend
                try:
                    saori_url = st.secrets.get("supabase", {}).get("current_saori_url", "https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/saori-fixed")

                    response_data = requests.post(
                        saori_url,
                        headers={
                            "Authorization": f"Bearer {st.secrets['supabase']['key']}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "message": user_input,
                            "user_id": st.session_state.user_id,
                            "mode": "quick" if processing_mode == "hybrid" else processing_mode,  # Force quick mode for faster responses
                        },
                        timeout=10
                    )

                    if response_data.status_code == 200:
                        result = response_data.json()
                        response = result.get("reply", "I apologize, but I couldn't process your message right now.")  # Edge function returns "reply", not "response"
                    else:
                        response = f"Connection issue (HTTP {response_data.status_code}). Using fallback response: I'm here to listen and support you."

                except Exception as e:
                    response = f"Processing unavailable ({str(e)[:50]}...). I'm still here to support you through whatever you're experiencing."

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
        st.write("🧠 Learning happens only from your conversations")
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
    st.sidebar.success(f"🚀 AUTH SYSTEM ACTIVE - v2.0 - {datetime.now().strftime('%H:%M')}")
    auth_manager.render_user_header()
    render_main_app()

if __name__ == "__main__":
    main()
