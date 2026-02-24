"""Phase 1: Parse Input Signals.

Extract emotional signals, glyphs, and sentiment from user input.
Handles both local parsing (via glyphs.signal_parser) and remote fallback.
"""

import logging
from typing import Dict, Any
import streamlit as st

logger = logging.getLogger(__name__)


def parse_input_signals(user_input: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
    """Parse input and extract emotional signals.
    
    Runs local signal parsing via glyphs and offers remote fallback
    if local parsing is incomplete or spaCy is unavailable.
    
    Args:
        user_input: User's message
        conversation_context: Conversation history
    
    Returns:
        Dict with keys:
        - voltage_response: str (poetic/resonant response)
        - best_glyph: dict (matched emotional glyph)
        - emotional_vector: list (emotion scores)
        - response_source: str (where response came from)
    """
    processing_mode = st.session_state.get("processing_mode", "local")
    logger.debug(f"parse_input_signals: mode={processing_mode}")
    
    if processing_mode == "hybrid":
        return _run_hybrid_parse(user_input, conversation_context)
    else:
        return _run_local_parse(user_input, conversation_context)


def _run_local_parse(user_input: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
    """Run local signal parsing with optional remote fallback."""
    try:
        from emotional_os.glyphs.signal_parser import parse_input
        from emotional_os.core.paths import get_path_manager

        # Get proper paths using PathManager
        pm = get_path_manager()
        lexicon_path = str(pm._resolve_path(
            "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
            "word_centric_emotional_lexicon_expanded.json"
        ))
        db_path = str(pm.glyph_db())

        # Local signal parsing
        local_analysis = parse_input(
            user_input,
            lexicon_path,
            db_path=db_path,
            conversation_context=conversation_context,
        )

        # Determine if remote fallback is needed
        prefers_remote = st.session_state.get("processing_mode") != "local"
        need_remote = prefers_remote or not local_analysis.get("voltage_response") or not local_analysis.get("best_glyph")

        # Check spaCy availability (non-import check)
        try:
            import importlib.util as _util
            spacy_available = _util.find_spec("spacy") is not None
        except Exception:
            spacy_available = False
        
        if not spacy_available:
            logger.info("spaCy not available; forcing remote parse")
            need_remote = True

        # Try remote if needed
        if need_remote:
            try:
                from .remote_parser import remote_parse_input
                remote = remote_parse_input(user_input, conversation_context)
                if remote:
                    logger.info("Using remote parse result")
                    local_analysis = remote
            except Exception as e:
                logger.debug(f"Remote parse fallback failed: {e}")

        # Ensure dict
        if not isinstance(local_analysis, dict):
            logger.warning(f"parse_input returned non-dict: {type(local_analysis)}")
            local_analysis = {}

        logger.info(f"parse_phase: voltage={bool(local_analysis.get('voltage_response'))}, glyph={bool(local_analysis.get('best_glyph'))}")
        return local_analysis

    except Exception as e:
        logger.error(f"Local parse FAILED: {e}", exc_info=True)
        return {}


def _run_hybrid_parse(user_input: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
    """Run hybrid parsing (prefer remote with local fallback)."""
    try:
        from .remote_parser import remote_parse_input
        
        # Try remote first
        try:
            remote = remote_parse_input(user_input, conversation_context)
            if remote and isinstance(remote, dict) and remote.get("voltage_response"):
                logger.info("Hybrid: using remote parse")
                return remote
        except Exception as e:
            logger.debug(f"Remote parse failed in hybrid: {e}")

        # Fallback to local
        logger.info("Hybrid: falling back to local parse")
        return _run_local_parse(user_input, conversation_context)

    except Exception as e:
        logger.error(f"Hybrid parse FAILED: {e}", exc_info=True)
        return {}
