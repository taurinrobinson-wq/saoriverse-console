"""Sprint 5c: Session Logger & Analysis

Comprehensive logging of voice interactions for emotional analysis.
Tracks prosody, emotional states, and conversation dynamics.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class InteractionEvent:
    """Single message or voice event."""

    timestamp: datetime
    """When the event occurred."""

    speaker: str
    """'user' or 'assistant'."""

    text: str
    """Message or transcribed text."""

    audio_hash: Optional[str] = None
    """Hash of audio (for deduplication/reference)."""

    duration_ms: Optional[float] = None
    """Duration of audio in milliseconds."""

    confidence: Optional[float] = None
    """STT/TTS confidence (0-1)."""

    emotional_state: Optional[Dict[str, float]] = None
    """Glyph signals: {voltage, tone, attunement, certainty, valence}."""

    prosody_plan: Optional[Dict[str, Any]] = None
    """Applied prosody characteristics."""

    latency_ms: Optional[float] = None
    """Round-trip latency for this interaction."""

    metadata: Dict[str, Any] = None
    """Additional context."""

    def __post_init__(self):
        """Initialize metadata."""
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "speaker": self.speaker,
            "text": self.text,
            "audio_hash": self.audio_hash,
            "duration_ms": self.duration_ms,
            "confidence": self.confidence,
            "emotional_state": self.emotional_state,
            "prosody_plan": self.prosody_plan,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
        }


@dataclass
class SessionSummary:
    """High-level session statistics."""

    session_id: str
    """Unique session identifier."""

    start_time: datetime
    """Session start."""

    end_time: Optional[datetime] = None
    """Session end."""

    total_user_messages: int = 0
    """Number of user messages."""

    total_assistant_messages: int = 0
    """Number of assistant responses."""

    avg_latency_ms: float = 0.0
    """Average latency across interactions."""

    emotional_trajectory: List[float] = None
    """Voltage values over time (arousal trajectory)."""

    dominant_tones: List[str] = None
    """Most common emotional tones."""

    conversation_quality: float = 0.0
    """0-1 quality metric based on engagement."""

    metadata: Dict[str, Any] = None
    """Additional context."""

    def __post_init__(self):
        """Initialize collections."""
        if self.emotional_trajectory is None:
            self.emotional_trajectory = []
        if self.dominant_tones is None:
            self.dominant_tones = []
        if self.metadata is None:
            self.metadata = {}

    def duration_seconds(self) -> float:
        """Get session duration in seconds."""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def messages_per_minute(self) -> float:
        """Calculate messages per minute."""
        duration = self.duration_seconds()
        if duration == 0:
            return 0
        total_messages = self.total_user_messages + self.total_assistant_messages
        return (total_messages / duration) * 60

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_user_messages": self.total_user_messages,
            "total_assistant_messages": self.total_assistant_messages,
            "avg_latency_ms": self.avg_latency_ms,
            "emotional_trajectory": self.emotional_trajectory,
            "dominant_tones": self.dominant_tones,
            "conversation_quality": self.conversation_quality,
            "duration_seconds": self.duration_seconds(),
            "messages_per_minute": self.messages_per_minute(),
            "metadata": self.metadata,
        }


class SessionLogger:
    """Comprehensive session logging and analysis."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        save_dir: Optional[str] = None,
    ):
        """Initialize session logger.

        Args:
            session_id: Optional session identifier
            save_dir: Directory to save session logs
        """
        self.session_id = session_id or self._generate_session_id()
        self.save_dir = Path(save_dir) if save_dir else Path("./session_logs")
        self.events: List[InteractionEvent] = []
        self.summary = SessionSummary(
            session_id=self.session_id,
            start_time=datetime.now(),
        )

        # Ensure save directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def log_user_message(
        self,
        text: str,
        audio_hash: Optional[str] = None,
        duration_ms: Optional[float] = None,
        confidence: Optional[float] = None,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Log user message.

        Args:
            text: Transcribed text
            audio_hash: Hash of audio bytes
            duration_ms: Audio duration
            confidence: STT confidence
            latency_ms: Processing latency
            metadata: Additional context
        """
        event = InteractionEvent(
            timestamp=datetime.now(),
            speaker="user",
            text=text,
            audio_hash=audio_hash,
            duration_ms=duration_ms,
            confidence=confidence,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )
        self.events.append(event)
        self.summary.total_user_messages += 1

    def log_assistant_message(
        self,
        text: str,
        emotional_state: Optional[Dict[str, float]] = None,
        prosody_plan: Optional[Dict[str, Any]] = None,
        audio_hash: Optional[str] = None,
        duration_ms: Optional[float] = None,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Log assistant response.

        Args:
            text: Response text
            emotional_state: Glyph signals
            prosody_plan: Prosody characteristics
            audio_hash: Hash of synthesized audio
            duration_ms: Audio duration
            latency_ms: Processing latency
            metadata: Additional context
        """
        event = InteractionEvent(
            timestamp=datetime.now(),
            speaker="assistant",
            text=text,
            emotional_state=emotional_state,
            prosody_plan=prosody_plan,
            audio_hash=audio_hash,
            duration_ms=duration_ms,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )
        self.events.append(event)
        self.summary.total_assistant_messages += 1

        # Track emotional trajectory
        if emotional_state and "voltage" in emotional_state:
            self.summary.emotional_trajectory.append(
                emotional_state["voltage"])

        # Track dominant tones
        if emotional_state and "tone" in emotional_state:
            tone = emotional_state["tone"]
            if tone not in self.summary.dominant_tones:
                self.summary.dominant_tones.append(tone)

    def calculate_session_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive session metrics.

        Returns:
            Dictionary with various metrics
        """
        if not self.events:
            return {"error": "No events logged"}

        # Latency stats
        latencies = [e.latency_ms for e in self.events if e.latency_ms]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        self.summary.avg_latency_ms = avg_latency

        # Confidence stats
        user_confidences = [
            e.confidence for e in self.events
            if e.speaker == "user" and e.confidence
        ]
        avg_user_confidence = (
            sum(user_confidences) / len(user_confidences)
            if user_confidences else 0
        )

        # Engagement calculation
        user_messages = [e for e in self.events if e.speaker == "user"]
        assistant_messages = [
            e for e in self.events if e.speaker == "assistant"]

        # Quality based on: consistency, responsiveness, emotional attunement
        consistency = self._calculate_consistency()
        responsiveness = self._calculate_responsiveness()
        attunement = self._calculate_attunement()

        quality_score = (consistency * 0.3 +
                         responsiveness * 0.3 + attunement * 0.4)
        self.summary.conversation_quality = quality_score

        return {
            "session_id": self.session_id,
            "total_events": len(self.events),
            "total_user_messages": self.summary.total_user_messages,
            "total_assistant_messages": self.summary.total_assistant_messages,
            "avg_latency_ms": avg_latency,
            "avg_user_confidence": avg_user_confidence,
            "consistency_score": consistency,
            "responsiveness_score": responsiveness,
            "attunement_score": attunement,
            "conversation_quality": quality_score,
            "duration_seconds": self.summary.duration_seconds(),
            "messages_per_minute": self.summary.messages_per_minute(),
        }

    def _calculate_consistency(self) -> float:
        """Calculate emotional consistency (0-1).

        Returns:
            Consistency score
        """
        if len(self.summary.emotional_trajectory) < 2:
            return 0.5

        trajectory = self.summary.emotional_trajectory
        # Lower variance = higher consistency
        variance = sum((x - sum(trajectory) / len(trajectory)) ** 2
                       for x in trajectory) / len(trajectory)
        # Normalize to 0-1 (assuming max reasonable variance of 0.25)
        consistency = 1.0 - min(1.0, variance / 0.25)
        return consistency

    def _calculate_responsiveness(self) -> float:
        """Calculate how responsive assistant is.

        Returns:
            Responsiveness score (0-1)
        """
        user_msgs = sum(1 for e in self.events if e.speaker == "user")
        assistant_msgs = sum(
            1 for e in self.events if e.speaker == "assistant")

        # Ideal ratio is 1:1 or slightly more assistant (quick responses)
        if user_msgs == 0:
            return 0.0

        ratio = assistant_msgs / user_msgs
        # Score: peak at 1.0 ratio, penalize deviation
        if ratio >= 0.8:
            return min(1.0, ratio)
        else:
            return 0.5  # Too few assistant responses

    def _calculate_attunement(self) -> float:
        """Calculate emotional attunement from logged signals.

        Returns:
            Attunement score (0-1)
        """
        assistant_events = [e for e in self.events if e.speaker == "assistant"]

        if not assistant_events:
            return 0.5

        attunements = [
            e.emotional_state.get("emotional_attunement", 0.5)
            for e in assistant_events
            if e.emotional_state
        ]

        if not attunements:
            return 0.5

        return sum(attunements) / len(attunements)

    def save_session(self) -> str:
        """Save session to JSON file.

        Returns:
            Path to saved session file
        """
        self.summary.end_time = datetime.now()
        metrics = self.calculate_session_metrics()

        session_data = {
            "summary": self.summary.to_dict(),
            "metrics": metrics,
            "events": [e.to_dict() for e in self.events],
        }

        save_path = self.save_dir / f"{self.session_id}.json"

        with open(save_path, "w") as f:
            json.dump(session_data, f, indent=2, default=str)

        return str(save_path)

    def get_summary_report(self) -> str:
        """Generate human-readable session summary.

        Returns:
            Formatted summary text
        """
        metrics = self.calculate_session_metrics()
        summary = self.summary

        report = f"""
