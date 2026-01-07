"""
Response Generation Rubric for Semantic Attunement

This module provides guidelines for generating responses that are attuned
to the semantic meaning of messages, not just surface patterns.
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum
from semantic_parsing_schema import (
    SemanticLayer, EmotionalStance, DisclosurePace, 
    ConversationalMove, ImpliedNeed
)


class ResponseQuality(Enum):
    """Quality ratings for responses"""
    MISALIGNED = 0      # Responds to wrong layer
    SURFACE_LEVEL = 1   # Responds to surface but misses depth
    PARTIAL_ATTUNEMENT = 2   # Gets some semantic layers
    WELL_ATTUNED = 3    # Understands multiple layers correctly
    MASTERFULLY_ATTUNED = 4  # Integrates all layers seamlessly


@dataclass
class ResponseRubric:
    """Evaluation criteria for semantic attunement"""
    
    # Response should reflect these elements
    addresses_emotional_stance: bool = False
    honors_disclosure_pace: bool = False
    recognizes_conversational_move: bool = False
    identifies_power_dynamics: bool = False
    meets_implied_needs: bool = False
    holds_contradictions: bool = False
    avoids_premature_closure: bool = False
    
    # Linguistic markers should NOT appear
    should_avoid_analysis: bool = True
    should_avoid_advice: bool = True
    should_avoid_normalization: bool = True
    should_avoid_judgment: bool = True
    should_avoid_rushing: bool = True
    
    # Quality measures
    presence_level: float = 0.0  # 0.0-1.0 How present is the response
    attunement_level: float = 0.0  # 0.0-1.0 How well attuned
    safety_level: float = 0.0    # 0.0-1.0 How safe/contained
    validation_level: float = 0.0  # 0.0-1.0 How validated
    
    quality_rating: ResponseQuality = ResponseQuality.SURFACE_LEVEL


class ResponseGenerationRubric:
    """
    Guidelines for generating responses attuned to semantic layers.
    """
    
    def __init__(self):
        self.rules_by_stance = {
            EmotionalStance.BRACING: self._respond_to_bracing,
            EmotionalStance.DISTANCING: self._respond_to_distancing,
            EmotionalStance.REVEALING: self._respond_to_revealing,
            EmotionalStance.AMBIVALENT: self._respond_to_ambivalent,
            EmotionalStance.SOFTENING: self._respond_to_softening,
        }
        
        self.rules_by_pace = {
            DisclosurePace.TESTING_SAFETY: self._respond_to_testing_safety,
            DisclosurePace.GRADUAL_REVEAL: self._respond_to_gradual_reveal,
            DisclosurePace.CONTEXTUAL_GROUNDING: self._respond_to_contextual_grounding,
            DisclosurePace.EMOTIONAL_EMERGENCE: self._respond_to_emotional_emergence,
        }
        
        self.rules_by_move = {
            ConversationalMove.TESTING_SAFETY: self._respond_to_safety_test,
            ConversationalMove.NAMING_EXPERIENCE: self._respond_to_naming,
            ConversationalMove.GROUNDING_IN_FACTS: self._respond_to_facts,
            ConversationalMove.REVEALING_IMPACT: self._respond_to_impact,
            ConversationalMove.EXPRESSING_AMBIVALENCE: self._respond_to_ambivalence,
            ConversationalMove.INVITING_RESPONSE: self._respond_to_invitation,
        }
    
    def generate_rubric(self, layer: SemanticLayer) -> ResponseRubric:
        """
        Generate evaluation rubric for a response to this semantic layer.
        """
        rubric = ResponseRubric()
        
        # Apply stance-specific rules
        stance_rules = self.rules_by_stance.get(layer.emotional_stance)
        if stance_rules:
            stance_rules(rubric)
        
        # Apply pace-specific rules
        pace_rules = self.rules_by_pace.get(layer.disclosure_pace)
        if pace_rules:
            pace_rules(rubric)
        
        # Apply move-specific rules
        for move in layer.conversational_moves:
            move_rules = self.rules_by_move.get(move)
            if move_rules:
                move_rules(rubric)
        
        # Apply implied needs
        for need in layer.implied_needs:
            self._apply_need(need, rubric)
        
        # Handle contradictions
        if layer.emotional_contradictions:
            rubric.holds_contradictions = True
        
        # Check pace requirements
        if layer.needs_pace_slowing:
            rubric.should_avoid_rushing = True
        
        # Calculate overall quality based on what's required
        rubric.quality_rating = self._calculate_quality(rubric)
        
        return rubric
    
    # STANCE-SPECIFIC RULES
    
    def _respond_to_bracing(self, rubric: ResponseRubric):
        """Respond to someone preparing for emotional impact"""
        rubric.addresses_emotional_stance = True
        rubric.should_avoid_rushing = True
        rubric.should_avoid_analysis = True
        rubric.safety_level = 0.9  # Safety is paramount
        rubric.presence_level = 0.8  # Steady, present
        # Required: Signal safety, match pace, avoid specificity
    
    def _respond_to_distancing(self, rubric: ResponseRubric):
        """Respond to protective, formal language"""
        rubric.addresses_emotional_stance = True
        rubric.should_avoid_rushing = True
        rubric.should_avoid_advice = True
        rubric.safety_level = 0.85
        rubric.attunement_level = 0.7
        # Required: Respect the distance, don't push
    
    def _respond_to_revealing(self, rubric: ResponseRubric):
        """Respond to vulnerability and openness"""
        rubric.addresses_emotional_stance = True
        rubric.honors_disclosure_pace = True
        rubric.validation_level = 0.9  # Validate the courage
        rubric.presence_level = 0.9
        # Required: Acknowledge trust, honor specificity
    
    def _respond_to_ambivalent(self, rubric: ResponseRubric):
        """Respond to mixed feelings and contradiction"""
        rubric.addresses_emotional_stance = True
        rubric.holds_contradictions = True
        rubric.should_avoid_clarity = True
        rubric.attunement_level = 0.9
        # Required: Hold both truths, don't resolve prematurely
    
    def _respond_to_softening(self, rubric: ResponseRubric):
        """Respond to emerging vulnerability"""
        rubric.addresses_emotional_stance = True
        rubric.honors_disclosure_pace = True
        rubric.should_avoid_rushing = True
        rubric.presence_level = 0.95
        rubric.attunement_level = 0.85
        # Required: Meet the vulnerability with presence
    
    # PACE-SPECIFIC RULES
    
    def _respond_to_testing_safety(self, rubric: ResponseRubric):
        """Respond to initial safety probe"""
        rubric.honors_disclosure_pace = True
        rubric.should_avoid_rushing = True
        rubric.should_avoid_specificity = True
        rubric.safety_level = 0.95
        # Required: Signal safety without demanding more, match vagueness
    
    def _respond_to_gradual_reveal(self, rubric: ResponseRubric):
        """Respond to controlled disclosure"""
        rubric.honors_disclosure_pace = True
        rubric.should_avoid_probing = True
        rubric.attunement_level = 0.8
        # Required: Follow the lead, don't push deeper
    
    def _respond_to_contextual_grounding(self, rubric: ResponseRubric):
        """Respond to facts used as emotional buffer"""
        rubric.honors_disclosure_pace = True
        rubric.recognizes_conversational_move = True
        rubric.validation_level = 0.85  # Acknowledge the scale
        # Required: Honor facts as context, don't jump to emotion
    
    def _respond_to_emotional_emergence(self, rubric: ResponseRubric):
        """Respond to core feelings emerging"""
        rubric.honors_disclosure_pace = True
        rubric.addresses_emotional_stance = True
        rubric.presence_level = 0.95
        rubric.attunement_level = 0.9
        # Required: Stay with uncertainty, don't offer premature clarity
    
    # CONVERSATIONAL MOVE-SPECIFIC RULES
    
    def _respond_to_safety_test(self, rubric: ResponseRubric):
        """Respond to someone testing if it's safe"""
        rubric.safety_level = 0.95
        rubric.should_avoid_overwhelming = True
        # Required: Signal safety subtly, invite without pressure
    
    def _respond_to_naming(self, rubric: ResponseRubric):
        """Respond to someone naming the event"""
        rubric.recognizes_conversational_move = True
        rubric.validation_level = 0.9  # Validate the courage to name
        rubric.attunement_level = 0.85  # Acknowledge emotional weight
        # Required: Honor finality weight, avoid cheerleading
    
    def _respond_to_facts(self, rubric: ResponseRubric):
        """Respond to factual grounding"""
        rubric.recognizes_conversational_move = True
        rubric.validation_level = 0.8  # Facts matter
        rubric.should_avoid_minimizing = True
        # Required: Acknowledge scale/complexity, don't dismiss as "just facts"
    
    def _respond_to_impact(self, rubric: ResponseRubric):
        """Respond to revelation of harm"""
        rubric.recognizes_conversational_move = True
        rubric.validation_level = 0.95  # This matters deeply
        rubric.should_avoid_analysis = True
        # Required: Witness the harm, don't analyze the relationship
    
    def _respond_to_ambivalence(self, rubric: ResponseRubric):
        """Respond to holding multiple truths"""
        rubric.holds_contradictions = True
        rubric.attunement_level = 0.95
        rubric.should_avoid_resolution = True
        # Required: Sit with "I don't know", don't resolve
    
    def _respond_to_invitation(self, rubric: ResponseRubric):
        """Respond to someone inviting deeper engagement"""
        rubric.honors_disclosure_pace = True
        rubric.presence_level = 0.95
        rubric.should_avoid_rushing = False  # Now can go deeper
        # Required: Meet the vulnerability, reflect back understanding
    
    # IMPLIED NEED-SPECIFIC RULES
    
    def _apply_need(self, need: ImpliedNeed, rubric: ResponseRubric):
        """Apply rules for specific implied needs"""
        
        if need == ImpliedNeed.CONTAINMENT:
            rubric.safety_level = 0.95
            rubric.should_avoid_rushing = True
        
        elif need == ImpliedNeed.VALIDATION:
            rubric.validation_level = 0.9
        
        elif need == ImpliedNeed.PERMISSION:
            rubric.validation_level = 0.85
            rubric.attunement_level = 0.8
        
        elif need == ImpliedNeed.ATTUNEMENT:
            rubric.attunement_level = 0.95
            rubric.presence_level = 0.9
        
        elif need == ImpliedNeed.PRESENCE:
            rubric.presence_level = 0.95
            rubric.should_avoid_advice = True
        
        elif need == ImpliedNeed.MEANING_MAKING:
            rubric.attunement_level = 0.9
            rubric.should_avoid_prescriptive = True
    
    def _calculate_quality(self, rubric: ResponseRubric) -> ResponseQuality:
        """Calculate overall quality based on rubric"""
        
        # Count how many critical elements are addressed
        critical_count = sum([
            rubric.addresses_emotional_stance,
            rubric.honors_disclosure_pace,
            rubric.recognizes_conversational_move,
        ])
        
        # Quality based on critical elements + attunement
        avg_attunement = (
            rubric.presence_level +
            rubric.attunement_level +
            rubric.safety_level +
            rubric.validation_level
        ) / 4.0
        
        if critical_count == 0:
            return ResponseQuality.MISALIGNED
        elif critical_count == 1 and avg_attunement < 0.6:
            return ResponseQuality.SURFACE_LEVEL
        elif critical_count == 1 or avg_attunement < 0.7:
            return ResponseQuality.PARTIAL_ATTUNEMENT
        elif critical_count >= 2 and avg_attunement >= 0.7:
            return ResponseQuality.WELL_ATTUNED
        else:
            return ResponseQuality.MASTERFULLY_ATTUNED


