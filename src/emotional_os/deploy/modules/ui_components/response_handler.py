"""
Response Processing Handler.

Orchestrates the full response pipeline including:
- Local signal parsing
- FirstPerson orchestration
- Affect analysis
- Response engine integration
- Prosody metadata handling
- Fallback protocol handling
- Repetition prevention
"""

import time
import logging
import streamlit as st

logger = logging.getLogger(__name__)


def handle_response_pipeline(user_input: str, conversation_context: dict) -> str:
    """Execute the full response processing pipeline.

    Runs local parsing, emotional analysis, response generation,
    and safety protocols. Returns clean response without metadata.

    Args:
        user_input: User's message
        conversation_context: Conversation history and context

    Returns:
        Clean response text (prosody metadata stripped)
    """
    start_time = time.time()
    response = ""
    processing_mode = st.session_state.get("processing_mode", "local")

    try:
        # Run appropriate pipeline based on mode
        if processing_mode == "local":
            response = _run_local_processing(user_input, conversation_context)
        else:  # hybrid or unknown -> default to hybrid
            response = _run_hybrid_processing(user_input, conversation_context)

        # Run through fallback protocols (safety layer)
        response = _apply_fallback_protocols(user_input, response)

        # Strip prosody metadata before returning
        response = strip_prosody_metadata(response)

        # Prevent verbatim repetition
        response = _prevent_response_repetition(response)

    except Exception as e:
        logger.warning(f"Response pipeline failed: {e}")
        response = "I'm here to listen. Can you tell me more?"

    processing_time = time.time() - start_time

    return response, processing_time


def _run_local_processing(user_input: str, conversation_context: dict) -> str:
    """Run all-local processing pipeline.

    Args:
        user_input: User message
        conversation_context: Conversation history

    Returns:
        Response text (may include prosody metadata)
    """
    try:
        from ..glyphs.signal_parser import parse_input

        # Local signal parsing with word-centric lexicon
        local_analysis = parse_input(
            user_input,
            "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
            db_path="emotional_os/glyphs/glyphs.db",
            conversation_context=conversation_context,
        )

        # Get the conversational response from the analysis
        response = _build_conversational_response(user_input, local_analysis)

        # Store analysis in session for debug if needed
        st.session_state["last_local_analysis"] = local_analysis

        return response

    except Exception as e:
        logger.warning(f"Local processing failed: {e}")
        return "I'm here to listen. Can you tell me more?"


def _build_conversational_response(user_input: str, local_analysis: dict) -> str:
    """Build a natural conversational response from signal analysis.
    
    Takes the raw glyph analysis and builds a response that:
    1. Acknowledges what the user said
    2. Uses the glyph insights naturally
    3. Stays conversational and warm
    
    Args:
        user_input: Original user message
        local_analysis: Analysis dict from parse_input
        
    Returns:
        Conversational response
    """
    glyphs = local_analysis.get("glyphs", [])
    best_glyph = local_analysis.get("best_glyph")
    voltage_response = local_analysis.get("voltage_response", "")
    
    # If we have a voltage response, use that as the primary response
    if voltage_response and voltage_response.strip():
        # Clean up any leftover metadata
        response = voltage_response.strip()
        if "Resonant Glyph:" in response:
            response = response.split("Resonant Glyph:")[0].strip()
        return response
    
    # Fallback: build a simple acknowledgment + glyph insight
    # This is a minimal conversational wrapper
    glyph_name = best_glyph.get("glyph_name", "") if best_glyph else ""
    glyph_desc = best_glyph.get("description", "") if best_glyph else ""
    
    if glyph_name:
        # Create a simple conversational response
        opening = "I hear you. "
        if len(user_input) < 30:
            opening += "That sounds important. "
        else:
            opening += "That's a lot to carry. "
        
        # Use glyph insight as support
        if glyph_desc:
            return f"{opening}I'm sensing {glyph_name.lower()} — {glyph_desc.lower()}."
        else:
            return opening
    
    # Last resort fallback
    return "I'm here to listen. Can you tell me more?"


def _run_hybrid_processing(user_input: str, conversation_context: dict) -> str:
    """Run hybrid processing pipeline (local + potential remote).

    Currently uses local processing as primary with remote as optional enhancement.

    Args:
        user_input: User message
        conversation_context: Conversation history

    Returns:
        Response text
    """
    # For now, hybrid mode uses same local pipeline
    # Remote AI enhancement can be added here in future
    return _run_local_processing(user_input, conversation_context)


def _apply_firstperson_insights(user_input: str, local_analysis: dict) -> dict:
    """Inject FirstPerson orchestrator insights into analysis.

    Adds theme detection, frequency analysis, memory context, and clarifying prompts.

    Args:
        user_input: User message
        local_analysis: Initial analysis dict

    Returns:
        Enhanced analysis dict
    """
    try:
        fp_orch = st.session_state.get("firstperson_orchestrator")
        if not fp_orch:
            return local_analysis

        firstperson_response = fp_orch.handle_conversation_turn(user_input)

        if isinstance(firstperson_response, dict):
            local_analysis["firstperson_insights"] = {
                "detected_theme": firstperson_response.get("detected_theme"),
                "theme_frequency": firstperson_response.get("theme_frequency"),
                "memory_context_injected": firstperson_response.get("memory_context_injected"),
                "clarifying_prompt": firstperson_response.get("clarifying_prompt"),
            }

    except Exception as e:
        logger.debug(f"FirstPerson processing failed: {e}")

    return local_analysis


