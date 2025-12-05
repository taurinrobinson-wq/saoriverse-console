"""
Conversation Memory Layer

Tracks the evolving emotional state across multiple user messages.
Integrates new information with prior context to build a coherent understanding.

Key principles:
1. Each message adds information
2. Information is integrated, not replaced
3. Glyphs evolve as understanding deepens
4. Causal chains are built from multiple inputs
5. Confidence levels track what we know vs. what's missing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


class ConfidenceLevel(Enum):
    """Confidence that system understands this aspect of user's state"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.85


@dataclass
class SemanticParsing:
    """Extracted semantic elements from a user message"""
    actor: str
    primary_affects: List[str]
    secondary_affects: List[str] = field(default_factory=list)
    tense: str = ""
    emphasis: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    temporal_scope: Optional[str] = None
    thought_patterns: List[str] = field(default_factory=list)
    action_capacity: Optional[str] = None
    raw_input: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MessageTurn:
    """Single message in conversation with analysis"""
    turn_number: int
    user_input: str
    timestamp: str
    parsed: SemanticParsing
    glyphs_identified: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)
    clarifications_asked: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "turn_number": self.turn_number,
            "user_input": self.user_input,
            "timestamp": self.timestamp,
            "parsed": self.parsed.to_dict(),
            "glyphs_identified": self.glyphs_identified,
            "missing_elements": self.missing_elements,
            "clarifications_asked": self.clarifications_asked,
        }


