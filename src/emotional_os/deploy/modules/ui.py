"""Compatibility UI module exposing `run_hybrid_pipeline` used by tests.

This module adapts the mobile-friendly pipeline for tests and older callers.
"""
from .ui_mobile import run_hybrid_pipeline_mobile


def run_hybrid_pipeline(effective_input: str, conversation_context: dict, saori_url: str, supabase_key: str):
    """Run the mobile hybrid pipeline with minimal parameters to satisfy tests.

    The mobile pipeline returns (response_text, debug_info, local_analysis) which
    aligns with the test expectations.
    """
    return run_hybrid_pipeline_mobile(effective_input, conversation_context, saori_url, supabase_key)
