"""
Response Processing Handler (Refactored).

Orchestrates the three-phase pipeline:
1. parse_phase - Extract signals, emotions, glyphs
2. interpret_phase - Generate base conversational response
3. generate_phase - Apply tiers, safety, synthesis

This is now a clean orchestrator instead of a 1,233-line monolith.
"""

import time
import logging
import streamlit as st
from src.emotional_os.tier1_foundation import Tier1Foundation
from src.emotional_os.tier2_aliveness import Tier2Aliveness
from src.emotional_os.tier3_poetic_consciousness import Tier3PoeticConsciousness
from ..ollama_client import get_ollama_client_singleton
from emotional_os.deploy.modules.ui_components.pipeline.parse_phase import parse_input_signals
from emotional_os.deploy.modules.ui_components.pipeline.interpret_phase import interpret_emotional_context
from emotional_os.deploy.modules.ui_components.pipeline.generate_phase import generate_enhanced_response

logger = logging.getLogger(__name__)


def handle_response_pipeline(user_input: str, conversation_context: dict) -> tuple:
    """Execute the full response processing pipeline.

    Orchestrates: parse → interpret → generate

    Args:
        user_input: User's message
        conversation_context: Conversation history

    Returns:
        (response_text, processing_time_seconds)
    """
    start_time = time.time()
    
    logger.info(f"handle_response_pipeline start: input_len={len(user_input) if user_input else 0}")

    # Tiers are eagerly initialized in session_manager.initialize_session_state()
    # This eliminates first-message lag (Phase 2 optimization)

    try:
        # PHASE 1: Parse input signals
        logger.debug("Phase 1: Parsing input signals...")
        analysis = parse_input_signals(user_input, conversation_context)

        # PHASE 2: Interpret emotional context (generate base response)
        logger.debug("Phase 2: Interpreting emotional context...")
        base_response = interpret_emotional_context(user_input, analysis, conversation_context)

        # PHASE 3: Generate enhanced response (apply tiers + synthesis)
        logger.debug("Phase 3: Generating enhanced response...")
        final_response, generate_time = generate_enhanced_response(user_input, base_response, conversation_context)

        processing_time = time.time() - start_time
        logger.info(f"Pipeline complete: {processing_time:.3f}s (generate_time: {generate_time:.3f}s)")

        return final_response, processing_time

    except Exception as e:
        logger.error(f"Response pipeline FAILED: {type(e).__name__}: {e}", exc_info=True)
        processing_time = time.time() - start_time
        return f"[ERROR] Response pipeline failed: {e}", processing_time




# Legacy wrapper for backwards compatibility
def generate_response(user_input: str, conversation_context: dict | None = None) -> str:
    """Legacy wrapper for backwards compatibility."""
    if conversation_context is None:
        conversation_context = {}
    response, _ = handle_response_pipeline(user_input, conversation_context)
    return response