def _apply_affect_analysis(user_input: str, local_analysis: dict) -> dict:
    """Inject emotional affect analysis into analysis.

    Detects tone, valence, arousal, and secondary tones.

    Args:
        user_input: User message
        local_analysis: Initial analysis dict

    Returns:
        Enhanced analysis dict
    """
    try:
        affect_parser = st.session_state.get("affect_parser")
        if not affect_parser:
            return local_analysis

        affect_analysis = affect_parser.analyze_affect(user_input)

        if affect_analysis:
            local_analysis["affect_analysis"] = {
                "tone": affect_analysis.tone,
                "tone_confidence": affect_analysis.tone_confidence,
                "valence": affect_analysis.valence,
                "arousal": affect_analysis.arousal,
                "secondary_tones": affect_analysis.secondary_tones,
            }

    except Exception as e:
        logger.debug(f"Affect analysis failed: {e}")

    return local_analysis


def _call_response_engine(user_input: str, local_analysis: dict) -> str:
    """Build conversational response from local analysis.

    Uses the voltage_response (contextual AI response) as the primary
    response, with the glyph as supporting metadata.

    Args:
        user_input: User message
        local_analysis: Complete analysis dict

    Returns:
        Response text
    """
    # Primary response is the voltage_response (already conversational)
    voltage_response = local_analysis.get("voltage_response", "")
    
    if not voltage_response:
        # Fallback if no voltage response
        return "I'm here to listen. Can you tell me more?"
    
    # Remove any "Resonant Glyph:" or debug metadata that might be appended
    if "Resonant Glyph:" in voltage_response:
        voltage_response = voltage_response.split("Resonant Glyph:")[0].strip()
    if "Local decoding:" in voltage_response:
        voltage_response = voltage_response.split("Local decoding:")[0].strip()
    
    return voltage_response


def _apply_fallback_protocols(user_input: str, response: str) -> str:
    """Apply fallback safety protocols to response.

    Args:
        user_input: User message
        response: Generated response

    Returns:
        Response after fallback processing
    """
    try:
        fallback = st.session_state.get("fallback_protocol")
        if not fallback:
            return response

        # Extract glyphs if available
        detected_triggers = []
        local_analysis = st.session_state.get("last_local_analysis", {})
        glyphs = local_analysis.get("glyphs", [])
        if glyphs:
            detected_triggers = [g.get("glyph_name", "")
                                 for g in glyphs if isinstance(g, dict)]

        # Process through fallback
        fallback_result = fallback.process_exchange(
            user_text=user_input,
            detected_triggers=detected_triggers if detected_triggers else None,
        )

        # Use fallback message if asking for clarification
        if fallback_result.get("decisions", {}).get("should_ask_clarification"):
            response = fallback_result.get(
                "companion_behavior", {}).get("message", response)

        # Store result for debugging
        key = f"protocol_result_{len(st.session_state.get('conversation_history_', []))}"
        try:
            st.session_state[key] = fallback_result
        except Exception:
            pass

    except Exception as e:
        logger.debug(f"Fallback protocol error: {e}")

    return response


def strip_prosody_metadata(response: str) -> str:
    """Remove prosody metadata from response before display.

    Prosody is used internally for voice synthesis metadata but should
    not be visible to users.

    Args:
        response: Response text potentially containing [PROSODY:...] JSON

    Returns:
        Clean response text without prosody
    """
    if not response:
        return ""

    try:
        if "[PROSODY:" in response:
            return response.split("[PROSODY:")[0].strip()
    except Exception:
        pass

    return response


def _prevent_response_repetition(response: str) -> str:
    """Prevent exact repetition of assistant's last message.

    If new response matches previous one, append a gentle follow-up prompt.

    Args:
        response: Current response

    Returns:
        Response with follow-up if repetition detected
    """
    try:
        from .session_manager import get_conversation_key

        key = get_conversation_key()
        history = st.session_state.get(key, [])

        if not history or len(history) == 0:
            return response

        # Get last assistant message
        last_assistant = history[-1].get("assistant",
                                         "") if isinstance(history[-1], dict) else ""

        if last_assistant and last_assistant.strip() == response.strip():
            # Generate context-aware follow-up
            followups = [
                "Can you tell me one specific detail about that?",
                "Would it help if we tried one small concrete step together?",
                "If you pick one thing to focus on right now, what would it be?",
                "That's important, would you like a short breathing practice or a practical plan?",
            ]

            idx = len(response) % len(followups)
            response = f"{response} {followups[idx]}"

    except Exception as e:
        logger.debug(f"Repetition prevention failed: {e}")

    return response


def get_debug_info() -> dict:
    """Get debug information from last processing.

    Returns:
        Dictionary with signals, glyphs, SQL, etc.
    """
    local_analysis = st.session_state.get("last_local_analysis", {})

    return {
        "signals": local_analysis.get("signals", []),
        "gates": local_analysis.get("gates", []),
        "glyphs": local_analysis.get("glyphs", []),
        "debug_sql": local_analysis.get("debug_sql", ""),
        "debug_glyph_rows": local_analysis.get("debug_glyph_rows", []),
        "firstperson_insights": local_analysis.get("firstperson_insights"),
        "affect_analysis": local_analysis.get("affect_analysis"),
    }
