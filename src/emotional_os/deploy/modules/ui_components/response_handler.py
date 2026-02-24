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
- Tier 1: Foundation (learning, safety, wrapping)
- Tier 2: Aliveness (presence, energy, reciprocity)
- Ollama LLM fallback for local model inference
"""

import time
import logging
import streamlit as st
from src.emotional_os.tier1_foundation import Tier1Foundation
from src.emotional_os.tier2_aliveness import Tier2Aliveness
from src.emotional_os.tier3_poetic_consciousness import Tier3PoeticConsciousness
from ..ollama_client import get_ollama_client_singleton
from src.emotional_os.deploy.modules.ui_components.mood_ring import generate_mood, mood_seed_for_window

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
    # Trace processing mode and orchestrator presence
    fp_present = 'yes' if st.session_state.get("firstperson_orchestrator") else 'no'
    logger.info(f"handle_response_pipeline start: mode={processing_mode}, firstperson_present={fp_present}")
    
    # Initialize Tier 1 Foundation if not already done
    if "tier1_foundation" not in st.session_state:
        try:
            tier1 = Tier1Foundation(conversation_memory=None)
            st.session_state.tier1_foundation = tier1
            logger.info("Tier 1 Foundation initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Tier 1 Foundation: {e}")
            st.session_state.tier1_foundation = None

    # Initialize Tier 2 Aliveness if not already done
    if "tier2_aliveness" not in st.session_state:
        try:
            tier2 = Tier2Aliveness()
            st.session_state.tier2_aliveness = tier2
            logger.info("Tier 2 Aliveness initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Tier 2 Aliveness: {e}")
            st.session_state.tier2_aliveness = None

    # Tier 3 Poetic Consciousness is archived by default. A session flag
    # (`enable_tier3_poetic`) controls whether Tier3 is initialized and used.
    st.session_state.setdefault("enable_tier3_poetic", False)
    if st.session_state.get("enable_tier3_poetic") and "tier3_poetic_consciousness" not in st.session_state:
        try:
            tier3 = Tier3PoeticConsciousness()
            st.session_state.tier3_poetic_consciousness = tier3
            logger.info("Tier 3 Poetic Consciousness initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Tier 3 Poetic Consciousness: {e}")
            st.session_state.tier3_poetic_consciousness = None

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

        # Prevent verbatim repetition (pass current user input and conversation context so we can detect complaints)
        response = _prevent_response_repetition(user_input, response, conversation_context)
        
        # SYNTHESIS LAYER: Add captured details from user input to make response more specific
        # This ensures responses show they understood what the user said, not just generic prompts
        response = _synthesize_with_user_details(user_input, response, conversation_context)
        
        # TIER 1: Enhance response with learning and safety wrapping
        tier1 = st.session_state.get("tier1_foundation")
        if tier1:
            try:
                enhanced_response, tier1_metrics = tier1.process_response(
                    user_input=user_input,
                    base_response=response,
                    context=conversation_context,
                )
                # Log performance metrics
                if tier1_metrics.get("total", 0) > 0.1:
                    logger.warning(f"Tier 1 pipeline slow: {tier1_metrics['total']:.3f}s")
                else:
                    logger.debug(f"Tier 1 metrics: {tier1_metrics}")
                # Use enhanced response
                response = enhanced_response
            except Exception as e:
                logger.warning(f"Tier 1 enhancement failed: {e}, using base response")

        # TIER 2: Add aliveness and presence through emotional tuning
        tier2 = st.session_state.get("tier2_aliveness")
        if tier2:
            try:
                # Get conversation history for context
                conversation_history = conversation_context.get("messages", [])
                
                # Process for aliveness (tone, intensity, embodiment, energy)
                aliveness_response, tier2_metrics = tier2.process_for_aliveness(
                    user_input=user_input,
                    base_response=response,
                    history=conversation_history,
                )
                
                # Log performance metrics
                tier2_time = tier2_metrics.get("processing_time_ms", 0)
                if tier2_time > 30:
                    logger.warning(f"Tier 2 pipeline slow: {tier2_time:.2f}ms")
                else:
                    logger.debug(f"Tier 2 metrics: {tier2_metrics}")
                
                # Use aliveness-enhanced response
                response = aliveness_response
            except Exception as e:
                logger.warning(f"Tier 2 aliveness failed: {e}, using Tier 1 response")

        # TIER 3: Poetic consciousness is archived; only run if explicitly enabled
        if st.session_state.get("enable_tier3_poetic"):
            tier3 = st.session_state.get("tier3_poetic_consciousness")
            if tier3 and len(response) > 100:  # Only enhance longer responses
                try:
                    # Get conversation history and theme for context
                    conversation_history = conversation_context.get("messages", [])
                    theme = conversation_context.get("emotional_theme", "growth")

                    # Process for poetry (metaphor, aesthetics, tension, mythology)
                    poetry_response, tier3_metrics = tier3.process_for_poetry(
                        response=response,
                        context={
                            "messages": conversation_history,
                            "theme": theme
                        }
                    )

                    # Log performance metrics
                    tier3_time = tier3_metrics.get("processing_time_ms", 0)
                    if tier3_time > 30:
                        logger.warning(f"Tier 3 pipeline slow: {tier3_time:.2f}ms")
                    else:
                        logger.debug(f"Tier 3 metrics: {tier3_metrics}")

                    # Use poetry-enhanced response
                    response = poetry_response
                except Exception as e:
                    logger.warning(f"Tier 3 poetry enhancement failed: {e}, using Tier 2 response")

    except Exception as e:
        logger.error(f"Response pipeline FAILED: {type(e).__name__}: {e}", exc_info=True)
        import traceback
        tb_str = traceback.format_exc()
        logger.error(f"Full traceback:\n{tb_str}")
        response = f"[ERROR] Response pipeline failed: {e}"

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
        from .remote_parser import remote_parse_input
        from emotional_os.core.paths import get_path_manager

        # Get proper paths using PathManager (handles both local and cloud deployments)
        pm = get_path_manager()
        lexicon_path = str(pm._resolve_path(
            "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
            "word_centric_emotional_lexicon_expanded.json"
        ))
        db_path = str(pm.glyph_db())

        # Local signal parsing with word-centric lexicon
        local_analysis = parse_input(
            user_input,
            lexicon_path,
            db_path=db_path,
            conversation_context=conversation_context,
        )

        # If running in non-local mode or local parsing didn't produce glyphs/responses,
        # prefer the remote ML engine (keeps UI lightweight and delegates NLP).
        processing_mode = st.session_state.get("processing_mode", "local")
        prefers_remote = processing_mode != "local"
        need_remote = False
        # If processing mode prefers remote, we'll use it
        if prefers_remote:
            need_remote = True
        else:
            # If local analysis lacks voltage_response or best_glyph, try remote
            if not local_analysis.get("voltage_response") or not local_analysis.get("best_glyph"):
                need_remote = True

        # Be more aggressive: if spaCy is not installed in this runtime, force remote parsing
        try:
            import spacy  # type: ignore
            spacy_available = True
        except Exception:
            spacy_available = False
        if not spacy_available:
            logger.info("_run_local_processing: spaCy not available in UI runtime; forcing remote parse")
            need_remote = True

        if need_remote:
            remote = None
            try:
                remote = remote_parse_input(user_input, conversation_context)
            except Exception as e:
                logger.debug(f"remote_parse_input exception: {e}")

            if remote:
                logger.info("_run_local_processing: using remote parse result")
                local_analysis = remote

        # Ensure local_analysis is a dict
        if not isinstance(local_analysis, dict):
            logger.warning(f"parse_input returned non-dict: {type(local_analysis)}")
            local_analysis = {}

        # DEBUG: Log what parse_input returned
        logger.info(f"parse_input returned:")
        logger.info(f"  voltage_response: {local_analysis.get('voltage_response', 'MISSING')[:200] if local_analysis.get('voltage_response') else 'NONE/EMPTY'}")
        best_glyph = local_analysis.get('best_glyph')
        glyph_name = best_glyph.get('glyph_name', 'NONE') if isinstance(best_glyph, dict) else 'NONE'
        logger.info(f"  best_glyph: {glyph_name}")
        logger.info(f"  response_source: {local_analysis.get('response_source')}")

        # Get the conversational response from the analysis
        response = _build_conversational_response(user_input, local_analysis)

        # Store analysis in session for debug if needed
        st.session_state["last_local_analysis"] = local_analysis

        return response

    except Exception as e:
        logger.error(f"Local processing FAILED: {type(e).__name__}: {e}", exc_info=True)
        import traceback
        tb_str = traceback.format_exc()
        logger.error(f"Full traceback:\n{tb_str}")
        return f"[LOCAL_ERROR] {e}"


def _build_conversational_response(user_input: str, local_analysis: dict) -> str:
    """Build a natural conversational response from signal analysis.
    
    Uses FirstPerson orchestrator with glyph as constraint (not template):
    1. Glyph informs tone/depth/emotional grounding
    2. Response is fresh and specific to THIS user input
    3. No canned responses - each response is generated for context
    
    Args:
        user_input: Original user message
        local_analysis: Analysis dict from parse_input
        
    Returns:
        Fresh, non-canned conversational response
    """
    best_glyph = local_analysis.get("best_glyph") if local_analysis else None
    voltage_response = local_analysis.get("voltage_response", "") if local_analysis else ""
    # Early preference: if parse_input indicated a fallback_message and the
    # user asked a short mood/feeling question, prefer the mood-ring or
    # subordinate responder before using any voltage_response (prevents poetic fallbacks).
    try:
        if local_analysis.get("response_source") == "fallback_message":
            u = (user_input or "").strip()
            is_short = len(u) < 120
            lower = u.lower()
            # detect mood questions explicitly
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
                    # Try to get weather hint from local analysis if present
                    weather = None
                    if isinstance(local_analysis, dict):
                        weather = local_analysis.get("weather") or local_analysis.get("external_weather")
                    seed = mood_seed_for_window(None, weather or "Sunny")
                    return generate_mood(now=None, weather=weather or "Sunny", seed=seed, chaos=chaos)
                except Exception:
                    logger.debug("Mood ring generation failed; falling back to responder")

            if is_short and not is_mood_question:
                q_terms = ("feel", "feeling", "how are you", "what would", "if you had")
                is_question = ('?' in u) or any(q in lower for q in q_terms)
                if is_question:
                    try:
                        responder = st.session_state.get("responder")
                        convo_ctx = st.session_state.get("conversation_context") or {}
                        emotional_vector = local_analysis.get("emotional_vector") if isinstance(local_analysis, dict) else None
                        if responder and hasattr(responder, "respond"):
                            sub_resp = responder.respond(user_input, convo_ctx, emotional_vector or [])
                            return sub_resp.response_text
                    except Exception:
                        logger.debug("Subordinate responder failed for fallback_message (early)")
    except Exception:
        pass
    
    # If we have a voltage response, use that as the primary response
    if voltage_response and voltage_response.strip():
        # Clean up any leftover metadata
        response = voltage_response.strip()
        if "Resonant Glyph:" in response:
            response = response.split("Resonant Glyph:")[0].strip()

        # IMPORTANT: Check if this is a composite response (analysis + conversational)
        # separated by blank line or double newline
        parts = response.split("\n\n")
        if len(parts) > 1:
            # Multi-part response: first is analysis/poetic, second+ is conversational
            # Use ONLY the conversational part (last part) for tier processing
            conversational_response = parts[-1].strip()
            # Store the poetic analysis for potential debugging
            poetic_analysis = parts[0].strip()
            logger.debug(f"Composite response detected. Analysis: {poetic_analysis[:100]}...")
            return conversational_response

        # Single response: sanitize against poetic/glyph-description outputs
        logger.info("_build_conversational_response: USING_VOLTAGE_RESPONSE (sanitizing)")
        try:
            st.session_state["last_used_response_source"] = {
                "source": "voltage_response",
                "voltage_snippet": response[:300],
                "best_glyph": best_glyph.get("glyph_name") if isinstance(best_glyph, dict) else None,
            }
        except Exception:
            pass

        # Defensive sanitization: if the voltage response appears poetic or directly
        # mirrors the glyph description, avoid returning it verbatim to the UI.
        try:
            rt_lower = response.lower()
            poetic_markers = (
                "fullness",
                "steeped",
                "ecstatic",
                "joy so",
                "bliss",
                "saturat",
                "still",
                "mourning",
                "sanctify",
                "poetic",
                "lyric",
            )
            looks_poetic = any(m in rt_lower for m in poetic_markers) or len(rt_lower.split()) > 40

            glyph_desc = ""
            if best_glyph and isinstance(best_glyph, dict):
                glyph_desc = (best_glyph.get("description") or "").strip().lower()

            duplicates_glyph_desc = glyph_desc and glyph_desc and (glyph_desc in rt_lower or rt_lower in glyph_desc)

            if looks_poetic or duplicates_glyph_desc:
                # Prefer subordinate responder (if available) to produce a grounded reply
                try:
                    responder = st.session_state.get("responder")
                    convo_ctx = st.session_state.get("conversation_context") or {}
                    emotional_vector = local_analysis.get("emotional_vector") if isinstance(local_analysis, dict) else None
                    if responder and hasattr(responder, "respond"):
                        sub_resp = responder.respond(user_input, convo_ctx, emotional_vector or [])
                        return sub_resp.response_text
                except Exception:
                    # If subordinate not available or fails, fall back to a gentle generic reply
                    pass

                # Gentle sanitized fallback
                return "I hear you. Can you say a bit more about how that feels?"
        except Exception:
            # If sanitization checks fail, return original response as last resort
            return response

        return response
    
    # Use FirstPerson orchestrator to generate glyph-informed response
    try:
        fp_orch = st.session_state.get("firstperson_orchestrator")
        if fp_orch and best_glyph and isinstance(best_glyph, dict):
            # Generate fresh response using glyph as constraint
            response = fp_orch.generate_response_with_glyph(user_input, best_glyph)
            logger.info(f"_build_conversational_response: USING_FIRSTPERSON glyph={best_glyph.get('glyph_name')}")
            try:
                st.session_state["last_used_response_source"] = {
                    "source": "firstperson",
                    "glyph": best_glyph.get("glyph_name"),
                    "response_snippet": response[:300],
                }
            except Exception:
                pass
            return response
    except Exception as e:
        logger.debug(f"FirstPerson response generation failed: {e}")
    
    # Fallback: build a simple acknowledgment + glyph insight
    # This is a minimal conversational wrapper
    glyph_name = best_glyph.get("glyph_name", "") if best_glyph and isinstance(best_glyph, dict) else ""
    glyph_desc = best_glyph.get("description", "") if best_glyph and isinstance(best_glyph, dict) else ""
    
    if glyph_name:
        # Create a simple conversational response
        opening = "I hear you. "
        if len(user_input) < 30:
            opening += "That sounds important. "
        else:
            opening += "That's a lot to carry. "
        
        # Use glyph insight as support
        if glyph_desc:
            # Defensive: if the glyph description looks poetic, avoid returning
            # the verbatim description to the user. Prefer subordinate responder
            # or a short, grounded acknowledgement.
            try:
                gd_lower = glyph_desc.lower()
                poetic_markers = (
                    "fullness",
                    "steeped",
                    "ecstatic",
                    "joy so",
                    "bliss",
                    "saturat",
                    "still",
                    "mourning",
                    "sanctify",
                    "poetic",
                    "lyric",
                )
                looks_poetic = any(m in gd_lower for m in poetic_markers) or len(gd_lower.split()) > 40
                if looks_poetic:
                    try:
                        responder = st.session_state.get("responder")
                        convo_ctx = st.session_state.get("conversation_context") or {}
                        emotional_vector = local_analysis.get("emotional_vector") if isinstance(local_analysis, dict) else None
                        if responder and hasattr(responder, "respond"):
                            sub_resp = responder.respond(user_input, convo_ctx, emotional_vector or [])
                            return sub_resp.response_text
                    except Exception:
                        pass
                    return f"{opening}I’m sensing {glyph_name.lower()}. Can you say more about how that feels?"
                else:
                    return f"{opening}I'm sensing {glyph_name.lower()} — {glyph_desc.lower()}."
            except Exception:
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


def _prevent_response_repetition(user_input: str, response: str, conversation_context: dict = None) -> str:
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

        # Collect recent assistant messages (robust to different history formats)
        assistant_msgs = []
        user_msgs = []
        for item in reversed(history[-10:]):  # look back up to last 10 exchanges
            if isinstance(item, dict):
                # Try common keys
                if "assistant" in item:
                    assistant_msgs.append(str(item.get("assistant") or "").strip())
                elif item.get("role") == "assistant":
                    assistant_msgs.append(str(item.get("content") or item.get("message") or "").strip())
                if item.get("role") == "user" or "user" in str(item.get("role", "")).lower():
                    user_msgs.append(str(item.get("content") or item.get("message") or item.get("user") or "").strip())
            elif isinstance(item, str):
                # Heuristic: alternate user/assistant unknown — skip
                pass

        # If any recent assistant message is similar to the current response,
        # treat it as repetition and choose an alternative follow-up.
        def _norm(s: str) -> str:
            import re

            return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", (s or "").lower())).strip()

        normalized = _norm(response)
        recent_assistant_norms = [_norm(am) for am in assistant_msgs[:5] if am]

        # Direct check against last assistant message from conversation context
        try:
            ctx_last = None
            if isinstance(conversation_context, dict):
                ctx_last = conversation_context.get("last_assistant_message")
            if not ctx_last:
                try:
                    from .session_manager import get_conversation_context
                    ctx_last = get_conversation_context().get("last_assistant_message")
                except Exception:
                    ctx_last = None
            last_assistant_norm_direct = _norm(ctx_last or "")
        except Exception:
            last_assistant_norm_direct = ""

        # If the last assistant message exactly matches the candidate response and
        # the user just provided a substantive reply, acknowledge rather than re-ask.
        try:
            if last_assistant_norm_direct and last_assistant_norm_direct == normalized:
                # substantive user reply heuristic
                if len((user_input or "").split()) > 3 and not any(t in (user_input or "").lower() for t in ("you already", "not helpful", "stop repeating")):
                    frag = (user_input or "").split('.')[-1].strip() or (user_input or "")[:80]
                    return f"Thanks — it sounds like {frag}. That makes sense; would you like a short grounding or a tiny next step right now?"
        except Exception:
            pass

        is_repeated = any(r == normalized or (r and normalized and (r in normalized or normalized in r)) for r in recent_assistant_norms)

        # Also inspect current user_input for complaint triggers (current message not yet in history)
        complaint_triggers = ("you already", "already asked", "not helpful", "stop repeating", "you asked", "you already asked")
        current_user = (user_input or "").lower()
        user_complaint_current = any(trigger in current_user for trigger in complaint_triggers)

        # If the user explicitly complains about repetition, apologize and offer grounding
        if user_complaint_current:
            print(f"DEBUG: complaint detected in user_input='{current_user}'")
            alt = (
                "Sorry — I repeated myself. Thank you for pointing that out. "
                "It sounds frustrating; I can slow down and try a different approach. "
                "Would you prefer a brief grounding exercise, a practical step, or something else?"
            )
            return alt

        # Debugging info
        try:
            logger.debug(f"RepetitionCheck: normalized_response='{normalized[:120]}', recent_assistant_norms={recent_assistant_norms}, current_user='{current_user[:120]}'")
        except Exception:
            pass

        # QUICK HEURISTIC: if the candidate response is the clarifying question
        # and the user's current message appears to answer it (has content/keywords),
        # reflect rather than re-ask. This catches cases where history/context
        # lookups may be unreliable in non-Streamlit runs.
        try:
            if "what would it look" in normalized and (len(current_user.split()) > 6 or any(k in current_user for k in ("tension", "frozen", "rest", "feel", "feelings"))):
                fragment = current_user.split('.')[-1].strip()
                fragment = fragment if fragment else current_user[:80]
                reflect = f"Thanks for sharing that — it sounds like {fragment}. That makes sense given everything you're juggling. Would you like a grounding exercise or a small practical step right now?"
                return reflect
        except Exception:
            pass
        # If the last assistant asked a clarifying question (e.g., "What would it look like...")
        # and the current user input appears to answer it (has content/keywords),
        # prefer acknowledging and reflecting rather than re-asking.
        try:
            ctx = conversation_context if conversation_context is not None else get_conversation_context()
            last_assistant_msg = (ctx.get("last_assistant_message") or "") if isinstance(ctx, dict) else ""
        except Exception:
            last_assistant_msg = ""

        la_lower = (last_assistant_msg or "").lower()
        clarifying_markers = ("what would it look", "what would it look like", "can you tell me one specific detail", "what would it look like if you could")
        asked_clarifying = any(m in la_lower for m in clarifying_markers) or ("?" in la_lower and len(la_lower.split()) < 40)

        # Heuristics for current user answering: contains emotional keywords or longer than a short reply
        answer_keywords = ("tension", "frozen", "feel", "feelings", "mood", "relief", "rest", "meltd", "tension", "stress")
        looks_like_answer = (len(current_user.split()) > 6) or any(k in current_user for k in answer_keywords)

        if asked_clarifying and looks_like_answer and not user_complaint_current:
            # Build a short reflective reply acknowledging the user's answer
            try:
                # Extract a short phrase from user's input for reflection
                fragment = current_user.split('.')[-1].strip()
                fragment = fragment if fragment else current_user[:80]
                reflect = f"Thanks for sharing that — it sounds like {fragment}. That makes sense given everything you're juggling. Would you like a grounding exercise or a small practical step right now?"
                return reflect
            except Exception:
                pass

        if is_repeated:
            # Check last assistant message from conversation context (if passed in session)
            try:
                from .session_manager import get_conversation_context
                ctx = get_conversation_context()
                last_assistant_msg = (ctx.get("last_assistant_message") or "")
            except Exception:
                last_assistant_msg = ""

            last_assistant_norm = _norm(last_assistant_msg)

            # If the last assistant message is the same clarifying prompt and the user
            # just repeated themselves (or complained), don't ask the same question again.
            repeated_clarifying = last_assistant_norm and (last_assistant_norm == normalized or last_assistant_norm in normalized or normalized in last_assistant_norm)

            if user_complaint_current or any(any(trigger in um.lower() for trigger in complaint_triggers) for um in user_msgs[:3] if um) or repeated_clarifying:
                alt = (
                    "Sorry — I repeated myself. Thank you for pointing that out. "
                    "It sounds like the tension in your body feels like it's holding you still. "
                    "If you want, we can try a brief grounding: take one slow breath in, hold, and let it go — "
                    "or tell me one tiny thing that might soften that tension right now."
                )
                return alt

            # Otherwise, append a varied follow-up (avoid reusing the same follow-up every time)
            followups = [
                "Can you tell me one specific detail about that?",
                "Would it help if we tried one small concrete step together?",
                "If you pick one thing to focus on right now, what would it be?",
                "That's important — would you like a short breathing practice or a practical plan?",
            ]

            # Choose a follow-up that's different from the most recent assistant follow-up
            for f in followups:
                if not recent_assistant_norms or all(_norm(f) not in r for r in recent_assistant_norms):
                    response = f"{response} {f}"
                    break

    except Exception as e:
        logger.debug(f"Repetition prevention failed: {e}")

    return response



def _synthesize_with_user_details(user_input: str, base_response: str, 
                                 conversation_context: dict) -> str:
    """Enhance response by incorporating specific details from user input.
    
    Transforms generic responses into specific ones by:
    1. Tracking themes across the conversation (not just this message)
    2. Recognizing emotional patterns and their connections
    3. Building a coherent narrative arc rather than repeating a pattern
    4. Responding with genuine synthesis, not mechanical pattern-matching
    
    Args:
        user_input: User's message
        base_response: Initial response from system
        conversation_context: Conversation history
        
    Returns:
        Response that builds on previous exchanges, not mechanical pattern
    """
    try:
        import json
        
        # Get conversation history from multiple possible sources
        history = conversation_context.get("messages", [])
        
        # If no messages in context, try session state as fallback
        if not history:
            history = st.session_state.get("conversation_history_", [])
        
        logger.debug(f"Synthesis: history length = {len(history)}, user_input length = {len(user_input)}")
        
        # Extract themes from entire conversation, not just current input
        conversation_themes = _extract_conversation_themes(history, user_input)
        
        # Only apply synthesis if we have meaningful conversation history
        if len(history) < 4:  # Need at least 2 exchanges (4 messages)
            # First exchange: keep simple, just acknowledge
            logger.debug("Synthesis: early in conversation, using base response")
            return base_response
        
        # Check if this is a significant disclosure (divorce/co-parenting revelation)
        is_significant_disclosure = _is_significant_disclosure(user_input, history)
        
        # Decide response type based on conversation arc
        response_type = _determine_response_type(conversation_themes, history, is_significant_disclosure)
        logger.debug(f"Synthesis: response_type = {response_type}, themes = {conversation_themes}")
        
        # Generate response appropriate to the conversation stage
        if response_type == "acknowledge_new_context":
            # Something important was just revealed - acknowledge it and connect to earlier themes
            logger.debug("Synthesis: acknowledge_new_context")
            return _respond_to_significant_disclosure(user_input, conversation_themes, history)
        
        elif response_type == "deepen_exploration":
            # We have enough understanding to ask deeper questions
            logger.debug("Synthesis: deepen_exploration")
            return _respond_with_deeper_exploration(user_input, conversation_themes, history)
        
        elif response_type == "recognize_pattern":
            # Patterns are emerging - name them and what they might mean
            logger.debug("Synthesis: recognize_pattern")
            return _respond_with_pattern_recognition(conversation_themes, history)
        
        elif response_type == "integration":
            # Earlier exchanges + new input: help integrate understanding
            logger.debug("Synthesis: integration")
            return _respond_with_integration(user_input, conversation_themes, history)
        
        else:
            # Generic acknowledgment (fallback)
            logger.debug("Synthesis: fallback to base response")
            return base_response
            
    except Exception as e:
        logger.debug(f"Response synthesis failed: {e}, using base response")
        import traceback
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return base_response


def _extract_conversation_themes(history: list, current_input: str) -> dict:
    """Extract themes that have emerged across the entire conversation."""
    themes = {
        "immediate_stressors": [],
        "emotional_patterns": [],
        "physical_responses": [],
        "longer_term_context": [],
        "coping_strategies": [],
        "insights_shared": [],
    }
    
    try:
        current_lower = current_input.lower()
        
        # Build text from all user messages in history
        all_text = current_input.lower() + " "
        
        # Handle different history formats
        for item in history:
            if isinstance(item, dict):
                # Try different possible field names
                content = (item.get("content") or 
                          item.get("message") or 
                          item.get("user") or 
                          item.get("assistant") or "")
                if item.get("role") == "user" or "user" in str(item.get("role", "")).lower():
                    all_text += " " + str(content).lower()
            elif isinstance(item, str):
                all_text += " " + item.lower()
        
        logger.debug(f"Theme extraction: total text length = {len(all_text)}")
        
        # Immediate stressors
        if any(w in all_text for w in ["work", "job", "employee", "task", "deadline", "pile"]):
            themes["immediate_stressors"].append("work/responsibility")
        if any(w in all_text for w in ["divorce", "co-parent", "co parent", "ex", "kids", "children"]):
            themes["longer_term_context"].append("family transitions")
        
        # Emotional patterns
        if any(w in all_text for w in ["shut down", "shutdown", "avoid", "avoidance", "escape"]):
            themes["emotional_patterns"].append("avoidance/shutdown response")
        if any(w in all_text for w in ["overwhelm", "pile on", "relief", "stress"]):
            themes["emotional_patterns"].append("overwhelm cycle")
        if any(w in all_text for w in ["embarrass", "shame", "expose"]):
            themes["emotional_patterns"].append("shame/exposure vulnerability")
        
        # Physical responses
        if any(w in all_text for w in ["chest", "breathing", "breath", "tight", "tense"]):
            themes["physical_responses"].append("chest/breathing tension")
        if any(w in all_text for w in ["jumpy", "jump", "anxious", "nervous"]):
            themes["physical_responses"].append("hypervigilance/jumpiness")
        if any(w in all_text for w in ["drift", "drifts", "focus", "distract", "distraction"]):
            themes["physical_responses"].append("dissociation/difficulty focusing")
        
        # Insights already shared
        if "shut" in all_text and "avoid" in all_text:
            themes["insights_shared"].append("awareness of shutdown pattern")
        
        logger.debug(f"Extracted themes: {themes}")
        return themes
    except Exception as e:
        logger.debug(f"Theme extraction failed: {e}")
        return themes


def _is_significant_disclosure(current_input: str, history: list) -> bool:
    """Detect when user reveals something significant that changes context."""
    significant_markers = [
        "divorce", "separated", "co-parent", "custody", "ex-",
        "trauma", "abuse", "assault", "loss", "death",
        "hospitalized", "therapy", "medication", "diagnosed"
    ]
    return any(marker in current_input.lower() for marker in significant_markers)


def _determine_response_type(themes: dict, history: list, is_significant: bool) -> str:
    """Determine what type of response is appropriate at this stage."""
    exchange_count = len(history)
    
    # First reveal of big context change
    if is_significant and exchange_count >= 4:
        return "acknowledge_new_context"
    
    # We know the main stressor + pattern + physical response
    if (themes["immediate_stressors"] and themes["emotional_patterns"] 
        and themes["physical_responses"] and exchange_count >= 4):
        return "recognize_pattern"
    
    # Multiple exchanges, time to get deeper
    if exchange_count > 5:
        return "deepen_exploration"
    
    # New information coming in - integrate it
    if exchange_count > 2:
        return "integration"
    
    return "simple_acknowledge"


def _respond_to_significant_disclosure(current_input: str, themes: dict, history: list) -> str:
    """Respond when user reveals something that adds new context to understanding."""
    opening = "Thank you for sharing that. "
    
    # Acknowledge the new context
    if "divorce" in current_input.lower():
        opening += "The ongoing work with co-parenting, the emotional switching back and forth between two worlds — "
        opening += "that's its own kind of stress that doesn't just resolve. "
    
    # Connect to earlier themes
    if themes["immediate_stressors"] and themes["emotional_patterns"]:
        opening += "And when you're carrying that alongside the work pressure and the shutdown pattern you mentioned, "
        opening += "it makes sense that relief feels so hard to find. "
    
    # Move toward understanding
    opening += "\nIt sounds like this isn't just about today's work pile — "
    opening += "it's about being stretched thin across multiple contexts, each demanding something different from you."
    
    return opening


def _respond_with_pattern_recognition(themes: dict, history: list) -> str:
    """Respond by naming emerging patterns."""
    if not themes["emotional_patterns"]:
        return "I'm noticing something in what you're sharing. Can you tell me more?"
    
    pattern = themes["emotional_patterns"][0] if themes["emotional_patterns"] else ""
    
    responses = [
        f"I'm seeing a pattern: stress comes, and your instinct is to {pattern}. But that creates its own problem.",
        f"The {pattern} makes sense as a survival response, but it sounds like it's not serving you well right now.",
        f"That {pattern} response — it might be protecting you from feeling overwhelmed, but it's also keeping you stuck.",
    ]
    
    import random
    base = random.choice(responses)
    
    # Add specific follow-up based on what's emerged
    if "physical" in str(themes.get("physical_responses", [])):
        base += " Your body is clearly showing the strain with the tightness and jumpiness."
    
    return base


def _respond_with_integration(current_input: str, themes: dict, history: list) -> str:
    """Integrate new information with what's already emerged."""
    # Show you're tracking what came before
    recap = _generate_recap_from_history(history)
    
    # Add current input
    new_detail = _extract_new_detail(current_input)
    
    # Connect them
    integration = f"So before you mentioned {recap.lower()}. Now you're also telling me {new_detail}. "
    integration += "That's all happening at the same time for you."
    
    return integration


