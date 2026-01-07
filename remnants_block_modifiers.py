"""
🎭 REMNANTS BLOCK MODIFIERS: Emotional Priority Adjustment
===========================================================

Adjusts dialogue block priorities based on NPC's current REMNANTS state.

This is how emotional evolution changes what an NPC chooses to say next.

Example:
    Same situation with two different REMNANTS states:
    
    Nima with low empathy/high skepticism:
    - Block priorities: CHALLENGE, DOUBT, ISOLATION
    
    Nima with high empathy/high trust:
    - Block priorities: ACKNOWLEDGMENT, VALIDATION, CONNECTION
    
    Same NPC, same situation, different response because emotional state
    tilts what kinds of blocks she's drawn to.

The modifiers are NUDGES, not overrides. A block with priority 5 becomes 7
(high empathy boosts VALIDATION), not replaced entirely. This keeps the
NPC's voice consistent while letting emotion shape the emphasis.
"""

from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field


@dataclass
class BlockPriorityAdjustment:
    """Record of how REMNANTS modified a block's priority."""
    block_name: str
    original_priority: float
    delta: float
    source: str  # e.g., "empathy:high", "authority:low"
    final_priority: float
    
    def __str__(self) -> str:
        sign = "+" if self.delta >= 0 else ""
        return f"{self.block_name}: {self.original_priority} {sign}{self.delta} → {self.final_priority}"