# Response patterns for reference
RESPONSE_PATTERNS = {
    "containment": [
        "I'm here with you in this.",
        "Take your time with this.",
        "You can share what feels safe right now.",
        "I can hold this space for you.",
    ],
    "validation": [
        "That matters deeply.",
        "What you're carrying is real.",
        "That weight makes sense.",
        "Your experience is valid.",
    ],
    "presence": [
        "I'm listening.",
        "I see you in this.",
        "You're not alone with this.",
        "I'm here.",
    ],
    "attunement": [
        "That duality you're holding...",
        "Both things are true.",
        "I hear the contradiction you're living.",
        "That ambivalence makes complete sense.",
    ],
    "permission": [
        "It's okay to feel this.",
        "You don't have to be clear about this yet.",
        "Uncertainty is allowed.",
        "You're allowed to grieve even as you heal.",
    ],
    "avoid_analysis": [
        "This isn't the time for fixing.",
        "I'm not here to solve this.",
        "Understanding can wait.",
        "What matters now is what you're feeling.",
    ],
    "avoid_advice": [
        "I'm not here to tell you what to do.",
        "You know your path.",
        "My job is to understand, not advise.",
        "The wisdom is already in you.",
    ],
}


__all__ = [
    "ResponseGenerationRubric",
    "ResponseRubric",
    "ResponseQuality",
    "RESPONSE_PATTERNS",
]
