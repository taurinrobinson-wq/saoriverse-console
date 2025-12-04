"""
Learning and Evolution Tracker Component.

Handles dynamic glyph generation, hybrid learning integration,
and learning statistics tracking.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def initialize_learning_system():
    """Initialize the hybrid learning system if available."""
    if "hybrid_processor" in st.session_state:
        return True

    try:
        from emotional_os.learning.hybrid_learner_v2 import get_hybrid_learner
        from emotional_os.learning.adaptive_signal_extractor import AdaptiveSignalExtractor

        try:
            from hybrid_processor_with_evolution import create_integrated_processor
        except ImportError:
            create_integrated_processor = None

        if not create_integrated_processor:
            logger.debug("Dynamic evolution not available")
            return False

        learner = get_hybrid_learner()
        user_id = st.session_state.get("user_id", "anonymous")
        st.session_state["persistent_user_id"] = user_id

        adaptive_extractor = AdaptiveSignalExtractor(
            adaptive=True,
            use_discovered=True,
            persistence_path=f"learning/user_signals/{user_id}_signals.json",
        )

        st.session_state["hybrid_processor"] = create_integrated_processor(
            hybrid_learner=learner,
            adaptive_extractor=adaptive_extractor,
            user_id=user_id,
        )

        st.session_state["learning_stats"] = {
            "exchanges_processed": 0,
            "signals_learned": 0,
            "glyphs_generated": 0,
        }

        return True

    except Exception as e:
        logger.debug(f"Learning system initialization failed: {e}")
        return False


def process_learning_exchange(user_input: str, response: str, glyphs: list):
    """Process exchange through learning system.

    Args:
        user_input: User message
        response: System response
        glyphs: List of activated glyphs

    Returns:
        Evolution result dict or None
    """
    try:
        processor = st.session_state.get("hybrid_processor")
        if not processor:
            return None

        user_id = st.session_state.get("persistent_user_id", "anonymous")

        evolution_result = processor.process_user_message(
            user_message=user_input,
            ai_response=response,
            user_id=user_id,
            conversation_id=st.session_state.get(
                "current_conversation_id", "default"),
            glyphs=glyphs,
        )

        return evolution_result

    except Exception as e:
        logger.debug(f"Learning exchange processing failed: {e}")
        return None


def track_learning_metrics(evolution_result: dict):
    """Update learning metrics from evolution result.

    Args:
        evolution_result: Result from process_learning_exchange()
    """
    try:
        if not evolution_result:
            return

        stats = st.session_state.get("learning_stats", {
            "exchanges_processed": 0,
            "signals_learned": 0,
            "glyphs_generated": 0,
        })

        stats["exchanges_processed"] = stats.get("exchanges_processed", 0) + 1

        learning_result = evolution_result.get("learning_result", {})
        if learning_result.get("learned_to_user"):
            signals_count = len(evolution_result.get("emotional_signals", []))
            stats["signals_learned"] = stats.get(
                "signals_learned", 0) + signals_count

        new_glyphs = evolution_result.get("pipeline_stages", {}).get(
            "glyph_generation", {}
        ).get("new_glyphs_generated", [])
        if new_glyphs:
            stats["glyphs_generated"] = stats.get(
                "glyphs_generated", 0) + len(new_glyphs)

        st.session_state["learning_stats"] = stats

    except Exception as e:
        logger.debug(f"Error tracking learning metrics: {e}")


def display_new_glyphs(new_glyphs: list):
    """Display newly generated glyphs.

    Args:
        new_glyphs: List of newly generated glyph objects
    """
    try:
        if not new_glyphs:
            return

        st.success(f"✨ {len(new_glyphs)} new glyph(s) discovered!")

        for glyph in new_glyphs:
            try:
                glyph_dict = glyph.to_dict() if hasattr(glyph, "to_dict") else glyph
                symbol = glyph_dict.get("symbol", "?")
                name = glyph_dict.get("name", "Unknown")
                emotions = " + ".join(glyph_dict.get("core_emotions", []))

                st.info(f"{symbol} **{name}** ({emotions})")

            except Exception as e:
                logger.debug(f"Error displaying glyph: {e}")

    except Exception as e:
        logger.debug(f"Error displaying new glyphs: {e}")


def display_learning_progress():
    """Display learning statistics in sidebar."""
    try:
        stats = st.session_state.get("learning_stats", {})

        if not stats:
            return

        st.sidebar.markdown("### 📊 Learning Progress")
        st.sidebar.metric(
            "Exchanges Processed",
            stats.get("exchanges_processed", 0),
        )
        st.sidebar.metric(
            "Signals Learned",
            stats.get("signals_learned", 0),
        )
        st.sidebar.metric(
            "Glyphs Generated",
            stats.get("glyphs_generated", 0),
        )

    except Exception as e:
        logger.debug(f"Error displaying learning progress: {e}")


def handle_dynamic_evolution(user_input: str, response: str, glyphs: list):
    """Complete workflow for dynamic evolution.

    Initializes learning if needed, processes exchange, tracks metrics,
    and displays results.

    Args:
        user_input: User message
        response: System response
        glyphs: List of activated glyphs
    """
    try:
        # Initialize if needed
        if not st.session_state.get("hybrid_processor"):
            if not initialize_learning_system():
                return

        # Process
        evolution_result = process_learning_exchange(
            user_input, response, glyphs)

        if evolution_result:
            # Track metrics
            track_learning_metrics(evolution_result)

            # Display new glyphs
            new_glyphs = evolution_result.get("pipeline_stages", {}).get(
                "glyph_generation", {}
            ).get("new_glyphs_generated", [])
            if new_glyphs:
                display_new_glyphs(new_glyphs)

            # Log result
            learning_result = evolution_result.get("learning_result", {})
            if learning_result.get("learned_to_shared"):
                logger.info(f"User contributed to shared lexicon")
            elif learning_result.get("learned_to_user"):
                logger.info(f"User learning to personal lexicon")

    except Exception as e:
        logger.debug(f"Dynamic evolution handling failed: {e}")
