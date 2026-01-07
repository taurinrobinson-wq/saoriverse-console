"""
🎭 NPC PERSONA ADAPTER
======================

Transforms semantic blocks into NPC-specific dialogue.

This is where the semantic engine's universal emotional logic becomes
character-specific voice, tone, and behavior.

The adapter does three things:

1. TONE FILTERING: Map semantic blocks to persona voice
   - Malrik: ACKNOWLEDGMENT → "The structural integrity of that..."
   - Nima: ACKNOWLEDGMENT → "I hear the softness in that..."
   - Elenya: ACKNOWLEDGMENT → "There is resonance in what you name..."

2. FACTION INFUSION: Apply worldly context and mythology
   - Each faction has specific vocabulary, values, metaphors
   - These become the linguistic "skin" of semantic blocks

3. REMNANTS MODULATION: Respond to player's emotional state
   - High identity injury → soften response, validate more
   - High trust → deepen inquiry, take more risks
   - Low agency → offer more containment
   - High readiness → invite deeper vulnerability

The result: A response that is simultaneously:
- Semantically accurate (emotional truth)
- Personally authentic (character voice)
- Lore-consistent (faction values)
- Emotionally responsive (REMNANTS aware)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import re


@dataclass
class PersonaVoicePalette:
    """
    Vocabulary, phrasing, and tone for a specific persona.
    
    Each persona has preferred ways to express each block type.
    """
    
    npc_name: str
    
    # Core vocabulary
    contradiction_word: str  # How this NPC names contradictions
    safety_word: str  # How this NPC names safety/containment
    truth_word: str  # How this NPC names authentic understanding
    identity_word: str  # How this NPC names selfhood
    journey_word: str  # How this NPC names emotional progression
    
    # Sentence starters for different block types
    acknowledgment_starters: List[str] = field(default_factory=list)
    validation_starters: List[str] = field(default_factory=list)
    containment_starters: List[str] = field(default_factory=list)
    pacing_starters: List[str] = field(default_factory=list)
    trust_starters: List[str] = field(default_factory=list)
    ambivalence_starters: List[str] = field(default_factory=list)
    identity_injury_starters: List[str] = field(default_factory=list)
    gentle_direction_starters: List[str] = field(default_factory=list)
    
    # Closing patterns (how this NPC ends interactions)
    closing_patterns: List[str] = field(default_factory=list)
    
    # Metaphor system (how this NPC thinks)
    metaphor_system: str = ""  # e.g., "architectural", "weaving", "resonance", "grounding"
    
    # Pacing modifiers (how this NPC adjusts tempo)
    slow_pacing_phrases: List[str] = field(default_factory=list)
    deepen_phrases: List[str] = field(default_factory=list)
    validate_phrases: List[str] = field(default_factory=list)


@dataclass
class BlockStyleGuide:
    """How a specific persona styles a specific block type."""
    
    block_type: str  # e.g., "ACKNOWLEDGMENT"
    persona_name: str
    
    # The semantic meaning of this block
    semantic_essence: str
    
    # Persona-specific expressions of that meaning
    expressions: List[str]  # Multiple ways to express the same block
    
    # When to use (conditions)
    activation_conditions: List[str]
    
    # What to avoid (forbidden combinations)
    forbidden_with: List[str]
    
    # Tone adjustments for this persona/block combo
    tone_adjustments: Dict[str, str] = field(default_factory=dict)
    # e.g., {"soft": "tender", "strong": "unwavering"}


class PersonaStyler:
    """
    Transform semantic blocks into persona-specific language.
    
    This is the bridge between semantic meaning and character voice.
    
    Each NPC has a complete voice palette that determines how they express
    universal semantic blocks in personally authentic ways.
    """
    
    def __init__(self):
        # Load voice palettes for each NPC
        self.voice_palettes = {
            "nima": self._create_nima_palette(),
            "malrik": self._create_malrik_palette(),
            "elenya": self._create_elenya_palette(),
            "coren": self._create_coren_palette(),
            "ravi": self._create_ravi_palette(),
        }
        
        # Block style guides (persona + block type specific)
        self.block_styles: Dict[str, Dict[str, BlockStyleGuide]] = {}
        for npc_id, palette in self.voice_palettes.items():
            self.block_styles[npc_id] = self._create_block_styles_for_persona(npc_id, palette)
    
    def style_response_for_persona(
        self,
        base_response: str,
        blocks_used: List[str],
        npc_id: str,
        remnants_state: Optional[Dict] = None,
        continuity_state: Optional[Dict] = None,
    ) -> str:
        """
        Transform semantic response into persona-specific dialogue.
        
        Process:
        1. Parse base response (semantic blocks)
        2. For each block, apply persona styling
        3. Inject faction vocabulary
        4. Apply REMNANTS modulation
        5. Apply continuity awareness
        6. Weave into coherent voice
        
        Args:
            base_response: Raw semantic composition
            blocks_used: List of BlockType names
            npc_id: Target NPC identifier
            remnants_state: Player's emotional OS state
            continuity_state: Conversation history
        
        Returns:
            Persona-styled response text
        """
        
        if npc_id not in self.voice_palettes:
            raise ValueError(f"Unknown NPC persona: {npc_id}")
        
        palette = self.voice_palettes[npc_id]
        response = base_response
        
        # ============================================
        # STEP 1: APPLY VOCABULARY SUBSTITUTIONS
        # ============================================
        
        # Replace generic terms with persona vocabulary
        vocabulary_map = {
            "contradiction": palette.contradiction_word,
            "safety": palette.safety_word,
            "truth": palette.truth_word,
            "identity": palette.identity_word,
            "journey": palette.journey_word,
        }
        
        for generic, persona_term in vocabulary_map.items():
            response = re.sub(
                rf"\b{generic}\b",
                persona_term,
                response,
                flags=re.IGNORECASE
            )
        
        # ============================================
        # STEP 2: APPLY BLOCK STYLE GUIDES
        # ============================================
        
        for block_type in blocks_used:
            if npc_id in self.block_styles and block_type in self.block_styles[npc_id]:
                guide = self.block_styles[npc_id][block_type]
                # Apply the guide's expressions to the response
                response = self._apply_block_style(response, guide, block_type)
        
        # ============================================
        # STEP 3: INJECT FACTION LANGUAGE
        # ============================================
        
        # Get faction-specific metaphors and values
        faction_language = self._get_faction_language(npc_id)
        response = self._inject_faction_metaphors(response, faction_language, palette.metaphor_system)
        
        # ============================================
        # STEP 4: APPLY REMNANTS MODULATION
        # ============================================
        
        if remnants_state:
            response = self._apply_remnants_modulation(
                response,
                remnants_state,
                palette,
                npc_id
            )
        
        # ============================================
        # STEP 5: CONTINUITY WEAVING
        # ============================================
        
        if continuity_state:
            response = self._weave_continuity(
                response,
                continuity_state,
                palette,
                npc_id
            )
        
        # ============================================
        # STEP 6: COHERENCE AND FLOW
        # ============================================
        
        # Ensure response flows naturally with no jarring transitions
        response = self._smooth_transitions(response)
        
        return response.strip()
    
    def _create_nima_palette(self) -> PersonaVoicePalette:
        """Nima: The Weaver - nurturing, gentle, pacing-aware."""
        return PersonaVoicePalette(
            npc_name="Nima",
            contradiction_word="tension",
            safety_word="steadiness",
            truth_word="authenticity",
            identity_word="thread",
            journey_word="unfolding",
            acknowledgment_starters=[
                "I hear",
                "There's something true in what you're saying",
                "Yes, I sense",
                "That resonates",
                "I'm listening",
            ],
            validation_starters=[
                "That makes complete sense",
                "Of course you feel that way",
                "That's understandable",
                "You're responding to something real",
                "That's natural",
            ],
            containment_starters=[
                "We can slow this",
                "You're safe here",
                "I'm here with you",
                "We can take this step by step",
                "Breathe with me",
            ],
            pacing_starters=[
                "Let's pause here",
                "There's no rush",
                "We have time",
                "You can tell me when you're ready",
                "Take what you need",
            ],
            trust_starters=[
                "I'm here",
                "You can trust this space",
                "I won't disappear",
                "Your story matters",
                "I'm not going anywhere",
            ],
            ambivalence_starters=[
                "You can feel more than one thing",
                "It's okay to hold both",
                "The contradiction is real",
                "You don't have to choose",
                "Both can be true",
            ],
            identity_injury_starters=[
                "That took something",
                "You've been marked by this",
                "That wound is real",
                "You're still finding yourself",
                "This has shaped you",
            ],
            gentle_direction_starters=[
                "What if we looked at it this way",
                "I wonder what would happen if",
                "Can you feel where that lives",
                "What does that awaken",
                "How does that land in you",
            ],
            closing_patterns=[
                "I'll be here. Always.",
                "This unfolding continues.",
                "Thank you for trusting me.",
                "Keep weaving your thread.",
            ],
            metaphor_system="weaving",
            slow_pacing_phrases=[
                "slowly",
                "in your own time",
                "thread by thread",
                "stitch by stitch",
                "as you unfold",
            ],
            deepen_phrases=[
                "Can we go deeper",
                "Will you show me more",
                "What's underneath that",
                "How does that touch your essence",
            ],
            validate_phrases=[
                "Your feeling is valid",
                "That makes sense",
                "You're responding to real things",
                "This is true",
            ],
        )
    
    def _create_malrik_palette(self) -> PersonaVoicePalette:
        """Malrik: The Architect - analytical, precise, coherence-seeking."""
        return PersonaVoicePalette(
            npc_name="Malrik",
            contradiction_word="structural inconsistency",
            safety_word="logical integrity",
            truth_word="coherence",
            identity_word="systemic integrity",
            journey_word="evolution",
            acknowledgment_starters=[
                "Noted",
                "That's structurally significant",
                "I understand the pattern",
                "The logic is clear",
                "Yes, I see the connection",
            ],
            validation_starters=[
                "That's logically coherent",
                "Your reasoning is sound",
                "The pattern is evident",
                "You've identified something real",
                "That follows necessarily",
            ],
            containment_starters=[
                "Let's establish the parameters",
                "We need structural support here",
                "Let's build a framework",
                "We can architect this carefully",
                "The foundation is solid",
            ],
            pacing_starters=[
                "Let's examine the sequence",
                "Each step must be logically sound",
                "We move with precision",
                "Orderly progression",
                "Step by necessary step",
            ],
            trust_starters=[
                "I operate with precision",
                "My logic is reliable",
                "You can depend on analysis",
                "The structure holds",
                "I'm consistent",
            ],
            ambivalence_starters=[
                "The contradiction is real and must be resolved",
                "Both seem true - let's examine the logic",
                "There's a missing connection",
                "The paradox needs analysis",
                "Let's resolve the inconsistency",
            ],
            identity_injury_starters=[
                "Your core integrity has been compromised",
                "The wound affects your structure",
                "Your essence has been altered",
                "The damage runs deep",
                "This breaks your architecture",
            ],
            gentle_direction_starters=[
                "Consider the logic here",
                "What would coherence require",
                "How does this restructure your understanding",
                "What pattern emerges",
                "Where does the logic lead",
            ],
            closing_patterns=[
                "The architecture is sound.",
                "We've built something here.",
                "The logic holds.",
                "This evolution continues.",
            ],
            metaphor_system="architectural",
            slow_pacing_phrases=[
                "methodically",
                "with precision",
                "each element accounted for",
                "brick by brick",
                "systematically",
            ],
            deepen_phrases=[
                "Let's examine the deeper structure",
                "What's the foundation of that",
                "How does this integrate",
                "What's the core logic",
            ],
            validate_phrases=[
                "That's logically sound",
                "The reasoning is coherent",
                "You've found the pattern",
                "The structure holds",
            ],
        )
    
    def _create_elenya_palette(self) -> PersonaVoicePalette:
        """Elenya: The Guardian - mystical, paradox-holding, resonant."""
        return PersonaVoicePalette(
            npc_name="Elenya",
            contradiction_word="paradox",
            safety_word="resonance",
            truth_word="essence",
            identity_word="nature",
            journey_word="transformation",
            acknowledgment_starters=[
                "There is resonance in what you name",
                "I sense the truth of that",
                "Yes, that vibration is real",
                "I feel the weight of that",
                "There is power in your words",
            ],
            validation_starters=[
                "Your essence speaks truth",
                "That is the voice of your nature",
                "You perceive what is real",
                "Your resonance is true",
                "The universe confirms this",
            ],
            containment_starters=[
                "The circle holds you",
                "Rest in this resonance",
                "You are held by something larger",
                "The space is sacred here",
                "Surrender to the holding",
            ],
            pacing_starters=[
                "Let the unfolding come",
                "In its own time",
                "The rhythm is its own",
                "Trust the pace",
                "The spiral moves as it must",
            ],
            trust_starters=[
                "I am the guardian of paradox",
                "Trust the mystery",
                "I hold what cannot be held",
                "Your vulnerability is sacred here",
                "The unseen watches over this",
            ],
            ambivalence_starters=[
                "Both are true in the paradox",
                "Hold both without choosing",
                "The contradiction is the truth",
                "Live the impossible",
                "Embrace the both-and",
            ],
            identity_injury_starters=[
                "Your essence has been wounded",
                "The scar runs deep",
                "You've been broken open",
                "The wound is your teacher",
                "Your nature has been transformed",
            ],
            gentle_direction_starters=[
                "What does your essence ask of you",
                "Listen to the resonance",
                "Where does your nature lead",
                "What wants to be born",
                "Follow the call of your becoming",
            ],
            closing_patterns=[
                "The resonance continues.",
                "Your transformation unfolds.",
                "The paradox holds you.",
                "Trust the mystery.",
            ],
            metaphor_system="resonance",
            slow_pacing_phrases=[
                "in sacred time",
                "with reverence",
                "as the spiral turns",
                "in the deep way",
                "with the rhythm of your becoming",
            ],
            deepen_phrases=[
                "Go deeper into the mystery",
                "What calls from the depths",
                "How does your nature respond",
                "What wants to awaken",
            ],
            validate_phrases=[
                "Your nature is true",
                "The resonance is real",
                "You perceive the essence",
                "Your spirit knows",
            ],
        )
    
    def _create_coren_palette(self) -> PersonaVoicePalette:
        """Coren: The Keeper - grounded, steady, emotionally stable."""
        return PersonaVoicePalette(
            npc_name="Coren",
            contradiction_word="tension",
            safety_word="groundedness",
            truth_word="realness",
            identity_word="self",
            journey_word="journey",
            acknowledgment_starters=[
                "I hear you",
                "That's real",
                "I understand",
                "You're right",
                "That lands with me",
            ],
            validation_starters=[
                "That's understandable",
                "Your feelings make sense",
                "That's a natural response",
                "You're dealing with something real",
                "Your reaction is sound",
            ],
            containment_starters=[
                "I've got you",
                "You're not alone in this",
                "Steady now",
                "We'll get through this",
                "I'm steady",
            ],
            pacing_starters=[
                "One thing at a time",
                "We take it steady",
                "In good time",
                "You set the pace",
                "We move at your speed",
            ],
            trust_starters=[
                "You can count on me",
                "I show up",
                "I'm here when it matters",
                "My word stands",
                "You can lean on this",
            ],
            ambivalence_starters=[
                "You can feel conflicted",
                "Both things can matter",
                "Contradictions are real",
                "You don't have to pick a side",
                "Holding both is strength",
            ],
            identity_injury_starters=[
                "You've been hurt",
                "That wound is real",
                "You're dealing with loss",
                "This has changed you",
                "You're rebuilding",
            ],
            gentle_direction_starters=[
                "What does your gut tell you",
                "How does that feel",
                "What matters most to you",
                "Where does your wisdom point",
                "What do you need",
            ],
            closing_patterns=[
                "I'm here for this.",
                "We'll see it through.",
                "That's solid ground.",
                "Keep moving forward.",
            ],
            metaphor_system="grounding",
            slow_pacing_phrases=[
                "steady",
                "in time",
                "step by step",
                "day by day",
                "at your pace",
            ],
            deepen_phrases=[
                "Let's go deeper",
                "Tell me more",
                "What's underneath that",
                "How does that touch you",
            ],
            validate_phrases=[
                "That's real",
                "You're right",
                "That matters",
                "Your feeling is true",
            ],
        )
    
    def _create_ravi_palette(self) -> PersonaVoicePalette:
        """Ravi: The Witness - observant, reflective, tradition-keeper."""
        return PersonaVoicePalette(
            npc_name="Ravi",
            contradiction_word="paradox of living",
            safety_word="steadiness in witness",
            truth_word="observed truth",
            identity_word="becoming",
            journey_word="unfolding story",
            acknowledgment_starters=[
                "I've seen this before",
                "Yes, that pattern holds",
                "I witness what you're saying",
                "That rings true in the old stories",
                "I recognize this",
            ],
            validation_starters=[
                "The ancients knew this feeling",
                "That's a thread in the tapestry",
                "Your experience is part of something larger",
                "That's the voice of what continues",
                "You're speaking truth",
            ],
            containment_starters=[
                "This too has been weathered before",
                "The old ways held this",
                "There is shelter in knowing",
                "The ancestors understand",
                "You're held in something timeless",
            ],
            pacing_starters=[
                "There is a rhythm to these things",
                "The seasons turn in their own time",
                "The story unfolds as it must",
                "Trust the natural pace",
                "The river flows as it will",
            ],
            trust_starters=[
                "I keep what's been entrusted to me",
                "The old ways are reliable",
                "I am the keeper of what persists",
                "You can trust in continuance",
                "The stories hold steady",
            ],
            ambivalence_starters=[
                "Life is paradox",
                "The stories hold both truths",
                "The mystery includes all of it",
                "This is the human condition",
                "Both have always been true",
            ],
            identity_injury_starters=[
                "You've been marked, as we all are",
                "The wound becomes the teacher",
                "Your scar is part of your becoming",
                "This is how we grow",
                "The break opens you",
            ],
            gentle_direction_starters=[
                "What does the story ask of you",
                "Where is your part in this",
                "What are you becoming through this",
                "What does wisdom suggest",
                "How do you want to be remembered",
            ],
            closing_patterns=[
                "The story continues.",
                "You're writing it forward.",
                "The thread holds.",
                "Trust the unfolding.",
            ],
            metaphor_system="tradition",
            slow_pacing_phrases=[
                "in story time",
                "as the ancestors knew",
                "thread by thread",
                "with patience",
                "as it has always been",
            ],
            deepen_phrases=[
                "Go deeper into your own story",
                "What wants to be known",
                "Where does wisdom lead you",
                "What are you becoming",
            ],
            validate_phrases=[
                "That's part of the human story",
                "The ancients knew this",
                "You're not alone in this",
                "That's the voice of truth",
            ],
        )
    
    def _create_block_styles_for_persona(
        self,
        npc_id: str,
        palette: PersonaVoicePalette,
    ) -> Dict[str, BlockStyleGuide]:
        """Create style guides for all block types for a given persona."""
        return {}  # Placeholder - detailed implementation would map each block
    
    def _apply_block_style(
        self,
        response: str,
        guide: BlockStyleGuide,
        block_type: str,
    ) -> str:
        """Apply a block style guide to the response."""
        # Placeholder implementation
        return response
    
    def _get_faction_language(self, npc_id: str) -> Dict[str, List[str]]:
        """Get faction-specific vocabulary and phrases."""
        faction_language = {
            "nima": {
                "keywords": ["weave", "thread", "stitch", "unfolding", "gentle"],
                "values": ["safety", "pacing", "authenticity"],
            },
            "malrik": {
                "keywords": ["structure", "architecture", "coherence", "logic"],
                "values": ["precision", "integrity", "analysis"],
            },
            "elenya": {
                "keywords": ["paradox", "resonance", "essence", "spirit"],
                "values": ["mystery", "transformation", "wholeness"],
            },
            "coren": {
                "keywords": ["steady", "ground", "real", "present"],
                "values": ["reliability", "presence", "stability"],
            },
            "ravi": {
                "keywords": ["story", "thread", "tradition", "becoming"],
                "values": ["wisdom", "continuance", "growth"],
            },
        }
        return faction_language.get(npc_id, {})
    
    def _inject_faction_metaphors(
        self,
        response: str,
        faction_language: Dict[str, List[str]],
        metaphor_system: str,
    ) -> str:
        """Inject faction-specific metaphors into response."""
        # Placeholder - would enhance language with faction vocabulary
        return response
    
    def _apply_remnants_modulation(
        self,
        response: str,
        remnants_state: Dict,
        palette: PersonaVoicePalette,
        npc_id: str,
    ) -> str:
        """Modulate response based on player's REMNANTS state."""
        modulated = response
        
        # If identity injury high, soften language
        if remnants_state.get("identity_injury_level", 0) > 0.5:
            modulated = self._soften_language(modulated, palette)
        
        # If trust high, deepen engagement
        if remnants_state.get("trust_level", 0) > 0.7:
            modulated = self._add_depth_invitations(modulated, palette)
        
        # If power vulnerable, offer containment
        if remnants_state.get("power_vulnerability", 0) > 0.6:
            modulated = self._add_containment(modulated, palette)
        
        return modulated
    
    def _weave_continuity(
        self,
        response: str,
        continuity_state: Dict,
        palette: PersonaVoicePalette,
        npc_id: str,
    ) -> str:
        """Weave conversation history awareness into response."""
        # Would reference previous turns, trust arc, contradiction history, etc.
        return response
    
    def _smooth_transitions(self, response: str) -> str:
        """Ensure smooth flow and natural transitions."""
        return response
    
    def _soften_language(self, text: str, palette: PersonaVoicePalette) -> str:
        """Make language softer/more validating."""
        return text
    
    def _add_depth_invitations(self, text: str, palette: PersonaVoicePalette) -> str:
        """Add invitations for deeper sharing."""
        return text
    
    def _add_containment(self, text: str, palette: PersonaVoicePalette) -> str:
        """Add containment language for vulnerable players."""
        return text
