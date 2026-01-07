"""Narrative Continuity Hooks Manager (Phase 3).

Tracks emotional pivots and weaves narrative callbacks into responses.
This creates conversational continuity by:

1. Extracting commitments from agent responses
2. Storing emotionally significant moments
3. Referencing past tension and insights naturally in future responses

Goal: Transform the conversation from episodic to narrative arc.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import re


class NarrativeHookManager:
    """Manages narrative continuity through emotional callbacks."""
    
    def __init__(self, user_id: str, conversation_id: str):
        """Initialize narrative hook manager.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation ID
        """
        self.user_id = user_id
        self.conversation_id = conversation_id
        
        # Store emotional pivots (moments of significance)
        self.pivots: List[Dict[str, Any]] = []
        
        # Track callbacks that have been woven (avoid repetition)
        self.woven_callbacks: List[str] = []
        
        # Commitment phrases to track
        self.commitment_patterns = [
            (r"I['\"]?m with you", "presence commitment"),
            (r"I['\"]?m here", "availability commitment"),
            (r"I care about", "emotional stake"),
            (r"I won['\"]?t(?:\s+forget|let)", "memory commitment"),
            (r"you['\"]?re not alone", "solidarity commitment"),
            (r"I hear you", "acknowledgment commitment"),
            (r"I understand", "comprehension commitment"),
            (r"I see you", "recognition commitment"),
            (r"I believe", "faith commitment"),
        ]
        
        # Callback patterns (ways to reference past moments)
        self.callback_triggers = {
            "unresolved": "When you mentioned {moment}, there was something unresolved. I've been thinking about it.",
            "escalation": "You seemed lighter when we talked about {moment}. This feels different now.",
            "pattern": "Just like last time with {moment}, I'm noticing something similar here.",
            "growth": "You've grown since {moment}. I can feel that shift.",
            "echo": "This reminds me of {moment}, but you're handling it differently.",
        }
    
    def extract_commitments(self, response_text: str) -> List[str]:
        """Extract commitments from a response.
        
        Args:
            response_text: Text of agent response
        
        Returns:
            List of commitment descriptions found
        """
        commitments = []
        response_lower = response_text.lower()
        
        for pattern, commitment_type in self.commitment_patterns:
            if re.search(pattern, response_lower, re.IGNORECASE):
                commitments.append(commitment_type)
        
        return commitments
    
    def record_emotional_pivot(
        self,
        turn_number: int,
        user_input: str,
        agent_mood_shift: Dict[str, str],
        response_text: str,
        significance: float = 0.5,
    ) -> None:
        """Record an emotionally significant moment.
        
        Args:
            turn_number: Turn number in conversation
            user_input: What user said
            agent_mood_shift: {"from": mood, "to": mood} indicating shift
            response_text: What agent responded
            significance: 0-1, how significant this moment is
        """
        pivot = {
            "turn": turn_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_input": user_input[:100],  # Store summary
            "mood_shift": agent_mood_shift,
            "response": response_text[:100],
            "significance": significance,
            "commitments": self.extract_commitments(response_text),
        }
        
        self.pivots.append(pivot)
    
    def get_unresolved_tension(self) -> Optional[str]:
        """Get the most recent unresolved tension from pivots.
        
        Returns:
            Description of tension or None
        """
        # Look for pivots that ended with uncertainty or care
        for pivot in reversed(self.pivots):
            mood = pivot["mood_shift"].get("to", "")
            if mood in ["concerned", "uncertain", "moved"]:
                return pivot["user_input"]
        
        return None
    
    def weave_callback(
        self,
        draft_response: str,
        unresolved_from_previous: Optional[str] = None,
    ) -> str:
        """Weave narrative callbacks naturally into response.
        
        Args:
            draft_response: The proposed response before callback injection
            unresolved_from_previous: Previous unresolved tension (if any)
        
        Returns:
            Response with callbacks woven in
        """
        if not self.pivots:
            return draft_response
        
        # If there's unresolved tension, reference it
        if unresolved_from_previous and len(draft_response) > 20:
            # Add callback before main response
            callback = self._generate_callback(unresolved_from_previous, "unresolved")
            if callback:
                # Insert callback at the start
                return f"{callback} {draft_response}"
        
        # Check for patterns that connect to previous turns
        callback = self._check_for_pattern_callback(draft_response)
        if callback:
            # Insert after first sentence
            sentences = draft_response.split(". ")
            if len(sentences) > 1:
                return f"{sentences[0]}. {callback} {'. '.join(sentences[1:])}"
        
        return draft_response
    
    def _generate_callback(self, moment: str, callback_type: str) -> Optional[str]:
        """Generate a callback reference to a past moment.
        
        Args:
            moment: The past moment to reference
            callback_type: Type of callback ("unresolved", "escalation", etc.)
        
        Returns:
            Callback text or None
        """
        if callback_type not in self.callback_triggers:
            callback_type = "unresolved"
        
        template = self.callback_triggers[callback_type]
        
        # Avoid repeating callbacks
        callback = template.format(moment=moment[:50])
        if callback in self.woven_callbacks:
            return None
        
        self.woven_callbacks.append(callback)
        return callback
    
    def _check_for_pattern_callback(self, current_response: str) -> Optional[str]:
        """Check if current response triggers pattern recognition callback.
        
        Args:
            current_response: Current response text
        
        Returns:
            Pattern callback text or None
        """
        # If we have multiple similar pivots, note the pattern
        if len(self.pivots) < 2:
            return None
        
        # Check for recurring themes in recent pivots
        recent_pivots = self.pivots[-3:]
        moods = [p["mood_shift"].get("to", "") for p in recent_pivots]
        
        # If same mood keeps appearing, it's a pattern
        if len(set(moods)) == 1 and moods[0] != "listening":
            pattern_mood = moods[0]
            earlier_pivot = recent_pivots[0]
            
            callback = f"I'm noticing we keep returning to {pattern_mood}. Like when you said '{earlier_pivot['user_input']}'."
            if callback not in self.woven_callbacks:
                self.woven_callbacks.append(callback)
                return callback
        
        return None
    
    def create_summary_for_next_session(self) -> Dict[str, Any]:
        """Create a summary of key narrative points for next session.
        
        Returns:
            Dictionary with key moments and patterns
        """
        if not self.pivots:
            return {"status": "no_pivots"}
        
        significant_pivots = [p for p in self.pivots if p["significance"] > 0.6]
        
        # Get most common mood shifts
        mood_shifts = {}
        for pivot in self.pivots:
            shift_key = f"{pivot['mood_shift'].get('from', '')} → {pivot['mood_shift'].get('to', '')}"
            mood_shifts[shift_key] = mood_shifts.get(shift_key, 0) + 1
        
        return {
            "total_turns": len(self.pivots),
            "significant_moments": [
                {
                    "turn": p["turn"],
                    "input": p["user_input"],
                    "commitments": p["commitments"],
                }
                for p in significant_pivots[:5]
            ],
            "common_mood_shifts": sorted(
                mood_shifts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3],
            "last_unresolved": self.get_unresolved_tension(),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence.
        
        Returns:
            Dictionary representation
        """
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "pivots": self.pivots,
            "woven_callbacks": self.woven_callbacks,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NarrativeHookManager":
        """Reconstruct from dictionary.
        
        Args:
            data: Dictionary from to_dict()
        
        Returns:
            Reconstructed manager
        """
        manager = cls(data["user_id"], data["conversation_id"])
        manager.pivots = data.get("pivots", [])
        manager.woven_callbacks = data.get("woven_callbacks", [])
        return manager


# Helper functions for integration

def extract_commitments_from_response(response_text: str) -> List[str]:
    """Module-level function to extract commitments.
    
    Args:
        response_text: Response to analyze
    
    Returns:
        List of commitment types found
    """
    manager = NarrativeHookManager("", "")
    return manager.extract_commitments(response_text)


def generate_callback_for_tension(tension: str, moment_description: str) -> str:
    """Module-level function to generate callback.
    
    Args:
        tension: Type of tension
        moment_description: Description of the moment
    
    Returns:
        Callback text
    """
    manager = NarrativeHookManager("", "")
    callback = manager._generate_callback(moment_description, "unresolved")
    return callback or "I'm thinking about what you shared earlier."