VOICE INTERACTION SESSION REPORT
{'='*60}

Session ID: {self.session_id}
Start Time: {summary.start_time.isoformat()}
End Time: {summary.end_time.isoformat() if summary.end_time else 'Ongoing'}
Duration: {summary.duration_seconds():.1f} seconds

CONVERSATION METRICS
{'-'*60}
Total User Messages: {summary.total_user_messages}
Total Assistant Responses: {summary.total_assistant_messages}
Message Frequency: {summary.messages_per_minute():.1f} msg/min
Average Latency: {metrics['avg_latency_ms']:.0f}ms

EMOTIONAL ANALYSIS
{'-'*60}
Emotional Trajectory (Arousal): {summary.emotional_trajectory}
Dominant Tones: {', '.join(summary.dominant_tones)}
Consistency Score: {metrics['consistency_score']:.2f}
Attunement Score: {metrics['attunement_score']:.2f}
Overall Quality: {metrics['conversation_quality']:.2f}

CONVERSATION QUALITY
{'-'*60}
Responsiveness: {metrics['responsiveness_score']:.2f}
Consistency: {metrics['consistency_score']:.2f}
Emotional Attunement: {metrics['attunement_score']:.2f}

Overall Conversation Quality: {metrics['conversation_quality']:.2f}/1.0
"""
        return report

    @staticmethod
    def _generate_session_id() -> str:
        """Generate unique session ID.

        Returns:
            Session ID based on timestamp and hash
        """
        timestamp = datetime.now().isoformat()
        hash_obj = hashlib.md5(timestamp.encode())
        return f"session_{hash_obj.hexdigest()[:8]}"


class SessionAnalyzer:
    """Analyzes patterns across sessions."""

    def __init__(self, session_dir: str = "./session_logs"):
        """Initialize analyzer.

        Args:
            session_dir: Directory containing session logs
        """
        self.session_dir = Path(session_dir)
        self.sessions = []
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load all session files from directory."""
        if not self.session_dir.exists():
            return

        for session_file in self.session_dir.glob("*.json"):
            try:
                with open(session_file) as f:
                    session_data = json.load(f)
                    self.sessions.append(session_data)
            except (json.JSONDecodeError, IOError):
                continue

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate metrics across all sessions.

        Returns:
            Dictionary with aggregate statistics
        """
        if not self.sessions:
            return {"error": "No sessions loaded"}

        latencies = []
        consistencies = []
        attunements = []
        qualities = []

        for session in self.sessions:
            metrics = session.get("metrics", {})
            if "avg_latency_ms" in metrics:
                latencies.append(metrics["avg_latency_ms"])
            if "consistency_score" in metrics:
                consistencies.append(metrics["consistency_score"])
            if "attunement_score" in metrics:
                attunements.append(metrics["attunement_score"])
            if "conversation_quality" in metrics:
                qualities.append(metrics["conversation_quality"])

        return {
            "total_sessions": len(self.sessions),
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "avg_consistency": sum(consistencies) / len(consistencies) if consistencies else 0,
            "avg_attunement": sum(attunements) / len(attunements) if attunements else 0,
            "avg_quality": sum(qualities) / len(qualities) if qualities else 0,
        }


if __name__ == "__main__":
    # Example usage
    logger = SessionLogger()

    # Log user message
    logger.log_user_message(
        "That sounds wonderful!",
        confidence=0.95,
        latency_ms=250,
    )

    # Log assistant response
    logger.log_assistant_message(
        "I'm so happy to hear that!",
        emotional_state={
            "voltage": 0.8,
            "tone": "excited",
            "emotional_attunement": 0.9,
            "certainty": 0.9,
            "valence": 0.9,
        },
        latency_ms=280,
    )

    # Print summary
    print(logger.get_summary_report())

    # Save session
    save_path = logger.save_session()
    print(f"Session saved to: {save_path}")
