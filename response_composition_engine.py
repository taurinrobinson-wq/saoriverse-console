"""
Response Composition Engine

Block-based response generator that composes responses from semantic blocks
rather than templates. Each block is independently activated by semantic tags.

Block Types:
- ContainmentBlock: Safety, grounding ("I'm here with you")
- ValidationBlock: Normalization ("That makes sense")
- PacingBlock: Slowing tempo ("We can take this slowly")
- AcknowledgmentBlock: Reflecting content ("I hear what you're saying")
- AmbivalenceBlock: Holding contradictions ("It's okay to feel more than one thing")
- TrustBlock: Reinforcing safety ("Thank you for sharing")
- IdentityInjuryBlock: Reflecting agency loss ("That took something from you")
- GentleDirectionBlock: Opening next step without pressure ("What part feels most present")
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum


class BlockType(Enum):
    """Types of response blocks"""
    CONTAINMENT = "containment"
    VALIDATION = "validation"
    PACING = "pacing"
    ACKNOWLEDGMENT = "acknowledgment"
    AMBIVALENCE = "ambivalence"
    TRUST = "trust"
    IDENTITY_INJURY = "identity_injury"
    GENTLE_DIRECTION = "gentle_direction"


@dataclass
class ResponseBlock:
    """A self-contained semantic response unit"""
    type: BlockType
    content: str
    semantic_trigger: str  # What semantic tag triggered this
    emotional_weight: float  # 0.0-1.0 intensity
    order_priority: int  # Lower = earlier in response
    forbidden_with: List[BlockType] = None  # Blocks that can't appear together
    requires_context: Optional[str] = None  # Required context to activate

    def __post_init__(self):
        if self.forbidden_with is None:
            self.forbidden_with = []


@dataclass
class ComposedResponse:
    """A response composed from multiple blocks"""
    blocks: List[ResponseBlock]
    full_text: str
    safety_level: float  # 0.0-1.0
    attunement_level: float  # 0.0-1.0
    pacing_appropriate: bool
    contains_forbidden_content: bool  # analysis, advice, interrogation


class ResponseBlockLibrary:
    """
    Library of semantic response blocks.
    Each block is independently composable and semantically meaningful.
    """

    def __init__(self):
        """Initialize the block library with core response blocks"""
        
        # CONTAINMENT BLOCKS - Create safety and ground
        self.containment_blocks = {
            "presence": ResponseBlock(
                type=BlockType.CONTAINMENT,
                content="I'm here with you.",
                semantic_trigger="containment_need",
                emotional_weight=0.3,
                order_priority=1,
                forbidden_with=[]
            ),
            "grounding": ResponseBlock(
                type=BlockType.CONTAINMENT,
                content="Take your time with this.",
                semantic_trigger="pace_slowing_need",
                emotional_weight=0.3,
                order_priority=1,
                forbidden_with=[]
            ),
            "safety_affirmation": ResponseBlock(
                type=BlockType.CONTAINMENT,
                content="What you're feeling is safe to feel here.",
                semantic_trigger="safety_need",
                emotional_weight=0.4,
                order_priority=1,
                forbidden_with=[]
            ),
        }
        
        # VALIDATION BLOCKS - Normalize and affirm experience
        self.validation_blocks = {
            "normalizing": ResponseBlock(
                type=BlockType.VALIDATION,
                content="That makes sense given what you're carrying.",
                semantic_trigger="validation_need",
                emotional_weight=0.4,
                order_priority=2,
                forbidden_with=[]
            ),
            "weight_acknowledgment": ResponseBlock(
                type=BlockType.VALIDATION,
                content="This is significant. It matters.",
                semantic_trigger="emotional_weight_high",
                emotional_weight=0.5,
                order_priority=2,
                forbidden_with=[]
            ),
            "experience_validation": ResponseBlock(
                type=BlockType.VALIDATION,
                content="Your experience is real and it counts.",
                semantic_trigger="identity_signals",
                emotional_weight=0.4,
                order_priority=2,
                forbidden_with=[]
            ),
        }
        
        # PACING BLOCKS - Manage tempo and depth
        self.pacing_blocks = {
            "slow_tempo": ResponseBlock(
                type=BlockType.PACING,
                content="We can take this at whatever pace feels right for you.",
                semantic_trigger="disclosure_pace_testing",
                emotional_weight=0.3,
                order_priority=3,
                forbidden_with=[BlockType.GENTLE_DIRECTION]
            ),
            "permission_slowness": ResponseBlock(
                type=BlockType.PACING,
                content="There's no rush here.",
                semantic_trigger="pace_slowing_need",
                emotional_weight=0.2,
                order_priority=3,
                forbidden_with=[BlockType.GENTLE_DIRECTION]
            ),
            "depth_opening": ResponseBlock(
                type=BlockType.PACING,
                content="When you're ready, we can go deeper with this.",
                semantic_trigger="readiness_signal",
                emotional_weight=0.4,
                order_priority=3,
                forbidden_with=[]
            ),
        }
        
        # ACKNOWLEDGMENT BLOCKS - Reflect what's being shared
        self.acknowledgment_blocks = {
            "basic_hearing": ResponseBlock(
                type=BlockType.ACKNOWLEDGMENT,
                content="I hear what you're saying.",
                semantic_trigger="conversational_move_naming",
                emotional_weight=0.2,
                order_priority=2,
                forbidden_with=[]
            ),
            "specific_reflection": ResponseBlock(
                type=BlockType.ACKNOWLEDGMENT,
                content="You're naming something that was real.",
                semantic_trigger="naming_experience_move",
                emotional_weight=0.3,
                order_priority=2,
                forbidden_with=[]
            ),
            "fact_recognition": ResponseBlock(
                type=BlockType.ACKNOWLEDGMENT,
                content="These facts matter. The time, the scale, the children—all of it matters.",
                semantic_trigger="identity_duration_markers",
                emotional_weight=0.4,
                order_priority=2,
                forbidden_with=[]
            ),
        }
        
        # AMBIVALENCE BLOCKS - Hold contradictions
        self.ambivalence_blocks = {
            "contradiction_permission": ResponseBlock(
                type=BlockType.AMBIVALENCE,
                content="It's okay to feel more than one thing at once.",
                semantic_trigger="emotional_contradiction",
                emotional_weight=0.5,
                order_priority=4,
                forbidden_with=[]
            ),
            "dual_truth_holding": ResponseBlock(
                type=BlockType.AMBIVALENCE,
                content="Both things are true. Relief and grief. Clarity and not knowing. You can hold them together.",
                semantic_trigger="contradiction_present",
                emotional_weight=0.6,
                order_priority=4,
                forbidden_with=[]
            ),
            "paradox_normalization": ResponseBlock(
                type=BlockType.AMBIVALENCE,
                content="That contradiction is where the real work is.",
                semantic_trigger="contradiction_high_tension",
                emotional_weight=0.5,
                order_priority=4,
                forbidden_with=[]
            ),
        }
        
        # TRUST BLOCKS - Reinforce safety in disclosure
        self.trust_blocks = {
            "gratitude_for_sharing": ResponseBlock(
                type=BlockType.TRUST,
                content="Thank you for sharing that with me.",
                semantic_trigger="trust_increase",
                emotional_weight=0.3,
                order_priority=5,
                forbidden_with=[]
            ),
            "trust_continuity": ResponseBlock(
                type=BlockType.TRUST,
                content="The more you share, the more I understand.",
                semantic_trigger="disclosure_progression",
                emotional_weight=0.4,
                order_priority=5,
                forbidden_with=[]
            ),
        }
        
        # IDENTITY INJURY BLOCKS - Reflect agency loss and power dynamics
        self.identity_injury_blocks = {
            "agency_loss_recognition": ResponseBlock(
                type=BlockType.IDENTITY_INJURY,
                content="It sounds like that took something from you. Your sense of what you could do, what you could be.",
                semantic_trigger="agency_loss",
                emotional_weight=0.6,
                order_priority=4,
                forbidden_with=[]
            ),
            "wound_acknowledgment": ResponseBlock(
                type=BlockType.IDENTITY_INJURY,
                content="Those words—undermined, pushed down—those point to something real about what happened to you.",
                semantic_trigger="impact_words_present",
                emotional_weight=0.6,
                order_priority=4,
                forbidden_with=[]
            ),
            "entanglement_recognition": ResponseBlock(
                type=BlockType.IDENTITY_INJURY,
                content="Eighteen years is a long time to be someone's partner. It gets into who you are.",
                semantic_trigger="identity_entanglement",
                emotional_weight=0.5,
                order_priority=4,
                forbidden_with=[]
            ),
        }
        
        # GENTLE DIRECTION BLOCKS - Open to next steps without pressure
        self.gentle_direction_blocks = {
            "exploratory_opening": ResponseBlock(
                type=BlockType.GENTLE_DIRECTION,
                content="What part of this feels most present for you right now?",
                semantic_trigger="ready_to_explore",
                emotional_weight=0.3,
                order_priority=6,
                forbidden_with=[BlockType.PACING],
                requires_context="emotional_emergence"
            ),
            "deeper_invitation": ResponseBlock(
                type=BlockType.GENTLE_DIRECTION,
                content="If you want to go deeper with any of this, I'm here.",
                semantic_trigger="readiness_signal",
                emotional_weight=0.3,
                order_priority=6,
                forbidden_with=[BlockType.PACING],
                requires_context="full_disclosure"
            ),
        }

    def get_block(self, block_type: BlockType, block_name: str) -> Optional[ResponseBlock]:
        """Retrieve a specific block from the library"""
        libraries = {
            BlockType.CONTAINMENT: self.containment_blocks,
            BlockType.VALIDATION: self.validation_blocks,
            BlockType.PACING: self.pacing_blocks,
            BlockType.ACKNOWLEDGMENT: self.acknowledgment_blocks,
            BlockType.AMBIVALENCE: self.ambivalence_blocks,
            BlockType.TRUST: self.trust_blocks,
            BlockType.IDENTITY_INJURY: self.identity_injury_blocks,
            BlockType.GENTLE_DIRECTION: self.gentle_direction_blocks,
        }
        
        if block_type in libraries and block_name in libraries[block_type]:
            return libraries[block_type][block_name]
        return None

    def get_blocks_by_type(self, block_type: BlockType) -> Dict[str, ResponseBlock]:
        """Get all blocks of a specific type"""
        libraries = {
            BlockType.CONTAINMENT: self.containment_blocks,
            BlockType.VALIDATION: self.validation_blocks,
            BlockType.PACING: self.pacing_blocks,
            BlockType.ACKNOWLEDGMENT: self.acknowledgment_blocks,
            BlockType.AMBIVALENCE: self.ambivalence_blocks,
            BlockType.TRUST: self.trust_blocks,
            BlockType.IDENTITY_INJURY: self.identity_injury_blocks,
            BlockType.GENTLE_DIRECTION: self.gentle_direction_blocks,
        }
        return libraries.get(block_type, {})


class ResponseCompositionEngine:
    """
    Assembles responses from semantic blocks based on semantic layer activation.
    
    Process:
    1. Receive semantic layer from parser
    2. Consult activation matrix to determine which blocks activate
    3. Apply priority weighting to determine order
    4. Check for forbidden combinations
    5. Compose response by concatenating blocks with connectors
    6. Validate response quality (safety, attunement, pacing, content restrictions)
    """

    def __init__(self):
        self.library = ResponseBlockLibrary()

    def compose(
        self,
        activated_blocks: List[BlockType],
        priorities: Dict[BlockType, int],
        safety_required: bool = True,
        pacing_required: str = "slow"
    ) -> ComposedResponse:
        """
        Compose a response from activated blocks.
        
        Args:
            activated_blocks: List of block types to include
            priorities: Dict mapping block types to priority order
            safety_required: Whether response must include safety blocks
            pacing_required: "slow", "moderate", or "deep"
        
        Returns:
            ComposedResponse with full text and metadata
        """
        
        # Collect actual blocks
        blocks_to_use = []
        
        for block_type in activated_blocks:
            blocks = self.library.get_blocks_by_type(block_type)
            if blocks:
                # Use first block of each type (can be refined)
                block = next(iter(blocks.values()))
                blocks_to_use.append(block)
        
        # Sort by priority
        blocks_to_use.sort(key=lambda b: b.order_priority)
        
        # Check for forbidden combinations
        forbidden_pairs = self._check_forbidden_combinations(blocks_to_use)
        if forbidden_pairs:
            blocks_to_use = self._resolve_conflicts(blocks_to_use, forbidden_pairs)
        
        # Compose text
        block_texts = [block.content for block in blocks_to_use]
        full_text = " ".join(block_texts)
        
        # Calculate quality metrics
        safety_level = self._calculate_safety(blocks_to_use, safety_required)
        attunement_level = self._calculate_attunement(blocks_to_use)
        pacing_appropriate = self._validate_pacing(blocks_to_use, pacing_required)
        contains_forbidden = self._check_forbidden_content(full_text)
        
        return ComposedResponse(
            blocks=blocks_to_use,
            full_text=full_text,
            safety_level=safety_level,
            attunement_level=attunement_level,
            pacing_appropriate=pacing_appropriate,
            contains_forbidden_content=contains_forbidden
        )

    def _check_forbidden_combinations(self, blocks: List[ResponseBlock]) -> List[tuple]:
        """Check for incompatible block combinations"""
        conflicts = []
        for i, block1 in enumerate(blocks):
            for block2 in blocks[i+1:]:
                if block2.type in block1.forbidden_with:
                    conflicts.append((block1.type, block2.type))
        return conflicts

    def _resolve_conflicts(
        self,
        blocks: List[ResponseBlock],
        conflicts: List[tuple]
    ) -> List[ResponseBlock]:
        """Remove lower-priority blocks from conflicts"""
        block_types_to_remove = set()
        
        for type1, type2 in conflicts:
            # Keep type1, remove type2 (arbitrary but deterministic)
            block_types_to_remove.add(type2)
        
        return [b for b in blocks if b.type not in block_types_to_remove]

    def _calculate_safety(self, blocks: List[ResponseBlock], required: bool) -> float:
        """Calculate safety level based on containment/grounding blocks"""
        has_containment = any(b.type == BlockType.CONTAINMENT for b in blocks)
        has_pacing = any(b.type == BlockType.PACING for b in blocks)
        
        if required and not has_containment:
            return 0.3
        
        base = 0.7 if has_containment else 0.4
        bonus = 0.2 if has_pacing else 0.0
        return min(1.0, base + bonus)

    def _calculate_attunement(self, blocks: List[ResponseBlock]) -> float:
        """Calculate attunement level based on block composition"""
        has_validation = any(b.type == BlockType.VALIDATION for b in blocks)
        has_acknowledgment = any(b.type == BlockType.ACKNOWLEDGMENT for b in blocks)
        has_ambivalence = any(b.type == BlockType.AMBIVALENCE for b in blocks)
        has_identity = any(b.type == BlockType.IDENTITY_INJURY for b in blocks)
        
        count = sum([has_validation, has_acknowledgment, has_ambivalence, has_identity])
        return min(1.0, 0.2 + (count * 0.2))

    def _validate_pacing(self, blocks: List[ResponseBlock], required_pace: str) -> bool:
        """Validate pacing matches requirements"""
        has_pacing = any(b.type == BlockType.PACING for b in blocks)
        has_direction = any(b.type == BlockType.GENTLE_DIRECTION for b in blocks)
        
        if required_pace in ["slow", "testing"]:
            # Slow pacing should have containment + pacing, avoid direction
            return has_pacing and not has_direction
        
        if required_pace == "deep":
            # Deep pacing can include direction
            return True
        
        return True

    def _check_forbidden_content(self, text: str) -> bool:
        """Check for analysis, advice, or interrogation"""
        forbidden_patterns = [
            r"have you considered",
            r"you should",
            r"you could try",
            r"what if",
            r"why did you",
            r"let me analyze",
            r"the problem is",
            r"you need to",
            r"the solution",
        ]
        
        text_lower = text.lower()
        for pattern in forbidden_patterns:
            if pattern in text_lower:
                return True
        
        return False
