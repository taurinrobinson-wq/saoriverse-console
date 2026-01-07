"""
Priority Weighting System

Implements 8-level priority stack that determines which semantic elements
take precedence when composing responses.

Priority Stack (high to low):
1. Safety / Containment
2. Pacing
3. Contradictions
4. Identity Injury / Agency Loss
5. Emotional Stance
6. Conversational Move
7. Disclosure Pacing
8. Contextual Details

Higher-priority elements override lower-priority ones.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
from response_composition_engine import BlockType


class PriorityLevel(Enum):
    """Priority levels in descending order"""
    SAFETY_CONTAINMENT = 1
    PACING = 2
    CONTRADICTIONS = 3
    IDENTITY_INJURY = 4
    EMOTIONAL_STANCE = 5
    CONVERSATIONAL_MOVE = 6
    DISCLOSURE_PACING = 7
    CONTEXTUAL_DETAILS = 8


@dataclass
class PriorityElement:
    """A prioritized semantic element"""
    level: PriorityLevel
    element_type: str  # e.g., "stance", "pacing", "contradiction"
    value: str  # e.g., "bracing", "testing_safety", "relief_vs_grief"
    blocks_to_activate: List[BlockType]
    override_lower_blocks: bool = False  # Whether to suppress lower-priority blocks


class PriorityWeightingSystem:
    """
    Determines response composition priorities from semantic layers.
    
    Process:
    1. Extract all semantic elements from layer
    2. Assign each to priority level
    3. Determine block activation based on priorities
    4. Apply overrides (high-priority suppresses low-priority)
    5. Return ordered block list for composition
    """

    # =========================================================================
    # PRIORITY ASSIGNMENT RULES
    # =========================================================================
    
    # LEVEL 1: Safety / Containment (always highest)
    SAFETY_RULES = {
        "needs_pace_slowing": True,  # Slowing = safety priority
        "bracing_stance": True,  # Bracing = safety priority
        "testing_safety_move": True,  # Testing = safety priority
    }
    
    # LEVEL 2: Pacing
    PACING_RULES = {
        "disclosure_pace_testing": {
            "blocks": [BlockType.PACING, BlockType.CONTAINMENT],
        },
        "disclosure_pace_gradual": {
            "blocks": [BlockType.PACING],
        },
    }
    
    # LEVEL 3: Contradictions
    CONTRADICTION_RULES = {
        "present": {
            "blocks": [BlockType.AMBIVALENCE],
            "override_lower": True,  # Contradictions override stance-only responses
        },
    }
    
    # LEVEL 4: Identity Injury / Agency Loss
    IDENTITY_INJURY_RULES = {
        "agency_loss": {
            "blocks": [BlockType.IDENTITY_INJURY],
            "override_lower": True,
        },
        "impact_words_present": {
            "blocks": [BlockType.IDENTITY_INJURY],
        },
        "identity_entanglement": {
            "blocks": [BlockType.IDENTITY_INJURY, BlockType.VALIDATION],
        },
    }
    
    # LEVEL 5: Emotional Stance (mid-priority)
    STANCE_RULES = {
        "revealing": [BlockType.VALIDATION, BlockType.ACKNOWLEDGMENT],
        "bracing": [BlockType.CONTAINMENT],
        "overwhelmed": [BlockType.CONTAINMENT, BlockType.VALIDATION],
    }
    
    # LEVEL 6: Conversational Move (mid-lower priority)
    MOVE_RULES = {
        "naming_experience": [BlockType.ACKNOWLEDGMENT],
        "revealing_impact": [BlockType.VALIDATION],
    }
    
    # LEVEL 7: Disclosure Pacing (lower priority, covered by level 2)
    DISCLOSURE_RULES = {
        "emotional_emergence": [BlockType.VALIDATION],
    }
    
    # LEVEL 8: Contextual Details (lowest priority)
    CONTEXT_RULES = {
        "identity_signals": [BlockType.ACKNOWLEDGMENT],
    }

    @staticmethod
    def extract_priority_elements(
        emotional_stance: str,
        disclosure_pacing: str,
        conversational_moves: List[str],
        power_dynamics: List[str],
        implied_needs: List[str],
        emotional_contradictions_present: bool,
        emotional_weight: float,
        has_impact_words: bool,
        needs_pace_slowing: bool,
        ready_to_go_deeper: bool,
    ) -> List[PriorityElement]:
        """
        Extract all priority elements from semantic layer.
        
        Returns list of PriorityElements ordered by priority.
        """
        
        elements = []
        
        # LEVEL 1: Safety / Containment
        if needs_pace_slowing:
            elements.append(PriorityElement(
                level=PriorityLevel.SAFETY_CONTAINMENT,
                element_type="pacing_need",
                value="slowing_required",
                blocks_to_activate=[BlockType.PACING, BlockType.CONTAINMENT],
                override_lower_blocks=True,
            ))
        
        if emotional_stance == "bracing":
            elements.append(PriorityElement(
                level=PriorityLevel.SAFETY_CONTAINMENT,
                element_type="stance",
                value="bracing",
                blocks_to_activate=[BlockType.CONTAINMENT],
                override_lower_blocks=False,
            ))
        
        if "testing_safety" in conversational_moves:
            elements.append(PriorityElement(
                level=PriorityLevel.SAFETY_CONTAINMENT,
                element_type="move",
                value="testing_safety",
                blocks_to_activate=[BlockType.CONTAINMENT],
                override_lower_blocks=False,
            ))
        
        # LEVEL 2: Pacing
        if disclosure_pacing == "testing_safety":
            elements.append(PriorityElement(
                level=PriorityLevel.PACING,
                element_type="pace",
                value="testing_safety",
                blocks_to_activate=[BlockType.PACING],
                override_lower_blocks=False,
            ))
        
        if "pace_slowing_need" in implied_needs or needs_pace_slowing:
            elements.append(PriorityElement(
                level=PriorityLevel.PACING,
                element_type="need",
                value="pacing",
                blocks_to_activate=[BlockType.PACING],
                override_lower_blocks=False,
            ))
        
        # LEVEL 3: Contradictions
        if emotional_contradictions_present:
            elements.append(PriorityElement(
                level=PriorityLevel.CONTRADICTIONS,
                element_type="contradiction",
                value="present",
                blocks_to_activate=[BlockType.AMBIVALENCE],
                override_lower_blocks=True,  # Contradictions must be held
            ))
        
        # LEVEL 4: Identity Injury / Agency Loss
        if "agency_loss" in power_dynamics:
            elements.append(PriorityElement(
                level=PriorityLevel.IDENTITY_INJURY,
                element_type="power_dynamic",
                value="agency_loss",
                blocks_to_activate=[BlockType.IDENTITY_INJURY],
                override_lower_blocks=True,
            ))
        
        if has_impact_words:
            elements.append(PriorityElement(
                level=PriorityLevel.IDENTITY_INJURY,
                element_type="impact_words",
                value="present",
                blocks_to_activate=[BlockType.IDENTITY_INJURY],
                override_lower_blocks=False,
            ))
        
        if "identity_entanglement" in power_dynamics:
            elements.append(PriorityElement(
                level=PriorityLevel.IDENTITY_INJURY,
                element_type="power_dynamic",
                value="identity_entanglement",
                blocks_to_activate=[BlockType.IDENTITY_INJURY, BlockType.VALIDATION],
                override_lower_blocks=False,
            ))
        
        # LEVEL 5: Emotional Stance
        if emotional_stance == "revealing":
            elements.append(PriorityElement(
                level=PriorityLevel.EMOTIONAL_STANCE,
                element_type="stance",
                value="revealing",
                blocks_to_activate=[BlockType.VALIDATION, BlockType.ACKNOWLEDGMENT],
                override_lower_blocks=False,
            ))
        
        if emotional_stance == "ambivalent":
            elements.append(PriorityElement(
                level=PriorityLevel.EMOTIONAL_STANCE,
                element_type="stance",
                value="ambivalent",
                blocks_to_activate=[BlockType.AMBIVALENCE],
                override_lower_blocks=False,
            ))
        
        # LEVEL 6: Conversational Move
        for move in conversational_moves:
            if move == "naming_experience":
                elements.append(PriorityElement(
                    level=PriorityLevel.CONVERSATIONAL_MOVE,
                    element_type="move",
                    value="naming_experience",
                    blocks_to_activate=[BlockType.ACKNOWLEDGMENT],
                    override_lower_blocks=False,
                ))
            elif move == "revealing_impact":
                elements.append(PriorityElement(
                    level=PriorityLevel.CONVERSATIONAL_MOVE,
                    element_type="move",
                    value="revealing_impact",
                    blocks_to_activate=[BlockType.VALIDATION],
                    override_lower_blocks=False,
                ))
        
        # LEVEL 7: Disclosure Pacing
        if disclosure_pacing == "emotional_emergence":
            elements.append(PriorityElement(
                level=PriorityLevel.DISCLOSURE_PACING,
                element_type="pace",
                value="emotional_emergence",
                blocks_to_activate=[BlockType.VALIDATION],
                override_lower_blocks=False,
            ))
        
        # LEVEL 8: Contextual Details
        if "identity_signals" in str(implied_needs):
            elements.append(PriorityElement(
                level=PriorityLevel.CONTEXTUAL_DETAILS,
                element_type="context",
                value="identity_signals",
                blocks_to_activate=[BlockType.ACKNOWLEDGMENT],
                override_lower_blocks=False,
            ))
        
        # Sort by priority
        elements.sort(key=lambda e: e.level.value)
        
        return elements

    @staticmethod
    def compute_block_activation_with_priorities(
        priority_elements: List[PriorityElement],
    ) -> Dict[BlockType, int]:
        """
        Compute final block activation considering priorities and overrides.
        
        Returns dict of BlockType -> activation_priority (lower = activate first).
        """
        
        block_priorities: Dict[BlockType, int] = {}
        blocks_to_suppress: set = set()
        
        for element in priority_elements:
            # If this element overrides lower priority, mark lower blocks for suppression
            if element.override_lower_blocks:
                # Find all lower-priority elements
                lower_elements = [
                    e for e in priority_elements
                    if e.level.value > element.level.value
                ]
                # Mark their blocks for potential suppression
                for lower_elem in lower_elements:
                    for block in lower_elem.blocks_to_activate:
                        # Only suppress if not also activated by higher priority
                        if block not in element.blocks_to_activate:
                            blocks_to_suppress.add(block)
            
            # Activate this element's blocks
            for block in element.blocks_to_activate:
                if block not in block_priorities:
                    block_priorities[block] = element.level.value
                else:
                    # Keep highest priority (lowest number)
                    block_priorities[block] = min(
                        block_priorities[block],
                        element.level.value
                    )
        
        # Remove suppressed blocks
        for block in blocks_to_suppress:
            if block in block_priorities:
                del block_priorities[block]
        
        return block_priorities

    @staticmethod
    def get_ordered_blocks(
        block_priorities: Dict[BlockType, int],
    ) -> List[BlockType]:
        """
        Get blocks ordered by priority.
        
        Returns list of BlockTypes in order of priority (highest first).
        """
        
        sorted_blocks = sorted(
            block_priorities.items(),
            key=lambda item: item[1]
        )
        
        return [block for block, _ in sorted_blocks]

    @staticmethod
    def validate_priority_alignment(
        priority_elements: List[PriorityElement],
        activated_blocks: List[BlockType],
        message_index: int,
    ) -> Tuple[bool, List[str]]:
        """
        Validate that activated blocks align with priority elements.
        
        Returns (is_valid, list_of_issues).
        """
        
        issues = []
        
        # Check high-priority elements are honored
        high_priority_elements = [
            e for e in priority_elements
            if e.level.value <= PriorityLevel.CONTRADICTIONS.value
        ]
        
        for element in high_priority_elements:
            # At least one block from high-priority element should be present
            has_block = any(
                block in activated_blocks
                for block in element.blocks_to_activate
            )
            if not has_block:
                issues.append(
                    f"High-priority element {element.value} ({element.element_type}) "
                    f"has no activated blocks"
                )
        
        # Check low-priority elements aren't suppressing high-priority
        for i, elem1 in enumerate(priority_elements):
            for elem2 in priority_elements[i+1:]:
                # elem1 is higher priority
                if elem1.override_lower_blocks:
                    # Check that elem1's blocks are present and elem2's aren't conflicting
                    pass
        
        is_valid = len(issues) == 0
        
        return is_valid, issues