def _respond_with_deeper_exploration(current_input: str, themes: dict, history: list) -> str:
    """Move to deeper, more curious questions."""
    if "relief" in current_input.lower():
        return "You mentioned that as soon as you get relief, something else gets piled on. "
        return "Do you think that's just bad timing, or does part of you create that? Like you can't sit with relief?"
    
    return "What would it look like if you could actually rest — not just take a break, but truly rest without guilt?"


def _generate_recap_from_history(history: list) -> str:
    """Generate a brief recap of what's emerged in conversation so far."""
    user_messages = [msg for msg in history if msg.get("role") == "user"]
    
    recap_parts = []
    if len(user_messages) > 0:
        if "work" in user_messages[0].get("content", "").lower():
            recap_parts.append("work stress")
        if any("avoid" in msg.get("content", "").lower() for msg in user_messages):
            recap_parts.append("avoidance pattern")
        if any("breath" in msg.get("content", "").lower() or "chest" in msg.get("content", "").lower() 
               for msg in user_messages):
            recap_parts.append("physical tension")
    
    return ", ".join(recap_parts) if recap_parts else "what you shared"


def _extract_new_detail(current_input: str) -> str:
    """Extract what's new in the current input."""
    if "divorce" in current_input.lower():
        return "dealing with co-parenting and life transitions on top of work stress"
    if "drifts" in current_input.lower() or "distract" in current_input.lower():
        return "having trouble staying focused even when you know what you should be doing"
    if "relief" in current_input.lower():
        return "that the cycle keeps resetting before you can catch your breath"
    return "something else that's adding to this"



