"""Compatibility UI module exposing `run_hybrid_pipeline` used by tests.

This module adapts the mobile-friendly pipeline for tests and older callers.
"""
import requests

import streamlit as st
from .ui_mobile import run_hybrid_pipeline_mobile


def run_hybrid_pipeline(effective_input: str, conversation_context: dict, saori_url: str, supabase_key: str):
    """Run the mobile hybrid pipeline with minimal parameters to satisfy tests.

    The mobile pipeline returns (response_text, debug_info, local_analysis) which
    aligns with the test expectations.
    """
    # Determine processing mode from Streamlit session state; tests set
    # `processing_mode` and `prefer_ai` in `st.session_state`.
    processing_mode = getattr(st.session_state, "processing_mode", "local")
    prefer_ai = getattr(st.session_state, "prefer_ai", False)
    # If tests (or UI) prefer AI and credentials are provided, allow remote path
    if prefer_ai and saori_url and supabase_key:
        processing_mode = "remote"

    composed, debug, local = run_hybrid_pipeline_mobile(
        effective_input, conversation_context, saori_url, supabase_key, processing_mode=processing_mode
    )

    # If local analysis is missing, try to compute it via the absolute
    # `emotional_os.glyphs.signal_parser.parse_input` so test mocks are
    # respected (they patch this fully-qualified name).
    if not local:
        try:
            from emotional_os.glyphs.signal_parser import parse_input as _parse

            local = _parse(
                effective_input,
                "emotional_os/parser/signal_lexicon.json",
                db_path="emotional_os/glyphs/glyphs.db",
                conversation_context=conversation_context,
            )
        except Exception:
            local = {}

    # Optionally include local decoding in the composed string for debugging/tests
    if getattr(st.session_state, "show_local_decoding", False):
        try:
            decoding = f"\n\nLocal decoding:\nVoltage: {local.get('voltage_response', '')}\nGlyphs: {', '.join([g.get('glyph_name','') for g in local.get('glyphs', [])]) if local.get('glyphs') else 'None'}"
            composed = f"{composed}{decoding}"
        except Exception:
            # If local data isn't structured as expected, still annotate
            composed = f"{composed}\n\nLocal decoding: (unavailable)"

    return composed, debug, local
