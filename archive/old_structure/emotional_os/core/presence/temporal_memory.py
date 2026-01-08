"""Temporal Memory - Emotional Residue and Affective Continuity

TemporalMemory creates a memory module that retains emotional residue
from past interactions for affective continuity. Emotional recall is
tied to feelings and moods, giving users a sense of being "remembered"
emotionally.

Key concepts:
- Emotional Residue: Traces of past emotional exchanges
- Affective Continuity: Consistent emotional relationship over time
- Mood Memory: Remembering emotional contexts, not just content
- Emotional Recall: Retrieving feelings associated with past interactions

Documentation:
    The TemporalMemory module stores emotional "capsules" that capture
    the essence of past interactions. Unlike content-based memory, this
    system prioritizes:
    - The feeling tone of past exchanges
    - Recurring emotional patterns
    - Significant emotional moments
    - The arc of the emotional relationship

    This enables the system to greet returning users with contextual
    emotional awareness, such as "Last time we spoke, you were carrying
    something heavy."
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import hashlib


class EmotionalSignificance(Enum):
    """Levels of emotional significance for memory storage."""
    ROUTINE = "routine"           # Normal interaction
    MEANINGFUL = "meaningful"     # Notable emotional content
    SIGNIFICANT = "significant"   # Important emotional moment
    PIVOTAL = "pivotal"          # Transformative interaction


class EmotionalArc(Enum):
    """Overall emotional arc of a session."""
    ASCENDING = "ascending"       # Moved toward positive
    DESCENDING = "descending"     # Moved toward difficult
    STABLE = "stable"             # Maintained state
    TRANSFORMING = "transforming" # Shifted perspective
    PROCESSING = "processing"     # Working through


@dataclass
class EmotionalResidue:
    """A capsule of emotional residue from a past interaction.

    Attributes:
        session_id: Unique identifier for the session
        timestamp: When the interaction occurred
        primary_emotion: Dominant emotion detected
        emotional_arc: How emotions evolved during session
        significance: How emotionally significant
        residual_feelings: List of lingering emotional traces
        unresolved_threads: Topics that remained open
        mood_signature: A fingerprint of the emotional state
        user_hash: Anonymous user identifier
    """
    session_id: str
    timestamp: datetime
    primary_emotion: str
    emotional_arc: EmotionalArc
    significance: EmotionalSignificance
    residual_feelings: List[str]
    unresolved_threads: List[str]
    mood_signature: str
    user_hash: str = ""

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "primary_emotion": self.primary_emotion,
            "emotional_arc": self.emotional_arc.value,
            "significance": self.significance.value,
            "residual_feelings": self.residual_feelings,
            "unresolved_threads": self.unresolved_threads,
            "mood_signature": self.mood_signature,
            "user_hash": self.user_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EmotionalResidue":
        """Deserialize from dictionary."""
        return cls(
            session_id=data.get("session_id", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(timezone.utc),
            primary_emotion=data.get("primary_emotion", "neutral"),
            emotional_arc=EmotionalArc(data.get("emotional_arc", "stable")),
            significance=EmotionalSignificance(data.get("significance", "routine")),
            residual_feelings=data.get("residual_feelings", []),
            unresolved_threads=data.get("unresolved_threads", []),
            mood_signature=data.get("mood_signature", ""),
            user_hash=data.get("user_hash", ""),
        )


@dataclass
class EmotionalRecall:
    """A recalled emotional memory for context."""
    residue: EmotionalResidue
    relevance_score: float
    time_distance: timedelta
    recall_reason: str


class TemporalMemory:
    """Memory system for emotional residue and affective continuity.

    This system enables emotional recall across sessions, allowing
    the system to maintain awareness of the user's emotional journey
    over time.

    Example:
        >>> memory = TemporalMemory()
        >>> memory.store_session_residue(
        ...     session_id="abc123",
        ...     emotions=["grief", "hope"],
        ...     arc=EmotionalArc.TRANSFORMING,
        ...     significance=EmotionalSignificance.MEANINGFUL
        ... )
        >>> recalls = memory.recall_for_context(current_emotion="hope")
        >>> print(recalls[0].recall_reason)
        "Similar emotional content"
    """

    def __init__(self, storage_path: Optional[str] = None, max_memories: int = 100):
        """Initialize temporal memory.

        Args:
            storage_path: Optional path for persistence
            max_memories: Maximum memories to retain
        """
        self._storage_path = storage_path
        self._max_memories = max_memories
        self._memories: List[EmotionalResidue] = []
        self._current_session: Optional[str] = None
        self._session_emotions: List[str] = []

        if storage_path:
            self._load_memories()

    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]

    def _generate_user_hash(self, identifier: str) -> str:
        """Generate anonymous user hash."""
        return hashlib.sha256(identifier.encode()).hexdigest()[:12]

    def _generate_mood_signature(self, emotions: List[str], arc: EmotionalArc) -> str:
        """Generate a mood signature from emotions and arc."""
        emotion_str = "-".join(sorted(set(emotions)))
        return f"{arc.value}:{emotion_str[:32]}"

    def start_session(self, user_identifier: Optional[str] = None) -> str:
        """Start a new emotional session.

        Args:
            user_identifier: Optional user identifier for continuity

        Returns:
            The new session ID
        """
        self._current_session = self._generate_session_id()
        self._session_emotions = []
        return self._current_session

    def record_emotion(self, emotion: str) -> None:
        """Record an emotion during the current session.

        Args:
            emotion: The detected emotion
        """
        if emotion not in self._session_emotions:
            self._session_emotions.append(emotion)

    def store_session_residue(
        self,
        session_id: Optional[str] = None,
        emotions: Optional[List[str]] = None,
        arc: EmotionalArc = EmotionalArc.STABLE,
        significance: EmotionalSignificance = EmotionalSignificance.ROUTINE,
        unresolved_threads: Optional[List[str]] = None,
        user_identifier: Optional[str] = None,
    ) -> EmotionalResidue:
        """Store emotional residue from a session.

        Args:
            session_id: Session identifier (uses current if not provided)
            emotions: List of emotions from session
            arc: The emotional arc of the session
            significance: How significant the session was
            unresolved_threads: Topics that remain open
            user_identifier: Optional user identifier

        Returns:
            The stored EmotionalResidue
        """
        sid = session_id or self._current_session or self._generate_session_id()
        emos = emotions or self._session_emotions or ["neutral"]
        threads = unresolved_threads or []
        user_hash = self._generate_user_hash(user_identifier) if user_identifier else ""

        # Derive primary emotion (first detected is usually primary)
        primary = emos[0] if emos else "neutral"

        # Generate residual feelings based on arc and emotions
        residual = self._derive_residual_feelings(emos, arc)

        # Generate mood signature
        signature = self._generate_mood_signature(emos, arc)

        residue = EmotionalResidue(
            session_id=sid,
            timestamp=datetime.now(timezone.utc),
            primary_emotion=primary,
            emotional_arc=arc,
            significance=significance,
            residual_feelings=residual,
            unresolved_threads=threads,
            mood_signature=signature,
            user_hash=user_hash,
        )

        self._memories.append(residue)

        # Maintain memory limit, prioritizing significant memories
        self._prune_memories()

        if self._storage_path:
            self._save_memories()

        return residue

    def _derive_residual_feelings(self, emotions: List[str], arc: EmotionalArc) -> List[str]:
        """Derive residual feelings from session emotions and arc."""
        residual = []

        # Map emotions to potential residual feelings
        residual_map = {
            "grief": ["lingering sadness", "tender openness"],
            "sadness": ["gentle melancholy", "quiet processing"],
            "joy": ["warmth", "lightness"],
            "anger": ["residual tension", "need for resolution"],
            "fear": ["heightened awareness", "need for safety"],
            "anxiety": ["underlying unease", "desire for clarity"],
            "hope": ["gentle anticipation", "emerging trust"],
            "love": ["connection warmth", "caring presence"],
            "confusion": ["unresolved questions", "seeking clarity"],
        }

        for emotion in emotions:
            if emotion in residual_map:
                residual.extend(residual_map[emotion])

        # Add arc-specific residuals
        arc_residuals = {
            EmotionalArc.ASCENDING: ["sense of movement", "emerging clarity"],
            EmotionalArc.DESCENDING: ["heaviness to process", "need for support"],
            EmotionalArc.TRANSFORMING: ["shift in perspective", "new understanding"],
            EmotionalArc.PROCESSING: ["ongoing work", "patience with self"],
        }

        if arc in arc_residuals:
            residual.extend(arc_residuals[arc])

        # Deduplicate and limit
        return list(dict.fromkeys(residual))[:5]

    def _prune_memories(self) -> None:
        """Prune memories to stay within limit, prioritizing significant ones."""
        if len(self._memories) <= self._max_memories:
            return

        # Sort by significance (keep significant) and recency
        def memory_priority(m: EmotionalResidue) -> Tuple[int, datetime]:
            sig_score = {
                EmotionalSignificance.PIVOTAL: 4,
                EmotionalSignificance.SIGNIFICANT: 3,
                EmotionalSignificance.MEANINGFUL: 2,
                EmotionalSignificance.ROUTINE: 1,
            }.get(m.significance, 0)
            return (sig_score, m.timestamp)

        sorted_memories = sorted(self._memories, key=memory_priority, reverse=True)
        self._memories = sorted_memories[:self._max_memories]

    def recall_for_context(
        self,
        current_emotion: Optional[str] = None,
        user_identifier: Optional[str] = None,
        max_recalls: int = 3,
    ) -> List[EmotionalRecall]:
        """Recall relevant emotional memories for context.

        Args:
            current_emotion: Current emotional context
            user_identifier: User identifier for personalized recall
            max_recalls: Maximum memories to recall

        Returns:
            List of relevant EmotionalRecall objects
        """
        recalls = []
        now = datetime.now(timezone.utc)
        user_hash = self._generate_user_hash(user_identifier) if user_identifier else ""

        for memory in self._memories:
            relevance = 0.0
            reasons = []

            # Same user boost
            if user_hash and memory.user_hash == user_hash:
                relevance += 0.4
                reasons.append("Previous conversation")

            # Emotional similarity boost
            if current_emotion and current_emotion == memory.primary_emotion:
                relevance += 0.3
                reasons.append("Similar emotional content")

            # Emotional pattern boost (in residual feelings)
            if current_emotion:
                for feeling in memory.residual_feelings:
                    if current_emotion.lower() in feeling.lower():
                        relevance += 0.2
                        reasons.append("Related emotional thread")
                        break

            # Significance boost
            sig_boost = {
                EmotionalSignificance.PIVOTAL: 0.3,
                EmotionalSignificance.SIGNIFICANT: 0.2,
                EmotionalSignificance.MEANINGFUL: 0.1,
                EmotionalSignificance.ROUTINE: 0.0,
            }.get(memory.significance, 0.0)
            relevance += sig_boost

            # Recency factor (more recent = more relevant, but not dominant)
            time_distance = now - memory.timestamp
            if time_distance.days < 7:
                relevance += 0.1
            elif time_distance.days < 30:
                relevance += 0.05

            if relevance > 0.2:  # Threshold for recall
                recall = EmotionalRecall(
                    residue=memory,
                    relevance_score=min(1.0, relevance),
                    time_distance=time_distance,
                    recall_reason=reasons[0] if reasons else "Emotional resonance",
                )
                recalls.append(recall)

        # Sort by relevance and return top N
        recalls.sort(key=lambda r: r.relevance_score, reverse=True)
        return recalls[:max_recalls]

    def get_emotional_context_phrase(
        self,
        current_emotion: Optional[str] = None,
        user_identifier: Optional[str] = None,
    ) -> Optional[str]:
        """Get a phrase expressing awareness of emotional history.

        Args:
            current_emotion: Current emotional context
            user_identifier: User identifier

        Returns:
            A contextual phrase or None
        """
        recalls = self.recall_for_context(current_emotion, user_identifier, max_recalls=1)

        if not recalls:
            return None

        recall = recalls[0]
        memory = recall.residue

        # Generate contextual phrase based on memory
        time_desc = self._time_description(recall.time_distance)

        if memory.emotional_arc == EmotionalArc.TRANSFORMING:
            return f"{time_desc}, you were working through something important."
        elif memory.emotional_arc == EmotionalArc.ASCENDING:
            return f"{time_desc}, things were beginning to feel lighter for you."
        elif memory.emotional_arc == EmotionalArc.DESCENDING:
            return f"{time_desc}, you were carrying something heavy. I remember that."
        elif memory.unresolved_threads:
            thread = memory.unresolved_threads[0]
            return f"{time_desc}, we touched on {thread}. Is that still present for you?"
        else:
            return f"I remember our conversation {time_desc}. Something of it stays with me."

    def _time_description(self, delta: timedelta) -> str:
        """Convert time delta to human-readable description."""
        if delta.days == 0:
            return "Earlier today"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        elif delta.days < 14:
            return "Last week"
        elif delta.days < 30:
            return "A few weeks ago"
        elif delta.days < 60:
            return "Last month"
        else:
            return "Some time ago"

    def _save_memories(self) -> None:
        """Persist memories to storage."""
        if not self._storage_path:
            return

        data = [m.to_dict() for m in self._memories]
        try:
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silent failure for non-critical persistence

    def _load_memories(self) -> None:
        """Load memories from storage."""
        if not self._storage_path:
            return

        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._memories = [EmotionalResidue.from_dict(d) for d in data]
        except FileNotFoundError:
            pass
        except Exception:
            pass  # Silent failure

    def get_relationship_summary(self, user_identifier: Optional[str] = None) -> Dict:
        """Get a summary of the emotional relationship with a user.

        Args:
            user_identifier: The user identifier

        Returns:
            Dictionary summarizing the emotional relationship
        """
        user_hash = self._generate_user_hash(user_identifier) if user_identifier else ""

        if not user_hash:
            return {"status": "no_history", "sessions": 0}

        user_memories = [m for m in self._memories if m.user_hash == user_hash]

        if not user_memories:
            return {"status": "new_relationship", "sessions": 0}

        # Analyze emotional patterns
        emotions = [m.primary_emotion for m in user_memories]
        arcs = [m.emotional_arc for m in user_memories]

        dominant_emotion = max(set(emotions), key=emotions.count) if emotions else "neutral"
        dominant_arc = max(set(arcs), key=arcs.count) if arcs else EmotionalArc.STABLE

        return {
            "status": "established",
            "sessions": len(user_memories),
            "dominant_emotion": dominant_emotion,
            "typical_arc": dominant_arc.value,
            "first_contact": user_memories[0].timestamp.isoformat() if user_memories else None,
            "last_contact": user_memories[-1].timestamp.isoformat() if user_memories else None,
        }

    def clear(self) -> None:
        """Clear all memories."""
        self._memories.clear()
        self._current_session = None
        self._session_emotions.clear()
