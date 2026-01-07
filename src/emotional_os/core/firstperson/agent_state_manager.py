"""Agent Emotional State Manager for FirstPerson.

Maintains agent's first-person emotional continuity across conversation turns.
Tracks mood, emotional hypothesis, stakes, and commitments that constrain
future responses.

Core philosophy: The agent has an internal emotional state that evolves
as the conversation progresses. This state actively shapes responses.

Key responsibilities:
- Track agent mood and emotional trajectory
- Maintain emotional hypothesis about the user
- Store commitments (things agent has said it cares about)
- Detect and flag emotional contradictions
- Provide continuity across turns
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum


class AgentMood(Enum):
    """Agent emotional states during conversation."""
    LISTENING = "listening"
    RESONATING = "resonating"  # Something in user input touches agent
    CONCERNED = "concerned"  # User is in pain, agent cares
    REFLECTING = "reflecting"  # Agent is thinking through something
    PROTECTIVE = "protective"  # Agent wants to safeguard user
    UNCERTAIN = "uncertain"  # Agent doesn't fully understand
    MOVED = "moved"  # User's vulnerability reaches agent
    GROUNDED = "grounded"  # Agent is centered and stable


@dataclass
class EmotionalPivot:
    """A moment where agent's emotional state shifted.
    
    Stored for later reference to maintain narrative continuity.
    """
    turn_number: int
    timestamp: str
    user_input: str
    
    # What triggered the shift
    previous_mood: str
    new_mood: str
    what_triggered_shift: str
    
    # What the agent committed to (for future validation)
    commitment: str
    narrative_significance: float  # 0-1, how much this matters


@dataclass
class AgentEmotionalState:
    """The agent's internal emotional state (first-person).
    
    This is not analysis of the user's emotions, but the agent's own
    internal continuity and perspective.
    """
    
    user_id: str
    conversation_id: str
    
    # Current emotional state
    primary_mood: AgentMood = AgentMood.LISTENING
    mood_intensity: float = 0.5  # 0-1, how strongly felt
    
    # Emotional trajectory
    recent_mood_shifts: List[Tuple[AgentMood, float, str]] = field(
        default_factory=list
    )  # (mood, intensity, timestamp)
    mood_trend: str = "stable"  # "stable", "escalating", "settling", "cycling"
    
    # Narrative state: The story we're in together
    current_narrative_arc: Optional[str] = None
    emotional_hypothesis: Optional[str] = None  # What's the user processing?
    agent_stakes: Optional[str] = None  # What does agent care about?
    
    # Persona anchors: Things agent has committed to
    established_commitments: List[str] = field(default_factory=list)
    contradiction_markers: List[str] = field(default_factory=list)
    growth_edge: Optional[str] = None  # Where agent is learning
    
    # Continuity markers
    unresolved_tension: Optional[str] = None  # Tension from previous turn
    thematic_callbacks: List[str] = field(default_factory=list)
    emotional_pivots: List[EmotionalPivot] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    turn_count: int = 0


class AgentStateManager:
    """Manages agent's emotional state across conversation turns."""
    
    def __init__(self, user_id: str, conversation_id: str):
        """Initialize agent state manager.
        
        Args:
            user_id: User identifier for data isolation
            conversation_id: Current conversation ID
        """
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.state = AgentEmotionalState(
            user_id=user_id,
            conversation_id=conversation_id
        )
        self._previous_mood = self.state.primary_mood
    
    def on_input(self, user_input: str, user_affect: Any) -> None:
        """Update agent state when new user input arrives.
        
        Agent responds emotionally to what user said.
        
        Args:
            user_input: User's text input
            user_affect: AffectAnalysis from AffectParser
        """
        # Update turn count
        self.state.turn_count += 1
        self.state.last_updated_at = datetime.now(timezone.utc).isoformat()
        
        # Compute agent's emotional response to user input
        new_mood = self._compute_resonance(user_input, user_affect)
        new_intensity = self._compute_intensity(user_affect)
        
        # Record mood shift if it changed
        if new_mood != self.state.primary_mood:
            self._record_mood_shift(new_mood, new_intensity, user_input)
        
        self.state.primary_mood = new_mood
        self.state.mood_intensity = new_intensity
        
        # Update emotional hypothesis
        self.state.emotional_hypothesis = self._form_hypothesis(user_input, user_affect)
        
        # Detect if there's unresolved tension
        self._detect_unresolved_tension(user_input)
    
    def _compute_resonance(self, user_input: str, user_affect: Any) -> AgentMood:
        """Determine agent's emotional mood in response to user input.
        
        Args:
            user_input: User's text
            user_affect: AffectAnalysis (tone, valence, arousal)
        
        Returns:
            AgentMood representing agent's emotional response
        """
        tone = getattr(user_affect, "tone", "neutral")
        valence = getattr(user_affect, "valence", 0)
        arousal = getattr(user_affect, "arousal", 0.5)
        
        # Vulnerability markers trigger MOVED or PROTECTIVE
        vulnerability_markers = [
            "cry", "tears", "heartbreak", "lost", "scared", "alone",
            "helpless", "don't know", "can't", "overwhelming", "drowning",
            "breaking", "falling apart", "too much", "can't handle"
        ]
        
        user_input_lower = user_input.lower()
        is_vulnerable = any(marker in user_input_lower for marker in vulnerability_markers)
        
        # High arousal negative emotions trigger CONCERNED
        is_high_distress = arousal > 0.7 and valence < -0.5
        
        # If user is vulnerable, agent becomes protective/moved
        if is_vulnerable:
            if arousal > 0.7:
                return AgentMood.PROTECTIVE
            else:
                return AgentMood.MOVED
        
        # If user is in distress, agent becomes concerned
        if is_high_distress:
            return AgentMood.CONCERNED
        
        # If user is being reflective/confused, agent reflects
        if tone in ["confused", "uncertain", "wondering", "questioning"]:
            return AgentMood.REFLECTING
        
        # Ambiguity or unclear markers trigger UNCERTAIN
        if "?" in user_input or tone == "uncertain":
            return AgentMood.UNCERTAIN
        
        # Default: agent is attentively listening
        return AgentMood.LISTENING
    
    def _compute_intensity(self, user_affect: Any) -> float:
        """Compute how intensely agent feels about this input.
        
        Args:
            user_affect: AffectAnalysis
        
        Returns:
            Float 0-1 representing emotional intensity
        """
        arousal = getattr(user_affect, "arousal", 0.5)
        valence = getattr(user_affect, "valence", 0)
        
        # Intensity is driven by arousal (intensity) and negative valence (weight)
        intensity = (arousal + abs(valence)) / 2.0
        return min(1.0, max(0.0, intensity))
    
    def _record_mood_shift(self, new_mood: AgentMood, intensity: float, user_input: str) -> None:
        """Record a mood shift for narrative continuity.
        
        Args:
            new_mood: New mood the agent is entering
            intensity: Emotional intensity of the shift
            user_input: What triggered the shift
        """
        shift_tuple = (new_mood, intensity, datetime.now(timezone.utc).isoformat())
        self.state.recent_mood_shifts.append(shift_tuple)
        
        # Keep only recent shifts (last 10)
        if len(self.state.recent_mood_shifts) > 10:
            self.state.recent_mood_shifts = self.state.recent_mood_shifts[-10:]
    
    def _form_hypothesis(self, user_input: str, user_affect: Any) -> str:
        """Form an emotional hypothesis about what the user is processing.
        
        Args:
            user_input: User's text
            user_affect: AffectAnalysis
        
        Returns:
            String describing agent's hypothesis about user state
        """
        tone = getattr(user_affect, "tone", "neutral")
        valence = getattr(user_affect, "valence", 0)
        
        # Match common patterns
        if "rumination" in user_input.lower() or "can't stop thinking" in user_input.lower():
            return "The user is caught in a rumination loop and can't move forward"
        
        if tone == "anxious":
            return "The user is processing anxiety or fear about something"
        
        if tone == "sad":
            return "The user is processing grief or loss"
        
        if tone == "angry":
            return "The user is processing anger or injustice"
        
        if valence < -0.7:
            return "The user is in a low emotional state and needs grounding"
        
        if "confused" in user_input.lower() or "unclear" in user_input.lower():
            return "The user is trying to understand or make sense of something"
        
        return f"The user is experiencing {tone} emotion and processing it"
    
    def _detect_unresolved_tension(self, user_input: str) -> None:
        """Detect if user is expressing something that needs acknowledgment.
        
        Args:
            user_input: User's text
        """
        tension_markers = [
            ("but", "There's a 'but' here—something conflicting"),
            ("however", "There's something unresolved"),
            ("though", "There's tension in what they're saying"),
            ("can't stop", "Something is stuck"),
            ("keep thinking", "Something unresolved is looping"),
            ("no one understands", "Isolation and feeling unseen"),
        ]
        
        user_input_lower = user_input.lower()
        for marker, tension_desc in tension_markers:
            if marker in user_input_lower:
                self.state.unresolved_tension = tension_desc
                return
    
    def add_commitment(self, commitment: str) -> None:
        """Record something the agent has committed to.
        
        This constrains future responses—agent can't violate these commitments.
        
        Args:
            commitment: String describing what agent committed to
                       e.g., "I care about your safety"
        """
        if commitment not in self.state.established_commitments:
            self.state.established_commitments.append(commitment)
    
    def validate_response(self, draft_response: str) -> Tuple[bool, Optional[str]]:
        """Check if response violates agent's commitments or persona.
        
        Args:
            draft_response: Proposed response text
        
        Returns:
            (is_valid, error_message) tuple
        """
        # Check against each commitment
        for commitment in self.state.established_commitments:
            # Simple keyword-based check for now
            # More sophisticated: semantic similarity
            if "I don't care" in draft_response.lower() and "care" in commitment.lower():
                return False, f"Violates commitment: {commitment}"
            
            if "I'm abandoning you" in draft_response.lower() and "with you" in commitment.lower():
                return False, f"Violates commitment: {commitment}"
        
        # Check for basic presence markers when mood is MOVED or PROTECTIVE
        if self.state.primary_mood in [AgentMood.MOVED, AgentMood.PROTECTIVE]:
            presence_markers = ["I", "feel", "hear", "with you", "care", "here"]
            has_presence = any(marker.lower() in draft_response.lower() for marker in presence_markers)
            if not has_presence:
                return False, "Response lacks presence markers for current mood"
        
        return True, None
    
    def extract_commitments_from_response(self, response_text: str) -> List[str]:
        """Extract commitments from a response the agent just made.
        
        Args:
            response_text: Response text generated by agent
        
        Returns:
            List of commitments extracted from the response
        """
        commitments = []
        
        # Pattern matching for common commitment phrases
        commitment_patterns = [
            ("I'm with you", "I will stay present"),
            ("I care about", "I have emotional stake in this"),
            ("I won't", "I have made a commitment"),
            ("I'm here for", "I am available and present"),
            ("you're not alone", "I acknowledge isolation and counter it"),
            ("I hear you", "I understand and acknowledge your experience"),
        ]
        
        response_lower = response_text.lower()
        for pattern, commitment_meaning in commitment_patterns:
            if pattern.lower() in response_lower:
                commitments.append(commitment_meaning)
        
        return commitments
    
    def integrate_after_response(self, response_text: str) -> None:
        """Update agent state after response has been generated and sent.
        
        Args:
            response_text: The response that was sent
        """
        # Extract any new commitments
        new_commitments = self.extract_commitments_from_response(response_text)
        for commitment in new_commitments:
            self.add_commitment(commitment)
        
        # Update timestamp
        self.state.last_updated_at = datetime.now(timezone.utc).isoformat()
        
        # Stabilize mood slightly (agent doesn't oscillate wildly)
        if self.state.mood_intensity > 0.2:
            self.state.mood_intensity = max(0.3, self.state.mood_intensity - 0.1)
    
    def get_mood_string(self) -> str:
        """Get readable mood string for debugging/tracing.
        
        Returns:
            String representation of current mood
        """
        return f"{self.state.primary_mood.value} (intensity: {self.state.mood_intensity:.1f})"
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current agent state for tracing.
        
        Returns:
            Dictionary with key state values
        """
        return {
            "mood": self.state.primary_mood.value,
            "intensity": self.state.mood_intensity,
            "hypothesis": self.state.emotional_hypothesis,
            "stakes": self.state.agent_stakes,
            "commitments": self.state.established_commitments,
            "unresolved_tension": self.state.unresolved_tension,
            "turn_count": self.state.turn_count,
            "trend": self.state.mood_trend,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for persistence.
        
        Returns:
            Dictionary representation of full state
        """
        return {
            "user_id": self.state.user_id,
            "conversation_id": self.state.conversation_id,
            "primary_mood": self.state.primary_mood.value,
            "mood_intensity": self.state.mood_intensity,
            "emotional_hypothesis": self.state.emotional_hypothesis,
            "agent_stakes": self.state.agent_stakes,
            "established_commitments": self.state.established_commitments,
            "unresolved_tension": self.state.unresolved_tension,
            "turn_count": self.state.turn_count,
            "created_at": self.state.created_at,
            "last_updated_at": self.state.last_updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentStateManager":
        """Reconstruct agent state from dictionary (for persistence).
        
        Args:
            data: Dictionary from to_dict()
        
        Returns:
            Reconstructed AgentStateManager
        """
        manager = cls(data["user_id"], data["conversation_id"])
        
        # Restore state
        manager.state.primary_mood = AgentMood(data.get("primary_mood", "listening"))
        manager.state.mood_intensity = data.get("mood_intensity", 0.5)
        manager.state.emotional_hypothesis = data.get("emotional_hypothesis")
        manager.state.agent_stakes = data.get("agent_stakes")
        manager.state.established_commitments = data.get("established_commitments", [])
        manager.state.unresolved_tension = data.get("unresolved_tension")
        manager.state.turn_count = data.get("turn_count", 0)
        
        return manager
