#!/usr/bin/env python3

import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

# Import central guard for remote AI usage
try:
    from scripts.local_integration import remote_ai_allowed, remote_ai_error
except Exception:
    # Conservative fallback: disallow remote AI if guard can't be imported
    def remote_ai_allowed():
        return False

    def remote_ai_error(msg: str = None):
        raise RuntimeError(
            msg or "Remote AI usage is not allowed in this environment")


@dataclass
class SaoriResponse:
    reply: str
    glyph: Optional[Dict]
    parsed_glyphs: List[Dict]
    upserted_glyphs: List[Dict]
    log: Dict


class SupabaseIntegrator:
    """Integration with your Supabase Saori edge function"""

    def __init__(self,
                 function_url: str,
                 supabase_anon_key: str = None,
                 user_token: str = None):
        self.function_url = function_url
        self.supabase_anon_key = supabase_anon_key
        self.user_token = user_token
        self.session = requests.Session()

        # Set up headers
        headers = {
            'Content-Type': 'application/json',
        }

        if user_token:
            headers['Authorization'] = f'Bearer {user_token}'
        elif supabase_anon_key:
            headers['Authorization'] = f'Bearer {supabase_anon_key}'

        self.session.headers.update(headers)

    def process_message(self,
                        message: str,
                        mode: str = "quick",
                        conversation_context: Dict = None,
                        conversation_style: str = "conversational") -> SaoriResponse:
        """
        Send message to your Supabase edge function for processing
        This leverages your complete emotional tagging and AI system
        """

        # Add conversational trigger words to ensure normal tone
        if conversation_style == "conversational":
            # The edge function looks for these keywords to switch to conversational mode
            if not any(word in message.lower() for word in ["plain", "normal", "conversational", "talk normal"]):
                message = f"Please talk normal. {message}"

        payload = {
            "message": message,
            "mode": mode,
            "style": conversation_style,
            "tone": "casual",
            "response_type": "conversational"
        }

        # Add conversation context if available (could enhance your edge function to use this)
        if conversation_context:
            payload["conversation_context"] = conversation_context

        try:
            response = self.session.post(
                self.function_url, json=payload, timeout=30)

            # Log response details for debugging
            logging.info(f"Supabase response status: {response.status_code}")
            logging.info(f"Response headers: {dict(response.headers)}")

            response.raise_for_status()

            data = response.json()

            return SaoriResponse(
                reply=data.get('reply', 'No response received'),
                glyph=data.get('glyph'),
                parsed_glyphs=data.get('parsed_glyphs', []),
                upserted_glyphs=data.get('upserted_glyphs', []),
                log=data.get('log', {})
            )

        except requests.exceptions.Timeout as e:
            error_msg = f"Request timed out after 30 seconds: {e}"
            logging.error(error_msg)
            return SaoriResponse(
                reply="Connection to the emotional processing system temporarily unavailable. (Timeout)",
                glyph=None,
                parsed_glyphs=[],
                upserted_glyphs=[],
                log={"error": error_msg}
            )
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {e}"
            logging.error(error_msg)
            return SaoriResponse(
                reply="Connection to the emotional processing system temporarily unavailable. (Network Error)",
                glyph=None,
                parsed_glyphs=[],
                upserted_glyphs=[],
                log={"error": error_msg}
            )
        except requests.RequestException as e:
            error_msg = f"Supabase edge function error: {e}"
            logging.error(error_msg)
            return SaoriResponse(
                reply=f"Connection to the emotional processing system temporarily unavailable. (HTTP {getattr(e.response, 'status_code', 'Unknown')})",
                glyph=None,
                parsed_glyphs=[],
                upserted_glyphs=[],
                log={"error": error_msg}
            )
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {e}"
            logging.error(error_msg)
            return SaoriResponse(
                reply="Response parsing error from emotional processing system.",
                glyph=None,
                parsed_glyphs=[],
                upserted_glyphs=[],
                log={"error": error_msg}
            )


