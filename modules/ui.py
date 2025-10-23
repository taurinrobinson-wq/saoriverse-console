
import streamlit as st
import time
import requests
import datetime
import json
from modules.auth import SaoynxAuthentication
from modules.doc_export import generate_doc

def inject_css(css_file_path):
    with open(css_file_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# UI rendering functions

def render_splash_interface(auth):
    inject_css("emotional_os_ui.css")
    st.markdown('<div style="text-align: center; margin-bottom: 1rem;">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            st.image("graphics/FirstPerson-Logo.svg", width=200)
        except:
            st.markdown('''
            <div style="font-size: 4rem;">🧠</div>
            <div style="font-size: 2rem; font-weight: 300; letter-spacing: 4px; color: #2E2E2E; margin: 0.5rem 0 0.2rem 0;">FirstPerson</div>
            <div style="font-size: 1rem; color: #666; letter-spacing: 2px; font-weight: 300; text-transform: uppercase;">Personal AI<br>Companion</div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.get('show_login', False):
        auth.render_login_form()
    elif st.session_state.get('show_register', False):
        auth.render_register_form()
    else:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            qcol1, qcol2 = st.columns([1, 1], gap="small")
            with qcol1:
                st.markdown('<div class="auth-question">existing user?</div>', unsafe_allow_html=True)
            with qcol2:
                st.markdown('<div class="auth-question">new user?</div>', unsafe_allow_html=True)
            bcol1, bcol2 = st.columns([1, 1], gap="small")
            with bcol1:
                if st.button("Sign In", key="existing_btn"):
                    st.session_state.show_login = True
                    st.rerun()
            with bcol2:
                if st.button("Register Now", key="new_btn"):
                    st.session_state.show_register = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="quick-access">', unsafe_allow_html=True)
        st.markdown('<div class="quick-title">Quick Access</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("⚡ Demo Mode", help="Try the system instantly"):
                auth.quick_login_bypass()
        st.markdown('</div>', unsafe_allow_html=True)

def render_main_app():
    inject_css("emotional_os_ui.css")
    col1, col2 = st.columns([0.5, 8], gap="small")
    with col1:
        try:
            st.image("graphics/FirstPerson-Logo.svg", width=50)
        except:
            st.markdown('<div style="font-size: 2.5rem; margin: 0; line-height: 1;">🧠</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<h1 style="margin: 0; margin-left: -35px; padding-top: 10px; color: #2E2E2E; font-weight: 300; letter-spacing: 2px; font-size: 2.2rem;">FirstPerson - Personal AI Companion</h1>', unsafe_allow_html=True)
    st.markdown("*Your private space for emotional processing and growth*")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"Welcome back, **{st.session_state.username}**! 👋")
    with col2:
        if st.button("⚙️ Settings", help="User settings and preferences"):
            st.info("Settings panel coming soon!")
    with col3:
        if st.button("🚪 Logout", help="Sign out of your account"):
            from modules.auth import SaoynxAuthentication
            auth = SaoynxAuthentication()
            auth.logout()
    conversation_key = f"conversation_history_{st.session_state.user_id}"
    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = []
    with st.container():
        col1, col2 = st.columns([2, 1])
    with col1:
        if 'processing_mode' not in st.session_state:
            st.session_state.processing_mode = "hybrid"
        processing_mode = st.selectbox(
            "Processing Mode",
            ["hybrid", "local", "ai_preferred"],
            index=["hybrid", "local", "ai_preferred"].index(st.session_state.processing_mode),
            help="Hybrid: Best performance, Local: Maximum privacy, AI: Most sophisticated responses"
        )
        st.session_state.processing_mode = processing_mode
    with col2:
        if st.button("Clear History", type="secondary"):
            st.session_state[conversation_key] = []
            st.rerun()
    chat_container = st.container()
    with chat_container:
        for i, exchange in enumerate(st.session_state[conversation_key]):
            with st.chat_message("user"):
                st.write(exchange["user"])
            with st.chat_message("assistant"):
                st.write(exchange["assistant"])
                if "processing_time" in exchange:
                    st.caption(f"Processed in {exchange['processing_time']} • Mode: {exchange.get('mode', 'unknown')}")
    if "uploaded_text" in st.session_state:
        with chat_container:
            with st.chat_message("user"):
                st.write("📄 Document uploaded for processing.")
            with st.chat_message("assistant"):
                with st.spinner("Metabolizing document..."):
                    response = f"Processed document content:\n\n{st.session_state['uploaded_text'][:500]}..."
                    st.write(response)
    uploaded_file = st.file_uploader("📄 Upload a document", type=["txt", "docx", "pdf"])
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")
        st.session_state["uploaded_text"] = file_content
        st.success("Document uploaded successfully!")
    user_input = st.chat_input("Share what you're feeling...")
    if user_input:
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Processing your emotional input..."):
                    start_time = time.time()
                    try:
                        saori_url = st.secrets["supabase"]["saori_function_url"]
                        response_data = requests.post(
                            saori_url,
                            headers={
                                "Authorization": f"Bearer {st.secrets['supabase']['key']}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "message": user_input,
                                "mode": processing_mode,
                                "user_id": st.session_state.user_id
                            },
                            timeout=15
                        )
                        if response_data.status_code == 200:
                            result = response_data.json()
                            response = result.get("reply", "I'm here to listen.")
                            glyph_info = result.get("glyph", {})
                            processing_details = result.get("log", {})
                        else:
                            response = "I'm experiencing some technical difficulties, but I'm still here for you."
                            glyph_info = {}
                            processing_details = {"error": f"HTTP {response_data.status_code}"}
                    except Exception as e:
                        response = "I'm having trouble connecting right now, but your feelings are still valid and important."
                        glyph_info = {}
                        processing_details = {"error": str(e)}
                    processing_time = time.time() - start_time
                    st.write(response)
                    if glyph_info and glyph_info.get("tag_name"):
                        st.caption(f"✨ Emotional resonance: {glyph_info.get('tag_name')} • Processed in {processing_time:.2f}s • Mode: {processing_mode}")
                    else:
                        st.caption(f"Processed in {processing_time:.2f}s • Mode: {processing_mode}")
        st.session_state[conversation_key].append({
            "user": user_input,
            "assistant": response,
            "processing_time": f"{processing_time:.2f}s",
            "mode": processing_mode,
            "glyph": glyph_info.get("tag_name") if glyph_info else None,
            "timestamp": datetime.datetime.now().isoformat()
        })
        st.rerun()
    if "show_personal_log" not in st.session_state:
        st.session_state.show_personal_log = False
    if st.button("Start Personal Log", help="Begin a structured emotional entry—date, event, mood, reflections, and insights."):
        st.session_state.show_personal_log = True
        st.rerun()
    if st.session_state.show_personal_log:
        import datetime as dt
        st.markdown("### 📘 Start Personal Log")
        st.markdown("Use this space to record a structured emotional entry. You'll log the date, event, mood, reflections, and insights.")
        date = st.date_input("Date", value=dt.date.today())
        log_time = st.time_input("Time", value=dt.datetime.now().time())
        event = st.text_area("Event", placeholder="What happened?")
        mood = st.text_input("Mood", placeholder="How did it feel?")
        reflections = st.text_area("Reflections", placeholder="What’s emerging emotionally?")
        insights = st.text_area("Insights", placeholder="What truth or clarity surfaced?")
        if st.button("Conclude Log"):
            st.success("Your personal log has been saved.")
            try:
                st.download_button(
                    label="Download as Word Doc",
                    data=generate_doc(date, log_time, event, mood, reflections, insights),
                    file_name="personal_log.docx"
                )
            except Exception as e:
                st.error(f"Error generating Word document: {e}")
        else:
            st.info("You can continue adding to this log.")
    with st.sidebar:
        st.subheader("Your Emotional Journey")
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
            user_data = {
                "user_id": st.session_state.user_id,
                "username": st.session_state.username,
                "conversations": st.session_state[conversation_key],
                "export_date": datetime.datetime.now().isoformat()
            }
            st.download_button(
                "Download JSON",
                json.dumps(user_data, indent=2),
                file_name=f"emotional_os_data_{st.session_state.username}_{datetime.datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
