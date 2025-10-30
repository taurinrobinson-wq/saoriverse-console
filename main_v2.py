import streamlit as st
from emotional_os.deploy.modules.auth import SaoynxAuthentication
from emotional_os.deploy.modules.doc_export import generate_doc
from emotional_os.deploy.modules.ui import render_splash_interface, render_main_app

# Page configuration
st.set_page_config(
    page_title="FirstPerson - Personal AI Companion",
    page_icon="graphics/FirstPerson-Logo.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    auth = SaoynxAuthentication()
    if st.session_state.authenticated:
        render_main_app()
    else:
        render_splash_interface(auth)

if __name__ == "__main__":
    main()