class HybridEmotionalProcessor:
    """
    Hybrid system that can use either:
    1. Your local glyph system (privacy-first, no external calls)
    2. Your Supabase system (AI-enhanced with your emotional taxonomy)
    3. Intelligent fallback between both
    """

    def __init__(self,
                 supabase_integrator: Optional[SupabaseIntegrator] = None,
                 use_local_fallback: bool = True,
                 limbic_engine=None):
        self.supabase = supabase_integrator
        self.use_local_fallback = use_local_fallback
        # Optional limbic engine (backend-only). If provided, will be used to
        # decorate baseline replies into a more companion-like tone.
        self.limbic_engine = limbic_engine

        # Import your local system
        if use_local_fallback:
            try:
                from parser.signal_parser import parse_input
                self.local_parser = parse_input
                self.local_available = True
            except ImportError:
                self.local_available = False
                logging.warning("Local glyph parser not available")
        else:
            self.local_available = False

    def process_emotional_input(self,
                                message: str,
                                conversation_context: Dict = None,
                                prefer_ai: bool = True,
                                privacy_mode: bool = False,
                                session_metadata: Dict = None,
                                **kwargs) -> Dict:
        """
        Process emotional input using hybrid approach

        Args:
            message: User input
            conversation_context: Previous conversation state
            prefer_ai: Whether to try AI-enhanced processing first
            privacy_mode: If True, only use local processing
        """

        if privacy_mode or not self.supabase:
            # Privacy-first: Only use local glyph system
            return self._process_local_only(message, conversation_context)

        if prefer_ai and self.supabase:
            # Try AI-enhanced processing first
            try:
                saori_response = self.supabase.process_message(
                    message,
                    conversation_context=conversation_context,
                    conversation_style="conversational"
                )

                result = {
                    "source": "supabase_ai",
                    "response": saori_response.reply,
                    "glyph_data": saori_response.glyph,
                    "parsed_glyphs": saori_response.parsed_glyphs,
                    "upserted_glyphs": saori_response.upserted_glyphs,
                    "emotional_metadata": saori_response.log,
                    "privacy_preserved": True,  # Your edge function uses symbolic processing
                    "processing_method": "encrypted_ai_enhanced"
                }

                # Attempt limbic decoration if available (backend-only)
                try:
                    decorated_result = self._attempt_limbic_decoration(
                        message, result, session_metadata=session_metadata)
                    return decorated_result
                except Exception as e:
                    # If decoration fails, return baseline result
                    logging.warning(f"Limbic decoration failed: {e}")
                    result['limbic_decorated'] = False
                    return result

            except Exception as e:
                logging.error(f"Supabase processing failed: {e}")
                if self.use_local_fallback:
                    return self._process_local_fallback(message, conversation_context, error=str(e))
                raise

        # Fallback to local processing
        return self._process_local_only(message, conversation_context)

    def _attempt_limbic_decoration(self, message: str, result: Dict, session_metadata: Dict = None) -> Dict:
        """Attempt to decorate a baseline reply using the limbic engine.

        Adds keys to result: limbic_decorated (bool), limbic_telemetry (dict)
        """
        # Default flags
        safety_flag = False
        decorated = False
        telemetry_entry = {}

        # If no limbic engine available, skip
        if not self.limbic_engine:
            result['limbic_decorated'] = False
            return result

        # Use sanctuary's sensitivity classifier if available
        try:
            from emotional_os.safety.sanctuary import is_sensitive_input
            safety_flag = is_sensitive_input(message)
        except Exception:
            safety_flag = False

        # Attempt to import decorator
        try:
            from emotional_os.glyphs.limbic_decorator import decorate_reply
        except Exception:
            decorate_reply = None

        limbic_result = None
        try:
            # Time the limbic engine processing for telemetry
            import time as _time
            _start = _time.time()
            limbic_result = self.limbic_engine.process_emotion_with_limbic_mapping(
                message)
            _end = _time.time()
            limbic_latency_ms = int((_end - _start) * 1000)
        except Exception as e:
            logging.warning(f"Limbic engine processing failed: {e}")
            limbic_result = None
            limbic_latency_ms = None

        # Check A/B session metadata: if participating and assigned to control, skip enrichment
        ab_participate = False
        ab_group = 'not_participating'
        if session_metadata and isinstance(session_metadata, dict):
            ab_participate = bool(
                session_metadata.get('ab_participate', False))
            ab_group = session_metadata.get('ab_group', ab_group)

        if ab_participate and ab_group == 'control':
            # Explicitly skip enrichment for control group
            logging.info(
                "A/B control group - skipping limbic decoration per-session")
            decorated = False
        elif not safety_flag and decorate_reply and limbic_result and isinstance(result, dict):
            try:
                baseline = result.get('response', '')
                decorated_text = decorate_reply(baseline, limbic_result)
                result['response'] = decorated_text
                decorated = True
            except Exception as e:
                logging.warning(f"decorate_reply failed: {e}")
                decorated = False

        result['limbic_decorated'] = bool(decorated)

        # Prepare telemetry entry
        try:
            import hashlib
            import json
            import time
            timestamp = time.time()
            message_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
            emotion = None
            glyphs = None
            if limbic_result and isinstance(limbic_result, dict):
                emotion = limbic_result.get('emotion')
                glyphs = limbic_result.get('glyphs')

            # Compute glyphs count for telemetry (handle lists or mappings)
            glyphs_count = None
            try:
                if glyphs is None:
                    glyphs_count = 0
                elif isinstance(glyphs, (list, tuple)):
                    glyphs_count = len(glyphs)
                elif isinstance(glyphs, dict):
                    # If glyphs is a mapping of emotion->list, sum lengths
                    glyphs_count = sum(
                        len(v) for v in glyphs.values() if isinstance(v, (list, tuple)))
                else:
                    glyphs_count = 1
            except Exception:
                glyphs_count = None

            telemetry_entry = {
                'timestamp': timestamp,
                'message_hash': message_hash,
                'emotion_detected': emotion,
                'glyphs_generated': json.dumps(glyphs) if glyphs is not None else None,
                'glyphs_count': glyphs_count,
                'limbic_decorated': bool(decorated),
                'safety_flag': bool(safety_flag),
                'ab_participate': bool(ab_participate),
                'ab_group': ab_group,
                'user_id': session_metadata.get('user_id') if session_metadata and isinstance(session_metadata, dict) else None,
                'latency_ms': limbic_latency_ms if 'limbic_latency_ms' in locals() else None
            }

            # Attempt to record telemetry via Supabase if available
            try:
                self._record_telemetry(telemetry_entry)
            except Exception as e:
                logging.warning(f"Telemetry recording failed: {e}")

            result['limbic_telemetry'] = telemetry_entry
        except Exception as e:
            logging.warning(f"Preparing limbic telemetry failed: {e}")

        return result

    def _record_telemetry(self, entry: Dict):
        """Record telemetry entry to Supabase REST endpoint if available.

        Expects a table named `limbic_telemetry` in your Supabase project with fields
        matching the keys we insert. This is best-effort and will not raise on failure.
        """
        if not self.supabase or not getattr(self.supabase, 'function_url', None):
            # No supabase configured; nothing to do
            return

        # Try to find base supabase URL
        import json
        import re
        function_url = self.supabase.function_url
        m = re.match(r'(https://[^/]+\.supabase\.co)', function_url)
        if not m:
            return

        supabase_url = m.group(1)
        rest_url = f"{supabase_url}/rest/v1/limbic_telemetry"

        headers = {
            'Content-Type': 'application/json',
            'apikey': getattr(self.supabase, 'supabase_anon_key', ''),
            'Authorization': f"Bearer {getattr(self.supabase, 'supabase_anon_key', '')}",
            'Prefer': 'return=representation'
        }

        # Format payload as a single-row insert (Supabase expects an array payload)
        payload = [
            {
                'timestamp': entry.get('timestamp'),
                'message_hash': entry.get('message_hash'),
                'emotion_detected': entry.get('emotion_detected'),
                'glyphs_generated': entry.get('glyphs_generated'),
                'glyphs_count': entry.get('glyphs_count'),
                'limbic_decorated': entry.get('limbic_decorated'),
                'safety_flag': entry.get('safety_flag'),
                'latency_ms': entry.get('latency_ms'),
                'ab_participate': entry.get('ab_participate'),
                'ab_group': entry.get('ab_group'),
                'user_id': entry.get('user_id'),
                'metadata': json.dumps({
                    k: v for k, v in entry.items()
                    if k not in (
                        'timestamp', 'message_hash', 'emotion_detected', 'glyphs_generated',
                        'glyphs_count', 'limbic_decorated', 'safety_flag', 'latency_ms',
                        'ab_participate', 'ab_group', 'user_id'
                    )
                })
            }
        ]

        try:
            # Use a fresh requests call to avoid interfering with the integrator session state
            import requests
            resp = requests.post(rest_url, headers=headers,
                                 json=payload, timeout=10)
            if resp.status_code not in (200, 201):
                logging.warning(
                    f"Supabase telemetry insert returned {resp.status_code}: {resp.text}")
        except Exception as e:
            logging.warning(f"Failed to POST telemetry to Supabase: {e}")

    def _process_local_only(self, message: str, conversation_context: Dict = None) -> Dict:
        """Process using only local glyph system"""

        if not self.local_available:
            return {
                "source": "error",
                "response": "Emotional processing system temporarily unavailable.",
                "error": "No processing methods available"
            }

        try:
            # Use your existing local parser
            result = self.local_parser(
                message,
                "parser/signal_lexicon.json",
                conversation_context=conversation_context
            )

            return {
                "source": "local_glyph_system",
                "response": result.get("voltage_response", "No response generated"),
                "signals": result.get("signals", []),
                "gates": result.get("gates", []),
                "glyphs": result.get("glyphs", []),
                "ritual_prompt": result.get("ritual_prompt", ""),
                "enhanced_data": result.get("enhanced_data"),
                "privacy_preserved": True,
                "processing_method": "local_encrypted"
            }

        except Exception as e:
            logging.error(f"Local processing failed: {e}")
            return {
                "source": "error",
                "response": "Local emotional processing encountered an error.",
                "error": str(e)
            }

    def _process_local_fallback(self, message: str, conversation_context: Dict = None, error: str = "") -> Dict:
        """Fallback to local processing with error context"""

        result = self._process_local_only(message, conversation_context)
        result["fallback_reason"] = f"Supabase error: {error}"
        result["source"] = "local_fallback"

        return result

