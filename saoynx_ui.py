"""
Clean SAOYNX UI - Professional login interface
Based on the splash page design with clean branding
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta
import hashlib
import secrets

# Page configuration
st.set_page_config(
    page_title="SAOYNX - AI Emotional Interfaces",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

class SaoynxAuthentication:
    """Clean authentication system matching SAOYNX design"""
    
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
        if 'session_expires' not in st.session_state:
            st.session_state.session_expires = None
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user login"""
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
                    # Set session state
                    st.session_state.authenticated = True
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.username = username
                    st.session_state.session_expires = (datetime.now() + timedelta(hours=8)).isoformat()
                    
                    return {"success": True, "message": "Login successful"}
                else:
                    error_msg = data.get("error", "Invalid username or password")
                    return {"success": False, "message": f"Login failed: {error_msg}"}
            else:
                return {"success": False, "message": f"Authentication service error (HTTP {response.status_code})"}
                
        except Exception as e:
            return {"success": False, "message": f"Login error: {str(e)}"}
    
    def create_user(self, username: str, password: str) -> dict:
        """Create new user account"""
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
                    "created_at": datetime.now().isoformat()
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
        """Quick demo access"""
        import uuid
        
        st.session_state.authenticated = True
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.username = "demo_user"
        st.session_state.session_expires = (datetime.now() + timedelta(hours=8)).isoformat()
        
        st.rerun()
    
    def logout(self):
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.session_expires = None
        st.rerun()
    
    def render_splash_interface(self):
        """Render the clean SAOYNX splash interface"""
        
        # Custom CSS matching your design
        st.markdown("""
        <style>
        /* Hide Streamlit default elements */
        .stDeployButton {display: none;}
        header[data-testid="stHeader"] {display: none;}
        .stMainBlockContainer {padding-top: 2rem;}
        
        /* Main container */
        .main-splash {
            max-width: 700px;
            margin: 0 auto;
            padding: 1.5rem 2rem;
            text-align: center;
        }
        
        /* Logo section */
        .logo-section {
            margin-bottom: 2rem;
        }
        
        .logo-text {
            font-size: 2.8rem;
            font-weight: 300;
            letter-spacing: 8px;
            color: #2E2E2E;
            margin: 0.8rem 0 0.3rem 0;
            font-family: 'Arial', sans-serif;
        }
        
        .logo-subtitle {
            font-size: 0.9rem;
            color: #666;
            letter-spacing: 4px;
            font-weight: 300;
            text-transform: uppercase;
            line-height: 1.2;
        }
        
        /* Auth sections */
        .auth-container {
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin: 2rem 0;
        }
        
        .auth-section {
            text-align: center;
            min-width: 180px;
        }
        
        .auth-title {
            font-size: 1.4rem;
            color: #2E2E2E;
            margin-bottom: 1.5rem;
            font-weight: 300;
        }
        
        /* Form styling */
        .stTextInput > div > div > input {
            border-radius: 30px;
            border: 2px solid #ddd;
            padding: 12px 20px;
            font-size: 1rem;
            text-align: center;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #666;
            box-shadow: 0 0 0 1px #666;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 30px;
            border: 2px solid #2E2E2E;
            background-color: #2E2E2E;
            color: white;
            padding: 12px 30px;
            font-size: 1rem;
            font-weight: 500;
            letter-spacing: 2px;
            text-transform: uppercase;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: white;
            color: #2E2E2E;
            border-color: #2E2E2E;
        }
        
        /* Quick access */
        .quick-access {
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #eee;
        }
        
        .quick-title {
            color: #999;
            font-size: 0.8rem;
            margin-bottom: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main container
        st.markdown('<div class="main-splash">', unsafe_allow_html=True)
        
        # Logo section
        st.markdown('<div class="logo-section">', unsafe_allow_html=True)
        
        # Display logo
        try:
            # Center the logo - use cleaner version
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image("Saonyx_Logo2.png", width=120)
        except:
            # Fallback if logo not found
            st.markdown('<div style="font-size: 2.5rem; color: #666;">🧠</div>', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="logo-text">SAOYNX</div>
        <div class="logo-subtitle">AI EMOTIONAL<br>INTERFACES</div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle different states
        if st.session_state.get('show_login', False):
            self.render_login_form()
        elif st.session_state.get('show_register', False):
            self.render_register_form()
        else:
            # Main splash screen - two columns as per your design
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                st.markdown('<div class="auth-section">', unsafe_allow_html=True)
                st.markdown('<div class="auth-title">existing user?</div>', unsafe_allow_html=True)
                
                if st.button("Sign In", key="existing_btn", use_container_width=False):
                    st.session_state.show_login = True
                    st.rerun()
                    
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="auth-section">', unsafe_allow_html=True)
                st.markdown('<div class="auth-title">new user?</div>', unsafe_allow_html=True)
                
                if st.button("Register Now", key="new_btn", use_container_width=False):
                    st.session_state.show_register = True
                    st.rerun()
                    
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Quick access section
            st.markdown('<div class="quick-access">', unsafe_allow_html=True)
            st.markdown('<div class="quick-title">Quick Access</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("⚡ Demo Mode", help="Try the system instantly"):
                    self.quick_login_bypass()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_login_form(self):
        """Clean login form matching your design"""
        
        st.markdown('<div class="main-splash">', unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back", key="back_login"):
            st.session_state.show_login = False
            st.rerun()
        
        # Logo (smaller)
        try:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image("Saonyx_Logo2.png", width=80)
        except:
            st.markdown('<div style="font-size: 2rem; text-align: center; color: #666;">🧠</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-title" style="text-align: center; margin: 1rem 0;">Sign In</div>', unsafe_allow_html=True)
        
        # Login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                # Match your design labels
                st.markdown('<div style="text-align: left; margin-bottom: 0.3rem; color: #666; font-size: 0.9rem;">login:</div>', unsafe_allow_html=True)
                username = st.text_input("login", label_visibility="collapsed", placeholder="username")
                
                st.markdown('<div style="text-align: left; margin-bottom: 0.3rem; margin-top: 0.8rem; color: #666; font-size: 0.9rem;">password:</div>', unsafe_allow_html=True)
                password = st.text_input("password", label_visibility="collapsed", type="password", placeholder="password")
                
                st.markdown('<div style="margin: 1rem 0 0.5rem 0;"></div>', unsafe_allow_html=True)
                login_submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if login_submitted:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        with st.spinner("Signing in..."):
                            result = self.authenticate_user(username, password)
                        
                        if result["success"]:
                            st.success("Welcome back!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(result["message"])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_register_form(self):
        """Clean registration form"""
        
        st.markdown('<div class="main-splash">', unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back", key="back_register"):
            st.session_state.show_register = False
            st.rerun()
        
        # Logo (smaller)
        try:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image("Saonyx_Logo2.png", width=80)
        except:
            st.markdown('<div style="font-size: 2rem; text-align: center; color: #666;">🧠</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-title" style="text-align: center; margin: 1rem 0;">Create Account</div>', unsafe_allow_html=True)
        
        # Register form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                # Match your design labels
                st.markdown('<div style="text-align: left; margin-bottom: 0.3rem; color: #666; font-size: 0.9rem;">login:</div>', unsafe_allow_html=True)
                username = st.text_input("login", label_visibility="collapsed", placeholder="choose username")
                
                st.markdown('<div style="text-align: left; margin-bottom: 0.3rem; margin-top: 0.8rem; color: #666; font-size: 0.9rem;">password:</div>', unsafe_allow_html=True)
                password = st.text_input("password", label_visibility="collapsed", type="password", placeholder="choose password")
                
                st.markdown('<div style="text-align: left; margin-bottom: 0.3rem; margin-top: 0.8rem; color: #666; font-size: 0.9rem;">confirm:</div>', unsafe_allow_html=True)
                confirm_password = st.text_input("confirm", label_visibility="collapsed", type="password", placeholder="confirm password")
                
                st.markdown('<div style="margin: 1rem 0 0.5rem 0;"></div>', unsafe_allow_html=True)
                register_submitted = st.form_submit_button("Register Now", use_container_width=True)
                
                if register_submitted:
                    if not username or not password:
                        st.error("Username and password are required")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating your account..."):
                            result = self.create_user(username, password)
                        
                        if result["success"]:
                            st.success("Account created! Please sign in.")
                            st.session_state.show_register = False
                            st.session_state.show_login = True
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(result["message"])
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_main_app():
    """Main app interface for authenticated users"""
    st.markdown("### 🧠 Welcome to SAOYNX")
    st.write(f"Hello, **{st.session_state.username}**!")
    
    if st.button("Sign Out"):
        auth = SaoynxAuthentication()
        auth.logout()
    
    # Your main app content here
    st.write("Main application interface goes here...")

def main():
    """Main application entry point"""
    auth = SaoynxAuthentication()
    
    # Check if user is authenticated
    if st.session_state.authenticated:
        render_main_app()
    else:
        auth.render_splash_interface()

if __name__ == "__main__":
    main()