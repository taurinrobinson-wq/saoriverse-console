import streamlit as st
from pathlib import Path

# Simple one-click title demo for Velinor
# Run with: streamlit run tools/run_title_demo.py

st.set_page_config(page_title="Velinor Title Demo", page_icon=None, layout="centered")
ROOT = Path(__file__).resolve().parents[1]

TITLE_IMAGE = ROOT / "velinor_title_transparent.png"
BACKGROUND = ROOT / "city_market.png"
NPC_IMAGE = ROOT / "Mariel_nobg.png"

st.title("Velinor — Demo Title Screen")

if TITLE_IMAGE.exists():
    st.image(str(TITLE_IMAGE), use_column_width=True)
else:
    st.info("Title image not found: %s" % TITLE_IMAGE)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("Start Demo"):
        st.session_state.started = True
    if st.button("Credits"):
        st.session_state.credits = not st.session_state.get("credits", False)
    if st.button("Quit"):
        st.session_state.started = False
        st.balloons()

if st.session_state.get("credits", False):
    st.markdown("**Credits** — Project: Velinor, Assets: You + AI, Demo: streamlit")

if st.session_state.get("started", False):
    st.header("Demo Scene")
    cols = st.columns([2,1])
    with cols[0]:
        if BACKGROUND.exists():
            st.image(str(BACKGROUND), caption="Market background", use_column_width=True)
        else:
            st.info(f"Background missing: {BACKGROUND}")
    with cols[1]:
        st.subheader("NPCs")
        if NPC_IMAGE.exists():
            st.image(str(NPC_IMAGE), width=240)
            st.write("Mariel — sample NPC")
        else:
            st.info(f"NPC image missing: {NPC_IMAGE}")

    st.write("\n---\n")
    st.write("This is a placeholder demo. Replace with scene code or Streamlit integrations as needed.")

else:
    st.write("Press Start Demo to open a simple scene preview.")
