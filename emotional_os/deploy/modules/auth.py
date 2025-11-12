import datetime
import json
import uuid

try:
    import requests
except Exception:
    requests = None

import streamlit as st


class SaoynxAuthentication:
    """Authentication and session management"""

    def render_login_form(self, in_sidebar: bool = False):
        """Render the login form. If in_sidebar=True use sidebar-scoped keys/flags."""
        # When rendered inside the sidebar expander the expander already
        # displays the "Sign in" label. Avoid repeating the header in that
        # case to keep the UI compact.
        if not in_sidebar:
            # Render a compact header for the auth form so the spacing
            # between Sign In / Register sections is small (0.2rem).
            try:
                st.markdown(
                    """
                    <style>
                    /* Ensure our compact auth headers win over theme defaults */
                    .fp-auth-header h2 { margin: 0.2rem 0 !important; font-size: 1.25rem; }
                    .fp-auth-header + * { margin-top: 0.2rem !important; }
                    /* Reduce the internal gap used by Streamlit emotion containers
                       which otherwise default to 1rem (theme). Match the user's
                       requested 0.2rem spacing for auth forms. Scoped selectors
                       use both attribute-start and the observed concrete class
                       name to maximise robustness across builds. */
                    .fp-auth-header + * [class^="st-emotion-cache"] { gap: 0.2rem !important; }
                    .fp-auth-header + * .st-emotion-cache-1ads5z7 { gap: 0.2rem !important; }
                    /* Compact the actual form controls (non-sidebar) so margin/padding
                       between inputs, labels and buttons is reduced. This targets the
                       Streamlit control wrappers and their inner divs. */
                    .fp-auth-header + * .stTextInput, .fp-auth-header + * .stTextArea,
                    .fp-auth-header + * .stSelectbox, .fp-auth-header + * .stNumberInput,
                    .fp-auth-header + * .stButton {
                        margin-bottom: 6px !important;
                    }
                    .fp-auth-header + * .stTextInput > div, .fp-auth-header + * .stTextArea > div {
                        padding: 4px 0 !important;
                    }
                    .fp-auth-header + * label {
                        margin-bottom: 4px !important;
                        font-size: 0.95rem !important;
                    }
                    </style>
                    <div class="fp-auth-header"><h2>Sign In</h2></div>
                    """,
                    unsafe_allow_html=True,
                )
                # Inject a tiny runtime script to forcibly set the gap on the
                # immediate container following the header. Using a runtime
                # adjustment avoids specificity wars with Emotion-generated
                # styles and works across class name changes.
                try:
                    st.components.v1.html(
                        """
                        <script>
                        (function(){
                            try{
                                const header = document.querySelector('.fp-auth-header');
                                if(!header) return;
                                let container = header.parentElement;
                                while(container && container !== document.body){
                                    const cs = window.getComputedStyle(container);
                                    if(cs.display === 'flex' || cs.display === 'grid'){
                                        container.style.setProperty('gap','0.2rem','important');
                                        container.style.setProperty('margin-top','0.2rem','important');
                                        // Also reduce any emotion-generated child gaps
                                        const child = container.querySelector('[class^="st-emotion-cache"]');
                                        if(child) child.style.setProperty('gap','0.2rem','important');
                                        break;
                                    }
                                    container = container.parentElement;
                                }
                            }catch(e){/* no-op */}
                        })();
                        </script>
                        """,
                        height=0,
                    )
                except Exception:
                    pass
            except Exception:
                st.markdown("## Sign In")

        # If rendered in the sidebar, apply compact spacing CSS to reduce
        # vertical whitespace between form fields so the sidebar feels denser.
        if in_sidebar:
            try:
                st.markdown(
                    """
                    <style>
                    /* Compact form spacing for sidebar auth forms */
                    [data-testid="stSidebar"] .stTextInput, [data-testid="stSidebar"] .stTextArea,
                    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stNumberInput,
                    [data-testid="stSidebar"] .stButton {
                        margin-bottom: 6px !important;
                    }
                    [data-testid="stSidebar"] .stTextInput > div, [data-testid="stSidebar"] .stTextArea > div {
                        padding: 4px 0 !important;
                    }
                    [data-testid="stSidebar"] label {
                        margin-bottom: 4px !important;
                        font-size: 0.95rem !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                # Runtime patch for register form container (same rationale as above)
                try:
                    st.components.v1.html(
                        """
                        <script>
                        (function(){
                            try{
                                const header = document.querySelector('.fp-auth-header');
                                if(!header) return;
                                let container = header.parentElement;
                                while(container && container !== document.body){
                                    const cs = window.getComputedStyle(container);
                                    if(cs.display === 'flex' || cs.display === 'grid'){
                                        container.style.setProperty('gap','0.2rem','important');
                                        container.style.setProperty('margin-top','0.2rem','important');
                                        const child = container.querySelector('[class^="st-emotion-cache"]');
                                        if(child) child.style.setProperty('gap','0.2rem','important');
                                        break;
                                    }
                                    container = container.parentElement;
                                }
                            }catch(e){/* no-op */}
                        })();
                        </script>
                        """,
                        height=0,
                    )
                except Exception:
                    pass
            except Exception:
                pass
        key_user = "sidebar_login_username" if in_sidebar else "login_username"
        key_pass = "sidebar_login_password" if in_sidebar else "login_password"
        key_btn = "sidebar_login_btn" if in_sidebar else "login_btn"
        key_back = "sidebar_login_back_btn" if in_sidebar else "login_back_btn"

        username = st.text_input("Username", key=key_user)
        password = st.text_input("Password", type="password", key=key_pass)
        if st.button("Login", key=key_btn):
            result = self.authenticate_user(username, password)
            if result["success"]:
                st.session_state['post_login_message'] = result.get(
                    "message", "Signed in")
                st.session_state['post_login_transition'] = True
                if in_sidebar:
                    st.session_state['sidebar_show_login'] = False
                else:
                    st.session_state.show_login = False
                st.rerun()
            else:
                st.error(result["message"])
        if st.button("Back", key=key_back):
            if in_sidebar:
                st.session_state['sidebar_show_login'] = False
            else:
                st.session_state.show_login = False
            st.rerun()

    def render_register_form(self, in_sidebar: bool = False):
        """Render the register form. If in_sidebar=True use sidebar-scoped keys/flags."""
        # When rendered inside the sidebar expander the expander already
        # displays the "Register" label. Avoid repeating the header in that
        # case to keep the UI compact.
        if not in_sidebar:
            # Compact header for Register form to reduce vertical spacing
            try:
                st.markdown(
                    """
                    <style>
                    /* Ensure our compact auth headers win over theme defaults */
                    .fp-auth-header h2 { margin: 0.2rem 0 !important; font-size: 1.25rem; }
                    .fp-auth-header + * { margin-top: 0.2rem !important; }
                    /* Reduce the internal gap used by Streamlit emotion containers
                       to keep Register form compact like Sign In. Also compact the
                       non-sidebar form controls (labels/inputs/buttons). */
                    .fp-auth-header + * [class^="st-emotion-cache"] { gap: 0.2rem !important; }
                    .fp-auth-header + * .st-emotion-cache-1ads5z7 { gap: 0.2rem !important; }
                    .fp-auth-header + * .stTextInput, .fp-auth-header + * .stTextArea,
                    .fp-auth-header + * .stSelectbox, .fp-auth-header + * .stNumberInput,
                    .fp-auth-header + * .stButton {
                        margin-bottom: 6px !important;
                    }
                    .fp-auth-header + * .stTextInput > div, .fp-auth-header + * .stTextArea > div {
                        padding: 4px 0 !important;
                    }
                    .fp-auth-header + * label {
                        margin-bottom: 4px !important;
                        font-size: 0.95rem !important;
                    }
                    </style>
                    <div class="fp-auth-header"><h2>Register New Account</h2></div>
                    """,
                    unsafe_allow_html=True,
                )
            except Exception:
                st.markdown("## Register New Account")

        # Apply the same compact spacing when the register form is shown in the sidebar
        if in_sidebar:
            try:
                st.markdown(
                    """
                    <style>
                    /* Compact form spacing for sidebar auth forms */
                    [data-testid="stSidebar"] .stTextInput, [data-testid="stSidebar"] .stTextArea,
                    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stNumberInput,
                    [data-testid="stSidebar"] .stButton {
                        margin-bottom: 6px !important;
                    }
                    [data-testid="stSidebar"] .stTextInput > div, [data-testid="stSidebar"] .stTextArea > div {
                        padding: 4px 0 !important;
                    }
                    [data-testid="stSidebar"] label {
                        margin-bottom: 4px !important;
                        font-size: 0.95rem !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            except Exception:
                pass
        key_fn = "sidebar_register_first_name" if in_sidebar else "register_first_name"
        key_ln = "sidebar_register_last_name" if in_sidebar else "register_last_name"
        key_email = "sidebar_register_email" if in_sidebar else "register_email"
        key_user = "sidebar_register_username" if in_sidebar else "register_username"
        key_pass = "sidebar_register_password" if in_sidebar else "register_password"
        key_btn = "sidebar_register_btn" if in_sidebar else "register_btn"
        key_back = "sidebar_register_back_btn" if in_sidebar else "register_back_btn"

        first_name = st.text_input(
            "First name *", key=key_fn, help="Required field")
        last_name = st.text_input(
            "Last name *", key=key_ln, help="Required field")
        email = st.text_input("Email *", key=key_email, help="Required field")
        username = st.text_input(
            "Username *", key=key_user, help="Required field")
        password = st.text_input(
            "Password *", type="password", key=key_pass, help="Required field")

        # Debug: log the st.text_input return values
        print(
            f"DEBUG: st.text_input values - first_name: {repr(first_name)}, last_name: {repr(last_name)}, email: {repr(email)}, username: {repr(username)}")

        if st.button("Register", key=key_btn):
            # Debug: log the form values before validation
            print(
                f"DEBUG: Form values - first_name: {repr(first_name)}, last_name: {repr(last_name)}, email: {repr(email)}, username: {repr(username)}")

            # Client-side validation for required fields
            if not first_name or not first_name.strip():
                st.error("First name is required")
                return
            if not last_name or not last_name.strip():
                st.error("Last name is required")
                return
            if not email or not email.strip():
                st.error("Email is required")
                return
            if not username or not username.strip():
                st.error("Username is required")
                return
            if not password or not password.strip():
                st.error("Password is required")
                return

            # Basic email validation
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email address")
                return

            # Debug: log values after validation
            print(
                f"DEBUG: After validation - first_name: {repr(first_name)}, last_name: {repr(last_name)}, email: {repr(email)}")

            payload = {
                "action": "create_user",
                "username": username,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "created_at": datetime.datetime.now().isoformat()
            }

            # Debug: log the payload
            print(f"DEBUG: Payload being sent: {payload}")

            result = self.create_user(
                username, password, first_name=first_name.strip(), last_name=last_name.strip(), email=email.strip())

            if result["success"]:
                st.session_state['post_login_message'] = result.get(
                    "message", "Account created")
                st.session_state['post_login_transition'] = True
                if in_sidebar:
                    st.session_state['sidebar_show_register'] = False
                else:
                    st.session_state.show_register = False
                st.rerun()
            else:
                st.error(result["message"])
        if st.button("Back", key=key_back):
            if in_sidebar:
                st.session_state['sidebar_show_register'] = False
            else:
                st.session_state.show_register = False
            st.rerun()

    def __init__(self):
        try:
            self.supabase_url = st.secrets["supabase"]["url"]
            self.supabase_key = st.secrets["supabase"]["key"]
            self.supabase_configured = True
        except KeyError:
            # Allow demo mode without Supabase
            self.supabase_url = None
            self.supabase_key = None
            self.supabase_configured = False
            st.warning("⚠️ Running in demo mode - Supabase not configured")
        self.init_session_state()

    def create_session_token(self, username: str, user_id: str) -> str:
        import base64
        session_data = {
            "username": username,
            "user_id": user_id,
            "created": datetime.datetime.now().isoformat(),
            "expires": (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
        }
        token = base64.b64encode(json.dumps(session_data).encode()).decode()
        return token

    def validate_session_token(self, token: str) -> dict:
        try:
            import base64
            decoded_data = base64.b64decode(token.encode()).decode()
            session_data = json.loads(decoded_data)
            required_fields = ["username", "user_id", "expires"]
            for field in required_fields:
                if field not in session_data:
                    return {"valid": False, "error": f"Missing field: {field}"}
            try:
                expires = datetime.datetime.fromisoformat(
                    session_data["expires"])
                if datetime.datetime.now() < expires:
                    return {"valid": True, "data": session_data}
                return {"valid": False, "error": "Session expired"}
            except ValueError as e:
                return {"valid": False, "error": f"Invalid date format: {e}"}
        except Exception as e:
            return {"valid": False, "error": f"Token validation error: {str(e)}"}

    def init_session_state(self):
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'session_expires' not in st.session_state:
            st.session_state.session_expires = None
        if not st.session_state.authenticated:
            # Streamlit exposes query params as lists (e.g. {'session_token': ['...']}).
            # Be defensive: accept either a raw string or a single-element list.
            query_params = st.query_params or {}
            raw_token = query_params.get("session_token")
            session_token = None
            if isinstance(raw_token, (list, tuple)):
                session_token = raw_token[0] if raw_token else None
            else:
                session_token = raw_token

            if session_token:
                session_result = self.validate_session_token(
                    str(session_token))
                if session_result["valid"]:
                    data = session_result["data"]
                    st.session_state.authenticated = True
                    st.session_state.user_id = data["user_id"]
                    st.session_state.username = data["username"]
                    st.session_state.session_expires = data["expires"]
                else:
                    if "session_token" in st.query_params:
                        del st.query_params["session_token"]

    def authenticate_user(self, username: str, password: str) -> dict:
        if not self.supabase_configured:
            # Demo mode - accept any credentials
            if username and password:
                user_id = str(uuid.uuid4())
                st.session_state.authenticated = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.session_state.session_expires = (
                    datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
                session_token = self.create_session_token(username, user_id)
                st.query_params["session_token"] = session_token
                return {"success": True, "message": "Demo login successful"}
            return {"success": False, "message": "Please enter username and password"}

        try:
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
                if data.get("authenticated"):
                    st.session_state.authenticated = True
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.username = username
                    st.session_state.first_name = data.get("first_name")
                    st.session_state.last_name = data.get("last_name")
                    st.session_state.email = data.get("email")
                    # Store the JWT token for authenticated API calls
                    if data.get("token") or data.get("access_token"):
                        st.session_state.user_jwt_token = data.get(
                            "token") or data.get("access_token")
                    st.session_state.session_expires = (
                        datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
                    session_token = self.create_session_token(
                        username, data.get("user_id"))
                    st.query_params["session_token"] = session_token
                    return {"success": True, "message": "Login successful"}
                error_msg = data.get("error", "Invalid username or password")
                return {"success": False, "message": f"Login failed: {error_msg}"}
            return {"success": False, "message": f"Authentication service error (HTTP {response.status_code})"}
        except Exception as e:
            return {"success": False, "message": f"Login error: {str(e)}"}

    def create_user(self, username: str, password: str, first_name: str, last_name: str, email: str) -> dict:
        # Demo-mode behavior: create and auto-authenticate a demo user
        if not self.supabase_configured:
            if username and password:
                user_id = str(uuid.uuid4())
                st.session_state.authenticated = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                if first_name:
                    st.session_state['first_name'] = first_name
                if last_name:
                    st.session_state['last_name'] = last_name
                if email:
                    st.session_state['email'] = email
                st.session_state.session_expires = (
                    datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
                session_token = self.create_session_token(username, user_id)
                st.query_params["session_token"] = session_token
                return {"success": True, "message": "Demo account created and signed in"}
            return {"success": False, "message": "Please enter username and password"}

        try:
            auth_url = st.secrets.get("supabase", {}).get(
                "auth_function_url", f"{self.supabase_url}/functions/v1/auth-manager")
            payload = {
                "action": "create_user",
                "username": username,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "created_at": datetime.datetime.now().isoformat()
            }

            response = requests.post(
                auth_url,
                headers={
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # If the remote returned a user id/profile, auto-authenticate
                    user_id = data.get('user_id') or data.get('id')
                    if user_id:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        # Store the JWT token for authenticated API calls
                        if data.get("token") or data.get("access_token"):
                            st.session_state.user_jwt_token = data.get(
                                "token") or data.get("access_token")
                        if data.get('first_name'):
                            st.session_state['first_name'] = data.get(
                                'first_name')
                        if data.get('last_name'):
                            st.session_state['last_name'] = data.get(
                                'last_name')
                        if data.get('email'):
                            st.session_state['email'] = data.get('email')
                        st.session_state.session_expires = (
                            datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
                        session_token = self.create_session_token(
                            username, user_id)
                        st.query_params["session_token"] = session_token
                        return {"success": True, "message": "Account created and signed in"}
                    return {"success": True, "message": "Account created successfully"}
                return {"success": False, "message": data.get("error", "Failed to create account")}
            error_data = response.json() if response.headers.get(
                'content-type', '').startswith('application/json') else {}
            return {"success": False, "message": error_data.get("error", "Failed to create account")}
        except Exception as e:
            return {"success": False, "message": f"Registration error: {str(e)}"}

    def quick_login_bypass(self):
        user_id = str(uuid.uuid4())
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.username = "demo_user"
        st.session_state.session_expires = (
            datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
        session_token = self.create_session_token("demo_user", user_id)
        st.query_params["session_token"] = session_token
        # Indicate a lightweight post-login transition so the UI shows a confirmation
        st.session_state['post_login_message'] = "Signed in as demo_user"
        st.session_state['post_login_transition'] = True
        st.rerun()

    def logout(self):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.user_jwt_token = None  # Clear JWT token
        st.session_state.session_expires = None
        if "session_token" in st.query_params:
            del st.query_params["session_token"]
        st.rerun()
