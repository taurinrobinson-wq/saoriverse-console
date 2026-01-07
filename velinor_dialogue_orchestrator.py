"""
🌌 VELINOR DIALOGUE ORCHESTRATOR
================================

The runtime layer that weaves the semantic engine into Velinor's emotional narrative system.

This orchestrator:
1. Receives player messages and routes to semantic parsing
2. Updates semantic continuity across turns
3. Computes activated blocks based on semantic attributes
4. Applies priority resolution (faction + persona-specific)
5. Composes semantic blocks into responses
6. Applies NPC persona styling
7. Updates REMNANTS and emotional OS state
8. Records quality metrics for analytics

The semantic engine becomes the FIRST PASS at meaning.
Velinor's systems (persona, faction, REMNANTS) become the SECOND PASS at personality.

Flow:
    player_message
        → [SemanticParser] → 7 semantic layers
        → [ContinuityEngine] → conversation history update
        → [ActivationMatrix] → activated blocks
        → [PriorityWeighting] → ordered blocks (with faction overrides)
        → [ResponseCompositionEngine] → composed semantic response
        → [PersonaAdapter] → NPC-specific styling + REMNANTS application
        → [RemnantsEngine] → emotional OS update
        → npc_response
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import json
from datetime import datetime

# Imports from semantic engine modules
# NOTE: These should exist from your v2.0 implementation
try:
    from semantic_parsing_schema import SemanticLayer
    from activation_matrix import ActivationMatrix
    from priority_weighting import PriorityWeightingSystem, PriorityLevel
    from response_composition_engine import ResponseCompositionEngine, BlockType
    from continuity_engine import ContinuityEngine, ConversationContinuity
except ImportError as e:
    print(f"Warning: Could not import semantic engine modules: {e}")
    print("Make sure semantic engine modules are in the same directory.")


@dataclass
class NPCPersona:
    """Configuration for an NPC's semantic behavior and personality."""
    npc_id: str
    npc_name: str
    faction: str  # e.g., "Elenya's Guardians", "Malrik's Architects", "Nima's Weavers"
    
    # Personality traits that filter block composition
    tone: str  # e.g., "analytical", "nurturing", "grounded", "mystical"
    emotional_logic: str  # What this NPC values emotionally
    linguistic_style: str  # How this NPC speaks
    
    # Semantic alignment: what this NPC prioritizes
    priority_overrides: Dict[str, PriorityLevel] = field(default_factory=dict)
    # Example: {"contradictions": PriorityLevel.SAFETY_CONTAINMENT}
    
    # Block type preferences (which blocks feel authentic to this NPC)
    preferred_blocks: Set[BlockType] = field(default_factory=set)
    forbidden_blocks: Set[BlockType] = field(default_factory=set)
    
    # How this NPC modulates blocks based on REMNANTS
    remnants_sensitivity: Dict[str, float] = field(default_factory=dict)
    # Example: {"identity_injury": 1.5, "trust_damage": 0.8}
    
    # Faction philosophy (maps to semantic concepts)
    faction_stance: str  # How this NPC's faction views emotional stances
    faction_pacing: str  # How this NPC's faction views disclosure pacing
    
    # Response templates (the "flavor" for each block type)
    block_phrases: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class DialogueContext:
    """Full context for a single dialogue turn."""
    player_id: str
    npc_id: str
    player_message: str
    semantic_layer: Optional[SemanticLayer] = None
    conversation_continuity: Optional[ConversationContinuity] = None
    npc_persona: Optional[NPCPersona] = None
    remnants_state: Dict[str, Any] = field(default_factory=dict)
    activated_blocks: Set[BlockType] = field(default_factory=set)
    priorities: Dict[str, Any] = field(default_factory=dict)
    response_quality: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DialogueResponse:
    """The fully composed response from orchestrator."""
    npc_response_text: str
    activated_blocks: List[str]
    safety_level: float
    attunement_level: float
    pacing_appropriate: bool
    contains_forbidden_content: bool
    quality_score: float
    updated_continuity: Optional[ConversationContinuity] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class VelinorDialogueOrchestrator:
    """
    Main orchestrator that wires semantic engine into Velinor's dialogue system.
    
    This is where:
    - semantic understanding meets NPC personality
    - universal emotional logic meets faction-specific behavior
    - player REMNANTS influence dialogue tone and pacing
    - conversations become emergent narratives
    """
    
    def __init__(self):
        self.semantic_parser = None  # Injected from calling code
        self.activation_matrix = ActivationMatrix()
        self.priority_weighting = PriorityWeightingSystem()
        self.response_composer = ResponseCompositionEngine()
        self.continuity_engine = ContinuityEngine()
        
        # NPC personas (loaded from persona files or config)
        self.npc_personas: Dict[str, NPCPersona] = {}
        
        # Conversation continuity tracking (per player)
        self.player_continuities: Dict[str, ConversationContinuity] = {}
        
        # REMNANTS state (injected from RemnantsEngine)
        self.remnants_engine = None
        
    def register_npc_persona(self, persona: NPCPersona) -> None:
        """Register an NPC's persona configuration."""
        self.npc_personas[persona.npc_id] = persona
    
    def handle_player_message(
        self,
        player_id: str,
        npc_id: str,
        player_message: str,
        semantic_parser=None,  # Injected SemanticParser instance
        remnants_engine=None,  # Injected RemnantsEngine instance
    ) -> DialogueResponse:
        """
        Main entry point: receive player message, return NPC response.
        
        This orchestrates the complete flow:
        1. Parse semantic meaning
        2. Update conversation continuity
        3. Activate response blocks
        4. Resolve priorities with faction/persona logic
        5. Compose semantic response
        6. Apply NPC personality
        7. Update REMNANTS state
        8. Record quality metrics
        
        Args:
            player_id: Unique player identifier
            npc_id: Target NPC identifier
            player_message: Raw player input text
            semantic_parser: SemanticParser instance (injected)
            remnants_engine: RemnantsEngine instance (injected)
        
        Returns:
            DialogueResponse with composed NPC response and metadata
        """
        
        # Create context object
        context = DialogueContext(
            player_id=player_id,
            npc_id=npc_id,
            player_message=player_message,
        )
        
        # ============================================
        # STEP 1: SEMANTIC PARSING
        # ============================================
        
        if semantic_parser is None:
            raise ValueError("semantic_parser must be injected")
        
        context.semantic_layer = semantic_parser.parse(player_message)
        
        # ============================================
        # STEP 2: UPDATE CONTINUITY
        # ============================================
        
        # Ensure we have continuity tracking for this player
        if player_id not in self.player_continuities:
            self.player_continuities[player_id] = ConversationContinuity()
        
        continuity = self.player_continuities[player_id]
        
        # Update continuity with new semantic layer
        continuity_index = continuity.turn_count
        self.continuity_engine.update_from_semantic_layer(
            context.semantic_layer,
            continuity_index
        )
        
        context.conversation_continuity = continuity
        
        # ============================================
        # STEP 3: ACTIVATION MATRIX
        # ============================================
        
        # Compute which blocks should activate based on semantic meaning
        activated_blocks = self.activation_matrix.compute_full_activation(
            stance=context.semantic_layer.stance if context.semantic_layer else None,
            pacing=context.semantic_layer.pacing if context.semantic_layer else None,
            moves=context.semantic_layer.moves if context.semantic_layer else [],
            dynamics=context.semantic_layer.dynamics if context.semantic_layer else None,
            needs=context.semantic_layer.implied_needs if context.semantic_layer else [],
            contradictions=bool(context.semantic_layer.contradictions) if context.semantic_layer else False,
            impact_words=bool(context.semantic_layer.impact_words) if context.semantic_layer else False,
            emotional_weight=context.semantic_layer.emotional_weight if context.semantic_layer else 0.5,
            identity_signals=len(context.semantic_layer.identity_signals) if context.semantic_layer else 0,
            readiness=getattr(context.semantic_layer, 'readiness', False),
        )
        
        context.activated_blocks = activated_blocks
        
        # ============================================
        # STEP 4: PRIORITY WEIGHTING + FACTION OVERRIDE
        # ============================================
        
        # Load NPC persona
        if npc_id not in self.npc_personas:
            raise ValueError(f"NPC persona not registered: {npc_id}")
        
        context.npc_persona = self.npc_personas[npc_id]
        persona = context.npc_persona
        
        # Compute priorities with faction/persona overrides
        priorities = self._compute_priorities_with_faction_logic(
            context.semantic_layer,
            persona,
            continuity,
        )
        
        context.priorities = priorities
        
        # ============================================
        # STEP 5: RESPONSE COMPOSITION
        # ============================================
        
        # Compose the semantic response
        composed_response = self.response_composer.compose(
            activated_blocks=activated_blocks,
            priorities=priorities,
            safety_required=persona.faction_stance.lower() not in ["analytical", "mystical"],
            pacing_required=persona.faction_pacing,
        )
        
        # ============================================
        # STEP 6: PERSONA STYLING + REMNANTS APPLICATION
        # ============================================
        
        # Load REMNANTS state
        if remnants_engine is None:
            raise ValueError("remnants_engine must be injected")
        
        remnants_state = remnants_engine.get_player_state(player_id)
        context.remnants_state = remnants_state
        
        # Apply persona styling to the composed response
        npc_response_text = self._apply_persona_style(
            composed_response.full_text,
            composed_response.blocks,
            persona,
            remnants_state,
            context.semantic_layer,
        )
        
        # ============================================
        # STEP 7: UPDATE REMNANTS STATE
        # ============================================
        
        # Map semantic findings to REMNANTS state updates
        self._update_remnants_from_semantic(
            player_id,
            context.semantic_layer,
            continuity,
            remnants_engine,
        )
        
        # ============================================
        # STEP 8: RECORD QUALITY METRICS
        # ============================================
        
        # Record response quality for analytics
        self.continuity_engine.record_response_quality(
            safety=composed_response.safety_level,
            attunement=composed_response.attunement_level,
        )
        
        context.response_quality = {
            "safety": composed_response.safety_level,
            "attunement": composed_response.attunement_level,
            "pacing_appropriate": composed_response.pacing_appropriate,
            "quality_score": (
                composed_response.safety_level * 0.4 +
                composed_response.attunement_level * 0.4 +
                (1.0 if composed_response.pacing_appropriate else 0.0) * 0.2
            ),
        }
        
        # ============================================
        # BUILD RESPONSE OBJECT
        # ============================================
        
        return DialogueResponse(
            npc_response_text=npc_response_text,
            activated_blocks=[str(b) for b in composed_response.blocks],
            safety_level=composed_response.safety_level,
            attunement_level=composed_response.attunement_level,
            pacing_appropriate=composed_response.pacing_appropriate,
            contains_forbidden_content=composed_response.contains_forbidden_content,
            quality_score=context.response_quality.get("quality_score", 0.5),
            updated_continuity=continuity,
            metadata={
                "semantic_layer": str(context.semantic_layer),
                "activated_blocks": [str(b) for b in activated_blocks],
                "npc_persona": persona.npc_name,
                "faction": persona.faction,
                "timestamp": context.timestamp.isoformat(),
            },
        )
    
    def _compute_priorities_with_faction_logic(
        self,
        semantic_layer: SemanticLayer,
        persona: NPCPersona,
        continuity: ConversationContinuity,
    ) -> Dict[str, Any]:
        """
        Compute block priorities with faction and persona modifications.
        
        This is where Velinor's world logic becomes the emotional physics.
        
        Each faction prioritizes different semantic attributes:
        - Elenya's Guardians: contradictions + identity injury
        - Malrik's Architects: stance + logic coherence
        - Nima's Weavers: pacing + emotional safety
        - Coren's Keepers: trust + emotional containment
        
        The priority system becomes faction-specific behavior.
        """
        
        # Start with universal priority extraction
        priorities = self.priority_weighting.extract_priority_elements(
            stance=semantic_layer.stance if semantic_layer else None,
            pacing=semantic_layer.pacing if semantic_layer else None,
            moves=semantic_layer.moves if semantic_layer else [],
            dynamics=semantic_layer.dynamics if semantic_layer else None,
            needs=semantic_layer.implied_needs if semantic_layer else [],
            contradictions=bool(semantic_layer.contradictions) if semantic_layer else False,
            impact_words=bool(semantic_layer.impact_words) if semantic_layer else False,
            emotional_weight=semantic_layer.emotional_weight if semantic_layer else 0.5,
            identity_signals=len(semantic_layer.identity_signals) if semantic_layer else 0,
            readiness=getattr(semantic_layer, 'readiness', False),
        )
        
        # Apply persona/faction overrides
        for semantic_attr, override_level in persona.priority_overrides.items():
            # This would modify the priority level for specific attributes
            # based on faction philosophy
            pass
        
        return priorities
    
    def _apply_persona_style(
        self,
        semantic_text: str,
        activated_blocks: List,
        persona: NPCPersona,
        remnants_state: Dict[str, Any],
        semantic_layer: Optional[SemanticLayer],
    ) -> str:
        """
        Transform semantic blocks into persona-specific language.
        
        This is where the response becomes a *character*, not just a semantic output.
        
        Process:
        1. Start with semantic blocks (universal emotional meaning)
        2. Apply persona tone (how this character sounds)
        3. Apply faction vocabulary (mythic language, values)
        4. Apply REMNANTS modifiers (emotional OS state)
        5. Apply pacing adjustments (slow if overwhelmed, deepen if ready)
        6. Weave in character voice (linguistic style)
        
        Result: A response that is simultaneously:
        - emotionally accurate (semantic blocks)
        - character authentic (persona style)
        - lore consistent (faction vocabulary)
        - emotionally responsive (REMNANTS aware)
        - pacing aware (continuity state)
        """
        
        response_text = semantic_text
        
        # ============================================
        # Apply persona tone
        # ============================================
        
        if persona.tone == "analytical":
            response_text = self._apply_analytical_tone(response_text, activated_blocks)
        elif persona.tone == "nurturing":
            response_text = self._apply_nurturing_tone(response_text, activated_blocks)
        elif persona.tone == "grounded":
            response_text = self._apply_grounded_tone(response_text, activated_blocks)
        elif persona.tone == "mystical":
            response_text = self._apply_mystical_tone(response_text, activated_blocks)
        
        # ============================================
        # Apply faction vocabulary
        # ============================================
        
        faction_vocabulary = self._get_faction_vocabulary(persona.faction)
        response_text = self._inject_faction_language(
            response_text,
            faction_vocabulary,
            semantic_layer,
        )
        
        # ============================================
        # Apply REMNANTS modifiers
        # ============================================
        
        # If player is injured (identity wound), soften the response
        if remnants_state.get("identity_injury", 0) > 0.5:
            response_text = self._soften_for_identity_injury(response_text)
        
        # If player is building trust, deepen engagement
        if remnants_state.get("trust_level", 0) > 0.7:
            response_text = self._deepen_for_trust(response_text)
        
        # If player is overwhelmed, slow the pacing
        if semantic_layer and getattr(semantic_layer, 'emotional_weight', 0) > 0.8:
            response_text = self._slow_pacing(response_text)
        
        # If player is ready, invite deeper engagement
        if semantic_layer and getattr(semantic_layer, 'readiness', False):
            response_text = self._deepen_invitation(response_text)
        
        return response_text
    
    def _apply_analytical_tone(self, text: str, blocks: List) -> str:
        """Apply Malrik-style analytical language."""
        # This would transform blocks like:
        # ACKNOWLEDGMENT → "Noted. The structure of that is..."
        # VALIDATION → "That's logically coherent. Here's why..."
        return text  # Placeholder
    
    def _apply_nurturing_tone(self, text: str, blocks: List) -> str:
        """Apply Nima-style nurturing language."""
        return text  # Placeholder
    
    def _apply_grounded_tone(self, text: str, blocks: List) -> str:
        """Apply Coren-style grounded language."""
        return text  # Placeholder
    
    def _apply_mystical_tone(self, text: str, blocks: List) -> str:
        """Apply Elenya-style mystical language."""
        return text  # Placeholder
    
    def _get_faction_vocabulary(self, faction: str) -> Dict[str, str]:
        """Get faction-specific vocabulary replacements."""
        vocabularies = {
            "Elenya's Guardians": {
                "contradiction": "paradox",
                "truth": "resonance",
                "identity": "essence",
            },
            "Malrik's Architects": {
                "contradiction": "structural inconsistency",
                "truth": "logical coherence",
                "identity": "systemic integrity",
            },
            "Nima's Weavers": {
                "contradiction": "tension",
                "truth": "authenticity",
                "identity": "thread",
            },
        }
        return vocabularies.get(faction, {})
    
    def _inject_faction_language(
        self,
        text: str,
        vocabulary: Dict[str, str],
        semantic_layer: Optional[SemanticLayer],
    ) -> str:
        """Inject faction-specific language into response."""
        # This would replace generic terms with faction vocabulary
        for generic, faction_term in vocabulary.items():
            text = text.replace(generic, faction_term)
        return text
    
    def _soften_for_identity_injury(self, text: str) -> str:
        """Soften response when player has identity wound."""
        # Make language more tender, validating, less demanding
        return text  # Placeholder
    
    def _deepen_for_trust(self, text: str) -> str:
        """Deepen engagement when player has built trust."""
        # Ask deeper questions, invite more vulnerability
        return text  # Placeholder
    
    def _slow_pacing(self, text: str) -> str:
        """Slow the pacing when player is overwhelmed."""
        # Add breaks, simplify language, reduce complexity
        return text  # Placeholder
    
    def _deepen_invitation(self, text: str) -> str:
        """Invite deeper engagement when player is ready."""
        # Ask provocative questions, go deeper
        return text  # Placeholder
    
    def _update_remnants_from_semantic(
        self,
        player_id: str,
        semantic_layer: SemanticLayer,
        continuity: ConversationContinuity,
        remnants_engine,
    ) -> None:
        """
        Map semantic findings to REMNANTS state updates.
        
        This is where the semantic engine feeds the emotional OS.
        
        Mappings:
        - contradictions → glyph instability
        - identity_injury → shadow glyphs
        - stance arc → faction drift
        - trust progression → resonance growth
        - pacing changes → attunement shifts
        - agency loss → power dynamics
        """
        
        if semantic_layer is None:
            return
        
        remnants_update = {}
        
        # Map contradictions to glyph state
        if semantic_layer.contradictions:
            remnants_update["glyph_instability"] = len(semantic_layer.contradictions) * 0.25
        
        # Map identity injuries to shadow glyphs
        if semantic_layer.identity_signals:
            remnants_update["identity_injury"] = len(semantic_layer.identity_signals) * 0.2
        
        # Map stance to faction resonance
        if semantic_layer.stance:
            remnants_update["current_stance"] = str(semantic_layer.stance)
        
        # Map pacing to attunement
        if semantic_layer.pacing:
            remnants_update["current_pacing"] = str(semantic_layer.pacing)
        
        # Map emotional weight to overall resonance
        remnants_update["emotional_weight"] = semantic_layer.emotional_weight
        
        # Update REMNANTS engine
        remnants_engine.update_player_state(player_id, remnants_update)


