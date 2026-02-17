import sys
import os
from datetime import datetime

# Ensure repo src and tools are on sys.path
ROOT = os.getcwd()
SRC = os.path.join(ROOT, "src")
TOOLS = os.path.join(ROOT, "tools")
for p in (SRC, TOOLS):
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st

# Reuse helpers from interactive CLI
from interactive_learning_ui import load_glyphs, simple_emotion_parser, make_responder_and_orchestrator


def init_state():
    if "glyphs" not in st.session_state:
        st.session_state.glyphs = load_glyphs()
    if "responder" not in st.session_state:
        responder, orchestrator, proto_mgr = make_responder_and_orchestrator(st.session_state.glyphs)
        st.session_state.responder = responder
        st.session_state.orchestrator = orchestrator
        st.session_state.proto_mgr = proto_mgr
    if "hybrid" not in st.session_state:
        try:
            from emotional_os_learning.hybrid_learner import get_hybrid_learner
            st.session_state.hybrid = get_hybrid_learner()
        except Exception:
            st.session_state.hybrid = None
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []
    if "dominant_threshold" not in st.session_state:
        st.session_state.dominant_threshold = 0.4


def append_log(entry: dict):
    entry["timestamp"] = datetime.now().isoformat()
    st.session_state.chat_log.append(entry)


def main():
    st.title("FirstPerson — Learning Sandbox (Streamlit)")
    init_state()

    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("Controls")
        if st.button("Reload lexicon"):
            st.session_state.glyphs = load_glyphs()
            st.session_state.responder.glyph_library = st.session_state.glyphs
            st.success(f"Loaded {len(st.session_state.glyphs)} glyphs")
        st.number_input("Dominant threshold", key="dominant_threshold", min_value=0.0, max_value=1.0, value=st.session_state.dominant_threshold, step=0.05)
        if st.button("Show protos"):
            pm = st.session_state.proto_mgr
            st.write({k: getattr(v, 'example_texts', []) for k, v in pm.proto_glyphs.items()})

    with col1:
        st.subheader("Chat")
        user_input = st.text_input("You", key="user_input")
        if st.button("Send") and user_input:
            ev = simple_emotion_parser(user_input)
            resp = st.session_state.responder.respond(user_input, {"user":"streamlit"}, ev)
            # Dominant observes
            dom = st.session_state.orchestrator.observe_exchange(user_input, {"response": resp.response_text, "confidence": resp.confidence}, ev)
            mismatch = getattr(dom, 'mismatch_degree', getattr(dom, 'confidence', 0.0))
            triggered = mismatch > st.session_state.dominant_threshold
            # Hybrid learning
            learned = False
            try:
                if st.session_state.hybrid:
                    learned = st.session_state.hybrid.learn_from_exchange(user_input, resp.response_text, emotional_signals=None, glyphs=[{"glyph_name": resp.glyph_name}])
            except Exception:
                learned = False

            # Append and show
            entry = {
                "user": user_input,
                "response": resp.response_text,
                "glyph": resp.glyph_name,
                "confidence": resp.confidence,
                "mismatch": mismatch,
                "triggered": triggered,
                "learned": learned,
            }
            append_log(entry)

    st.markdown("---")
    st.subheader("Recent activity")
    for e in reversed(st.session_state.chat_log[-20:]):
        st.write(e)


if __name__ == "__main__":
    main()
