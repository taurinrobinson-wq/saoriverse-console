    def render_login_form(self):
        """Render ultra-clean login form"""
        st.title("🚀 Emotional OS")
        st.markdown("*Your Personal AI Companion*")
        
        # Show working account form if requested
        if st.session_state.get('show_working_account_form', False):
            self.create_working_account()
            if st.button("← Back"):
                st.session_state.show_working_account_form = False
                st.rerun()
            return
        
        # Ultra-clean interface - just two buttons
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Create Account", type="primary", use_container_width=True):
                st.session_state.show_working_account_form = True
                st.rerun()
        
        with col2:
            if st.button("⚡ Quick Demo", type="secondary", use_container_width=True):
                self.quick_login_bypass()
                return
        
        # Optional: Add hidden advanced settings
        with st.expander("⚙️ Advanced", expanded=False):
            if st.button("🔧 Debug"):
                self.test_backend_connection()