class RemnantsBlockModifiers:
    """
    Adjusts dialogue block priorities based on REMNANTS emotional state.
    
    Each REMNANTS trait provides nudges to certain block categories:
    
    - EMPATHY (>0.7): Boost VALIDATION, ACKNOWLEDGMENT, SAFETY
    - EMPATHY (<0.3): Boost CHALLENGE, DISTANCE, INDEPENDENCE
    
    - SKEPTICISM (>0.7): Boost AMBIVALENCE, DOUBT, CHALLENGE
    - SKEPTICISM (<0.3): Boost TRUST, AGREEMENT, SAFETY
    
    - AUTHORITY (>0.7): Boost GENTLE_DIRECTION, SUGGESTION, WISDOM
    - AUTHORITY (<0.3): Boost QUESTIONING, EXPLORATION, UNCERTAINTY
    
    - NEED (>0.7): Boost CONTAINMENT, TOGETHERNESS, RELATIONAL
    - NEED (<0.3): Boost INDEPENDENCE, AUTONOMY, SOLITUDE
    
    - TRUST (>0.7): Boost AGREEMENT, OPENNESS, COLLABORATION
    - TRUST (<0.3): Boost CAUTION, PROTECTION, SKEPTICISM
    
    - MEMORY (>0.7): Boost CONTINUITY, REFERENCE, HISTORY
    - MEMORY (<0.3): Boost PRESENT, NOVELTY, IMMEDIACY
    
    - RESOLVE (>0.7): Boost COMMITMENT, DIRECTION, CONVICTION
    - RESOLVE (<0.3): Boost AMBIVALENCE, UNCERTAINTY, WAVERING
    
    - COURAGE (>0.7): Boost VULNERABILITY, COURAGE, BREAKTHROUGH
    - COURAGE (<0.3): Boost PROTECTION, CAUTION, RETREAT
    
    The nudges are typically +0.5 to +2.0 (additive), not multiplicative.
    This keeps blocks with higher base priority still higher, while letting
    emotion create meaningful shifts in emphasis.
    """
    
    # Canonical block categories that can be adjusted
    BLOCK_CATEGORIES = [
        "VALIDATION",          # "You matter"
        "ACKNOWLEDGMENT",      # "I see you"
        "SAFETY",             # "You're safe with me"
        "CONTAINMENT",        # "I can hold this"
        "TOGETHERNESS",       # "We're in this together"
        "RELATIONAL",         # "This connects us"
        
        "CHALLENGE",          # "I disagree"
        "DOUBT",             # "That's questionable"
        "AMBIVALENCE",       # "I hold two things"
        "DISTANCE",          # "I need space"
        "INDEPENDENCE",      # "You need to choose"
        "SOLITUDE",          # "I need to be alone"
        
        "GENTLE_DIRECTION",  # "Maybe consider..."
        "SUGGESTION",        # "What if..."
        "WISDOM",            # "From what I've learned..."
        "COMMITMENT",        # "I'm choosing this"
        "CONVICTION",        # "This is true"
        
        "QUESTIONING",       # "Why?"
        "EXPLORATION",       # "Let's discover"
        "UNCERTAINTY",       # "I don't know"
        "CAUTION",          # "Be careful"
        "PROTECTION",       # "I'll protect you"
        "SKEPTICISM",       # "I don't believe that"
        
        "CONTINUITY",        # "Like before..."
        "REFERENCE",         # "Remember when..."
        "HISTORY",          # "We have a past"
        "PRESENT",          # "Right now..."
        "NOVELTY",          # "This is new"
        "IMMEDIACY",        # "This moment matters"
        
        "VULNERABILITY",     # "I'm afraid too"
        "COURAGE",          # "I'm choosing anyway"
        "BREAKTHROUGH",     # "Something changed"
        "RETREAT",          # "I need to withdraw"
        
        "AGREEMENT",        # "Yes, you're right"
        "OPENNESS",         # "I'm open to you"
        "COLLABORATION",    # "Let's work together"
    ]
    
    @staticmethod
    def adjust_block_priorities(
        block_priorities: Dict[str, float],
        remnants: Dict[str, float],
        npc_name: Optional[str] = None
    ) -> Tuple[Dict[str, float], List[BlockPriorityAdjustment]]:
        """
        Adjust block priorities based on REMNANTS emotional state.
        
        Args:
            block_priorities: Dict[block_name, priority_score]
            remnants: Dict[trait_name, value (-1.0 to 1.0)]
            npc_name: For logging/debugging
            
        Returns:
            (adjusted_priorities, list_of_adjustments)
        """
        
        adjusted = dict(block_priorities)  # Copy to avoid mutation
        adjustments: List[BlockPriorityAdjustment] = []
        
        # Apply each REMNANTS trait's modulations
        RemnantsBlockModifiers._apply_empathy_modulation(adjusted, remnants, adjustments)
        RemnantsBlockModifiers._apply_skepticism_modulation(adjusted, remnants, adjustments)
        RemnantsBlockModifiers._apply_authority_modulation(adjusted, remnants, adjustments)
        RemnantsBlockModifiers._apply_need_modulation(adjusted, remnants, adjustments)
        RemnantsBlockModifiers._apply_trust_modulation(adjusted, remnants, adjustments)
        RemnantsBlockModifiers._apply_memory_modulation(adjusted, remnants, adjustments)
        RemnantsBlockModifiers._apply_resolve_modulation(adjusted, remnants, adjustments)
        RemnantsBlockModifiers._apply_courage_modulation(adjusted, remnants, adjustments)
        
        # Clamp all priorities to reasonable range
        adjusted = {k: max(0.0, min(10.0, v)) for k, v in adjusted.items()}
        
        return adjusted, adjustments
    
    @staticmethod
    def _apply_empathy_modulation(
        priorities: Dict[str, float],
        remnants: Dict[str, float],
        adjustments: List[BlockPriorityAdjustment]
    ) -> None:
        """
        Adjust blocks based on EMPATHY level.
        
        High empathy (>0.7):
        - Boost VALIDATION, ACKNOWLEDGMENT, SAFETY, TOGETHERNESS
        - Reduce CHALLENGE, DISTANCE
        
        Low empathy (<0.3):
        - Boost CHALLENGE, DISTANCE, INDEPENDENCE
        - Reduce VALIDATION, ACKNOWLEDGMENT
        """
        empathy = remnants.get("empathy", 0.0)
        
        if empathy > 0.7:
            # High empathy boosters
            for block in ["VALIDATION", "ACKNOWLEDGMENT", "SAFETY", "TOGETHERNESS", "RELATIONAL"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="empathy:high",
                        final_priority=priorities[block]
                    ))
            
            # Low empathy reducers
            for block in ["CHALLENGE", "DISTANCE", "SKEPTICISM"]:
                if block in priorities:
                    delta = -0.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="empathy:high_reduces",
                        final_priority=priorities[block]
                    ))
        
        elif empathy < 0.3:
            # Low empathy boosters
            for block in ["CHALLENGE", "DISTANCE", "INDEPENDENCE", "SKEPTICISM", "DOUBT"]:
                if block in priorities:
                    delta = 1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="empathy:low",
                        final_priority=priorities[block]
                    ))
            
            # High empathy reducers
            for block in ["VALIDATION", "ACKNOWLEDGMENT", "TOGETHERNESS"]:
                if block in priorities:
                    delta = -0.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="empathy:low_reduces",
                        final_priority=priorities[block]
                    ))
    
    @staticmethod
    def _apply_skepticism_modulation(
        priorities: Dict[str, float],
        remnants: Dict[str, float],
        adjustments: List[BlockPriorityAdjustment]
    ) -> None:
        """
        Adjust blocks based on SKEPTICISM level.
        
        High skepticism (>0.7):
        - Boost AMBIVALENCE, DOUBT, CHALLENGE, QUESTIONING
        - Reduce AGREEMENT, OPENNESS
        
        Low skepticism (<0.3):
        - Boost AGREEMENT, OPENNESS, SAFETY, TRUST
        - Reduce DOUBT, CHALLENGE
        """
        skepticism = remnants.get("skepticism", 0.0)
        
        if skepticism > 0.7:
            for block in ["AMBIVALENCE", "DOUBT", "CHALLENGE", "QUESTIONING", "CAUTION"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="skepticism:high",
                        final_priority=priorities[block]
                    ))
            
            for block in ["AGREEMENT", "OPENNESS", "TRUST"]:
                if block in priorities:
                    delta = -1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="skepticism:high_reduces",
                        final_priority=priorities[block]
                    ))
        
        elif skepticism < 0.3:
            for block in ["AGREEMENT", "OPENNESS", "SAFETY", "TRUST", "VALIDATION"]:
                if block in priorities:
                    delta = 1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="skepticism:low",
                        final_priority=priorities[block]
                    ))
            
            for block in ["DOUBT", "CHALLENGE", "QUESTIONING"]:
                if block in priorities:
                    delta = -0.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="skepticism:low_reduces",
                        final_priority=priorities[block]
                    ))
    
    @staticmethod
    def _apply_authority_modulation(
        priorities: Dict[str, float],
        remnants: Dict[str, float],
        adjustments: List[BlockPriorityAdjustment]
    ) -> None:
        """
        Adjust blocks based on AUTHORITY level.
        
        High authority (>0.7):
        - Boost GENTLE_DIRECTION, WISDOM, COMMITMENT, CONVICTION
        - Reduce UNCERTAINTY, QUESTIONING
        
        Low authority (<0.3):
        - Boost QUESTIONING, EXPLORATION, UNCERTAINTY, VULNERABILITY
        - Reduce COMMITMENT, CONVICTION
        """
        authority = remnants.get("authority", 0.0)
        
        if authority > 0.7:
            for block in ["GENTLE_DIRECTION", "WISDOM", "COMMITMENT", "CONVICTION", "SUGGESTION"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="authority:high",
                        final_priority=priorities[block]
                    ))
            
            for block in ["UNCERTAINTY", "QUESTIONING", "EXPLORATION"]:
                if block in priorities:
                    delta = -0.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="authority:high_reduces",
                        final_priority=priorities[block]
                    ))
        
        elif authority < 0.3:
            for block in ["QUESTIONING", "EXPLORATION", "UNCERTAINTY", "VULNERABILITY", "AMBIVALENCE"]:
                if block in priorities:
                    delta = 1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="authority:low",
                        final_priority=priorities[block]
                    ))
            
            for block in ["COMMITMENT", "CONVICTION", "GENTLE_DIRECTION"]:
                if block in priorities:
                    delta = -0.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="authority:low_reduces",
                        final_priority=priorities[block]
                    ))
    
    @staticmethod
    def _apply_need_modulation(
        priorities: Dict[str, float],
        remnants: Dict[str, float],
        adjustments: List[BlockPriorityAdjustment]
    ) -> None:
        """
        Adjust blocks based on NEED level.
        
        High need (>0.7):
        - Boost CONTAINMENT, TOGETHERNESS, RELATIONAL, SAFETY
        - Reduce INDEPENDENCE, DISTANCE, SOLITUDE
        
        Low need (<0.3):
        - Boost INDEPENDENCE, SOLITUDE, DISTANCE
        - Reduce CONTAINMENT, TOGETHERNESS
        """
        need = remnants.get("need", 0.0)
        
        if need > 0.7:
            for block in ["CONTAINMENT", "TOGETHERNESS", "RELATIONAL", "SAFETY", "ACKNOWLEDGMENT"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="need:high",
                        final_priority=priorities[block]
                    ))
            
            for block in ["INDEPENDENCE", "DISTANCE", "SOLITUDE"]:
                if block in priorities:
                    delta = -0.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="need:high_reduces",
                        final_priority=priorities[block]
                    ))
        
        elif need < 0.3:
            for block in ["INDEPENDENCE", "SOLITUDE", "DISTANCE", "EXPLORATION"]:
                if block in priorities:
                    delta = 1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="need:low",
                        final_priority=priorities[block]
                    ))
            
            for block in ["CONTAINMENT", "TOGETHERNESS", "RELATIONAL"]:
                if block in priorities:
                    delta = -0.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="need:low_reduces",
                        final_priority=priorities[block]
                    ))
    
    @staticmethod
    def _apply_trust_modulation(
        priorities: Dict[str, float],
        remnants: Dict[str, float],
        adjustments: List[BlockPriorityAdjustment]
    ) -> None:
        """
        Adjust blocks based on TRUST level.
        
        High trust (>0.7):
        - Boost COLLABORATION, OPENNESS, AGREEMENT, VULNERABILITY
        
        Low trust (<0.3):
        - Boost CAUTION, PROTECTION, SKEPTICISM, DISTANCE
        """
        trust = remnants.get("trust", 0.0)
        
        if trust > 0.7:
            for block in ["COLLABORATION", "OPENNESS", "AGREEMENT", "VULNERABILITY", "RELATIONAL"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="trust:high",
                        final_priority=priorities[block]
                    ))
        
        elif trust < 0.3:
            for block in ["CAUTION", "PROTECTION", "SKEPTICISM", "DISTANCE", "DOUBT"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="trust:low",
                        final_priority=priorities[block]
                    ))
            
            for block in ["COLLABORATION", "OPENNESS", "VULNERABILITY"]:
                if block in priorities:
                    delta = -1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="trust:low_reduces",
                        final_priority=priorities[block]
                    ))
    
    @staticmethod
    def _apply_memory_modulation(
        priorities: Dict[str, float],
        remnants: Dict[str, float],
        adjustments: List[BlockPriorityAdjustment]
    ) -> None:
        """
        Adjust blocks based on MEMORY level.
        
        High memory (>0.7):
        - Boost CONTINUITY, REFERENCE, HISTORY
        
        Low memory (<0.3):
        - Boost PRESENT, NOVELTY, IMMEDIACY
        """
        memory = remnants.get("memory", 0.0)
        
        if memory > 0.7:
            for block in ["CONTINUITY", "REFERENCE", "HISTORY"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="memory:high",
                        final_priority=priorities[block]
                    ))
        
        elif memory < 0.3:
            for block in ["PRESENT", "NOVELTY", "IMMEDIACY"]:
                if block in priorities:
                    delta = 1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="memory:low",
                        final_priority=priorities[block]
                    ))
    
    @staticmethod
    def _apply_resolve_modulation(
        priorities: Dict[str, float],
        remnants: Dict[str, float],
        adjustments: List[BlockPriorityAdjustment]
    ) -> None:
        """
        Adjust blocks based on RESOLVE level.
        
        High resolve (>0.7):
        - Boost COMMITMENT, CONVICTION, BREAKTHROUGH
        
        Low resolve (<0.3):
        - Boost AMBIVALENCE, UNCERTAINTY, WAVERING
        """
        resolve = remnants.get("resolve", 0.0)
        
        if resolve > 0.7:
            for block in ["COMMITMENT", "CONVICTION", "BREAKTHROUGH"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="resolve:high",
                        final_priority=priorities[block]
                    ))
        
        elif resolve < 0.3:
            for block in ["AMBIVALENCE", "UNCERTAINTY", "QUESTIONING"]:
                if block in priorities:
                    delta = 1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="resolve:low",
                        final_priority=priorities[block]
                    ))
    
    @staticmethod
    def _apply_courage_modulation(
        priorities: Dict[str, float],
        remnants: Dict[str, float],
        adjustments: List[BlockPriorityAdjustment]
    ) -> None:
        """
        Adjust blocks based on COURAGE level.
        
        High courage (>0.7):
        - Boost VULNERABILITY, BREAKTHROUGH, COMMITMENT
        
        Low courage (<0.3):
        - Boost PROTECTION, RETREAT, CAUTION
        """
        courage = remnants.get("courage", 0.0)
        
        if courage > 0.7:
            for block in ["VULNERABILITY", "BREAKTHROUGH", "COMMITMENT"]:
                if block in priorities:
                    delta = 1.5
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="courage:high",
                        final_priority=priorities[block]
                    ))
        
        elif courage < 0.3:
            for block in ["PROTECTION", "RETREAT", "CAUTION", "DISTANCE"]:
                if block in priorities:
                    delta = 1.0
                    priorities[block] += delta
                    adjustments.append(BlockPriorityAdjustment(
                        block_name=block,
                        original_priority=priorities[block] - delta,
                        delta=delta,
                        source="courage:low",
                        final_priority=priorities[block]
                    ))