# Configuration and factory functions


def create_supabase_integrator(config: Dict = None) -> Optional[SupabaseIntegrator]:
    """Create Supabase integrator from config or environment variables"""
    # If remote AI is globally disallowed, block creation when explicit config exists
    if not remote_ai_allowed():
        # If caller passed explicit config, hard-fail
        if config:
            remote_ai_error(
                "Supabase integrator creation blocked: remote AI is disabled by default.")
        # If no config provided, silently return None to avoid accidental external calls
        return None

    if config:
        return SupabaseIntegrator(
            function_url=config.get('function_url'),
            supabase_anon_key=config.get('anon_key'),
            user_token=config.get('user_token')
        )

    # Try to get from environment
    function_url = os.getenv('SUPABASE_FUNCTION_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    user_token = os.getenv('SUPABASE_USER_TOKEN')

    if function_url:
        return SupabaseIntegrator(
            function_url=function_url,
            supabase_anon_key=anon_key,
            user_token=user_token
        )

    return None


def create_hybrid_processor(supabase_config: Dict = None,
                            use_local_fallback: bool = True,
                            limbic_engine=None) -> HybridEmotionalProcessor:
    """Create hybrid processor with optional Supabase integration"""
    # If remote AI is disallowed, block creation when an explicit supabase_config
    # is provided (hard-fail). Otherwise return a processor with no supabase integrator.
    if not remote_ai_allowed():
        # caller explicitly provided supabase_config → raise
        if supabase_config or os.getenv('SUPABASE_FUNCTION_URL'):
            remote_ai_error(
                "Hybrid processor creation blocked: remote AI is disabled by default.")
        # No supabase configured; proceed with None integrator (local-only)
        supabase_integrator = None
    else:
        supabase_integrator = create_supabase_integrator(supabase_config)

    return HybridEmotionalProcessor(
        supabase_integrator=supabase_integrator,
        use_local_fallback=use_local_fallback,
        limbic_engine=limbic_engine
    )
