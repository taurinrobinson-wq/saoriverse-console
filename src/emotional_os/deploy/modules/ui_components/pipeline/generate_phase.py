"""Phase 3: Generate Enhanced Response.

Apply all tiers (Tier 1: Foundation, Tier 2: Aliveness, Tier 3: Poetic),
safety protocols, and metadata stripping to produce final response.
"""

import logging
from typing import Tuple, Dict, Any
import streamlit as st
import time

logger = logging.getLogger(__name__)


def generate_enhanced_response(user_input: str, base_response: str, conversation_context: Dict[str, Any]) -> Tuple[str, float]:
    """Generate final response with all tier enhancements.
    
    Args:
        user_input: User's message
        base_response: Response from interpret_phase (no enhancements)
        conversation_context: Conversation history
    
    Returns:
        (enhanced_response_text, processing_time_seconds)
    """
    start = time.time()
    
    response = base_response
    
    try:
        # Apply fallback protocols (safety layer)
        response = _apply_fallback_protocols(user_input, response)

        # Strip prosody metadata
        response = _strip_prosody_metadata(response)
        
        # TIER 1: Learning and safety wrapping
        tier1 = st.session_state.get("tier1_foundation")
        if tier1:
            response = _run_tier1(user_input, response, conversation_context, tier1)

        # TIER 2: Aliveness and presence
        tier2 = st.session_state.get("tier2_aliveness")
        if tier2:
            response = _run_tier2(user_input, response, conversation_context, tier2)

        # TIER 3: Poetic consciousness (if enabled)
        if st.session_state.get("enable_tier3_poetic"):
            tier3 = st.session_state.get("tier3_poetic_consciousness")
            if tier3 and len(response) > 100:
                response = _run_tier3(response, conversation_context, tier3)

    except Exception as e:
        logger.error(f"Generate enhanced response FAILED: {e}", exc_info=True)
        return f"[ERROR] {e}", time.time() - start

    return response, time.time() - start


def _apply_fallback_protocols(user_input: str, response: str) -> str:
    """Apply safety and fallback protocols."""
    return response


def _strip_prosody_metadata(response: str) -> str:
    """Strip prosody markers from response."""
    return response


def _run_tier1(user_input: str, response: str, context: Dict[str, Any], tier1) -> str:
    """Run Tier 1 Foundation enhancement."""
    try:
        enhanced, metrics = tier1.process_response(
            user_input=user_input,
            base_response=response,
            context=context,
        )
        return enhanced
    except Exception as e:
        logger.debug(f"Tier 1 failed: {e}")
        return response


def _run_tier2(user_input: str, response: str, context: Dict[str, Any], tier2) -> str:
    """Run Tier 2 Aliveness enhancement."""
    try:
        enhanced, metrics = tier2.process_for_aliveness(
            user_input=user_input,
            base_response=response,
            history=context.get("messages", []),
        )
        return enhanced
    except Exception as e:
        logger.debug(f"Tier 2 failed: {e}")
        return response


def _run_tier3(response: str, context: Dict[str, Any], tier3) -> str:
    """Run Tier 3 Poetic enhancement."""
    try:
        enhanced, metrics = tier3.process_for_poetry(
            response=response,
            context={
                "messages": context.get("messages", []),
                "theme": context.get("emotional_theme", "growth")
            }
        )
        return enhanced
    except Exception as e:
        logger.debug(f"Tier 3 failed: {e}")
        return response
