#!/usr/bin/env python3

import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
try:
    # Use the centralized guard from scripts/local_integration to determine
    # whether remote AI calls are allowed.
    from scripts.local_integration import remote_ai_allowed
except Exception:
    # If import fails for any reason, conservatively disallow remote AI.
    def remote_ai_allowed():
        return False
# Global hard guard: when set, disallow any remote/OpenAI calls across the process.
import os as _os
FORCE_LOCAL_ONLY = str(_os.getenv('FORCE_LOCAL_ONLY', '')
                       ).lower() in ('1', 'true', 'yes')
try:
    from learning.clarification_memory import suggest_for_input
except Exception:
    def suggest_for_input(_text, min_count=1):
        return None


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
        # Prevent creating a Supabase integrator when global local-only guard is enabled
        if FORCE_LOCAL_ONLY:
            raise RuntimeError(
                "Remote AI integrator creation blocked by FORCE_LOCAL_ONLY environment guard")
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

        # Build LLM prompt overlay if the conversation context includes tone or forced intent
        llm_overrides = {}
        try:
            if conversation_context and isinstance(conversation_context, dict):
                # Include deterministic routing artifacts where present
                if conversation_context.get('forced_intent'):
                    llm_overrides['forced_intent'] = conversation_context.get(
                        'forced_intent')
                if conversation_context.get('dominant_emotion'):
                    llm_overrides['dominant_emotion'] = conversation_context.get(
                        'dominant_emotion')
                if conversation_context.get('tone_overlay'):
                    llm_overrides['tone_overlay'] = conversation_context.get(
                        'tone_overlay')

                # If a clarification provenance exists, include its record_id for traceability
                prov = conversation_context.get('clarification_provenance')
                if prov and isinstance(prov, dict):
                    llm_overrides['clarification_record_id'] = prov.get(
                        'record_id')

            # Construct a gentle prompt prefix that guides the remote LLM to apply the tone overlay.
            if llm_overrides.get('tone_overlay') or llm_overrides.get('forced_intent'):
                parts = []
                if llm_overrides.get('forced_intent'):
                    parts.append(
                        f"Interpret the user's intent as: {llm_overrides['forced_intent']}.")
                if llm_overrides.get('dominant_emotion'):
                    parts.append(
                        f"Adopt a tone reflecting {llm_overrides['dominant_emotion']}.")
                if llm_overrides.get('tone_overlay'):
                    # Use a short overlay directive; this is safe to send as instruction text.
                    parts.append(
                        f"Tone guidance: {llm_overrides['tone_overlay']}")

                prompt_prefix = " ".join(parts)
                if prompt_prefix:
                    llm_overrides['prompt_prefix'] = prompt_prefix
        except Exception:
            # Be resilient: do not fail supabase payload assembly if overrides fail
            llm_overrides = {}

        if llm_overrides:
            payload['llm_overrides'] = llm_overrides

        # Add conversation context if available (could enhance your edge function to use this)
        if conversation_context:
            payload["conversation_context"] = conversation_context
            # If a clarification provenance exists, surface it explicitly for server-side telemetry
            try:
                prov = conversation_context.get('clarification_provenance') if isinstance(
                    conversation_context, dict) else None
                if prov:
                    payload['clarification_provenance'] = {
                        'record_id': prov.get('record_id'),
                        'trigger': prov.get('trigger'),
                        'suggestion': prov.get('suggestion'),
                        'confidence': prov.get('confidence'),
                        'applied_at': prov.get('applied_at')
                    }
            except Exception:
                pass

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
                 use_local_fallback: bool = True):
        self.supabase = supabase_integrator
        self.use_local_fallback = use_local_fallback
        # Clarification bias settings: suggestions with confidence >= this
        # will be attached to the conversation_context as `clarification_bias`.
        # Tune these as needed; these are conservative defaults.
        self.clarification_min_confidence = 0.6
        self.clarification_min_count = 1

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
                                privacy_mode: bool = False) -> Dict:
        """
        Process emotional input using hybrid approach
        """

        # Ensure conversation_context is a mutable dict
        if conversation_context is None:
            conversation_context = {}

        # Query the clarification memory and attach a bias if applicable
        try:
            suggestion = suggest_for_input(
                message, min_count=self.clarification_min_count)
        except Exception:
            suggestion = None

        applied_clarification = None
        if suggestion and isinstance(suggestion, dict):
            # apply only if confidence meets threshold
            try:
                conf = float(suggestion.get('confidence') or 0.0)
            except Exception:
                conf = 0.0
            if conf >= float(self.clarification_min_confidence):
                conversation_context = dict(conversation_context)
                conversation_context['clarification_bias'] = suggestion
                applied_clarification = suggestion

        if privacy_mode or not self.supabase:
            # Privacy-first: Only use local glyph system
            result = self._process_local_only(message, conversation_context)
            if applied_clarification:
                # Surface both the raw suggestion and the richer provenance if available
                result['clarification_applied'] = applied_clarification
                if isinstance(conversation_context, dict) and conversation_context.get('clarification_provenance'):
                    result['clarification_provenance'] = conversation_context.get(
                        'clarification_provenance')
            return result

        if prefer_ai and self.supabase:
            # Try AI-enhanced processing first
            try:
                saori_response = self.supabase.process_message(
                    message,
                    conversation_context=conversation_context,
                    conversation_style="conversational"
                )

                out = {
                    "source": "supabase_ai",
                    "response": saori_response.reply,
                    "glyph_data": saori_response.glyph,
                    "parsed_glyphs": saori_response.parsed_glyphs,
                    "upserted_glyphs": saori_response.upserted_glyphs,
                    "emotional_metadata": saori_response.log,
                    "privacy_preserved": True,
                    "processing_method": "encrypted_ai_enhanced",
                }
                if applied_clarification:
                    out['clarification_applied'] = applied_clarification
                    if isinstance(conversation_context, dict) and conversation_context.get('clarification_provenance'):
                        out['clarification_provenance'] = conversation_context.get(
                            'clarification_provenance')
                return out

            except Exception as e:
                logging.error(f"Supabase processing failed: {e}")
                if self.use_local_fallback:
                    return self._process_local_fallback(message, conversation_context, error=str(e))
                raise

        # Fallback to local processing
        result = self._process_local_only(message, conversation_context)
        if applied_clarification:
            result['clarification_applied'] = applied_clarification
            if isinstance(conversation_context, dict) and conversation_context.get('clarification_provenance'):
                result['clarification_provenance'] = conversation_context.get(
                    'clarification_provenance')
        return result

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
    # Respect global local-only guard: never create an integrator when forced local-only is enabled
    if FORCE_LOCAL_ONLY:
        logging.info(
            "FORCE_LOCAL_ONLY enabled: skipping SupabaseIntegrator creation")
        return None
    # If remote AI calls are disabled, do not create an integrator.
    if not remote_ai_allowed():
        # If user passed an explicit config that would use Supabase, raise
        # to make misconfiguration explicit. Otherwise return None.
        if config and (config.get('function_url') or config.get('anon_key') or config.get('user_token')):
            raise RuntimeError(
                "Remote AI calls are disabled (processing mode 'local'). "
                "Set PROCESSING_MODE or ALLOW_REMOTE_AI to opt in."
            )
        # Check env-based config and refuse to create an integrator if present.
        if os.getenv('SUPABASE_FUNCTION_URL') or os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_USER_TOKEN'):
            raise RuntimeError(
                "Remote AI calls are disabled (processing mode 'local'). "
                "Set PROCESSING_MODE or ALLOW_REMOTE_AI to opt in."
            )
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
                            use_local_fallback: bool = True) -> HybridEmotionalProcessor:
    """Create hybrid processor with optional Supabase integration"""
    # If remote AI is disabled, creating a hybrid processor that would call
    # external services is an explicit opt-in. Detect and refuse creation
    # unless remote AI is allowed.
    if not remote_ai_allowed() and supabase_config:
        raise RuntimeError(
            "Hybrid processor creation blocked: remote AI disabled (processing mode 'local'). "
            "Set PROCESSING_MODE or ALLOW_REMOTE_AI to opt in."
        )

    supabase_integrator = create_supabase_integrator(supabase_config)

    return HybridEmotionalProcessor(
        supabase_integrator=supabase_integrator,
        use_local_fallback=use_local_fallback
    )


def create_local_processor(use_local_fallback: bool = True) -> HybridEmotionalProcessor:
    """Create a local-only emotional processor.

    This factory returns a HybridEmotionalProcessor configured with no
    Supabase integrator so it will operate entirely with local parsing
    and local fallbacks. It does not attempt remote calls.
    """
    # Do not create or attach a SupabaseIntegrator; operate locally only
    return HybridEmotionalProcessor(supabase_integrator=None, use_local_fallback=use_local_fallback)
