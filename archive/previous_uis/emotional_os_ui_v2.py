"""Archived: emotional_os_ui_v2.py
This copy was moved into archive/previous_uis on user's request. The active, canonical UI is
`main_v2.py` and its modules under `emotional_os/deploy/modules/ui.py`.

Original file preserved for reference and possible rollback.
"""

import streamlit as st
from parser.signal_parser import parse_input
from learning.lexicon_learner import learn_from_conversation_data, get_learning_insights
from supabase_integration import create_hybrid_processor
import datetime
import json
import os
import re
from typing import Dict, List

# Import poetry enrichment system for local mode
try:
    from parser.poetry_enrichment import PoetryEnrichment
    POETRY_AVAILABLE = True
    POETRY_ERROR = None
except ImportError as e:
    POETRY_AVAILABLE = False
    POETRY_ERROR = str(e)

# Import the auto-evolving glyph system
try:
    from evolving_glyph_integrator import EvolvingGlyphIntegrator
    EVOLUTION_AVAILABLE = True
    EVOLUTION_IMPORT_ERROR = None
except ImportError as e:
    EVOLUTION_AVAILABLE = False
    EVOLUTION_IMPORT_ERROR = str(e)
    st.warning(f"Auto-evolving glyph system not available - Import error: {e}")

st.set_page_config(page_title="Emotional OS", layout="wide", initial_sidebar_state="expanded")

# The rest of the original UI has been archived. See `main_v2.py` for the canonical app.
