"""
🎭 VELINOR DIALOGUE ORCHESTRATOR V2: The Complete Fusion Engine
===============================================================

This is the conductor. All instruments (semantic parser, TONE mapper, REMNANTS
engine, block modifiers, faction philosophy, persona styling) play together here.

The orchestrator receives player speech, conducts it through 11 stages, and
returns an emotionally responsive NPC reply that reflects:
1. Player's emotional posture (via semantic extraction)
2. NPC's emotional evolution (via REMNANTS)
3. NPC's personality (via persona styling)
4. Faction philosophy (via priority nudges)
5. Continuity across the conversation (via memory engine)

This makes Velinor dialogues emergent: same player choice produces different
responses depending on NPC's emotional state. Conversations have emotional arcs.

The flow:
    Player Speech
        ↓
    [1. Parse Semantic Layer]
        ↓
    [2. Update Continuity Record]
        ↓
    [3. Map Semantic → TONE Effects]
        ↓
    [4. Apply TONE to REMNANTS]
        ↓
    [5. Activate Dialogue Blocks]
        ↓
    [6. Compute Initial Block Priorities]
        ↓
    [7. Adjust Priorities by REMNANTS]
        ↓
    [8. Apply Faction Philosophy Nudges]
        ↓
    [9. Compose Response Text]
        ↓
    [10. Apply Persona + REMNANTS Styling]
        ↓
    [11. Record Quality Metrics]
        ↓
    NPC Response (emotionally intelligent, personality-authentic, faction-coherent)
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class DialogueQuality:
    """Metrics about the dialogue that just happened."""
    timestamp: str
    player_message_index: int
    semantic_emotional_weight: float
    tone_effects_count: int
    remnants_delta: Dict[str, float]
    blocks_activated: int
    blocks_selected: List[str]
    faction_nudges_applied: int
    final_remnants_state: Dict[str, float]
    quality_score: float = 0.0  # 0-100
    emotional_arc_continuity: float = 0.0  # How well this connects to prior messages


@dataclass
class ConversationContinuity:
    """Track the emotional/conversational arc across multiple turns."""
    npc_id: str
    npc_name: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    emotional_arc: Dict[str, List[float]] = field(default_factory=dict)  # trait -> values over time
    key_moments: List[Dict[str, Any]] = field(default_factory=list)  # Pivotal dialogue moments
    player_approach: str = "unknown"  # How is player engaging? (compassionate, clinical, dismissive)
    
    def record_turn(self, player_message: str, npc_response: str, remnants: Dict[str, float]) -> None:
        """Record a conversational turn and its emotional effects."""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "player_message": player_message,
            "npc_response": npc_response,
            "remnants_snapshot": dict(remnants),
        }
        self.conversation_history.append(turn)
        
        # Track emotional arc
        for trait, value in remnants.items():
            if trait not in self.emotional_arc:
                self.emotional_arc[trait] = []
            self.emotional_arc[trait].append(value)
    
    def get_arc_trajectory(self, trait: str) -> str:
        """Describe how a REMNANTS trait has evolved across conversation."""
        if trait not in self.emotional_arc or len(self.emotional_arc[trait]) < 2:
            return "undetermined"
        
        values = self.emotional_arc[trait]
        start, end = values[0], values[-1]
        delta = end - start
        
        if delta > 0.3:
            return "increasing"
        elif delta < -0.3:
            return "decreasing"
        else:
            return "stable"


class VelinorDialogueOrchestratorV2:
    """
    The complete dialogue fusion engine.
    
    Dependencies:
    - SemanticParser (extracts emotional meaning)
    - ToneMapper (semantic → TONE)
    - NPCManager (holds REMNANTS for each NPC)
    - DialogueBlockStore (holds all dialogue blocks)
    - ResponseCompositionEngine (composes text from blocks)
    - PersonaBase subclasses (applies voice styling)
    - RemnantsBlockModifiers (priority adjustment by emotion)
    - FactionPriorityOverrides (philosophy as nudges)
    - ContinuityEngine (tracks conversation arc)
    """
    
    def __init__(
        self,
        semantic_parser: Any,  # SemanticParser instance
        tone_mapper: Any,      # ToneMapper class
        npc_manager: Any,      # NPCManager with apply_tone_effects()
        block_store: Any,      # DialogueBlockStore with get_blocks()
        composition_engine: Any,  # ResponseCompositionEngine
        persona_map: Dict[str, Any],  # {npc_name: PersonaBase instance}
        continuity_engine: Any = None,  # Optional: ContinuityEngine
    ):
        """
        Initialize the orchestrator with all dependencies.
        """
        self.semantic_parser = semantic_parser
        self.tone_mapper = tone_mapper
        self.npc_manager = npc_manager
        self.block_store = block_store
        self.composition_engine = composition_engine
        self.persona_map = persona_map
        self.continuity_engine = continuity_engine
        
        # Track conversations across turns
        self.conversation_continuity: Dict[str, ConversationContinuity] = {}
        
        # Track dialogue quality metrics
        self.dialogue_quality_log: List[DialogueQuality] = []
    
    def handle_player_message(
        self,
        player_message: str,
        npc_id: str,
        npc_name: str,
        message_index: int = 0,
        **context
    ) -> str:
        """
        Main entry point: player speech → NPC response.
        
        This orchestrates all 11 stages of the fusion pipeline.
        
        Args:
            player_message: What the player said
            npc_id: Unique NPC identifier
            npc_name: Display name of NPC
            message_index: Turn number in conversation
            **context: Additional context (location, faction, etc.)
            
        Returns:
            NPC's response text
        """
        
        # ============ STAGE 1: Parse Semantic Layer ============
        semantic_layer = self._stage_1_parse_semantic(player_message)
        
        # ============ STAGE 2: Update Continuity Record ============
        continuity = self._stage_2_update_continuity(npc_id, npc_name)
        
        # ============ STAGE 3: Map Semantic → TONE ============
        tone_effects = self._stage_3_map_semantic_to_tone(semantic_layer)
        
        # ============ STAGE 4: Apply TONE to REMNANTS ============
        self._stage_4_apply_tone_to_remnants(npc_id, tone_effects)
        
        # ============ STAGE 5: Activate Dialogue Blocks ============
        available_blocks = self._stage_5_activate_blocks(npc_name, context)
        
        # ============ STAGE 6: Compute Initial Priorities ============
        block_priorities = self._stage_6_compute_initial_priorities(available_blocks)
        
        # ============ STAGE 7: Adjust by REMNANTS ============
        current_remnants = self.npc_manager.get_remnants(npc_id)
        block_priorities, remnants_adjustments = self._stage_7_adjust_by_remnants(
            block_priorities, current_remnants, npc_name
        )
        
        # ============ STAGE 8: Apply Faction Nudges ============
        faction = context.get("faction", self._infer_faction(npc_name))
        block_priorities, faction_nudges = self._stage_8_apply_faction_overrides(
            block_priorities, faction
        )
        
        # ============ STAGE 9: Compose Response ============
        composed_text = self._stage_9_compose_response(
            available_blocks, block_priorities, npc_name
        )
        
        # ============ STAGE 10: Apply Persona + REMNANTS Styling ============
        final_response = self._stage_10_apply_styling(
            composed_text, npc_name, current_remnants
        )
        
        # ============ STAGE 11: Record Quality Metrics ============
        self._stage_11_record_quality(
            message_index, semantic_layer, tone_effects, current_remnants,
            len(available_blocks), block_priorities, faction_nudges, final_response
        )
        
        # Record in continuity
        continuity.record_turn(player_message, final_response, current_remnants)
        
        return final_response
    
    # ========== THE 11 STAGES ==========
    
    def _stage_1_parse_semantic(self, player_message: str) -> Any:
        """
        Stage 1: Extract semantic layer from player message.
        
        Returns: SemanticLayer object with:
        - emotional_stance
        - disclosure_pace
        - emotional_contradictions
        - power_dynamics
        - implied_needs
        - meta_properties (emotional_weight, etc.)
        - identity_signals
        """
        if not hasattr(self, 'semantic_parser') or self.semantic_parser is None:
            # Fallback: return mock semantic layer
            return self._mock_semantic_layer(player_message)
        
        return self.semantic_parser.parse(player_message)
    
    def _stage_2_update_continuity(self, npc_id: str, npc_name: str) -> ConversationContinuity:
        """
        Stage 2: Ensure continuity tracking is active for this NPC.
        
        Creates a new continuity record if this is the first message.
        """
        if npc_id not in self.conversation_continuity:
            self.conversation_continuity[npc_id] = ConversationContinuity(
                npc_id=npc_id,
                npc_name=npc_name
            )
        
        return self.conversation_continuity[npc_id]
    
    def _stage_3_map_semantic_to_tone(self, semantic_layer: Any) -> Dict[str, float]:
        """
        Stage 3: Convert semantic findings to TONE effects.
        
        TONE effects are standardized emotional inputs that feed the REMNANTS engine.
        """
        return self.tone_mapper.map_semantics_to_tone(semantic_layer)
    
    def _stage_4_apply_tone_to_remnants(self, npc_id: str, tone_effects: Dict[str, float]) -> None:
        """
        Stage 4: Apply TONE effects to NPC's REMNANTS.
        
        This is where player emotion begins to shape NPC emotional state.
        """
        if hasattr(self.npc_manager, 'apply_tone_effects'):
            self.npc_manager.apply_tone_effects(npc_id, tone_effects)
    
    def _stage_5_activate_blocks(self, npc_name: str, context: Dict) -> List[Any]:
        """
        Stage 5: Get dialogue blocks available for this NPC in this context.
        
        Filtering by:
        - NPC name
        - Location/context
        - Conversation state
        """
        if not hasattr(self.block_store, 'get_blocks'):
            return []
        
        return self.block_store.get_blocks(
            npc_name=npc_name,
            context=context
        )
    
    def _stage_6_compute_initial_priorities(self, available_blocks: List[Any]) -> Dict[str, float]:
        """
        Stage 6: Get base priorities for each block.
        
        These come from the block definitions (base relevance to situation).
        """
        priorities = {}
        
        for block in available_blocks:
            block_name = getattr(block, 'name', str(block))
            base_priority = getattr(block, 'priority', 5.0)
            priorities[block_name] = base_priority
        
        return priorities
    
    def _stage_7_adjust_by_remnants(
        self,
        block_priorities: Dict[str, float],
        remnants: Dict[str, float],
        npc_name: str
    ) -> Tuple[Dict[str, float], List]:
        """
        Stage 7: Adjust block priorities based on REMNANTS emotional state.
        
        This is where emotional evolution changes what the NPC says next.
        """
        from remnants_block_modifiers import RemnantsBlockModifiers
        
        return RemnantsBlockModifiers.adjust_block_priorities(
            block_priorities, remnants, npc_name
        )
    
    def _stage_8_apply_faction_overrides(
        self,
        block_priorities: Dict[str, float],
        faction: str
    ) -> Tuple[Dict[str, float], List]:
        """
        Stage 8: Apply faction philosophy nudges to priorities.
        
        Ensures NPC responses reflect their faction's values.
        """
        from faction_priority_overrides import FactionPriorityOverrides
        
        return FactionPriorityOverrides.apply_for_faction(block_priorities, faction)
    
    def _stage_9_compose_response(
        self,
        available_blocks: List[Any],
        block_priorities: Dict[str, float],
        npc_name: str
    ) -> str:
        """
        Stage 9: Compose response text from blocks using adjusted priorities.
        
        Selects blocks with highest priority and combines them into coherent response.
        """
        # Sort blocks by adjusted priority
        block_dict = {getattr(b, 'name', str(b)): b for b in available_blocks}
        sorted_blocks = sorted(
            block_priorities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Select top blocks (e.g., top 3)
        selected_blocks = [block_dict[name] for name, _ in sorted_blocks[:3]
                          if name in block_dict]
        
        if not selected_blocks:
            return f"[{npc_name} looks at you but says nothing]"
        
        # Compose text from selected blocks
        if hasattr(self.composition_engine, 'compose'):
            return self.composition_engine.compose(selected_blocks)
        
        # Fallback: concatenate block text
        return " ".join(getattr(b, 'text', str(b)) for b in selected_blocks)
    
    def _stage_10_apply_styling(
        self,
        text: str,
        npc_name: str,
        remnants: Dict[str, float]
    ) -> str:
        """
        Stage 10: Apply persona and REMNANTS emotional styling.
        
        This makes the response sound like the NPC, and like them in their
        current emotional state.
        """
        # Get NPC's persona
        if npc_name not in self.persona_map:
            return text  # No persona defined, return as-is
        
        persona = self.persona_map[npc_name]
        
        # Apply REMNANTS-based styling
        if hasattr(persona, 'apply_style_and_remnants'):
            return persona.apply_style_and_remnants(text, remnants)
        
        return text
    
    def _stage_11_record_quality(
        self,
        message_index: int,
        semantic_layer: Any,
        tone_effects: Dict[str, float],
        remnants: Dict[str, float],
        blocks_count: int,
        block_priorities: Dict[str, float],
        faction_nudges: List,
        final_response: str
    ) -> None:
        """
        Stage 11: Record quality metrics about this dialogue interaction.
        
        Useful for:
        - Understanding dialogue quality over time
        - Identifying where the system is working well
        - Finding edge cases where modulation breaks down
        """
        weight = getattr(semantic_layer, 'emotional_weight', 0.5)
        
        quality = DialogueQuality(
            timestamp=datetime.now().isoformat(),
            player_message_index=message_index,
            semantic_emotional_weight=weight,
            tone_effects_count=len(tone_effects),
            remnants_delta={k: v for k, v in tone_effects.items() if v != 0},
            blocks_activated=blocks_count,
            blocks_selected=list(block_priorities.keys())[:3],
            faction_nudges_applied=len(faction_nudges),
            final_remnants_state=dict(remnants),
        )
        
        self.dialogue_quality_log.append(quality)
    
    # ========== HELPER METHODS ==========
    
    def _mock_semantic_layer(self, message: str) -> Any:
        """Fallback semantic layer when parser isn't available."""
        @dataclass
        class MockSemanticLayer:
            text: str
            emotional_stance: str = "REVEALING"
            disclosure_pace: str = "GRADUAL_REVEAL"
            emotional_contradictions: List = field(default_factory=list)
            power_dynamics: List = field(default_factory=list)
            implied_needs: List = field(default_factory=list)
            identity_signals: List = field(default_factory=list)
            meta_properties: Dict = field(default_factory=dict)
        
        return MockSemanticLayer(text=message)
    
    def _infer_faction(self, npc_name: str) -> str:
        """Infer faction from NPC name if not provided in context."""
        from faction_priority_overrides import get_faction_from_npc_name
        return get_faction_from_npc_name(npc_name)
    
    def get_conversation_arc(self, npc_id: str) -> Optional[ConversationContinuity]:
        """
        Retrieve the emotional arc of a conversation with an NPC.
        
        Useful for understanding how the relationship has evolved.
        """
        return self.conversation_continuity.get(npc_id)
    
    def get_dialogue_quality_report(self) -> Dict[str, Any]:
        """
        Get a report of dialogue quality metrics across all conversations.
        """
        if not self.dialogue_quality_log:
            return {"status": "no_dialogues_recorded"}
        
        return {
            "total_dialogues": len(self.dialogue_quality_log),
            "average_blocks_activated": sum(q.blocks_activated for q in self.dialogue_quality_log) / len(self.dialogue_quality_log),
            "average_semantic_weight": sum(q.semantic_emotional_weight for q in self.dialogue_quality_log) / len(self.dialogue_quality_log),
            "total_faction_nudges": sum(q.faction_nudges_applied for q in self.dialogue_quality_log),
            "most_recent_conversation": self.dialogue_quality_log[-1] if self.dialogue_quality_log else None,
        }