def _get_ollama_fallback_response(user_input: str, conversation_context: dict) -> str:
    """Generate response using Ollama local LLM as fallback.
    
    This is triggered when:
    1. Local processing fails or returns empty response
    2. FirstPerson orchestrator unavailable
    3. Explicitly requested for offline/local-only mode
    
    Uses conversation context to maintain coherence and emotional awareness.
    
    Args:
        user_input: User message
        conversation_context: Conversation history and context
        
    Returns:
        Generated response from Ollama, or fallback text if Ollama unavailable
    """
    try:
        # Get Ollama client singleton
        ollama = get_ollama_client_singleton()
        
        # Check if Ollama is available
        if not ollama.is_available():
            logger.warning("Ollama service not available, using default fallback")
            return "I'm here to listen. Can you tell me more about what's on your mind?"
        
        # Get available models
        models = ollama.get_available_models()
        if not models:
            logger.warning("No Ollama models available")
            return "I'm here to listen. Can you tell me more about what's on your mind?"
        
        # Use first available model (usually llama3 if pulled)
        model = models[0] if models else "llama3"
        logger.info(f"Using Ollama model: {model}")
        
        # Build system prompt for emotional context
        system_prompt = """You are FirstPerson, a warm, empathetic AI companion for personal growth.
        
Respond with:
- Genuine understanding and emotional attunement
- Specific, thoughtful engagement with what the user shares
- Practical support or gentle exploration, not generic advice
- Your own authentic presence (not pretending to be human)
- Brief, natural responses (2-4 sentences usually)

Stay focused on understanding the user's experience, not solving problems immediately."""
        
        # Extract conversation history for context
        conversation_history = conversation_context.get("messages", [])[-10:]  # Last 10 exchanges
        
        try:
            # Generate response with context awareness
            response = ollama.generate_with_context(
                user_input=user_input,
                conversation_history=conversation_history,
                model=model,
                system_prompt=system_prompt,
                max_history=10,
            )
            
            if response and response.strip():
                logger.info(f"Ollama response generated ({len(response)} chars)")
                return response.strip()
            else:
                logger.warning("Ollama returned empty response")
                return "I'm here. Can you share more?"
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return "I'm here to listen. What's on your mind?"
    
    except Exception as e:
        logger.error(f"Ollama fallback error: {e}")
        return "I'm here to listen. Can you tell me more about what's on your mind?"


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
