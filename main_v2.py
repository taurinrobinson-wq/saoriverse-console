"""Main entry point for the streamlit FirstPerson app."""

from emotional_os.deploy.modules.ui import render_main_app, render_splash_interface, delete_user_history_from_supabase
from emotional_os.deploy.modules.auth import SaoynxAuthentication
import streamlit as st
from pathlib import Path
import os
import base64
import json

# Must be first Streamlit command
st.set_page_config(
    page_title="FirstPerson - Personal AI Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Replace default favicon with project logo (use embedded data URI so Streamlit
# will show the SVG as the browser favicon regardless of static file serving).
try:
    logo_path = Path("static/graphics/FirstPerson-Logo.svg")
    if logo_path.exists():
        svg_bytes = logo_path.read_bytes()
        b64 = base64.b64encode(svg_bytes).decode("ascii")
        st.markdown(
            f"<link rel=\"icon\" href=\"data:image/svg+xml;base64,{b64}\" type=\"image/svg+xml\">", unsafe_allow_html=True)
except Exception:
    # Non-fatal: keep the emoji favicon if embedding fails
    pass


# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['theme'] = 'Light'
    st.session_state['theme_loaded'] = False

    # Initialize learning persistence
    st.session_state['learning_settings'] = {
        'processing_mode': 'hybrid',  # Default to hybrid mode
        'enable_learning': True,      # Enable learning by default
        'persist_learning': True      # Enable persistence by default
    }

    # Create learning directories if they don't exist
    os.makedirs('learning/user_signals', exist_ok=True)
    os.makedirs('learning/user_overrides', exist_ok=True)
    os.makedirs('learning/conversation_glyphs', exist_ok=True)


# Customize navigation text
st.markdown("""
    <style>
    div.st-emotion-cache-j7qwjs span.st-emotion-cache-6tkfeg {
        visibility: hidden;
        position: relative;
    }
    
    div.st-emotion-cache-j7qwjs span.st-emotion-cache-6tkfeg::before {
        visibility: visible;
        position: absolute;
        content: "FirstPerson - Emotional AI Companion";
        left: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Remove stacked markdown blocks that only contain <style> tags (they create visible padding).
# This script hides any element-container whose markdown child contains only a <style> element.
st.markdown("""
<script>
(function(){
    function removeStyleOnlyMarkdown(){
        try{
            const containers = document.querySelectorAll('div[data-testid="stMarkdownContainer"]');
            containers.forEach(c=>{
                // If the container has exactly one child and it's a STYLE tag, hide the nearest element-container
                if(c.children.length === 1 && c.children[0].tagName && c.children[0].tagName.toLowerCase() === 'style'){
                    // Walk up to find the element-container wrapper
                    let el = c;
                    while(el && !el.classList.contains('element-container')){
                        el = el.parentElement;
                    }
                    if(el){
                        el.style.display = 'none';
                        el.style.margin = '0';
                        el.style.padding = '0';
                    }
                }
            });
        }catch(e){console.warn('removeStyleOnlyMarkdown failed', e)}
    }

    window.addEventListener('load', function(){
        removeStyleOnlyMarkdown();
        // run again shortly after load for dynamic rendering
        setTimeout(removeStyleOnlyMarkdown, 150);
    });

    // Observe DOM changes to catch dynamically injected style blocks
    const observer = new MutationObserver(function(mutations){
        removeStyleOnlyMarkdown();
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)

# Hide the top brand row (emoji + H1) when the app is embedded in certain layouts.
# This prevents the duplicated header/title from rendering in pages where space is limited.
# Targets the header H1 id and the adjacent emoji block.
st.markdown("""
    <style>
    /* Hide specific header by id */
    /* Primary: hide the H1 Streamlit generates for the page header */
    h1#firstperson-personal-ai-companion { display: none !important; }

    /* Fallbacks: hide heading container that may be wrapped by Streamlit test ids */
    [data-testid="stHeadingWithActionElements"] { display: none !important; }
    [data-testid="stHeadingWithActionElements"] h1 { display: none !important; }

    /* Also hide any h1 whose id starts with the page slug (defensive) */
    h1[id^="firstperson"] { display: none !important; }

    /* Hide the small emoji/logo block rendered adjacent to the header */
    /* This targets the inner markdown container with the inline style font-size: 2.5rem */
    div[data-testid="stMarkdownContainer"] div[style*="font-size: 2.5rem"] { display: none !important; }

    /* Hide any horizontal block that contains the brand row to avoid layout shift */
    div[data-testid="stHorizontalBlock"] > div > div > div > div > div > div > div > h1 { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Target specific Streamlit-generated padding block class and reduce its top padding
st.markdown("""
    <style>
    /* Reduce top padding on the large header container that pushes content down */
    .st-emotion-cache-7tauuy { padding: 0rem 1rem 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# Apply theme only if not already loaded for this session
if not st.session_state.get('theme_loaded'):
    if st.session_state.get('theme') == 'Dark':
        st.markdown("""
            <style>
            body, .stApp {background-color: #0E1117; color: #FAFAFA;}
            .stButton>button {
                background-color: #262730;
                color: #FAFAFA;
                border: 1px solid #555;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            body, .stApp {background-color: #FFFFFF; color: #31333F;}
            .stButton>button {
                background-color: #F0F2F6;
                color: #31333F;
                border: 1px solid #E0E0E0;
            }
            </style>
        """, unsafe_allow_html=True)
    st.session_state['theme_loaded'] = True

# Basic theme compatibility
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {color: inherit;}
    .stMarkdown {color: inherit;}
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

# Reduce font sizes in the sidebar for a denser layout
st.markdown("""
    <style>
    /* Target the Streamlit sidebar container and reduce text sizes */
    [data-testid="stSidebar"] { font-size: 0.92rem !important; }

    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stWidgetLabel,
    [data-testid="stSidebar"] .stButton>button,
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stMetric {
        font-size: 0.92rem !important;
        line-height: 1.15 !important;
    }

    /* Slightly larger for small titles if present */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] .stTitle {
        font-size: 1rem !important;
    }

    /* Ensure buttons and inputs remain usable */
    [data-testid="stSidebar"] .stButton>button {
        padding: 6px 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Fallback: ensure a download control exists in the sidebar for authenticated users only
try:
    # Only show the fallback download when a user is signed in
    if st.session_state.get('authenticated', False) and st.session_state.get('user_id'):
        with st.sidebar:
            try:
                conversation_key = f"conversation_history_{st.session_state.get('user_id')}"
                user_data = {
                    "user_id": st.session_state.get('user_id'),
                    "username": st.session_state.get('username'),
                    "conversations": st.session_state.get(conversation_key, []),
                    "export_date": __import__('datetime').datetime.now().isoformat()
                }
                st.download_button(
                    "Download My Data",
                    json.dumps(user_data, indent=2),
                    file_name=f"emotional_os_data_{st.session_state.get('username') or 'user'}_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    key="download_fallback_main"
                )
            except Exception:
                # Non-fatal; ensure sidebar rendering doesn't break
                pass
except Exception:
    pass

# Optional local preprocessor (privacy-first steward)
try:
    from local_inference.preprocessor import Preprocessor
    PREPROCESSOR_AVAILABLE = True
except Exception:
    Preprocessor = None
    PREPROCESSOR_AVAILABLE = False

# Optional limbic integration (safe import)
try:
    from emotional_os.glyphs.limbic_integration import LimbicIntegrationEngine
    HAS_LIMBIC = True
except Exception:
    LimbicIntegrationEngine = None
    HAS_LIMBIC = False


def main():
    """Main application entry point."""
    # Initialize authentication
    auth = SaoynxAuthentication()

    # Check if user is authenticated
    if st.session_state.get('authenticated', False):
        render_main_app()
    else:
        render_splash_interface(auth)


if __name__ == "__main__":
    main()
