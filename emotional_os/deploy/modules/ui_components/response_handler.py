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
        from emotional_os.glyphs.signal_parser import parse_input

        # Local signal parsing
        local_analysis = parse_input(
            user_input,
            "emotional_os/parser/signal_lexicon.json",
            db_path="emotional_os/glyphs/glyphs.db",
            conversation_context=conversation_context,
        )

        # FirstPerson orchestration (relational AI)
        local_analysis = _apply_firstperson_insights(
            user_input, local_analysis)

        # Affect analysis (emotional tone, valence, arousal)
        local_analysis = _apply_affect_analysis(user_input, local_analysis)

        # Response engine integration
        response = _call_response_engine(user_input, local_analysis)

        # Store analysis in session for debug if needed
        st.session_state["last_local_analysis"] = local_analysis

        return response

    except Exception as e:
        logger.warning(f"Local processing failed: {e}")
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
    """Call the main response engine with analysis context.

    Args:
        user_input: User message
        local_analysis: Complete analysis dict

    Returns:
        Response text or empty string if engine fails
    """
    try:
        from core.main_response_engine import process_user_input as _engine_process

        ctx = {"local_analysis": local_analysis}

        # Add preprocessing insights if available
        last_preproc = st.session_state.get("last_preproc", {})
        if isinstance(last_preproc, dict):
            if last_preproc.get("intent"):
                ctx["emotion"] = last_preproc.get("intent")
            if last_preproc.get("confidence"):
                ctx["intensity"] = "high" if last_preproc.get(
                    "confidence", 0) > 0.7 else "gentle"

        response = _engine_process(user_input, ctx)

        return response if response else ""

    except Exception as e:
        logger.warning(f"Response engine call failed: {e}")

        # Fallback: build basic response from local analysis
        glyphs = local_analysis.get("glyphs", [])
        voltage_response = local_analysis.get("voltage_response", "")
        best_glyph = local_analysis.get("best_glyph")
        glyph_display = best_glyph.get(
            "glyph_name", "None") if best_glyph else "None"

        if glyphs:
            return f"{voltage_response}\n\nResonant Glyph: {glyph_display}"
        else:
            return voltage_response or "I'm here to listen."


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
                "That's important — would you like a short breathing practice or a practical plan?",
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
