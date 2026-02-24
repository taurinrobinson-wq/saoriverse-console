"""Phase 2: Interpret Emotional Context.

Generate base conversational response from parsed signals without tier enhancements.
Runs FirstPerson orchestration, mood ring, responder fallbacks.
"""

import logging
import re
from typing import Dict, Any, Optional
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
    """Build conversational response from signal analysis using multiple strategies.
    
    1. Mood ring for mood questions
    2. Subordinate responder for fallback signals
    3. Voltage response if available
    4. FirstPerson orchestrator with glyph
    5. Simple acknowledgment fallback
    """
    best_glyph = analysis.get("best_glyph") if analysis else None
    voltage_response = analysis.get("voltage_response", "") if analysis else ""

    # Try mood ring for mood questions (early)
    try:
        if analysis.get("response_source") == "fallback_message":
            u = (user_input or "").strip()
            is_short = len(u) < 120
            lower = u.lower()
            
            mood_phrases = (
                "what's your mood",
                "what is your mood",
                "what's your mood really",
                "how are you feeling",
                "what are you feeling",
            )
            is_mood_question = (
                ("mood" in lower and ("your" in lower or "you" in lower))
                or any(p in lower for p in mood_phrases)
            )
            chaos = "really" in lower

            if is_short and is_mood_question:
                try:
                    from emotional_os.deploy.modules.ui_components.mood_ring import generate_mood, mood_seed_for_window
                    weather = analysis.get("weather") or analysis.get("external_weather")
                    seed = mood_seed_for_window(None, weather or "Sunny")
                    return generate_mood(now=None, weather=weather or "Sunny", seed=seed, chaos=chaos)
                except Exception:
                    logger.debug("Mood ring generation failed")

            # Try subordinate responder for short questions
            if is_short and not is_mood_question:
                q_terms = ("feel", "feeling", "how are you", "what would", "if you had")
                is_question = ('?' in u) or any(q in lower for q in q_terms)
                if is_question:
                    try:
                        responder = st.session_state.get("responder")
                        convo_ctx = st.session_state.get("conversation_context") or {}
                        emotional_vector = analysis.get("emotional_vector") if isinstance(analysis, dict) else None
                        if responder and hasattr(responder, "respond"):
                            sub_resp = responder.respond(user_input, convo_ctx, emotional_vector or [])
                            return sub_resp.response_text
                    except Exception:
                        logger.debug("Subordinate responder failed")
    except Exception:
        pass

    # Use voltage response if available
    if voltage_response and voltage_response.strip():
        response = voltage_response.strip()
        if "Resonant Glyph:" in response:
            response = response.split("Resonant Glyph:")[0].strip()

        # Handle composite responses (analysis + conversational)
        parts = response.split("\n\n")
        if len(parts) > 1:
            conversational_response = parts[-1].strip()
            logger.debug(f"Composite response detected")
            return conversational_response

        # Check if response looks too poetic
        try:
            rt_lower = response.lower()
            poetic_markers = (
                "fullness", "steeped", "ecstatic", "joy so", "bliss",
                "saturat", "still", "mourning", "sanctify", "poetic", "lyric",
            )
            looks_poetic = any(m in rt_lower for m in poetic_markers) or len(rt_lower.split()) > 40

            glyph_desc = ""
            if best_glyph and isinstance(best_glyph, dict):
                glyph_desc = (best_glyph.get("description") or "").strip().lower()

            duplicates_glyph_desc = glyph_desc and (glyph_desc in rt_lower or rt_lower in glyph_desc)

            if looks_poetic or duplicates_glyph_desc:
                try:
                    responder = st.session_state.get("responder")
                    convo_ctx = st.session_state.get("conversation_context") or {}
                    emotional_vector = analysis.get("emotional_vector") if isinstance(analysis, dict) else None
                    if responder and hasattr(responder, "respond"):
                        sub_resp = responder.respond(user_input, convo_ctx, emotional_vector or [])
                        return sub_resp.response_text
                except Exception:
                    pass

                return "I hear you. Can you say a bit more about how that feels?"
        except Exception:
            return response

        return response

    # Use FirstPerson orchestrator
    try:
        fp_orch = st.session_state.get("firstperson_orchestrator")
        if fp_orch and best_glyph and isinstance(best_glyph, dict):
            response = fp_orch.generate_response_with_glyph(user_input, best_glyph)
            logger.info(f"Using FirstPerson glyph={best_glyph.get('glyph_name')}")
            return response
    except Exception as e:
        logger.debug(f"FirstPerson generation failed: {e}")

    # Fallback simple acknowledgment
    glyph_name = best_glyph.get("glyph_name", "") if best_glyph and isinstance(best_glyph, dict) else ""
    glyph_desc = best_glyph.get("description", "") if best_glyph and isinstance(best_glyph, dict) else ""

    if glyph_name:
        opening = "I hear you. "
        if len(user_input) < 30:
            opening += "That sounds important. "
        else:
            opening += "That's a lot to carry. "

        if glyph_desc:
            gd_lower = glyph_desc.lower()
            poetic_markers = (
                "fullness", "steeped", "ecstatic", "joy so", "bliss",
                "saturat", "still", "mourning", "sanctify", "poetic", "lyric",
            )
            looks_poetic = any(m in gd_lower for m in poetic_markers) or len(gd_lower.split()) > 40
            if looks_poetic:
                return f"{opening}I'm sensing {glyph_name.lower()}. Can you say more about how that feels?"
            else:
                return f"{opening}I'm sensing {glyph_name.lower()} — {glyph_desc.lower()}."

        return opening

    return "I'm here to listen. Can you tell me more?"


def _prevent_response_repetition(user_input: str, response: str, conversation_context: Optional[Dict]) -> str:
    """Prevent verbatim repetition in responses (stub for now)."""
    # TODO: Full extraction from response_handler _prevent_response_repetition
    return response


def _synthesize_with_user_details(user_input: str, response: str, conversation_context: Dict) -> str:
    """Enhance response by incorporating specific user details (stub for now)."""
    # TODO: Full extraction from response_handler _synthesize_with_user_details
    return response
