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

    def render_login_form(self):
        st.markdown("## Sign In")
        username = st.text_input("Username", key="login_username")
        password = st.text_input(
            "Password", type="password", key="login_password")
        if st.button("Login", key="login_btn"):
            result = self.authenticate_user(username, password)
            if result["success"]:
                # Set a transient post-login transition so the UI can show
                # a gentle confirmation toast before moving into the main UI.
                st.session_state['post_login_message'] = result.get(
                    "message", "Signed in")
                st.session_state['post_login_transition'] = True
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error(result["message"])
        if st.button("Back", key="login_back_btn"):
            st.session_state.show_login = False
            st.rerun()

    def render_register_form(self):
        st.markdown("## Register New Account")
        # Collect first/last name and email to populate user profile
        first_name = st.text_input("First name", key="register_first_name")
        last_name = st.text_input("Last name", key="register_last_name")
        email = st.text_input("Email", key="register_email")
        username = st.text_input("Username", key="register_username")
        password = st.text_input(
            "Password", type="password", key="register_password")
        if st.button("Register", key="register_btn"):
            result = self.create_user(
                username, password, first_name=first_name, last_name=last_name, email=email)
            if result["success"]:
                # Trigger the same post-login transition used for login
                st.session_state['post_login_message'] = result.get(
                    "message", "Account created")
                st.session_state['post_login_transition'] = True
                st.session_state.show_register = False
                st.rerun()
            else:
                st.error(result["message"])
        if st.button("Back", key="register_back_btn"):
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

    def create_user(self, username: str, password: str, first_name: str = None, last_name: str = None, email: str = None) -> dict:
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
                "created_at": datetime.datetime.now().isoformat()
            }
            if first_name:
                payload['first_name'] = first_name
            if last_name:
                payload['last_name'] = last_name
            if email:
                payload['email'] = email

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
        st.session_state.session_expires = None
        if "session_token" in st.query_params:
            del st.query_params["session_token"]
        st.rerun()
