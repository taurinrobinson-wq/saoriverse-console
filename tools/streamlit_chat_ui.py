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
from feedback_store import append_feedback, append_conversation


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
    # Persist conversation exchange for batch/dominant processing later
    try:
        append_conversation({
            "user": entry.get("user"),
            "response": entry.get("response"),
            "glyph": entry.get("glyph"),
            "confidence": entry.get("confidence"),
            "mismatch": entry.get("mismatch"),
            "triggered": entry.get("triggered"),
            "learned": entry.get("learned"),
        })
    except Exception:
        pass


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
    # Render recent activity with feedback controls
    chat = st.session_state.chat_log
    # Show up to last 20 entries in reverse chronological order
    start = max(0, len(chat) - 20)
    for idx in range(len(chat) - 1, start - 1, -1):
        e = chat[idx]
        # Display in a compact, readable format
        st.markdown(f"**User:** {e.get('user')}  \n**Response:** {e.get('response')}")

        # Feedback controls: thumbs up / thumbs down
        if not e.get('feedback'):
            col_up, col_down = st.columns([1, 1])
            if col_up.button("👍", key=f"thumbs_up_{idx}"):
                e['feedback'] = 'positive'
                # Persist feedback for later batch processing by Dominant
                try:
                    append_feedback({
                        'user': e.get('user'),
                        'response': e.get('response'),
                        'glyph': e.get('glyph'),
                        'confidence': e.get('confidence', 0.0),
                        'type': 'positive',
                    })
                except Exception:
                    pass

                # Inform orchestrator of positive feedback (if available)
                try:
                    st.session_state.orchestrator.observe_exchange(e.get('user'), {"response": e.get('response'), "confidence": e.get('confidence', 0.0)}, simple_emotion_parser(e.get('user')))
                except Exception:
                    pass

            if col_down.button("👎", key=f"thumbs_down_{idx}"):
                e['feedback'] = 'negative'
                e['feedback_stage'] = 'awaiting_reason'
                try:
                    append_feedback({
                        'user': e.get('user'),
                        'response': e.get('response'),
                        'glyph': e.get('glyph'),
                        'confidence': e.get('confidence', 0.0),
                        'type': 'negative',
                    })
                except Exception:
                    pass

        # Show feedback status immediately so user gets visual confirmation
        if e.get('feedback'):
            fb = e.get('feedback')
            if fb == 'positive':
                st.success('Feedback recorded: 👍')
                # append to a feedback log for later review/learning
                try:
                    st.session_state.feedback_log = st.session_state.get('feedback_log', [])
                    st.session_state.feedback_log.append({
                        'user': e.get('user'),
                        'response': e.get('response'),
                        'type': 'positive',
                        'ts': __import__('datetime').datetime.now().isoformat(),
                    })
                except Exception:
                    pass
            elif fb == 'corrected':
                st.info('Response marked as corrected by alternative.')
            elif fb == 'negative':
                st.warning('Negative feedback received — awaiting your notes.')

        # If negative feedback was given, collect corrective feedback and generate an alternative
        if e.get('feedback') == 'negative' and e.get('feedback_stage') == 'awaiting_reason':
            fb_text = st.text_area("What was off about the response? (helpful: tell me what to change)", key=f"fb_text_{idx}")
            if st.button("Submit feedback and try an alternative", key=f"fb_submit_{idx}"):
                e['feedback_text'] = fb_text
                e['feedback_stage'] = 'submitted'
                # Persist the negative feedback with user's corrective text
                try:
                    append_feedback({
                        'user': e.get('user'),
                        'response': e.get('response'),
                        'glyph': e.get('glyph'),
                        'confidence': e.get('confidence', 0.0),
                        'type': 'negative_with_note',
                        'note': fb_text,
                    })
                except Exception:
                    pass
                # Record observation with orchestrator if available
                try:
                    st.session_state.orchestrator.observe_exchange(e.get('user'), {"response": e.get('response'), "confidence": e.get('confidence', 0.0)}, simple_emotion_parser(e.get('user')))
                except Exception:
                    pass

                # Generate an alternative grounded response using the subordinate responder
                try:
                    responder = st.session_state.get('responder')
                    if responder and hasattr(responder, 'respond'):
                        # Create an alternative reply using the human-style helper
                        try:
                            alt_text = responder._human_style_response(None, e.get('user'))
                        except Exception:
                            alt_text = responder._human_style_response(None, e.get('user')) if hasattr(responder, '_human_style_response') else None
                        if not alt_text:
                            alt_text = "Sorry — can you tell me what you'd prefer me to change?"
                        else:
                            alt_text = f"{alt_text} Is this better?"
                    else:
                        alt_text = "Sorry — can you tell me what you'd prefer me to change?"
                except Exception:
                    alt_text = "Sorry — can you tell me what you'd prefer me to change?"

                alt_entry = {
                    "user": f"assistant_alt_for_{idx}",
                    "response": alt_text,
                    "glyph": "alternative",
                    "confidence": 1.0,
                    "mismatch": 1.0,
                    "triggered": True,
                    "learned": False,
                    "origin": "alternative",
                    "related_index": idx,
                }
                st.session_state.chat_log.append(alt_entry)

        # If an alternative exists for this entry, render a simple accept/reject UI
        # Look for any chat entries appended with related_index == idx
        alts = [c for c in chat if c.get('origin') == 'alternative' and c.get('related_index') == idx]
        for aidx, alt in enumerate(alts):
            st.markdown(f"**Alternative {aidx+1}:** {alt.get('response')}")
            if not alt.get('feedback'):
                col_yes, col_no = st.columns([1, 1])
                if col_yes.button("Yes — this is better", key=f"alt_yes_{idx}_{aidx}"):
                    alt['feedback'] = 'positive'
                    # Mark original as improved
                    chat[idx]['feedback'] = 'corrected'
                    # Optionally notify orchestrator/dominant of successful correction
                    try:
                        st.session_state.orchestrator.observe_exchange(chat[idx].get('user'), {"response": alt.get('response'), "confidence": alt.get('confidence', 1.0)}, simple_emotion_parser(chat[idx].get('user')))
                    except Exception:
                        pass
                if col_no.button("No — try again", key=f"alt_no_{idx}_{aidx}"):
                    alt['feedback'] = 'negative'
                    # Generate another alternative (simple strategy: new human-style phrasing)
                    try:
                        responder = st.session_state.get('responder')
                        try:
                            new_alt = responder._human_style_response(None, chat[idx].get('user'))
                        except Exception:
                            new_alt = None
                        if new_alt:
                            new_alt = new_alt + " Is this better?"
                        else:
                            new_alt = "Can you tell me a bit more about how you'd like this to be different?"
                    except Exception:
                        new_alt = "Can you tell me a bit more about how you'd like this to be different?"
                    new_entry = {
                        "user": f"assistant_alt_for_{idx}",
                        "response": new_alt,
                        "glyph": "alternative",
                        "confidence": 1.0,
                        "mismatch": 1.0,
                        "triggered": True,
                        "learned": False,
                        "origin": "alternative",
                        "related_index": idx,
                    }
                    st.session_state.chat_log.append(new_entry)


if __name__ == "__main__":
    main()
