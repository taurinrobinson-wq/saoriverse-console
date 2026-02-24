"""Phase 1: Parse Input Signals.

Extract emotional signals, glyphs, and sentiment from user input.
Handles both local parsing (via glyphs.signal_parser) and remote fallback.
"""

import logging
from typing import Dict, Any, Optional
import streamlit as st

logger = logging.getLogger(__name__)


def parse_input_signals(user_input: str, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
    """Parse input and extract emotional signals.
    
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
    try:
        from emotional_os.glyphs.signal_parser import parse_input

        from emotional_os.core.paths import get_path_manager

        pm = get_path_manager()
        lexicon_path = str(pm._resolve_path(
            "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
            "word_centric_emotional_lexicon_expanded.json"
        ))
        db_path = str(pm.glyph_db())

        # Local parsing
        local_analysis = parse_input(
            user_input,
            lexicon_path,
            db_path=db_path,
            conversation_context=conversation_context,
        )

        return local_analysis if isinstance(local_analysis, dict) else {}

    except Exception as e:
        logger.error(f"Parse signals FAILED: {e}", exc_info=True)
        return {}