# ============================================================
# Integration Example: Using the Orchestrator
# ============================================================

def example_usage():
    """
    Example of how to use VelinorDialogueOrchestratorV2.
    
    In real implementation, you would:
    1. Initialize semantic parser
    2. Initialize ToneMapper
    3. Initialize NPCManager with REMNANTS
    4. Initialize DialogueBlockStore
    5. Initialize ResponseCompositionEngine
    6. Create PersonaBase subclasses for each NPC
    7. Create orchestrator with all dependencies
    8. Call handle_player_message for each player interaction
    """
    
    # Pseudo-code
    # orchestrator = VelinorDialogueOrchestratorV2(
    #     semantic_parser=semantic_parser,
    #     tone_mapper=tone_mapper,
    #     npc_manager=npc_manager,
    #     block_store=block_store,
    #     composition_engine=composition_engine,
    #     persona_map={
    #         "Nima": NimaPersona(),
    #         "Ravi": RaviPersona(),
    #         "Kaelen": KaelenPersona(),
    #     }
    # )
    #
    # player_message = "I want to understand what happened to Ophina"
    # response = orchestrator.handle_player_message(
    #     player_message=player_message,
    #     npc_id="npc_nima_001",
    #     npc_name="Nima",
    #     message_index=0,
    #     context={"location": "marketplace", "faction": "nima"}
    # )
    #
    # print(response)
    # # Nima's response will be emotionally responsive to the player's approach
    
    pass
