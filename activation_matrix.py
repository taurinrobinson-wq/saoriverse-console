"""
Activation Matrix

Maps semantic layer attributes to response block activation.
This is a deterministic, testable system that translates semantic understanding
into compositional response behavior.

Matrix Structure:
- Emotional Stance -> BlockTypes
- Disclosure Pacing -> BlockTypes
- Conversational Moves -> BlockTypes
- Power Dynamics -> BlockTypes
- Implied Needs -> BlockTypes
- Contradictions -> BlockTypes

All mappings are deterministic and can be tested independently.
"""

from typing import Set, Dict, List
from enum import Enum
from response_composition_engine import BlockType


class ActivationMatrix:
    """
    Maps semantic attributes to response block activation.
    
    Usage:
        matrix = ActivationMatrix()
        blocks = matrix.activate_for_stance(EmotionalStance.BRACING)
        # Returns: {BlockType.CONTAINMENT, BlockType.PACING}
    """

    # =========================================================================
    # EMOTIONAL STANCE ACTIVATION RULES
    # =========================================================================
    
    STANCE_ACTIVATION = {
        "bracing": {
            BlockType.CONTAINMENT,
            BlockType.PACING,
        },
        "revealing": {
            BlockType.ACKNOWLEDGMENT,
            BlockType.VALIDATION,
            BlockType.TRUST,
        },
        "distancing": {
            BlockType.PACING,
            BlockType.CONTAINMENT,
        },
        "overwhelmed": {
            BlockType.CONTAINMENT,
            BlockType.PACING,
            BlockType.VALIDATION,
        },
        "ambivalent": {
            BlockType.AMBIVALENCE,
            BlockType.ACKNOWLEDGMENT,
        },
        "resigned": {
            BlockType.VALIDATION,
            BlockType.CONTAINMENT,
        },
        "guarded": {
            BlockType.CONTAINMENT,
            BlockType.PACING,
        },
        "neutral": {
            BlockType.ACKNOWLEDGMENT,
        },
    }

    # =========================================================================
    # DISCLOSURE PACING ACTIVATION RULES
    # =========================================================================
    
    PACING_ACTIVATION = {
        "testing_safety": {
            BlockType.CONTAINMENT,
            BlockType.PACING,
        },
        "gradual_reveal": {
            BlockType.ACKNOWLEDGMENT,
            BlockType.VALIDATION,
            BlockType.TRUST,
        },
        "contextual_grounding": {
            BlockType.ACKNOWLEDGMENT,
            BlockType.PACING,
        },
        "emotional_emergence": {
            BlockType.VALIDATION,
            BlockType.AMBIVALENCE,
        },
        "full_disclosure": {
            BlockType.VALIDATION,
            BlockType.GENTLE_DIRECTION,
        },
    }

    # =========================================================================
    # CONVERSATIONAL MOVE ACTIVATION RULES
    # =========================================================================
    
    MOVE_ACTIVATION = {
        "testing_safety": {
            BlockType.CONTAINMENT,
        },
        "naming_experience": {
            BlockType.ACKNOWLEDGMENT,
        },
        "grounding_in_facts": {
            BlockType.ACKNOWLEDGMENT,
        },
        "revealing_impact": {
            BlockType.VALIDATION,
        },
        "expressing_ambivalence": {
            BlockType.AMBIVALENCE,
        },
        "inviting_response": {
            BlockType.GENTLE_DIRECTION,
        },
        "softening": {
            BlockType.PACING,
        },
        "withholding": {
            BlockType.CONTAINMENT,
        },
        "seeking_validation": {
            BlockType.VALIDATION,
        },
    }

    # =========================================================================
    # POWER DYNAMICS ACTIVATION RULES
    # =========================================================================
    
    DYNAMICS_ACTIVATION = {
        "self_protection": {
            BlockType.CONTAINMENT,
            BlockType.PACING,
        },
        "boundary_setting": {
            BlockType.ACKNOWLEDGMENT,
        },
        "identity_entanglement": {
            BlockType.VALIDATION,
            BlockType.IDENTITY_INJURY,
        },
        "agency_loss": {
            BlockType.IDENTITY_INJURY,
        },
        "dominance_imbalance": {
            BlockType.IDENTITY_INJURY,
        },
        "reclaiming_agency": {
            BlockType.VALIDATION,
        },
        "mutual_influence": {
            BlockType.ACKNOWLEDGMENT,
        },
    }

    # =========================================================================
    # IMPLIED NEED ACTIVATION RULES
    # =========================================================================
    
    NEED_ACTIVATION = {
        "containment": {
            BlockType.CONTAINMENT,
        },
        "validation": {
            BlockType.VALIDATION,
        },
        "attunement": {
            BlockType.ACKNOWLEDGMENT,
            BlockType.VALIDATION,
        },
        "permission": {
            BlockType.PACING,
        },
        "presence": {
            BlockType.CONTAINMENT,
        },
        "pacing": {
            BlockType.PACING,
        },
        "acknowledgment": {
            BlockType.ACKNOWLEDGMENT,
        },
        "meaning_making": {
            BlockType.GENTLE_DIRECTION,
        },
        "restoration": {
            BlockType.VALIDATION,
            BlockType.IDENTITY_INJURY,
        },
    }

    # =========================================================================
    # CONTRADICTION ACTIVATION RULES
    # =========================================================================
    
    # If emotional_contradictions.present == True, activate ambivalence block
    CONTRADICTION_ACTIVATION = {
        True: {
            BlockType.AMBIVALENCE,
        },
        False: set(),
    }

    # =========================================================================
    # PRIVATE ACTIVATION RULES (determined from state)
    # =========================================================================
    
    # Identity signals detected
    IDENTITY_SIGNAL_ACTIVATION = {
        "high": {
            BlockType.TRUST,
            BlockType.VALIDATION,
        },
        "moderate": {
            BlockType.ACKNOWLEDGMENT,
        },
        "low": set(),
    }

    # Impact words present (agency injury markers)
    IMPACT_WORD_ACTIVATION = {
        True: {
            BlockType.IDENTITY_INJURY,
        },
        False: set(),
    }

    # Emotional weight
    EMOTIONAL_WEIGHT_ACTIVATION = {
        "high": {
            BlockType.VALIDATION,
            BlockType.IDENTITY_INJURY,
        },
        "moderate": {
            BlockType.VALIDATION,
        },
        "low": {
            BlockType.ACKNOWLEDGMENT,
        },
    }

    # Readiness to go deeper
    READINESS_ACTIVATION = {
        True: {
            BlockType.GENTLE_DIRECTION,
        },
        False: set(),
    }

    @staticmethod
    def activate_for_stance(stance_value: str) -> Set[BlockType]:
        """Get blocks activated by emotional stance"""
        return ActivationMatrix.STANCE_ACTIVATION.get(stance_value, set()).copy()

    @staticmethod
    def activate_for_pacing(pacing_value: str) -> Set[BlockType]:
        """Get blocks activated by disclosure pacing"""
        return ActivationMatrix.PACING_ACTIVATION.get(pacing_value, set()).copy()

    @staticmethod
    def activate_for_moves(moves: List[str]) -> Set[BlockType]:
        """Get blocks activated by conversational moves"""
        result = set()
        for move in moves:
            result.update(
                ActivationMatrix.MOVE_ACTIVATION.get(move, set())
            )
        return result

    @staticmethod
    def activate_for_dynamics(dynamics: List[str]) -> Set[BlockType]:
        """Get blocks activated by power dynamics"""
        result = set()
        for dynamic in dynamics:
            result.update(
                ActivationMatrix.DYNAMICS_ACTIVATION.get(dynamic, set())
            )
        return result

    @staticmethod
    def activate_for_needs(needs: List[str]) -> Set[BlockType]:
        """Get blocks activated by implied needs"""
        result = set()
        for need in needs:
            result.update(
                ActivationMatrix.NEED_ACTIVATION.get(need, set())
            )
        return result

    @staticmethod
    def activate_for_contradictions(present: bool) -> Set[BlockType]:
        """Get blocks activated by emotional contradictions"""
        return ActivationMatrix.CONTRADICTION_ACTIVATION.get(present, set()).copy()

    @staticmethod
    def activate_for_impact_words(present: bool) -> Set[BlockType]:
        """Get blocks activated by presence of impact words"""
        return ActivationMatrix.IMPACT_WORD_ACTIVATION.get(present, set()).copy()

    @staticmethod
    def activate_for_emotional_weight(weight: float) -> Set[BlockType]:
        """Get blocks activated by emotional weight"""
        if weight >= 0.7:
            category = "high"
        elif weight >= 0.4:
            category = "moderate"
        else:
            category = "low"
        
        return ActivationMatrix.EMOTIONAL_WEIGHT_ACTIVATION.get(category, set()).copy()

    @staticmethod
    def activate_for_identity_signals(signal_count: int) -> Set[BlockType]:
        """Get blocks activated by identity signals"""
        if signal_count >= 3:
            category = "high"
        elif signal_count >= 1:
            category = "moderate"
        else:
            category = "low"
        
        return ActivationMatrix.IDENTITY_SIGNAL_ACTIVATION.get(category, set()).copy()

    @staticmethod
    def activate_for_readiness(ready: bool) -> Set[BlockType]:
        """Get blocks activated by readiness to go deeper"""
        return ActivationMatrix.READINESS_ACTIVATION.get(ready, set()).copy()

    @staticmethod
    def compute_full_activation(
        emotional_stance: str,
        disclosure_pacing: str,
        conversational_moves: List[str],
        power_dynamics: List[str],
        implied_needs: List[str],
        emotional_contradictions_present: bool,
        emotional_weight: float,
        has_impact_words: bool,
        identity_signal_count: int,
        ready_to_go_deeper: bool,
    ) -> Set[BlockType]:
        """
        Compute complete block activation from all semantic layers.
        
        Returns union of all activated blocks.
        """
        
        blocks = set()
        
        # Accumulate activations from all layers
        blocks.update(ActivationMatrix.activate_for_stance(emotional_stance))
        blocks.update(ActivationMatrix.activate_for_pacing(disclosure_pacing))
        blocks.update(ActivationMatrix.activate_for_moves(conversational_moves))
        blocks.update(ActivationMatrix.activate_for_dynamics(power_dynamics))
        blocks.update(ActivationMatrix.activate_for_needs(implied_needs))
        blocks.update(
            ActivationMatrix.activate_for_contradictions(emotional_contradictions_present)
        )
        blocks.update(ActivationMatrix.activate_for_emotional_weight(emotional_weight))
        blocks.update(ActivationMatrix.activate_for_impact_words(has_impact_words))
        blocks.update(ActivationMatrix.activate_for_identity_signals(identity_signal_count))
        blocks.update(ActivationMatrix.activate_for_readiness(ready_to_go_deeper))
        
        return blocks


