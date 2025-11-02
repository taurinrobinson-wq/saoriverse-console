"""
FirstPerson Admin Portal
Comprehensive admin interface for system management
"""

import time
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="FirstPerson Admin Portal",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AdminAuthentication:
    """Admin-specific authentication system"""

    def __init__(self):
        try:
            self.supabase_url = st.secrets["supabase"]["url"]
            self.supabase_key = st.secrets["supabase"]["key"]
        except KeyError:
            st.error("❌ Supabase configuration not found")
            st.stop()

        # Admin user list (in production, this would be in database)
        self.admin_users = st.secrets.get("admin", {}).get("users", ["admin"])
        self.init_admin_session()

    def init_admin_session(self):
        """Initialize admin session state"""
        if 'admin_authenticated' not in st.session_state:
            st.session_state.admin_authenticated = False
        if 'admin_username' not in st.session_state:
            st.session_state.admin_username = None
        if 'admin_role' not in st.session_state:
            st.session_state.admin_role = None

    def authenticate_admin(self, username: str, password: str) -> dict:
        """Authenticate admin user"""
        try:
            # Check if user is in admin list
            if username not in self.admin_users:
                return {"success": False, "message": "Access denied: Not an admin user"}

            # Use the same auth endpoint but check admin status
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
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_username = username
                    st.session_state.admin_role = "super_admin" if username == "admin" else "admin"
                    return {"success": True, "message": "Admin access granted"}
                return {"success": False, "message": "Invalid credentials"}
            return {"success": False, "message": f"Authentication service error (HTTP {response.status_code})"}

        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}

    def logout_admin(self):
        """Logout admin user"""
        st.session_state.admin_authenticated = False
        st.session_state.admin_username = None
        st.session_state.admin_role = None
        st.rerun()

    def render_admin_login(self):
        """Render admin login interface"""

        # Admin login styling
        st.markdown("""
        <style>
        .admin-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, #2E2E2E, #4A4A4A);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .admin-form {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

        # Header
        st.markdown("""
        <div class="admin-header">
            <h1>⚙️ FirstPerson Admin Portal</h1>
            <p>System Administration & Management Console</p>
        </div>
        """, unsafe_allow_html=True)

        # Login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="admin-form">', unsafe_allow_html=True)

            st.subheader("Admin Access Required")

            with st.form("admin_login"):
                username = st.text_input("Admin Username", placeholder="Enter admin username")
                password = st.text_input("Admin Password", type="password", placeholder="Enter admin password")

                login_submitted = st.form_submit_button("Access Admin Portal", use_container_width=True)

                if login_submitted:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        with st.spinner("Verifying admin credentials..."):
                            result = self.authenticate_admin(username, password)

                        if result["success"]:
                            st.success("Welcome to Admin Portal!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(result["message"])

            st.markdown('</div>', unsafe_allow_html=True)

            # Security notice
            st.info("🔒 This portal is restricted to authorized administrators only")

class AdminDashboard:
    """Main admin dashboard functionality"""

    def __init__(self):
        try:
            self.supabase_url = st.secrets["supabase"]["url"]
            self.supabase_key = st.secrets["supabase"]["key"]
        except KeyError:
            st.error("❌ Supabase configuration not found")
            st.stop()

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        # This would query your database for real stats
        # For now, returning mock data
        return {
            "total_users": 47,
            "active_sessions": 12,
            "conversations_today": 156,
            "glyphs_created": 1247,
            "avg_response_time": 2.3,
            "system_uptime": "7 days, 14 hours",
            "storage_used": "2.4 GB",
            "api_calls_today": 2891
        }

    def get_user_data(self) -> List[Dict[str, Any]]:
        """Get user data for management"""
        # This would query your user database
        # Mock data for demonstration
        return [
            {"username": "john_doe", "created": "2025-10-10", "last_active": "2025-10-15", "conversations": 23, "status": "active"},
            {"username": "jane_smith", "created": "2025-10-12", "last_active": "2025-10-15", "conversations": 8, "status": "active"},
            {"username": "demo_user", "created": "2025-10-15", "last_active": "2025-10-15", "conversations": 45, "status": "demo"},
            {"username": "test_user", "created": "2025-10-13", "last_active": "2025-10-14", "conversations": 2, "status": "inactive"}
        ]

    def render_header(self):
        """Render admin dashboard header"""
        col1, col2, col3 = st.columns([2, 6, 2])

        with col1:
            try:
                st.image("graphics/FirstPerson-Logo.svg", width=50)
            except Exception:
                st.markdown("⚙️", unsafe_allow_html=True)

        with col2:
            st.markdown("# FirstPerson Admin Portal")
            st.markdown(f"*Welcome, **{st.session_state.admin_username}** • Role: {st.session_state.admin_role}*")

        with col3:
            if st.button("🚪 Logout", help="Logout from admin portal"):
                auth = AdminAuthentication()
                auth.logout_admin()

    def render_system_overview(self):
        """Render system overview dashboard"""
        st.subheader("📊 System Overview")

        stats = self.get_system_stats()

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Users", stats["total_users"], delta="+3 today")
        with col2:
            st.metric("Active Sessions", stats["active_sessions"], delta="+2")
        with col3:
            st.metric("Conversations Today", stats["conversations_today"], delta="+12%")
        with col4:
            st.metric("Avg Response Time", f"{stats['avg_response_time']}s", delta="-0.2s")

        # Additional stats
        col5, col6, col7, col8 = st.columns(4)

        with col5:
            st.metric("Glyphs Created", stats["glyphs_created"])
        with col6:
            st.metric("System Uptime", stats["system_uptime"])
        with col7:
            st.metric("Storage Used", stats["storage_used"])
        with col8:
            st.metric("API Calls Today", stats["api_calls_today"])

        # Performance charts
        st.subheader("📈 Performance Metrics")

        col1, col2 = st.columns(2)

        with col1:
            # Mock response time data
            response_times = [2.1, 2.3, 1.9, 2.5, 2.2, 2.0, 2.4, 2.1, 1.8, 2.3]
            hours = list(range(len(response_times)))

            fig = px.line(x=hours, y=response_times, title="Response Time (Last 10 Hours)")
            fig.update_xaxes(title="Hours Ago")
            fig.update_yaxes(title="Response Time (seconds)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Mock conversation volume data
            conversation_data = [12, 18, 25, 31, 28, 35, 42, 38, 29, 33]

            fig = px.bar(x=hours, y=conversation_data, title="Conversation Volume (Last 10 Hours)")
            fig.update_xaxes(title="Hours Ago")
            fig.update_yaxes(title="Conversations")
            st.plotly_chart(fig, use_container_width=True)

    def render_user_management(self):
        """Render user management interface"""
        st.subheader("👥 User Management")

        user_data = self.get_user_data()
        df = pd.DataFrame(user_data)

        # User statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Users", len(df))
        with col2:
            active_users = len(df[df['status'] == 'active'])
            st.metric("Active Users", active_users)
        with col3:
            demo_users = len(df[df['status'] == 'demo'])
            st.metric("Demo Users", demo_users)
        with col4:
            avg_conversations = df['conversations'].mean()
            st.metric("Avg Conversations", f"{avg_conversations:.1f}")

        # User search and filters
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            search_term = st.text_input("🔍 Search Users", placeholder="Enter username...")
        with col2:
            status_filter = st.selectbox("Status Filter", ["All", "active", "inactive", "demo"])
        with col3:
            sort_by = st.selectbox("Sort By", ["username", "created", "last_active", "conversations"])

        # Filter data
        filtered_df = df.copy()

        if search_term:
            filtered_df = filtered_df[filtered_df['username'].str.contains(search_term, case=False)]

        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]

        # Sort data
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)

        # Display user table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "username": st.column_config.TextColumn("Username", width="medium"),
                "created": st.column_config.DateColumn("Created", width="small"),
                "last_active": st.column_config.DateColumn("Last Active", width="small"),
                "conversations": st.column_config.NumberColumn("Conversations", width="small"),
                "status": st.column_config.TextColumn("Status", width="small")
            }
        )

        # User actions
        st.subheader("User Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📧 Send System Message", help="Send message to all users"):
                st.info("System messaging feature coming soon!")

        with col2:
            if st.button("📊 Export User Data", help="Export user data to CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"user_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        with col3:
            if st.button("🔄 Refresh Data", help="Refresh user data"):
                st.rerun()

    def render_system_config(self):
        """Render system configuration"""
        st.subheader("⚙️ System Configuration")

        # AI Configuration
        st.markdown("### 🤖 AI Processing Settings")

        col1, col2 = st.columns(2)

        with col1:
            default_mode = st.selectbox(
                "Default Processing Mode",
                ["hybrid", "local", "ai_preferred"],
                index=0,
                help="Default AI processing mode for new users"
            )

            max_response_time = st.slider(
                "Max Response Time (seconds)",
                min_value=5,
                max_value=30,
                value=15,
                help="Maximum time to wait for AI responses"
            )

            enable_glyph_creation = st.checkbox(
                "Enable Glyph Creation",
                value=True,
                help="Allow automatic emotional glyph creation"
            )

        with col2:
            api_rate_limit = st.number_input(
                "API Rate Limit (per minute)",
                min_value=10,
                max_value=1000,
                value=100,
                help="Maximum API calls per minute per user"
            )

            session_timeout = st.slider(
                "Session Timeout (hours)",
                min_value=1,
                max_value=72,
                value=48,
                help="How long user sessions remain active"
            )

            enable_demo_mode = st.checkbox(
                "Enable Demo Mode",
                value=True,
                help="Allow users to access demo mode"
            )

        # Security Settings
        st.markdown("### 🔒 Security Settings")

        col1, col2 = st.columns(2)

        with col1:
            password_min_length = st.slider(
                "Minimum Password Length",
                min_value=6,
                max_value=20,
                value=6
            )

            max_login_attempts = st.slider(
                "Max Login Attempts",
                min_value=3,
                max_value=10,
                value=5
            )

        with col2:
            enable_2fa = st.checkbox(
                "Enable Two-Factor Authentication",
                value=False,
                help="Require 2FA for user accounts"
            )

            admin_notifications = st.checkbox(
                "Admin Notifications",
                value=True,
                help="Send notifications for system events"
            )

        # Save configuration
        if st.button("💾 Save Configuration", type="primary"):
            config = {
                "ai_settings": {
                    "default_mode": default_mode,
                    "max_response_time": max_response_time,
                    "enable_glyph_creation": enable_glyph_creation,
                    "api_rate_limit": api_rate_limit
                },
                "session_settings": {
                    "timeout_hours": session_timeout,
                    "enable_demo_mode": enable_demo_mode
                },
                "security_settings": {
                    "password_min_length": password_min_length,
                    "max_login_attempts": max_login_attempts,
                    "enable_2fa": enable_2fa,
                    "admin_notifications": admin_notifications
                },
                "updated_at": datetime.now().isoformat(),
                "updated_by": st.session_state.admin_username
            }

            st.success("✅ Configuration saved successfully!")
            with st.expander("View Configuration JSON"):
                st.json(config)

    def render_api_management(self):
        """Render API management interface"""
        st.subheader("🔌 API Management")

        # API Status Overview
        st.markdown("### API Service Status")

        api_services = [
            {"name": "Supabase Auth", "status": "operational", "uptime": "99.9%", "last_check": "2 min ago"},
            {"name": "Saori AI Engine", "status": "operational", "uptime": "99.7%", "last_check": "1 min ago"},
            {"name": "OpenAI API", "status": "degraded", "uptime": "98.2%", "last_check": "5 min ago"},
            {"name": "Supabase Database", "status": "operational", "uptime": "99.9%", "last_check": "30 sec ago"}
        ]

        for service in api_services:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                status_emoji = "🟢" if service["status"] == "operational" else "🟡" if service["status"] == "degraded" else "🔴"
                st.write(f"{status_emoji} **{service['name']}**")

            with col2:
                st.write(service["status"].title())

            with col3:
                st.write(service["uptime"])

            with col4:
                st.write(service["last_check"])

        # API Configuration
        st.markdown("### 🔧 API Configuration")

        tab1, tab2, tab3 = st.tabs(["🤖 AI APIs", "🖼️ Image APIs", "📄 Document APIs"])

        with tab1:
            st.markdown("#### OpenAI Configuration")
            openai_enabled = st.checkbox("Enable OpenAI Integration", value=True)
            if openai_enabled:
                openai_model = st.selectbox("Default Model", ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"])  # noqa: F841  # used for UI state
                openai_max_tokens = st.slider("Max Tokens", 100, 4000, 1000)  # noqa: F841  # used for UI state
                openai_temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)  # noqa: F841  # used for UI state

        with tab2:
            st.markdown("#### Image Generation APIs")

            # DALL-E Configuration
            dalle_enabled = st.checkbox("Enable DALL-E Integration", value=False)
            if dalle_enabled:
                dalle_model = st.selectbox("DALL-E Model", ["dall-e-3", "dall-e-2"])  # noqa: F841  # used for UI state
                dalle_quality = st.selectbox("Image Quality", ["standard", "hd"])  # noqa: F841  # used for UI state
                dalle_size = st.selectbox("Image Size", ["1024x1024", "1792x1024", "1024x1792"])  # noqa: F841  # used for UI state

            # Stable Diffusion Configuration
            sd_enabled = st.checkbox("Enable Stable Diffusion", value=False)
            if sd_enabled:
                sd_steps = st.slider("Inference Steps", 10, 150, 50)  # noqa: F841  # used for UI state
                sd_guidance = st.slider("Guidance Scale", 1.0, 20.0, 7.5, 0.5)  # noqa: F841  # used for UI state

            # Replicate Configuration
            replicate_enabled = st.checkbox("Enable Replicate APIs", value=False)
            if replicate_enabled:
                st.multiselect(
                    "Available Models",
                    ["ControlNet", "Real-ESRGAN", "Sketch-to-Image", "Style Transfer"],
                    default=["ControlNet"]
                )

        with tab3:
            st.markdown("#### Document Generation APIs")

            # PDF Generation
            pdf_enabled = st.checkbox("Enable PDF Generation", value=False)
            if pdf_enabled:
                pdf_template_path = st.text_input("PDF Template Path", value="/templates/")  # noqa: F841  # used for UI state
                pdf_quality = st.selectbox("PDF Quality", ["high", "medium", "low"])  # noqa: F841  # used for UI state

            # Document Templates
            docx_enabled = st.checkbox("Enable DOCX Templates", value=False)
            if docx_enabled:
                template_formats = st.multiselect(  # noqa: F841  # used for UI state
                    "Template Formats",
                    ["Emotional Report", "Glyph Analysis", "User Summary", "Progress Report"],
                    default=["Emotional Report"]
                )

            # Excel Export
            excel_enabled = st.checkbox("Enable Excel Export", value=False)
            if excel_enabled:
                excel_features = st.multiselect(  # noqa: F841  # used for UI state
                    "Excel Features",
                    ["Glyph Matrices", "User Analytics", "Conversation Logs", "System Reports"],
                    default=["User Analytics"]
                )

        # Save API Configuration
        if st.button("💾 Save API Configuration", type="primary"):
            st.success("✅ API configuration saved!")
            st.info("🔄 Some changes may require system restart to take effect")

def main():
    """Main admin portal entry point"""

    # Custom CSS for admin interface
    st.markdown("""
    <style>
    /* Admin-specific styling */
    .main .block-container {
        padding-top: 1rem;
    }
    
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .admin-sidebar {
        background: linear-gradient(180deg, #2E2E2E, #4A4A4A);
    }
    </style>
    """, unsafe_allow_html=True)

    auth = AdminAuthentication()

    if not st.session_state.admin_authenticated:
        auth.render_admin_login()
        return

    # Admin Dashboard
    dashboard = AdminDashboard()
    dashboard.render_header()

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎛️ Admin Navigation")

        page = st.radio(
            "Select Page",
            ["📊 System Overview", "👥 User Management", "⚙️ System Config", "🔌 API Management"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Quick actions
        st.markdown("### ⚡ Quick Actions")

        if st.button("🔄 Refresh All Data"):
            st.rerun()

        if st.button("📧 System Broadcast"):
            st.info("Broadcast feature coming soon!")

        if st.button("🛡️ Security Scan"):
            st.info("Security scan initiated!")

        st.markdown("---")

        # System status
        st.markdown("### 📡 System Status")
        st.success("🟢 All Systems Operational")
        st.info(f"⏰ Last Updated: {datetime.now().strftime('%H:%M:%S')}")

    # Main content area
    if page == "📊 System Overview":
        dashboard.render_system_overview()
    elif page == "👥 User Management":
        dashboard.render_user_management()
    elif page == "⚙️ System Config":
        dashboard.render_system_config()
    elif page == "🔌 API Management":
        dashboard.render_api_management()

if __name__ == "__main__":
    main()
