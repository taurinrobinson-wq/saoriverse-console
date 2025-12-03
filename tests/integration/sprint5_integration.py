"""Sprint 5 Integration Bridge

Connects Sprint 5 modules (performance profiling, advanced prosody, session logging,
UI enhancements) to the existing response pipeline.

This module hooks into:
- DynamicResponseComposer for enhanced prosody
- Response pipeline for session logging
- Edge case validation for input/output
- Performance monitoring

Usage:
    from sprint5_integration import get_enhanced_response
    
    response, metadata = get_enhanced_response(
        user_input="What a stressful day!",
        emotional_state={"voltage": 0.8, "tone": "frustrated"},
        conversation_context=[...]
    )
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Sprint 5 modules
from spoken_interface.performance_profiler import PerformanceProfiler, ModelPerformanceBenchmark
from spoken_interface.advanced_prosody import AdvancedProsodyPlanner, EmotionalContinuityTracker
from spoken_interface.session_logger import SessionLogger
from spoken_interface.voice_ui_enhancements import VoiceUIEnhancements, EdgeCaseManager

logger = logging.getLogger(__name__)

# Global instances (lazy-initialized)
_profiler: Optional[PerformanceProfiler] = None
_prosody_planner: Optional[AdvancedProsodyPlanner] = None
_session_logger: Optional[SessionLogger] = None
_ui_enhancements: Optional[VoiceUIEnhancements] = None
_continuity_tracker: Optional[EmotionalContinuityTracker] = None


def init_sprint5_systems(enable_profiling: bool = False, session_dir: str = "./logs/sessions") -> None:
    """Initialize Sprint 5 systems globally.

    Args:
        enable_profiling: Whether to enable performance profiling (default False - overhead)
        session_dir: Directory for saving session logs
    """
    global _profiler, _prosody_planner, _session_logger, _ui_enhancements, _continuity_tracker

    if enable_profiling:
        _profiler = PerformanceProfiler()
        logger.info("Performance profiling enabled")

    _prosody_planner = AdvancedProsodyPlanner()
    _session_logger = SessionLogger(save_dir=session_dir)
    _ui_enhancements = VoiceUIEnhancements()
    _continuity_tracker = EmotionalContinuityTracker()

    logger.info("Sprint 5 systems initialized")


def validate_user_input(user_text: str, confidence: float = 1.0) -> Tuple[bool, Optional[str]]:
    """Validate user input for edge cases before processing.

    Args:
        user_text: The user's message text
        confidence: Transcription confidence (0-1)

    Returns:
        (is_valid, error_message) - if not valid, error_message explains the issue
    """
    if not _ui_enhancements:
        return True, None

    # Check for empty input
    if not user_text or not user_text.strip():
        return False, "Your message appears empty. Please try again."

    # Check transcription quality
    is_valid, error_msg = _ui_enhancements.handle_transcription_edge_cases(
        text=user_text,
        confidence=confidence
    )

    return is_valid, error_msg


def enhance_response_with_prosody(
    response_text: str,
    emotional_state: Optional[Dict[str, Any]] = None,
    user_input: str = ""
) -> Tuple[str, Dict[str, Any]]:
    """Enhance response with advanced prosody planning.

    For high-emotion responses (frustrated, anxious, excited), generates
    dynamic prosody directives that make the response more emotionally
    authentic.

    Args:
        response_text: The base response
        emotional_state: Parsed emotional signals (voltage, tone, attunement, certainty)
        user_input: Original user input (for context)

    Returns:
        (enhanced_response, prosody_directives) - response text and prosody metadata
    """
    if not _prosody_planner or not emotional_state:
        return response_text, {}

    # Only enhance for emotionally significant responses
    tone = emotional_state.get("tone", "neutral")
    if tone not in ["excited", "frustrated", "anxious", "sad", "empathetic"]:
        return response_text, {}

    try:
        # Plan advanced prosody
        prosody_plan = _prosody_planner.plan_advanced_prosody(
            text=response_text,
            voltage=emotional_state.get("voltage", 0.5),
            tone=tone,
            attunement=emotional_state.get("attunement", 0.5),
            certainty=emotional_state.get("certainty", 0.5)
        )

        # Return prosody directives as metadata
        prosody_directives = {
            "base_rate": prosody_plan.base_rate,
            "pitch_contour": prosody_plan.pitch_contour,
            "energy_contour": prosody_plan.energy_contour,
            "emphasis_points": [
                {"word_index": ep.word_index, "type": str(
                    ep.type), "intensity": ep.intensity}
                for ep in prosody_plan.emphasis_points
            ],
            "micro_pauses": [
                {"position": mp.position, "duration_ms": mp.duration_ms,
                    "purpose": mp.purpose}
                for mp in prosody_plan.micro_pauses
            ],
            "breath_style": str(prosody_plan.breath_style),
            "breathiness": prosody_plan.breathiness,
            "terminal_pitch": prosody_plan.terminal_pitch,
        }

        return response_text, prosody_directives

    except Exception as e:
        logger.warning(f"Prosody enhancement failed: {e}")
        return response_text, {}


def log_interaction(
    user_text: str,
    assistant_response: str,
    emotional_state: Optional[Dict[str, Any]] = None,
    latency_ms: float = 0.0,
    confidence: float = 1.0,
    prosody_plan: Optional[Dict[str, Any]] = None
) -> None:
    """Log user/assistant interaction to session.

    Args:
        user_text: User's message
        assistant_response: System's response
        emotional_state: Parsed emotional signals
        latency_ms: Response latency in milliseconds
        confidence: Transcription confidence
        prosody_plan: Prosody directives applied to response
    """
    if not _session_logger:
        return

    try:
        # Log user message
        _session_logger.log_user_message(
            text=user_text,
            confidence=confidence,
            # Assume user/AI split latency evenly
            latency_ms=int(latency_ms / 2)
        )

        # Log assistant message
        _session_logger.log_assistant_message(
            text=assistant_response,
            emotional_state=emotional_state or {},
            prosody_plan=prosody_plan,
            latency_ms=int(latency_ms / 2)
        )

        # Track emotional continuity
        if _continuity_tracker and emotional_state:
            _continuity_tracker.add_response(
                text=assistant_response,
                voltage=emotional_state.get("voltage", 0.5),
                tone=emotional_state.get("tone", "neutral"),
                attunement=emotional_state.get("attunement", 0.5)
            )

    except Exception as e:
        logger.warning(f"Interaction logging failed: {e}")


def get_session_metrics() -> Dict[str, Any]:
    """Get current session metrics.

    Returns:
        Dictionary with:
        - consistency_score: Emotional stability (0-1)
        - responsiveness_score: Response speed quality (0-1)
        - attunement_score: Empathetic engagement (0-1)
        - quality_score: Overall conversation quality (0-1)
        - emotional_continuity: Session consistency (0-1)
        - total_messages: Total interactions
    """
    if not _session_logger:
        return {}

    try:
        metrics = _session_logger.calculate_session_metrics()

        # Add continuity score
        if _continuity_tracker:
            continuity = _continuity_tracker.get_emotional_continuity_score()
            metrics["emotional_continuity"] = continuity

        return metrics

    except Exception as e:
        logger.warning(f"Metrics calculation failed: {e}")
        return {}


def get_session_summary_report() -> str:
    """Get human-readable session summary report.

    Returns:
        Formatted text report of session statistics
    """
    if not _session_logger:
        return "No session data available"

    try:
        return _session_logger.get_summary_report()
    except Exception as e:
        logger.warning(f"Summary report generation failed: {e}")
        return "Unable to generate report"


def save_session() -> Optional[str]:
    """Save current session to file.

    Returns:
        Path to saved session file, or None if save failed
    """
    if not _session_logger:
        return None

    try:
        return _session_logger.save_session()
    except Exception as e:
        logger.warning(f"Session save failed: {e}")
        return None


def measure_operation(operation_name: str, func, *args, **kwargs) -> Any:
    """Measure latency of an operation.

    Args:
        operation_name: Name of operation for profiling
        func: Function to measure
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result from func
    """
    if not _profiler:
        return func(*args, **kwargs)

    return _profiler.measure(operation_name, func, *args, **kwargs)


def get_performance_summary() -> Dict[str, Any]:
    """Get performance profiling summary.

    Returns:
        Dictionary with latency statistics by operation
    """
    if not _profiler:
        return {}

    return _profiler.get_summary()


def get_model_recommendation(target_latency_ms: int) -> Dict[str, str]:
    """Get model recommendations for target latency.

    Args:
        target_latency_ms: Target latency in milliseconds

    Returns:
        Dictionary with recommended models:
        - whisper_model: Recommended Whisper model size
        - tts_model: Recommended TTS model
    """
    try:
        whisper = ModelPerformanceBenchmark.get_whisper_recommendation(
            target_latency_ms)
        tts = ModelPerformanceBenchmark.get_tts_recommendation(
            target_latency_ms)

        return {
            "whisper_model": whisper,
            "tts_model": tts,
            "target_latency_ms": target_latency_ms
        }
    except Exception as e:
        logger.warning(f"Model recommendation failed: {e}")
        return {}


# Quick convenience function for complete pipeline
def get_enhanced_response(
    user_input: str,
    emotional_state: Optional[Dict[str, Any]] = None,
    conversation_context: Optional[List[Dict[str, str]]] = None,
    confidence: float = 1.0,
    latency_ms: float = 0.0,
    use_profiling: bool = False
) -> Tuple[str, Dict[str, Any]]:
    """Get enhanced response with all Sprint 5 features integrated.

    This is the main integration point - use this to get responses that benefit
    from advanced prosody, session logging, and performance tracking.

    Args:
        user_input: User's message
        emotional_state: Parsed emotional signals
        conversation_context: Previous messages for context
        confidence: Transcription confidence (0-1)
        latency_ms: Latency of response generation in ms
        use_profiling: Whether to measure performance (adds ~1-2ms overhead)

    Returns:
        (response_text, metadata) where metadata contains:
        - prosody_directives: Advanced prosody plan
        - session_metrics: Current session metrics
        - performance_summary: Latency metrics (if profiling enabled)
    """
    # Initialize if needed
    if not _session_logger:
        init_sprint5_systems(enable_profiling=use_profiling)

    # Validate input
    is_valid, error_msg = validate_user_input(user_input, confidence)
    if not is_valid:
        # Log the error
        if _session_logger:
            _session_logger.log_user_message(user_input, confidence=0.0)

        return error_msg or "Unable to process input", {
            "error": error_msg,
            "prosody_directives": {},
            "session_metrics": {}
        }

    # Get base response from existing system
    # (This would be called from DynamicResponseComposer or AI service)
    # For now, just return a placeholder that shows integration
    response_text = "Response would be generated here"

    # Enhance with prosody
    response_text, prosody_directives = enhance_response_with_prosody(
        response_text,
        emotional_state=emotional_state,
        user_input=user_input
    )

    # Log interaction
    log_interaction(
        user_text=user_input,
        assistant_response=response_text,
        emotional_state=emotional_state,
        latency_ms=latency_ms,
        confidence=confidence,
        prosody_plan=prosody_directives
    )

    # Gather metrics
    metrics = get_session_metrics()
    perf_summary = get_performance_summary() if use_profiling else {}

    return response_text, {
        "prosody_directives": prosody_directives,
        "session_metrics": metrics,
        "performance_summary": perf_summary,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Example usage
    init_sprint5_systems(enable_profiling=True)

    # Simulate a stressful interaction
    user_msg = "what a freakin' stressful day this has been!"
    emotional = {
        "voltage": 0.8,
        "tone": "frustrated",
        "attunement": 0.6,
        "certainty": 0.5
    }

    response, metadata = get_enhanced_response(
        user_input=user_msg,
        emotional_state=emotional,
        latency_ms=250.0
    )

    print(f"Response: {response}")
    print(
        f"Prosody directives: {json.dumps(metadata['prosody_directives'], indent=2)}")
    print(
        f"Session metrics: {json.dumps(metadata['session_metrics'], indent=2)}")

    # Save session
    session_path = save_session()
    print(f"\nSession saved to: {session_path}")