class BlockActivationValidator:
    """Validates block activation against expected patterns"""

    @staticmethod
    def validate_activation(
        expected_blocks: Set[BlockType],
        actual_blocks: Set[BlockType],
        threshold: float = 0.8
    ) -> bool:
        """
        Check if actual activation matches expected within threshold.
        
        Returns True if ≥ threshold match.
        """
        if not expected_blocks:
            return len(actual_blocks) == 0
        
        intersection = len(expected_blocks & actual_blocks)
        match_ratio = intersection / len(expected_blocks)
        
        return match_ratio >= threshold

    @staticmethod
    def validate_forbidden_absence(
        activated_blocks: Set[BlockType],
        message_index: int
    ) -> bool:
        """
        Validate that forbidden blocks don't appear at wrong message indices.
        
        Rules:
        - GENTLE_DIRECTION before message 4: forbidden
        - IDENTITY_INJURY in messages 1-2: avoid (use later)
        """
        
        # GENTLE_DIRECTION only after message 3
        if message_index < 3 and BlockType.GENTLE_DIRECTION in activated_blocks:
            return False
        
        # IDENTITY_INJURY better in messages 3-4
        if message_index < 2 and BlockType.IDENTITY_INJURY in activated_blocks:
            # Not forbidden but sub-optimal
            pass
        
        return True
