"""
Session State Management.

Handles initialization of session state, orchestrator setup, preferences loading,
conversation context building, and session-wide state management.

Key responsibilities:
- Initialize conversation manager
- Setup FirstPerson orchestrator
- Initialize Affect Parser
- Load/save user preferences
- Handle demo -> auth migration
- Build conversation context for analysis
"""

import uuid
import logging
import streamlit as st

logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize all session state variables and orchestrators.

    Sets up:
    - ConversationManager for persistence
    - FirstPersonOrchestrator for relational AI
    - AffectParser for emotional analysis
    - FallbackProtocol for safety
    - Voice mode
    - Processing mode and preferences
    - Authentication state
    - Tier 1 Foundation for enhanced responses
    - Tier 2 Aliveness for emotional presence
    - Tier 3 Poetic Consciousness for creative depth
    - Ollama LLM client for local model inference
    """
    _ensure_auth_defaults()
    _ensure_conversation_defaults()
    _ensure_processor_instances()
    _ensure_processing_prefs()
    _ensure_fallback_protocol()
    _ensure_voice_mode()
    _ensure_theme_defaults()
    _ensure_tier1_foundation()
    _ensure_tier2_aliveness()
    _ensure_tier3_poetic_consciousness()
    _ensure_ollama_client()


def _ensure_auth_defaults():
    """Ensure authentication-related session defaults exist."""
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault(
        "demo_mode", not st.session_state.get("authenticated"))
    st.session_state.setdefault("sidebar_show_login", False)
    st.session_state.setdefault("sidebar_show_register", False)

    # Demo mode placeholder for later auth migration
    if not st.session_state.get("authenticated") and "demo_placeholder_id" not in st.session_state:
        st.session_state["demo_placeholder_id"] = f"demo_{uuid.uuid4().hex[:8]}"

    # Default user identification
    if "user_id" not in st.session_state:
        if st.session_state.get("authenticated"):
            st.session_state["user_id"] = st.session_state.get("user_id")
        else:
            st.session_state["user_id"] = st.session_state.get(
                "demo_placeholder_id", f"anon_{uuid.uuid4().hex[:8]}"
            )

    st.session_state.setdefault("username", "Demo User" if not st.session_state.get(
        "authenticated") else "User")


def _ensure_conversation_defaults():
    """Ensure conversation and persistence defaults exist."""
    st.session_state.setdefault("persist_history", True)
    st.session_state.setdefault("persist_confirmed", False)

    # Current conversation tracking
    if "current_conversation_id" not in st.session_state:
        st.session_state["current_conversation_id"] = str(uuid.uuid4())

    st.session_state.setdefault("conversation_title", "New Conversation")
    st.session_state.setdefault("header_rendered", False)


def _ensure_processor_instances():
    """Initialize FirstPerson and Affect Parser if available."""
    # FirstPerson Orchestrator (relational AI)
    if "firstperson_orchestrator" not in st.session_state:
        try:
            from ..core.firstperson import create_orchestrator

            user_id = st.session_state.get("user_id", "anon")
            conversation_id = st.session_state.get(
                "current_conversation_id", "default")

            orchestrator = create_orchestrator(user_id, conversation_id)
            if orchestrator:
                orchestrator.initialize_session()
                st.session_state["firstperson_orchestrator"] = orchestrator
        except Exception as e:
            logger.debug(f"FirstPerson orchestrator init failed: {e}")
            st.session_state["firstperson_orchestrator"] = None

        # Subordinate responder + orchestrator for fast grounded replies
        if "responder" not in st.session_state:
            try:
                # Use shared factory where available
                from src.responder_factory import make_responder_and_orchestrator

                glyphs = {}
                try:
                    # Try to load glyph library if available
                    from src.emotional_os_learning import get_archetype_library
                    glyphs = get_archetype_library() if callable(get_archetype_library) else {}
                except Exception:
                    glyphs = {}

                responder, orchestrator, proto_mgr = make_responder_and_orchestrator(glyphs)
                st.session_state["responder"] = responder
                st.session_state["dominant_orchestrator"] = orchestrator
                st.session_state["proto_mgr"] = proto_mgr
                logger.info("Subordinate responder and orchestrator initialized in session")
            except Exception as e:
                logger.debug(f"Responder factory init failed: {e}")
                st.session_state["responder"] = None

    # Affect Parser (emotional tone detection)
    if "affect_parser" not in st.session_state:
        try:
            from ..core.firstperson import create_affect_parser

            parser = create_affect_parser()
            if parser:
                st.session_state["affect_parser"] = parser
        except Exception as e:
            logger.debug(f"Affect parser init failed: {e}")
            st.session_state["affect_parser"] = None


def _ensure_processing_prefs():
    """Normalize and ensure processing preference defaults."""
    # Map legacy ai_preferred to local
    if st.session_state.get("processing_mode") == "ai_preferred":
        st.session_state["processing_mode"] = "local"
        st.session_state["prefer_ai"] = False

    # Default to local processing
    if "processing_mode" not in st.session_state:
        import os
        st.session_state["processing_mode"] = os.getenv(
            "DEFAULT_PROCESSING_MODE", "local")

    st.session_state.setdefault("prefer_ai", False)


def _ensure_fallback_protocol():
    """Initialize Fallback Protocol for safety handling if available."""
    if "fallback_protocol" not in st.session_state:
        try:
            from ..safety.fallback_protocols import FallbackProtocol

            st.session_state["fallback_protocol"] = FallbackProtocol()
        except Exception as e:
            logger.debug(f"Fallback protocol init failed: {e}")
            st.session_state["fallback_protocol"] = None


def _ensure_voice_mode():
    """Initialize voice mode state."""
    st.session_state.setdefault("voice_mode_enabled", False)
    st.session_state.setdefault("last_audio_input", None)
    st.session_state.setdefault("last_audio_output", None)


def _ensure_tier1_foundation():
    """Initialize Tier 1 Foundation for response enhancement.
    
    Sets up the foundation layer with:
    - LexiconLearner for vocabulary expansion
    - Sanctuary safety for compassionate wrapping
    - Signal detection for emotion understanding
    """
    if "tier1_foundation" not in st.session_state:
        try:
            from src.emotional_os.tier1_foundation import Tier1Foundation
            tier1 = Tier1Foundation(conversation_memory=None)
            st.session_state["tier1_foundation"] = tier1
            logger.info("Tier 1 Foundation initialized in session")
        except Exception as e:
            logger.warning(f"Failed to initialize Tier 1 Foundation: {e}")
            st.session_state["tier1_foundation"] = None


def _ensure_tier2_aliveness():
    """Initialize Tier 2 Aliveness for emotional presence and adaptivity.
    
    Sets up the aliveness layer with:
    - AttunementLoop for tone synchronization
    - EmotionalReciprocity for intensity matching
    - EmbodiedSimulation for physical presence metaphors
    - EnergyTracker for conversation pacing
    """
    if "tier2_aliveness" not in st.session_state:
        try:
            from src.emotional_os.tier2_aliveness import Tier2Aliveness
            tier2 = Tier2Aliveness()
            st.session_state["tier2_aliveness"] = tier2
            logger.info("Tier 2 Aliveness initialized in session")
        except Exception as e:
            logger.warning(f"Failed to initialize Tier 2 Aliveness: {e}")
            st.session_state["tier2_aliveness"] = None


def _ensure_tier3_poetic_consciousness():
    """Initialize Tier 3 Poetic Consciousness for creative depth.
    
    Sets up the poetic layer with:
    - PoetryEngine for metaphor and symbolic language
    - SaoriLayer for Japanese aesthetic principles
    - TensionManager for creative exploration
    - MythologyWeaver for personal narrative building
    """
    # Tier 3 (poetic) layer is deprecated/archived by default. Keep a
    # session placeholder for backward compatibility but do not initialize
    # the poetic machinery unless explicitly enabled via
    # `st.session_state['enable_tier3_poetic'] = True`.
    st.session_state.setdefault("enable_tier3_poetic", False)
    if "tier3_poetic_consciousness" not in st.session_state:
        st.session_state["tier3_poetic_consciousness"] = None
        if st.session_state.get("enable_tier3_poetic"):
            try:
                from src.emotional_os.tier3_poetic_consciousness import Tier3PoeticConsciousness
                tier3 = Tier3PoeticConsciousness()
                st.session_state["tier3_poetic_consciousness"] = tier3
                logger.info("Tier 3 Poetic Consciousness initialized in session (enabled)")
            except Exception as e:
                logger.warning(f"Failed to initialize Tier 3 Poetic Consciousness: {e}")
                st.session_state["tier3_poetic_consciousness"] = None


def load_conversation_manager():
    """Initialize or retrieve ConversationManager from session.

    Returns:
        ConversationManager instance or None
    """
    if "conversation_manager" in st.session_state:
        return st.session_state.get("conversation_manager")

    try:
        from ..conversation_manager import ConversationManager

        user_id = st.session_state.get("user_id")
        if not user_id:
            return None

        mgr = ConversationManager(user_id)
        st.session_state["conversation_manager"] = mgr

        # Load user preferences
        try:
            prefs = mgr.load_user_preferences()
            if prefs:
                if "persist_history" not in st.session_state:
                    st.session_state["persist_history"] = prefs.get(
                        "persist_history", True)
                if "persist_confirmed" not in st.session_state:
                    st.session_state["persist_confirmed"] = prefs.get(
                        "persist_confirmed", False)
        except Exception as e:
            logger.debug(f"Failed to load user preferences: {e}")

        return mgr

    except Exception as e:
        logger.debug(f"ConversationManager init failed: {e}")
        return None


def migrate_demo_to_auth():
    """Migrate demo conversation to authenticated user's storage.

    Runs once when user transitions from demo to authenticated.
    Copies ephemeral demo messages to persistent user storage.
    """
    # Check if migration should run
    if not (st.session_state.get("authenticated") and
            st.session_state.get("demo_placeholder_id") and
            not st.session_state.get("demo_migrated")):
        return

    try:
        from ..conversation_manager import (
            ConversationManager,
            generate_auto_name,
        )

        demo_id = st.session_state.get("demo_placeholder_id")
        demo_key = f"conversation_history_{demo_id}"
        user_id_now = st.session_state.get("user_id")
        user_key = f"conversation_history_{user_id_now}"

        # Check if there's demo content to migrate
        if demo_key not in st.session_state or not st.session_state.get(demo_key):
            st.session_state["demo_migrated"] = True
            return

        demo_messages = st.session_state.get(demo_key)

        # Don't migrate if user already has content
        if user_key in st.session_state and st.session_state.get(user_key):
            st.session_state["demo_migrated"] = True
            return

        # Copy to user's key
        st.session_state[user_key] = demo_messages

        # Persist via ConversationManager if available
        try:
            mgr = ConversationManager(user_id_now)
            conv_id = str(uuid.uuid4())

            # Extract first message for auto-naming
            first_msg = None
            if isinstance(demo_messages, list) and demo_messages:
                first_entry = demo_messages[0]
                if isinstance(first_entry, dict):
                    first_msg = first_entry.get(
                        "user") or first_entry.get("assistant")

            title = first_msg[:50] if first_msg else "Migrated Conversation"
            if generate_auto_name and first_msg:
                title = generate_auto_name(first_msg)

            mgr.save_conversation(conv_id, title, demo_messages)
            st.session_state["current_conversation_id"] = conv_id

        except Exception as e:
            logger.debug(f"ConversationManager migration failed: {e}")

        st.session_state["demo_migrated"] = True

    except Exception as e:
        logger.debug(f"Demo migration failed: {e}")
        st.session_state["demo_migrated"] = True


def get_conversation_key() -> str:
    """Get the session state key for current conversation history.

    Returns:
        Session key for conversation history (e.g., "conversation_history_user123")
    """
    user_id = st.session_state.get("user_id", "anon")
    return f"conversation_history_{user_id}"


def ensure_conversation_history():
    """Ensure conversation history list exists in session state."""
    key = get_conversation_key()
    if key not in st.session_state:
        st.session_state[key] = []


def get_conversation_context() -> dict:
    """Build conversation context for emotional analysis.

    Extracts message history and last assistant message to provide
    to parsers for detecting feedback, corrections, and context.

    Returns:
        Dictionary with 'messages' list and 'last_assistant_message'
    """
    key = get_conversation_key()
    history = st.session_state.get(key, [])

    context = {
        "last_assistant_message": None,
        "messages": [],
    }

    # Build messages list with role/content pairs
    for i, exchange in enumerate(history):
        if isinstance(exchange, dict):
            if "user" in exchange:
                context["messages"].append({
                    "role": "user",
                    "content": exchange["user"],
                })
            if "assistant" in exchange:
                context["messages"].append({
                    "role": "assistant",
                    "content": exchange["assistant"],
                })

    # Find last assistant message
    try:
        for exchange in reversed(history):
            if isinstance(exchange, dict) and "assistant" in exchange:
                context["last_assistant_message"] = exchange.get("assistant")
                break
    except Exception:
        pass

    return context


def add_exchange_to_history(user_input: str, assistant_response: str, metadata: dict = None):
    """Add a user/assistant exchange to conversation history.

    Args:
        user_input: User's message
        assistant_response: Assistant's response
        metadata: Optional metadata (processing_time, mode, etc.)
    """
    import datetime

    key = get_conversation_key()
    ensure_conversation_history()

    entry = {
        "user": user_input,
        "assistant": assistant_response,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    if metadata:
        entry.update(metadata)

    st.session_state[key].append(entry)


def clear_conversation_history():
    """Clear current conversation history."""
    key = get_conversation_key()
    st.session_state[key] = []


def get_session_summary() -> dict:
    """Get summary of important session state values.

    Useful for debugging and understanding current session state.

    Returns:
        Dictionary with key session values
    """
    key = get_conversation_key()

    return {
        "authenticated": st.session_state.get("authenticated"),
        "user_id": st.session_state.get("user_id"),
        "username": st.session_state.get("username"),
        "processing_mode": st.session_state.get("processing_mode"),
        "conversation_id": st.session_state.get("current_conversation_id"),
        "conversation_title": st.session_state.get("conversation_title"),
        "message_count": len(st.session_state.get(key, [])),
        "has_orchestrator": st.session_state.get("firstperson_orchestrator") is not None,
        "has_affect_parser": st.session_state.get("affect_parser") is not None,
        "persist_history": st.session_state.get("persist_history"),
    }


def _ensure_theme_defaults():
    """Ensure theme and UI defaults persist across reruns."""
    # Initialize theme if not set
    st.session_state.setdefault("theme", "Light")
    st.session_state.setdefault("theme_select_row", "Light")
    # Mark theme as loaded to prevent unnecessary resets
    if "theme_loaded" not in st.session_state:
        st.session_state["theme_loaded"] = False


def _ensure_ollama_client():
    """Initialize Ollama LLM client for local model inference.
    
    Sets up:
    - Ollama HTTP client for local LLM service
    - Health check and model availability detection
    - Fallback response generation capability
    - Status tracking for UI display
    """
    if "ollama_client" not in st.session_state:
        try:
            from ..ollama_client import get_ollama_client_singleton
            
            client = get_ollama_client_singleton()
            st.session_state["ollama_client"] = client
            
            # Check availability and models in background
            is_available = client.is_available()
            models = client.get_available_models() if is_available else []
            
            st.session_state["ollama_available"] = is_available
            st.session_state["ollama_models"] = models
            
            if is_available:
                logger.info(f"Ollama initialized: {len(models)} models available")
            else:
                logger.debug("Ollama service not available (will use FirstPerson pipeline)")
                
        except Exception as e:
            logger.debug(f"Ollama client init failed: {e}")
            st.session_state["ollama_client"] = None
            st.session_state["ollama_available"] = False
            st.session_state["ollama_models"] = []
