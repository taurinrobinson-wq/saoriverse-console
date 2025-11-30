"""Mobile/Service adapter for FirstPerson hybrid pipeline.

This module implements a self-contained, Streamlit-free hybrid
pipeline suitable for FastAPI / React clients. It performs the local
signal parsing, attempts a remote AI call when available, and falls
back to local composition when needed. It intentionally avoids
importing the Streamlit UI runtime so it won't interfere with the
existing Streamlit-based `ui.py`.
"""
from typing import Tuple, Dict, Any
import os


def run_hybrid_pipeline_mobile(effective_input: str,
                               conversation_context: dict,
                               saori_url: str,
                               supabase_key: str,
                               user_id: str = None,
                               processing_mode: str = 'local') -> Tuple[str, Dict[str, Any], dict]:
    """Run the hybrid pipeline in a mobile/service-friendly way.

    Returns (response_text, debug_info, local_analysis).
    """
    try:
        try:
            from emotional_os.glyphs.signal_parser import parse_input
        except Exception:
            parse_input = None

        # Perform local analysis
        local_analysis = {}
        if parse_input:
            try:
                local_analysis = parse_input(
                    effective_input,
                    "emotional_os/parser/signal_lexicon.json",
                    db_path="emotional_os/glyphs/glyphs.db",
                    conversation_context=conversation_context,
                )
            except Exception:
                local_analysis = {}

        glyphs = local_analysis.get('glyphs', [])
        voltage_response = local_analysis.get('voltage_response', '')
        ritual_prompt = local_analysis.get('ritual_prompt', '')

        # Try remote AI if configured and the processing mode allows it.
        # When `processing_mode` is 'local' we prefer fully-local composition
        # and avoid calling the remote SAORI function.
        if processing_mode != 'local' and saori_url and supabase_key:
            try:
                import requests as _requests
            except Exception:
                _requests = None

            if _requests is not None:
                payload = {
                    "message": effective_input,
                    "mode": processing_mode,
                    "user_id": user_id,
                    "local_voltage_response": voltage_response,
                    "local_glyphs": ', '.join([g.get('glyph_name', '') for g in glyphs]) if glyphs else '',
                    "local_ritual_prompt": ritual_prompt
                }
                try:
                    resp = _requests.post(
                        saori_url,
                        headers={
                            "Authorization": f"Bearer {supabase_key}",
                            "Content-Type": "application/json"
                        },
                        json=payload,
                        timeout=15,
                    )
                except Exception:
                    resp = None

                if resp is None:
                    # Remote call failed — fall back to local composer
                    try:
                        from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer
                        composer = DynamicResponseComposer()
                        if glyphs:
                            response_text = composer.compose_multi_glyph_response(
                                effective_input, glyphs, conversation_context=conversation_context, top_n=5)
                        else:
                            response_text = "I'm listening, but I couldn't feel a clear glyphic resonance yet."
                    except Exception:
                        response_text = (
                            f"Local Analysis: {voltage_response}\n"
                            f"Activated Glyphs: {', '.join([g.get('glyph_name','') for g in glyphs]) if glyphs else 'None'}\n"
                            f"{ritual_prompt}\n(AI enhancement unavailable)"
                        )
                    return response_text, {}, local_analysis

                # Handle remote response
                try:
                    result = resp.json()
                except Exception:
                    result = None

                if resp.status_code != 200:
                    # Try to extract any helpful text
                    ai_reply = None
                    try:
                        ai_reply = (result or {}).get('reply') or (
                            result or {}).get('error') or ''
                    except Exception:
                        ai_reply = None

                    if ai_reply:
                        # Decode AI reply locally
                        try:
                            composed = ai_reply
                            debug = {}
                            if parse_input:
                                ai_local = parse_input(composed, "emotional_os/parser/signal_lexicon.json",
                                                       db_path="emotional_os/glyphs/glyphs.db",
                                                       conversation_context=conversation_context)
                                debug = {
                                    'signals': ai_local.get('signals', []),
                                    'gates': ai_local.get('gates', []),
                                    'glyphs': ai_local.get('glyphs', []),
                                }
                            return composed, debug, local_analysis
                        except Exception:
                            pass

                    # Final fallback: local composer
                    try:
                        from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer
                        composer = DynamicResponseComposer()
                        if glyphs:
                            response_text = composer.compose_multi_glyph_response(
                                effective_input, glyphs, conversation_context=conversation_context, top_n=5)
                        else:
                            response_text = "I'm listening, but I couldn't feel a clear glyphic resonance yet."
                    except Exception:
                        response_text = (
                            f"AI service error (HTTP {getattr(resp, 'status_code', 'unknown')}).\n"
                            f"Local Analysis: {voltage_response}\n"
                            f"Activated Glyphs: {', '.join([g.get('glyph_name','') for g in glyphs]) if glyphs else 'None'}\n"
                            f"{ritual_prompt}\n(AI enhancement unavailable)"
                        )
                    return response_text, {}, local_analysis

                # Success: return AI-enhanced reply and local debug
                ai_reply = result.get('reply', "I'm here to listen.") if isinstance(
                    result, dict) else (getattr(resp, 'text', '') or '')
                try:
                    composed = ai_reply
                    debug = {}
                    if parse_input:
                        ai_local = parse_input(ai_reply, "emotional_os/parser/signal_lexicon.json",
                                               db_path="emotional_os/glyphs/glyphs.db",
                                               conversation_context=conversation_context)
                        debug = {
                            'signals': ai_local.get('signals', []),
                            'gates': ai_local.get('gates', []),
                            'glyphs': ai_local.get('glyphs', []),
                        }
                    return composed, debug, local_analysis
                except Exception:
                    return ai_reply, {}, local_analysis

        # No remote AI: compose locally
        try:
            from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer
            composer = DynamicResponseComposer()
            if glyphs:
                response_text = composer.compose_multi_glyph_response(
                    effective_input, glyphs, conversation_context=conversation_context, top_n=5)
            else:
                response_text = "I'm listening, but I couldn't feel a clear glyphic resonance yet."
        except Exception:
            response_text = (
                f"Local Analysis: {voltage_response}\n"
                f"Activated Glyphs: {', '.join([g.get('glyph_name','') for g in glyphs]) if glyphs else 'None'}\n"
                f"{ritual_prompt}\n(AI enhancement unavailable)"
            )

        return response_text, {}, local_analysis
    except Exception:
        # When the mobile adapter fails unexpectedly, prefer delegating to
        # the canonical pipeline while passing an explicit
        # `session_state_override` so the canonical code does not rely on
        # a Streamlit session in this process.
        try:
            from emotional_os.deploy.modules.ui import run_hybrid_pipeline

            session_override = {
                'user_id': user_id,
                'processing_mode': processing_mode
            }
            return run_hybrid_pipeline(
                effective_input,
                conversation_context,
                saori_url,
                supabase_key,
                session_state_override=session_override,
            )
        except Exception:
            # If delegation to the canonical pipeline fails, do a
            # conservative local-only fallback so the caller still
            # receives a useful reply rather than an exception.
            try:
                try:
                    from emotional_os.glyphs.signal_parser import parse_input
                except Exception:
                    parse_input = None

                local_analysis = {}
                if parse_input:
                    try:
                        local_analysis = parse_input(
                            effective_input,
                            "emotional_os/parser/signal_lexicon.json",
                            db_path="emotional_os/glyphs/glyphs.db",
                            conversation_context=conversation_context,
                        )
                    except Exception:
                        local_analysis = {}

                glyphs = local_analysis.get('glyphs', [])
                voltage_response = local_analysis.get('voltage_response', '')
                ritual_prompt = local_analysis.get('ritual_prompt', '')

                try:
                    from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer
                    composer = DynamicResponseComposer()
                    if glyphs:
                        response_text = composer.compose_multi_glyph_response(
                            effective_input, glyphs, conversation_context=conversation_context, top_n=5)
                    else:
                        response_text = "I'm listening, but I couldn't feel a clear glyphic resonance yet."
                except Exception:
                    response_text = (
                        f"Local Analysis: {voltage_response}\n"
                        f"Activated Glyphs: {', '.join([g.get('glyph_name','') for g in glyphs]) if glyphs else 'None'}\n"
                        f"{ritual_prompt}\n(AI enhancement unavailable)"
                    )

                return response_text, {}, local_analysis
            except Exception:
                try:
                    return "I'm listening (local analysis unavailable).", {}, {}
                except Exception:
                    return "", {}, {}

    # End run_hybrid_pipeline_mobile
