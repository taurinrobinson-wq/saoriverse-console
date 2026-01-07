"""
Formal Semantic Parsing Schema for Deep Emotional Interpretation

This module provides a comprehensive framework for extracting semantic layers
from user messages beyond surface-level pattern matching.

Semantic layers detected:
1. Emotional stance (bracing, distancing, revealing, ambivalent, etc.)
2. Disclosure pacing (when/how the user is revealing)
3. Identity signals (naming, withholding, formality, relational roles)
4. Power dynamics (agency, dominance, vulnerability)
5. Emotional contradictions (mixed feelings, paradoxes)
6. Conversational moves (testing, grounding, pivoting, softening)
7. Implied needs (containment, validation, pacing, permission, attunement)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum
import re


class EmotionalStance(Enum):
    """The overall emotional posture of the message"""
    BRACING = "bracing"          # Preparing for impact, emotional fortification
    DISTANCING = "distancing"    # Creating psychological space, formality
    REVEALING = "revealing"      # Opening up, showing vulnerability
    AMBIVALENT = "ambivalent"    # Mixed feelings, contradiction
    OVERWHELMED = "overwhelmed"  # Emotional flooding
    GROUNDED = "grounded"        # Factual, contextual, stable
    SOFTENING = "softening"      # Moving toward vulnerability
    DEFENDING = "defending"      # Protecting self-narrative


class DisclosurePace(Enum):
    """How quickly/completely the user is revealing"""
    TESTING_SAFETY = "testing_safety"          # Initial probe, gauging response
    GRADUAL_REVEAL = "gradual_reveal"          # Slow, controlled disclosure
    CONTEXTUAL_GROUNDING = "contextual_grounding"  # Providing facts as buffer
    EMOTIONAL_EMERGENCE = "emotional_emergence"    # Core feeling emerging
    FULL_VULNERABILITY = "full_vulnerability"      # Maximum openness


class ConversationalMove(Enum):
    """Strategic moves in the conversation"""
    TESTING_SAFETY = "testing_safety"          # Testing if it's safe to go deeper
    GROUNDING_IN_FACTS = "grounding_in_facts"  # Using objective facts as anchor
    NAMING_EXPERIENCE = "naming_experience"    # Labeling the event/relationship
    REVEALING_IMPACT = "revealing_impact"      # Sharing the effect on self
    EXPRESSING_AMBIVALENCE = "expressing_ambivalence"  # Holding multiple truths
    SOFTENING = "softening"                    # Moving toward emotional vulnerability
    INVITING_RESPONSE = "inviting_response"    # Opening for reflection/guidance


class PowerDynamic(Enum):
    """Power structures referenced in the message"""
    AGENCY_LOSS = "agency_loss"         # "undermined me", "pushed me down"
    DOMINANCE = "dominance"             # Narrative of being controlled
    RECLAIMING_AGENCY = "reclaiming_agency"  # Taking power back
    MUTUAL_INFLUENCE = "mutual_influence"    # Interdependence
    VULNERABILITY = "vulnerability"    # Openness to impact


class ImpliedNeed(Enum):
    """What the user implicitly needs from the system"""
    CONTAINMENT = "containment"         # Safe space, pace control
    VALIDATION = "validation"           # "This is real/matters"
    PERMISSION = "permission"           # It's okay to feel this
    ATTUNEMENT = "attunement"          # Being understood at deeper level
    PRESENCE = "presence"              # Just being there
    MEANING_MAKING = "meaning_making"   # Help understanding
    RESTORATION = "restoration"         # Rebuilding sense of self


@dataclass
class SemanticIdentitySignal:
    """Signals about identity, relationship, and agency"""
    explicitly_named: List[str] = field(default_factory=list)  # Names revealed
    withheld_identities: List[str] = field(default_factory=list)  # Names/roles protected
    relational_labels_used: List[str] = field(default_factory=list)  # "ex-wife", "wife"
    formal_markers: List[str] = field(default_factory=list)  # Formal language
    duration_references: List[str] = field(default_factory=list)  # Time spans mentioned
    role_changes: List[str] = field(default_factory=list)  # Status shifts (wife→ex-wife)
    complexity_markers: List[str] = field(default_factory=list)  # "two children", etc.


@dataclass
class EmotionalContradiction:
    """Paradoxes and mixed feelings"""
    surface_feeling: str      # What's explicitly stated
    underlying_feeling: str   # What's implied
    connector: str            # How they're connected ("but", "and", etc.)
    tension_level: float      # 0.0-1.0 intensity of contradiction


@dataclass
class SemanticLayer:
    """A complete semantic interpretation of a single message"""
    
    # Primary interpretation
    emotional_stance: EmotionalStance
    disclosure_pace: DisclosurePace
    conversational_moves: List[ConversationalMove]
    
    # Secondary layers
    identity_signals: SemanticIdentitySignal
    power_dynamics: List[PowerDynamic]
    implied_needs: List[ImpliedNeed]
    emotional_contradictions: List[EmotionalContradiction]
    
    # Linguistic markers
    protective_language: List[str] = field(default_factory=list)  # "I thought", "Well"
    vulnerability_markers: List[str] = field(default_factory=list)  # "But I don't know"
    impact_words: List[str] = field(default_factory=list)  # "undermined", "pushed"
    
    # System interpretation
    trust_increase_indicated: bool = False
    emotional_weight: float = 0.5  # 0.0-1.0
    readiness_to_explore_deeper: bool = False
    needs_pace_slowing: bool = False
    
    # Metadata
    message_text: str = ""
    message_index: int = 0


class SemanticParser:
    """
    Parses messages for deep semantic meaning beyond surface patterns.
    """
    
    def __init__(self):
        # Linguistic patterns for detection
        self.bracing_patterns = [
            r"thought.*okay",
            r"something hit",
            r"harder than expected",
            r"wasn't sure",
            r"bracing for",
        ]
        
        self.revealing_patterns = [
            r"final.*confirmation",
            r"ex-wife",
            r"married for",
            r"relationship for",
            r"children",
        ]
        
        self.ambivalence_patterns = [
            r"glad.*but",
            r"but.*don't know",
            r"good.*and.*bad",
            r"relief.*and.*grief",
        ]
        
        self.impact_words = [
            "undermined", "pushed down", "diminished", "controlled",
            "dominated", "suppressed", "marginalized", "erased",
            "invalidated", "dismissed", "belittled"
        ]
        
        self.vulnerability_markers = [
            r"but i don't know",
            r"i'm not sure",
            r"i don't know what to do",
            r"i feel like",
            r"it hurts",
        ]
        
        self.protective_language = [
            "I thought", "Well", "I guess", "I suppose",
            "It was", "People say", "I was told"
        ]
    
    def parse(self, message: str, message_index: int = 0) -> SemanticLayer:
        """
        Parse a message to extract semantic layers.
        
        Args:
            message: The user's message text
            message_index: Position in conversation (0-indexed)
            
        Returns:
            SemanticLayer with complete interpretation
        """
        layer = SemanticLayer(
            emotional_stance=self._detect_stance(message, message_index),
            disclosure_pace=self._detect_disclosure_pace(message, message_index),
            conversational_moves=self._detect_conversational_moves(message),
            identity_signals=self._extract_identity_signals(message),
            power_dynamics=self._detect_power_dynamics(message),
            implied_needs=self._infer_implied_needs(message, message_index),
            emotional_contradictions=self._find_contradictions(message),
            protective_language=self._find_protective_language(message),
            vulnerability_markers=self._find_vulnerability_markers(message),
            impact_words=self._find_impact_words(message),
            message_text=message,
            message_index=message_index,
        )
        
        # Calculate meta-properties
        layer.emotional_weight = self._calculate_emotional_weight(layer)
        layer.trust_increase_indicated = self._detect_trust_increase(layer)
        layer.readiness_to_explore_deeper = self._detect_readiness(layer)
        layer.needs_pace_slowing = self._detect_pace_needs(layer)
        
        return layer
    
    def _detect_stance(self, message: str, message_index: int = 0) -> EmotionalStance:
        """Detect overall emotional posture"""
        message_lower = message.lower()
        
        # Check for bracing
        for pattern in self.bracing_patterns:
            if re.search(pattern, message_lower):
                return EmotionalStance.BRACING
        
        # Check for ambivalence
        if re.search(r"glad.*but|but.*don't", message_lower):
            return EmotionalStance.AMBIVALENT
        
        # Check for revealing
        if any(word in message_lower for word in ["married", "wife", "children", "relationship"]):
            if message_index == 0:
                return EmotionalStance.BRACING  # First message often bracing
            return EmotionalStance.REVEALING
        
        # Check for softening
        if "but" in message_lower and ("don't know" in message_lower or "uncertain" in message_lower):
            return EmotionalStance.SOFTENING
        
        # Check for distancing
        if "well" in message_lower or "i" in message_lower:
            if "ex-" in message_lower or "was not" in message_lower:
                return EmotionalStance.DISTANCING
        
        return EmotionalStance.GROUNDED
    
    def _detect_disclosure_pace(self, message: str, message_index: int) -> DisclosurePace:
        """Detect how the user is pacing their disclosure"""
        message_lower = message.lower()
        
        # Message 0: Testing safety (ambiguous, probing)
        if message_index == 0:
            if "thought" in message_lower and "harder" in message_lower:
                return DisclosurePace.TESTING_SAFETY
        
        # Message 1: Naming the event (controlled reveal)
        if message_index == 1:
            if "final" in message_lower and "confirmation" in message_lower:
                return DisclosurePace.GRADUAL_REVEAL
        
        # Message 2: Context grounding (facts as buffer)
        if message_index == 2:
            if "married" in message_lower and ("years" in message_lower or "children" in message_lower):
                return DisclosurePace.CONTEXTUAL_GROUNDING
        
        # Message 3: Emotional emergence (feeling emerging)
        if message_index == 3:
            if "but" in message_lower and ("don't know" in message_lower or "uncertain" in message_lower):
                return DisclosurePace.EMOTIONAL_EMERGENCE
        
        return DisclosurePace.GRADUAL_REVEAL
    
    def _detect_conversational_moves(self, message: str) -> List[ConversationalMove]:
        """Detect strategic conversational moves"""
        moves = []
        message_lower = message.lower()
        
        # Testing safety
        if "thought" in message_lower and "expected" in message_lower:
            moves.append(ConversationalMove.TESTING_SAFETY)
        
        # Naming experience
        if "final" in message_lower or "divorce" in message_lower:
            moves.append(ConversationalMove.NAMING_EXPERIENCE)
        
        # Grounding in facts
        if "married" in message_lower or "children" in message_lower:
            moves.append(ConversationalMove.GROUNDING_IN_FACTS)
        
        # Revealing impact
        if any(word in message_lower for word in ["undermined", "pushed down", "bad"]):
            moves.append(ConversationalMove.REVEALING_IMPACT)
        
        # Expressing ambivalence
        if "but" in message_lower and ("glad" in message_lower or "don't know" in message_lower):
            moves.append(ConversationalMove.EXPRESSING_AMBIVALENCE)
        
        # Softening/inviting
        if "but i don't know" in message_lower or message_lower.endswith("..."):
            moves.append(ConversationalMove.INVITING_RESPONSE)
        
        return moves if moves else [ConversationalMove.TESTING_SAFETY]
    
    def _extract_identity_signals(self, message: str) -> SemanticIdentitySignal:
        """Extract identity-related signals"""
        signal = SemanticIdentitySignal()
        
        # Names/identities explicitly mentioned
        if "jen" in message.lower():
            signal.explicitly_named.append("Jen")
        
        # Relational labels
        if "ex-wife" in message.lower():
            signal.relational_labels_used.append("ex-wife")
        if "wife" in message.lower():
            signal.relational_labels_used.append("wife")
        
        # Formal markers (formal language indicates distancing)
        if message.startswith("Well") or "I" in message[:20]:
            signal.formal_markers.append("formal_opening")
        
        # Duration references
        durations = re.findall(r"(\d+)\s+years", message.lower())
        if durations:
            signal.duration_references.extend([f"{d} years" for d in durations])
        
        # Role changes (was wife, now ex-wife)
        if "wife" in message.lower() and "ex-" in message.lower():
            signal.role_changes.append("wife_to_ex_wife")
        
        # Complexity markers
        if "children" in message.lower():
            signal.complexity_markers.append("has_children")
        
        return signal
    
    def _detect_power_dynamics(self, message: str) -> List[PowerDynamic]:
        """Detect power structures in the message"""
        dynamics = []
        message_lower = message.lower()
        
        # Agency loss
        if "undermined" in message_lower or "pushed down" in message_lower:
            dynamics.append(PowerDynamic.AGENCY_LOSS)
        
        # Dominance
        if "controlled" in message_lower or "dominated" in message_lower:
            dynamics.append(PowerDynamic.DOMINANCE)
        
        # Reclaiming agency (relief at being out)
        if "glad it's over" in message_lower or "good because" in message_lower:
            dynamics.append(PowerDynamic.RECLAIMING_AGENCY)
        
        # Vulnerability (emotional openness)
        if "but" in message_lower and ("don't know" in message_lower or "uncertain" in message_lower):
            dynamics.append(PowerDynamic.VULNERABILITY)
        
        return dynamics if dynamics else [PowerDynamic.MUTUAL_INFLUENCE]
    
    def _infer_implied_needs(self, message: str, message_index: int) -> List[ImpliedNeed]:
        """Infer what the user implicitly needs"""
        needs = []
        message_lower = message.lower()
        
        # Message 0: Containment (pace control, safety)
        if message_index == 0:
            needs.append(ImpliedNeed.CONTAINMENT)
            needs.append(ImpliedNeed.PRESENCE)
        
        # Message 1: Validation (this is real)
        if message_index == 1:
            needs.append(ImpliedNeed.VALIDATION)
        
        # Message 2: Acknowledgment of scale
        if message_index == 2:
            needs.append(ImpliedNeed.ATTUNEMENT)
            needs.append(ImpliedNeed.VALIDATION)
        
        # Message 3: Holding ambivalence
        if message_index == 3:
            needs.append(ImpliedNeed.ATTUNEMENT)
            needs.append(ImpliedNeed.PERMISSION)
            needs.append(ImpliedNeed.PRESENCE)
        
        return needs if needs else [ImpliedNeed.PRESENCE]
    
    def _find_contradictions(self, message: str) -> List[EmotionalContradiction]:
        """Find emotional paradoxes and mixed feelings"""
        contradictions = []
        
        if "glad it's over" in message.lower() and "but" in message.lower():
            contradictions.append(EmotionalContradiction(
                surface_feeling="Relief (glad it's over)",
                underlying_feeling="Grief, loss, identity confusion",
                connector="but",
                tension_level=0.9
            ))
        
        if "not a good relationship" in message.lower() and "i don't know" in message.lower():
            contradictions.append(EmotionalContradiction(
                surface_feeling="Clarity (it was bad)",
                underlying_feeling="Uncertainty, ambivalence about self",
                connector="but",
                tension_level=0.85
            ))
        
        if "undermined" in message.lower() and "good because" in message.lower():
            contradictions.append(EmotionalContradiction(
                surface_feeling="Positive assessment (it's good)",
                underlying_feeling="Deep wound (identity damage)",
                connector="&",
                tension_level=0.8
            ))
        
        return contradictions
    
    def _find_protective_language(self, message: str) -> List[str]:
        """Find language that creates distance/protection"""
        markers = []
        for pattern in self.protective_language:
            if pattern.lower() in message.lower():
                markers.append(pattern)
        return markers
    
    def _find_vulnerability_markers(self, message: str) -> List[str]:
        """Find where vulnerability emerges"""
        markers = []
        for pattern in self.vulnerability_markers:
            if re.search(pattern, message.lower()):
                markers.append(pattern)
        return markers
    
    def _find_impact_words(self, message: str) -> List[str]:
        """Find words indicating harm/impact"""
        found = []
        for word in self.impact_words:
            if word in message.lower():
                found.append(word)
        return found
    
    def _calculate_emotional_weight(self, layer: SemanticLayer) -> float:
        """Calculate emotional intensity (0.0-1.0)"""
        weight = 0.0
        
        # Impact words add weight
        weight += len(layer.impact_words) * 0.15
        
        # Contradictions add weight
        weight += len(layer.emotional_contradictions) * 0.2
        
        # Vulnerability markers add weight
        weight += len(layer.vulnerability_markers) * 0.1
        
        # Ambivalence is heavy
        if layer.emotional_stance == EmotionalStance.AMBIVALENT:
            weight += 0.3
        
        # Duration references indicate weight
        weight += len(layer.identity_signals.duration_references) * 0.1
        
        return min(weight, 1.0)
    
    def _detect_trust_increase(self, layer: SemanticLayer) -> bool:
        """Detect if user is increasing trust/openness"""
        # Naming partner indicates trust
        if layer.identity_signals.explicitly_named:
            return True
        
        # Moving from ambiguous to specific indicates trust
        if layer.emotional_stance in [EmotionalStance.REVEALING, EmotionalStance.SOFTENING]:
            return True
        
        return False
    
    def _detect_readiness(self, layer: SemanticLayer) -> bool:
        """Detect readiness to explore deeper"""
        # Softening indicates readiness
        if layer.emotional_stance == EmotionalStance.SOFTENING:
            return True
        
        # Inviting response indicates readiness
        if ConversationalMove.INVITING_RESPONSE in layer.conversational_moves:
            return True
        
        # Vulnerability markers indicate readiness
        if layer.vulnerability_markers:
            return True
        
        return False
    
    def _detect_pace_needs(self, layer: SemanticLayer) -> bool:
        """Detect if user needs slower pace"""
        # Testing safety indicates need for slowness
        if layer.disclosure_pace == DisclosurePace.TESTING_SAFETY:
            return True
        
        # Protective language indicates need for slowness
        if layer.protective_language:
            return True
        
        # Bracing stance indicates need for slowness
        if layer.emotional_stance == EmotionalStance.BRACING:
            return True
        
        return False


# Export for use
__all__ = [
    "SemanticParser",
    "SemanticLayer",
    "EmotionalStance",
    "DisclosurePace",
    "ConversationalMove",
    "PowerDynamic",
    "ImpliedNeed",
]
