#!/usr/bin/env python3
"""
Conversation Learning Module

Analyzes successful conversations to extract new archetypes or refine existing ones.
This is the "organizer" phase that runs after each conversation to distill
lived dialogue into learnable rules and patterns.

Workflow:
1. User has a good conversation with the system
2. Learning module runs automatically to extract patterns
3. New patterns added to archetype library
4. Next similar conversation uses the newly learned archetype
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from emotional_os.learning.conversation_archetype import (
    get_archetype_library,
    ConversationArchetype,
)


class ConversationLearner:
    """Analyzes conversations to extract learnable patterns."""
    
    def __init__(self):
        """Initialize the learning module."""
        self.library = get_archetype_library()
        
        # Keywords that signal emotional transitions or arcs
        self.emotion_keywords = {
            "relief": ["relief", "finally", "done", "break", "rest", "pause", "quiet"],
            "gratitude": ["grateful", "grateful", "wonderful", "special", "precious", "sweet", "hug"],
            "overwhelm": ["overwhelm", "fragile", "heavy", "drowning", "too much", "breaking"],
            "joy": ["happy", "excited", "joy", "delight", "loved", "celebrate"],
            "grief": ["grief", "loss", "lost", "miss", "sad", "mourning", "sorrow"],
            "complexity": ["but", "mixed", "both", "though", "however", "yet", "complex"],
            "loss": ["divorce", "change", "lost", "gone", "changed", "different", "absence"],
        }
    
    def analyze_conversation(
        self,
        turns: List[Dict[str, str]],
    ) -> Optional[Dict[str, Any]]:
        """Analyze a conversation to extract patterns.
        
        Args:
            turns: List of {"role": "user"|"assistant", "content": "..."} dicts
            
        Returns:
            Extracted pattern dict, or None if no strong pattern detected
        """
        if not turns or len(turns) < 4:  # Need at least 2 user + 2 system turns
            return None
        
        # Extract emotional arc
        emotional_arc = self._extract_emotional_arc(turns)
        if not emotional_arc:
            return None
        
        # Extract entry cues
        first_user_message = next(
            (t["content"] for t in turns if t["role"] == "user"),
            None,
        )
        entry_cues = self._extract_entry_cues(first_user_message or "", emotional_arc)
        
        # Extract response principles
        response_principles = self._extract_response_principles(turns)
        
        # Extract continuity bridges
        continuity_bridges = self._extract_continuity_bridges(turns)
        
        # Extract tone guidelines
        tone_guidelines = self._extract_tone_guidelines(turns)
        
        return {
            "emotional_arc": emotional_arc,
            "entry_cues": entry_cues,
            "response_principles": response_principles,
            "continuity_bridges": continuity_bridges,
            "tone_guidelines": tone_guidelines,
        }
    
    def _extract_emotional_arc(self, turns: List[Dict[str, str]]) -> Optional[str]:
        """Identify the overall emotional journey in the conversation.
        
        Examples: "ReliefToGratitude", "OverwhelmToClarity", "GriefToAcceptance"
        """
        user_messages = [t["content"].lower() for t in turns if t["role"] == "user"]
        
        if not user_messages:
            return None
        
        # Detect starting emotion
        start_emotion = None
        for emotion, keywords in self.emotion_keywords.items():
            if any(kw in user_messages[0] for kw in keywords):
                start_emotion = emotion
                break
        
        # Detect ending emotion (from last user message or system response)
        end_emotion = None
        all_text = " ".join(user_messages).lower()
        
        # Look for transitions
        for emotion, keywords in self.emotion_keywords.items():
            if emotion != start_emotion:
                if any(kw in all_text for kw in keywords):
                    end_emotion = emotion
                    break
        
        if start_emotion and end_emotion and start_emotion != end_emotion:
            return f"{start_emotion.capitalize()}To{end_emotion.capitalize()}"
        
        return start_emotion.capitalize() if start_emotion else None
    
    def _extract_entry_cues(
        self,
        first_user_message: str,
        emotional_arc: str,
    ) -> List[str]:
        """Extract keywords that signal this emotional pattern."""
        if not first_user_message:
            return []
        
        cues = []
        message_lower = first_user_message.lower()
        
        # Extract all emotion keywords found
        for emotion, keywords in self.emotion_keywords.items():
            for kw in keywords:
                if kw in message_lower:
                    cues.append(kw)
        
        # Add some key phrases
        if "child" in message_lower or "hug" in message_lower or "love" in message_lower:
            cues.append("familial_connection")
        
        if "divorce" in message_lower or "change" in message_lower or "loss" in message_lower:
            cues.append("life_change")
        
        return list(set(cues))[:10]  # Return top 10 unique cues
    
    def _extract_response_principles(
        self,
        turns: List[Dict[str, str]],
    ) -> List[str]:
        """Extract principles from how the system responded successfully."""
        principles = []
        
        system_responses = [t["content"] for t in turns if t["role"] == "assistant"]
        user_followups = [turns[i+1]["content"] for i, t in enumerate(turns[:-1]) if t["role"] == "assistant"]
        
        # Check if system validated first
        if system_responses:
            first_response = system_responses[0].lower()
            if any(word in first_response for word in ["hear", "understand", "sound", "real", "valid"]):
                principles.append("Validate emotion first")
        
        # Check if system balanced multiple emotions
        for response in system_responses:
            response_lower = response.lower()
            if any(word in response_lower for word in ["both", "mixed", "and also", "though", "yet"]):
                principles.append("Balance mixed emotions")
        
        # Check if system invited elaboration without prescribing
        for response in system_responses:
            response_lower = response.lower()
            if "?" in response and not any(word in response_lower for word in ["should", "must", "need to", "have to", "do this"]):
                principles.append("Invite elaboration with open questions")
        
        # Check if user deepened after each response
        for followup in user_followups:
            if len(followup.strip()) > 20:  # User wrote more detail
                principles.append("Create space for deeper disclosure")
        
        return list(set(principles))
    
    def _extract_continuity_bridges(
        self,
        turns: List[Dict[str, str]],
    ) -> List[str]:
        """Extract how the system maintained continuity across turns."""
        bridges = []
        
        system_responses = [t["content"] for t in turns if t["role"] == "assistant"]
        
        for response in system_responses:
            response_lower = response.lower()
            
            # Check for references to prior context
            if any(word in response_lower for word in ["yesterday", "before", "earlier", "prior", "when you", "sounds like"]):
                bridges.append("Reference prior emotional state")
            
            # Check for theme carrying
            if any(word in response_lower for word in ["that", "this", "these", "what you said", "consistency"]):
                bridges.append("Carry forward key themes")
            
            # Check for proportional connection
            if "overwhelm" in response_lower or "holding" in response_lower:
                bridges.append("Connect current moment to prior load")
        
        return list(set(bridges))
    
    def _extract_tone_guidelines(
        self,
        turns: List[Dict[str, str]],
    ) -> List[str]:
        """Extract style and tone patterns from successful responses."""
        guidelines = []
        
        system_responses = [t["content"] for t in turns if t["role"] == "assistant"]
        
        for response in system_responses:
            response_lower = response.lower()
            
            # Check for warm language
            if any(word in response_lower for word in ["wonderful", "special", "precious", "real", "matters"]):
                guidelines.append("Use warm, embracing language")
            
            # Check for metaphor/poetic language
            if any(word in response_lower for word in ["felt", "melted", "silence", "deafening", "tapestry", "vivid"]):
                guidelines.append("Mirror user's metaphorical language")
            
            # Check for proportional (not overblown) empathy
            short_response = len(response.split()) < 25
            if short_response and "?" in response:
                guidelines.append("Gentle pacing — validate then pause")
            
            # Check for empathetic reflection
            if any(phrase in response_lower for phrase in ["i see", "i hear", "sounds like", "makes sense"]):
                guidelines.append("Reflect feelings back empathetically")
        
        return list(set(guidelines))
    
    def create_archetype_from_analysis(
        self,
        analysis: Dict[str, Any],
        name: Optional[str] = None,
    ) -> Optional[ConversationArchetype]:
        """Convert extracted analysis into a new archetype.
        
        Args:
            analysis: Output from analyze_conversation()
            name: Optional custom name; otherwise derived from emotional arc
            
        Returns:
            New ConversationArchetype ready to add to library
        """
        if not analysis:
            return None
        
        archetype_name = name or analysis.get("emotional_arc", "UnnamedPattern")
        
        archetype = ConversationArchetype(
            name=archetype_name,
            entry_cues=analysis.get("entry_cues", []),
            response_principles=analysis.get("response_principles", []),
            continuity_bridges=analysis.get("continuity_bridges", []),
            tone_guidelines=analysis.get("tone_guidelines", []),
            pattern_template=f"Pattern learned from {archetype_name} arc",
            success_weight=1.0,
        )
        
        return archetype
    
    def learn_from_conversation(
        self,
        turns: List[Dict[str, str]],
        user_rating: Optional[float] = None,
    ) -> Optional[str]:
        """End-to-end: analyze conversation and add to library if strong pattern.
        
        Args:
            turns: Conversation turns
            user_rating: Optional user feedback (0-1, higher = better)
            
        Returns:
            Name of new/updated archetype, or None if no pattern learned
        """
        analysis = self.analyze_conversation(turns)
        if not analysis:
            return None
        
        archetype = self.create_archetype_from_analysis(analysis)
        if not archetype:
            return None
        
        # Check if archetype already exists
        if archetype.name in self.library.archetypes:
            # Merge principles with existing
            existing = self.library.archetypes[archetype.name]
            existing.entry_cues = list(set(existing.entry_cues + archetype.entry_cues))
            existing.response_principles = list(set(existing.response_principles + archetype.response_principles))
            existing.continuity_bridges = list(set(existing.continuity_bridges + archetype.continuity_bridges))
            existing.tone_guidelines = list(set(existing.tone_guidelines + archetype.tone_guidelines))
            
            # Update success weight if user provided rating
            if user_rating is not None:
                existing.record_usage(success=user_rating > 0.6)
        else:
            # Add new archetype
            if user_rating is not None:
                archetype.record_usage(success=user_rating > 0.6)
            self.library.add_archetype(archetype)
        
        return archetype.name


# Singleton instance
_learner: Optional[ConversationLearner] = None


def get_conversation_learner() -> ConversationLearner:
    """Get or create the global conversation learner."""
    global _learner
    if _learner is None:
        _learner = ConversationLearner()
    return _learner
