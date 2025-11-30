"""
Streamlit UI for Real-Time Glyph Ingestion Status
------------------------------------------------
Displays live ingestion status, glyph lineage, and resonance shifts.
"""

import json
import os

import streamlit as st

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "deploy", "processed_glyphs")
GLYPH_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "deploy", "glyphs_db.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "deploy", "ingestion_log.jsonl")

st.set_page_config(page_title="Glyph Ingestion Status", layout="wide")
st.title("Glyph Ingestion Ritual Status")


# Load glyphs
def load_glyphs():
    if os.path.exists(GLYPH_DB_PATH):
        with open(GLYPH_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


glyphs = load_glyphs()

# Live status
st.subheader("Live Ingestion Status")
st.write(f"Total glyphs ingested: {len(glyphs)}")

# Glyph lineage table
st.subheader("Glyph Lineage")
if glyphs:
    st.dataframe(
        [
            {
                "Name": g.get("glyph_name", ""),
                "Category": g.get("category", ""),
                "Valence": g.get("valence", ""),
                "Function": g.get("function", ""),
                "Lineage": g.get("lineage", ""),
                "Timestamp": g.get("timestamp", ""),
                "Origin File": g.get("origin_file", ""),
            }
            for g in glyphs
        ]
    )
else:
    st.info("No glyphs ingested yet.")

# Resonance shifts (emotional signals summary)
st.subheader("Resonance Shifts (Emotional Signals)")
if glyphs:
    from collections import Counter

    signals = [s for g in glyphs for s in g.get("emotional_signals", [])]
    signal_counts = Counter(signals)
    st.bar_chart(signal_counts)
else:
    st.info("No emotional signals detected yet.")

# Ritual log
st.subheader("Ritual Log")
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        logs = [json.loads(line) for line in f if line.strip()]
    for log in reversed(logs[-20:]):
        st.write(f"[{log['timestamp']}] {log['message']}")
else:
    st.info("No ritual logs found.")
