"""FirstPerson - Personal AI Companion"""
import streamlit as st

st.set_page_config(
    page_title="FirstPerson - Personal AI Companion",
    page_icon="🧠",
    layout="wide",
)

st.markdown("# 🧠 FirstPerson - Personal AI Companion")
st.write("Welcome to FirstPerson, your emotional AI companion.")

st.markdown("""
## Features
- 🎯 Emotional AI processing
- 💭 Personalized responses
- 🧬 Adaptive learning
- 🔒 Privacy-first design
""")

st.sidebar.markdown("## Navigation")
page = st.sidebar.radio("Select:", ["Chat", "About"])

if page == "Chat":
    st.subheader("Chat Interface")
    user_input = st.text_input("Your message:")
    if user_input:
        st.write(f"You: {user_input}")
        st.write("Assistant: Response generation in development...")
else:
    st.subheader("About FirstPerson")
    st.write("Advanced emotional AI system with local-first processing")

st.sidebar.markdown("---")
st.sidebar.markdown("**v1.0.0** | Streamlit Cloud Deployment")