# ============================================
# INTEGRATION HELPERS
# ============================================

def create_nima_persona() -> NPCPersona:
    """Nima: The Weaver - nurturing, pacing-aware, safety-focused."""
    return NPCPersona(
        npc_id="nima",
        npc_name="Nima",
        faction="Nima's Weavers",
        tone="nurturing",
        emotional_logic="safety and pacing",
        linguistic_style="gentle, attentive, thread-like",
        preferred_blocks={BlockType.PACING, BlockType.CONTAINMENT, BlockType.ACKNOWLEDGMENT},
        faction_stance="values slowing down and safety",
        faction_pacing="believes in gradual unfolding",
    )


def create_malrik_persona() -> NPCPersona:
    """Malrik: The Architect - analytical, coherence-seeking, logically rigorous."""
    return NPCPersona(
        npc_id="malrik",
        npc_name="Malrik",
        faction="Malrik's Architects",
        tone="analytical",
        emotional_logic="structural coherence and logic",
        linguistic_style="precise, architectural metaphors, rigorous",
        preferred_blocks={BlockType.VALIDATION, BlockType.ACKNOWLEDGMENT},
        faction_stance="values coherence and logical integrity",
        faction_pacing="believes contradictions must be resolved",
    )


def create_elenya_persona() -> NPCPersona:
    """Elenya: The Guardian - mystical, paradox-holding, spiritually attuned."""
    return NPCPersona(
        npc_id="elenya",
        npc_name="Elenya",
        faction="Elenya's Guardians",
        tone="mystical",
        emotional_logic="paradox and resonance",
        linguistic_style="poetic, paradoxical, resonant metaphors",
        preferred_blocks={BlockType.AMBIVALENCE, BlockType.IDENTITY_INJURY, BlockType.TRUST},
        faction_stance="values holding contradictions",
        faction_pacing="believes depth comes through paradox",
    )


def create_coren_persona() -> NPCPersona:
    """Coren: The Keeper - grounded, containment-focused, emotionally steady."""
    return NPCPersona(
        npc_id="coren",
        npc_name="Coren",
        faction="Coren's Keepers",
        tone="grounded",
        emotional_logic="emotional safety and trust",
        linguistic_style="steady, rooted, practical",
        preferred_blocks={BlockType.CONTAINMENT, BlockType.PACING, BlockType.TRUST},
        faction_stance="values emotional stability",
        faction_pacing="believes in steady, reliable presence",
    )