@dataclass
class IntegratedEmotionalState:
    """Combined understanding of user's emotional state across all messages"""
    primary_affects: List[str]
    secondary_affects: List[str] = field(default_factory=list)
    intensity: str = "medium"  # low, medium, high
    primary_domains: List[str] = field(default_factory=list)
    temporal_scope: str = "unknown"
    thought_patterns: List[str] = field(default_factory=list)
    action_capacity: str = "unknown"
    confidence: float = 0.5
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CausalUnderstanding:
    """Understanding of the causal chain in user's situation"""
    root_triggers: List[str] = field(default_factory=list)
    mechanisms: List[str] = field(default_factory=list)  # HOW stress manifests
    manifestations: List[str] = field(default_factory=list)  # WHAT stress causes
    agency_state: str = "unknown"
    contributing_factors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SystemKnowledge:
    """What the system has learned and still needs to know"""
    confirmed_facts: List[str] = field(default_factory=list)
    high_confidence_needs: List[str] = field(default_factory=list)
    low_confidence_needs: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ConversationMemory:
    """Manages conversation history and integrated understanding"""
    
    def __init__(self):
        self.turns: List[MessageTurn] = []
        self.integrated_state: Optional[IntegratedEmotionalState] = None
        self.causal_understanding: Optional[CausalUnderstanding] = None
        self.system_knowledge: Optional[SystemKnowledge] = None
        self.glyph_evolution: List[List[str]] = []  # Track glyph changes per turn
        
    def add_turn(
        self, 
        user_input: str,
        parsed: SemanticParsing,
        glyphs_identified: List[str],
        missing_elements: List[str],
        clarifications_asked: List[str],
    ) -> MessageTurn:
        """Add a new message turn to memory and integrate it"""
        turn = MessageTurn(
            turn_number=len(self.turns) + 1,
            user_input=user_input,
            timestamp=datetime.now().isoformat(),
            parsed=parsed,
            glyphs_identified=glyphs_identified,
            missing_elements=missing_elements,
            clarifications_asked=clarifications_asked,
        )
        self.turns.append(turn)
        self.glyph_evolution.append(glyphs_identified)
        self._integrate_new_information(turn)
        return turn
    
    def _integrate_new_information(self, turn: MessageTurn) -> None:
        """Integrate new turn into overall understanding"""
        if len(self.turns) == 1:
            # First message - initialize states
            self._initialize_from_first_turn(turn)
        else:
            # Subsequent message - enrich existing understanding
            self._enrich_from_new_turn(turn)
    
    def _initialize_from_first_turn(self, turn: MessageTurn) -> None:
        """Set up initial integrated state from first message"""
        self.integrated_state = IntegratedEmotionalState(
            primary_affects=turn.parsed.primary_affects,
            secondary_affects=turn.parsed.secondary_affects,
            intensity="medium",
            primary_domains=turn.parsed.domains,
            temporal_scope=turn.parsed.temporal_scope or "unknown",
            thought_patterns=turn.parsed.thought_patterns,
            action_capacity=turn.parsed.action_capacity or "unknown",
            confidence=0.7,
        )
        
        self.causal_understanding = CausalUnderstanding(
            root_triggers=[],
            mechanisms=[],
            manifestations=[],
            agency_state=turn.parsed.action_capacity or "unknown",
        )
        
        self.system_knowledge = SystemKnowledge(
            confirmed_facts=[
                f"User experiencing: {', '.join(turn.parsed.primary_affects)}"
            ],
            high_confidence_needs=[
                "What triggered this emotional state?",
                "How does this manifest in their body/mind?",
                "What have they tried to address it?",
            ],
            assumptions=[
                f"Temporal scope: {turn.parsed.temporal_scope}"
            ],
        )
    
    def _enrich_from_new_turn(self, turn: MessageTurn) -> None:
        """Update integrated state with new information"""
        if not self.integrated_state or not self.causal_understanding or not self.system_knowledge:
            return
        
        # Add new affects, avoiding duplicates
        for affect in turn.parsed.primary_affects:
            if affect not in self.integrated_state.primary_affects:
                self.integrated_state.primary_affects.append(affect)
        
        for affect in turn.parsed.secondary_affects:
            if affect not in self.integrated_state.secondary_affects:
                self.integrated_state.secondary_affects.append(affect)
        
        # Add new domains
        for domain in turn.parsed.domains:
            if domain not in self.integrated_state.primary_domains:
                self.integrated_state.primary_domains.append(domain)
        
        # Add thought patterns
        for pattern in turn.parsed.thought_patterns:
            if pattern not in self.integrated_state.thought_patterns:
                self.integrated_state.thought_patterns.append(pattern)
        
        # Update action capacity if new information
        if turn.parsed.action_capacity and turn.parsed.action_capacity != "unknown":
            self.integrated_state.action_capacity = turn.parsed.action_capacity
        
        # Increase confidence with additional information
        self.integrated_state.confidence = min(0.95, self.integrated_state.confidence + 0.15)
        
        # Extract causal information from this turn
        self._extract_causal_chains(turn)
        
        # Update system knowledge
        self._update_system_knowledge(turn)
    
    def _extract_causal_chains(self, turn: MessageTurn) -> None:
        """Extract causal understanding from message"""
        if not self.causal_understanding:
            return
        
        # Analyze domains as potential triggers
        for domain in turn.parsed.domains:
            if domain not in self.causal_understanding.root_triggers:
                self.causal_understanding.root_triggers.append(domain)
        
        # Thought patterns as mechanisms
        for pattern in turn.parsed.thought_patterns:
            if "flooding" in pattern.lower() or "racing" in pattern.lower():
                if "cognitive flooding" not in self.causal_understanding.mechanisms:
                    self.causal_understanding.mechanisms.append("cognitive flooding")
            
            if "fragmentation" in pattern.lower():
                if "fragmented thinking" not in self.causal_understanding.mechanisms:
                    self.causal_understanding.mechanisms.append("fragmented thinking")
        
        # Secondary affects as manifestations
        for affect in turn.parsed.secondary_affects:
            if affect not in self.causal_understanding.manifestations:
                self.causal_understanding.manifestations.append(affect)
        
        # Update agency state
        if turn.parsed.action_capacity and turn.parsed.action_capacity != "unknown":
            self.causal_understanding.agency_state = turn.parsed.action_capacity
    
    def _update_system_knowledge(self, turn: MessageTurn) -> None:
        """Update what we know and what we need to know"""
        if not self.system_knowledge:
            return
        
        # Add confirmed facts from new turn
        new_facts = [
            f"Domain: {', '.join(turn.parsed.domains)}" if turn.parsed.domains else None,
            f"Thought patterns: {', '.join(turn.parsed.thought_patterns)}" if turn.parsed.thought_patterns else None,
            f"Action capacity: {turn.parsed.action_capacity}" if turn.parsed.action_capacity else None,
        ]
        
        for fact in new_facts:
            if fact and fact not in self.system_knowledge.confirmed_facts:
                self.system_knowledge.confirmed_facts.append(fact)
        
        # Update high-confidence needs based on what's still missing
        self.system_knowledge.high_confidence_needs = turn.missing_elements.copy()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get comprehensive conversation summary"""
        return {
            "turn_count": len(self.turns),
            "turns": [turn.to_dict() for turn in self.turns],
            "integrated_state": self.integrated_state.to_dict() if self.integrated_state else None,
            "causal_understanding": self.causal_understanding.to_dict() if self.causal_understanding else None,
            "system_knowledge": self.system_knowledge.to_dict() if self.system_knowledge else None,
            "glyph_evolution": self.glyph_evolution,
        }
    
    def get_glyph_set(self) -> List[str]:
        """Get the current evolved glyph set"""
        if not self.glyph_evolution:
            return []
        # Return all unique glyphs seen across conversation
        return list(set(glyph for glyphs in self.glyph_evolution for glyph in glyphs))
    
    def get_emotional_profile_brief(self) -> str:
        """Get a brief text summary of emotional profile"""
        if not self.integrated_state:
            return "Unknown emotional state"
        
        affects = ", ".join(self.integrated_state.primary_affects)
        domains = f" (in {', '.join(self.integrated_state.primary_domains)})" if self.integrated_state.primary_domains else ""
        intensity_word = self.integrated_state.intensity.upper()
        
        return f"{intensity_word}: {affects}{domains}"
    
    def get_next_clarifications(self) -> List[str]:
        """Get the most important clarifications to ask"""
        if not self.system_knowledge:
            return []
        
        # Return top 3 high-confidence needs
        return self.system_knowledge.high_confidence_needs[:3]
    
    def get_causal_narrative(self) -> str:
        """Get human-readable explanation of the causal chain"""
        if not self.causal_understanding:
            return "Unknown causal chain"
        
        parts = []
        
        if self.causal_understanding.root_triggers:
            parts.append(f"Trigger: {', '.join(self.causal_understanding.root_triggers)}")
        
        if self.causal_understanding.mechanisms:
            parts.append(f"Mechanism: {', '.join(self.causal_understanding.mechanisms)}")
        
        if self.causal_understanding.manifestations:
            parts.append(f"Manifestation: {', '.join(self.causal_understanding.manifestations)}")
        
        if self.causal_understanding.agency_state:
            parts.append(f"Agency: {self.causal_understanding.agency_state}")
        
        return " -> ".join(parts)
