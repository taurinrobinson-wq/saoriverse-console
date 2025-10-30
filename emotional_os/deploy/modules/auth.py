import streamlit as st
import requests
import json
import datetime
import uuid

class SaoynxAuthentication:
    def render_login_form(self):
        st.markdown("## Sign In")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn"):
            result = self.authenticate_user(username, password)
            if result["success"]:
                st.success(result["message"])
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error(result["message"])
        if st.button("Back", key="login_back_btn"):
            st.session_state.show_login = False
            st.rerun()

    def render_register_form(self):
        st.markdown("## Register New Account")
        username = st.text_input("Username", key="register_username")
        password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register", key="register_btn"):
            result = self.create_user(username, password)
            if result["success"]:
                st.success(result["message"])
                st.session_state.show_register = False
                st.rerun()
            else:
                st.error(result["message"])
        if st.button("Back", key="register_back_btn"):
            st.session_state.show_register = False
            st.rerun()
    """Authentication and session management"""
    def __init__(self):
        try:
            self.supabase_url = st.secrets["supabase"]["url"]
            self.supabase_key = st.secrets["supabase"]["key"]
        except KeyError:
            st.error("❌ Supabase configuration not found in secrets")
            st.stop()
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
                expires = datetime.datetime.fromisoformat(session_data["expires"])
                if datetime.datetime.now() < expires:
                    return {"valid": True, "data": session_data}
                else:
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
            query_params = st.query_params
            session_token = query_params.get("session_token")
            if session_token:
                session_result = self.validate_session_token(session_token)
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
        try:
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
                if data.get("authenticated"):
                    st.session_state.authenticated = True
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.username = username
                    st.session_state.session_expires = (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
                    session_token = self.create_session_token(username, data.get("user_id"))
                    st.query_params["session_token"] = session_token
                    return {"success": True, "message": "Login successful"}
                else:
                    error_msg = data.get("error", "Invalid username or password")
                    return {"success": False, "message": f"Login failed: {error_msg}"}
            else:
                return {"success": False, "message": f"Authentication service error (HTTP {response.status_code})"}
        except Exception as e:
            return {"success": False, "message": f"Login error: {str(e)}"}
    def create_user(self, username: str, password: str) -> dict:
        try:
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
                    "password": password,
                    "created_at": datetime.datetime.now().isoformat()
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {"success": True, "message": "Account created successfully"}
                else:
                    return {"success": False, "message": data.get("error", "Failed to create account")}
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                return {"success": False, "message": error_data.get("error", "Failed to create account")}
        except Exception as e:
            return {"success": False, "message": f"Registration error: {str(e)}"}
    def quick_login_bypass(self):
        user_id = str(uuid.uuid4())
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.username = "demo_user"
        st.session_state.session_expires = (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
        session_token = self.create_session_token("demo_user", user_id)
        st.query_params["session_token"] = session_token
        st.rerun()
    def logout(self):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.session_expires = None
        if "session_token" in st.query_params:
            del st.query_params["session_token"]
        st.rerun()
