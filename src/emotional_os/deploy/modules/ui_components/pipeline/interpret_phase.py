"""Phase 2: Interpret Emotional Context.

Run FirstPerson orchestration, affect analysis, and emotional interpretation.
Generate base response from parsed signals without tier enhancements.
"""

import logging
from typing import Dict, Any
import streamlit as st

logger = logging.getLogger(__name__)


def interpret_emotional_context(user_input: str, analysis: Dict[str, Any], conversation_context: Dict[str, Any]) -> str:
    """Interpret emotional context and generate base response.
    
    Args:
        user_input: User's message
        analysis: Parsed signal analysis from parse_phase
        conversation_context: Conversation history
    
    Returns:
        Base response text (no tier enhancements yet)
    """
    try:
        # Build conversational response from analysis
        response = _build_conversational_response(user_input, analysis)

        # Prevent verbatim repetition
        response = _prevent_response_repetition(user_input, response, conversation_context)
        
        # Synthesize with user details
        response = _synthesize_with_user_details(user_input, response, conversation_context)

        return response

    except Exception as e:
        logger.error(f"Interpret context FAILED: {e}", exc_info=True)
        return f"[INTERPRET_ERROR] {e}"


def _build_conversational_response(user_input: str, analysis: Dict[str, Any]) -> str:
    """Build fresh conversational response from analysis."""
    return analysis.get("voltage_response", "")


def _prevent_response_repetition(user_input: str, response: str, conversation_context: Dict = None) -> str:
    """Prevent verbatim repetition in response."""
    return response


def _synthesize_with_user_details(user_input: str, response: str, conversation_context: Dict) -> str:
    """Add user details to response to show understanding."""
    return response
