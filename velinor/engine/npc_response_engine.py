"""
NPC Response Engine for Velinor: Remnants of the Tone

This module handles NPC dialogue and behavior in response to player traits.

Core principle: NPCs are not generic - each has personality biases and responds
differently to different trait profiles.

Each NPC has:
- Base personality (how they naturally are)
- Trait comfort levels (which traits they understand/respect)
- Dialogue variants for different player traits
- State tracking (how they feel about the player right now)
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from trait_system import TraitType, TraitProfiler
from coherence_calculator import CoherenceCalculator, CoherenceLevel


class NPCPersonalityType(Enum):
    """NPC personality archetypes"""
    EMPATHETIC = "empathetic"  # Understands emotion, responds to emotional choices
    SKEPTICAL = "skeptical"  # Questions everything, respects accountability
    INTEGRATOR = "integrator"  # Holds multiple truths, seeks synthesis
    AWARE = "aware"  # Perceptive, notices patterns, sees subtext


@dataclass
class DialogueVariant:
    """A dialogue option tailored to a specific player trait"""
    text: str
    npc_trait_comfort: float  # How much NPC agrees with this trait (0-1)
    relationship_shift: float  # How much this affects relationship (-1 to +1)
    coherence_required: float = 0.0  # Minimum coherence to trigger this variant


@dataclass
class NPCDialogueProfile:
    """
    How an NPC responds to different player traits.
    
    Each trait has multiple dialogue options indexed by depth level.
    """
    # For each trait, store dialogue variants by coherence depth level
    empathy_dialogues: Dict[str, DialogueVariant] = field(default_factory=dict)
    skepticism_dialogues: Dict[str, DialogueVariant] = field(default_factory=dict)
    integration_dialogues: Dict[str, DialogueVariant] = field(default_factory=dict)
    awareness_dialogues: Dict[str, DialogueVariant] = field(default_factory=dict)
    
    # NPC's own trait preferences
    personality_type: NPCPersonalityType = NPCPersonalityType.INTEGRATOR
    preferred_traits: List[TraitType] = field(default_factory=list)
    uncomfortable_traits: List[TraitType] = field(default_factory=list)


class NPCResponseEngine:
    """
    Generates NPC dialogue and behavior based on player traits and coherence.
    
    This is called by the main dialogue system to get NPC responses.
    """
    
    def __init__(self, profiler: TraitProfiler):
        self.profiler = profiler
        self.calculator = CoherenceCalculator(profiler)
        self.npc_profiles: Dict[str, NPCDialogueProfile] = {}
        self._initialize_npc_profiles()
    
    def get_npc_response(
        self,
        npc_name: str,
        dialogue_prompt: str,
        context: Optional[Dict] = None,
    ) -> str:
        """
        Get NPC response to player's statement.
        
        Process:
        1. Determine player's current trait pattern
        2. Get NPC's trait comfort level for that pattern
        3. Get coherence level
        4. Select appropriate dialogue variant
        5. Return customized response
        """
        if npc_name not in self.npc_profiles:
            return f"{npc_name} considers what you've said."
        
        # Get player pattern
        primary_trait, secondary_trait, strength = self.calculator.get_pattern_analysis()
        
        # Get coherence report
        report = self.calculator.get_coherence_report()
        
        # Get NPC profile
        npc_profile = self.npc_profiles[npc_name]
        
        # Determine response tone based on trait comfort and coherence
        response = self._generate_response(
            npc_name=npc_name,
            npc_profile=npc_profile,
            player_primary_trait=primary_trait,
            player_secondary_trait=secondary_trait,
            coherence_report=report,
            dialogue_prompt=dialogue_prompt,
            context=context,
        )
        
        return response
    
    def get_npc_reaction_to_choice(
        self,
        npc_name: str,
        choice_trait: TraitType,
    ) -> str:
        """
        Get NPC's immediate reaction to a player choice.
        
        This is shown right after player makes a dialogue choice.
        Varies based on:
        - How coherent the choice is
        - How much NPC agrees with that trait
        - Current relationship state
        """
        if npc_name not in self.npc_profiles:
            return ""
        
        npc_profile = self.npc_profiles[npc_name]
        report = self.calculator.get_coherence_report()
        
        # Is this choice coherent with player's pattern?
        is_coherent = choice_trait == report.primary_pattern
        
        # How does NPC feel about this trait?
        trait_comfort = self._get_trait_comfort(npc_profile, choice_trait)
        
        # Generate reaction
        if trait_comfort > 0.8:
            if is_coherent:
                return f"{npc_name} nods. 'That's consistent with who you are.'"
            else:
                return f"{npc_name} looks surprised. 'That's different from what I expected.'"
        
        elif trait_comfort > 0.5:
            if is_coherent:
                return f"{npc_name} acknowledges what you said."
            else:
                return f"{npc_name} seems thrown off by the contradiction."
        
        else:
            if is_coherent:
                return f"{npc_name} frowns. 'I don't understand that choice.'"
            else:
                return f"{npc_name} looks at you with confusion and something like disappointment."
        
    def should_npc_trust_player(self, npc_name: str) -> bool:
        """
        Does this NPC trust the player enough to open up?
        
        Based on:
        - Player coherence (consistency builds trust)
        - Trait alignment (NPC respects traits they share)
        - Past interactions
        """
        report = self.calculator.get_coherence_report()
        
        # Base: Need at least moderate coherence
        if report.overall_coherence < 50:
            return False
        
        if npc_name not in self.npc_profiles:
            return report.overall_coherence > 60
        
        npc_profile = self.npc_profiles[npc_name]
        
        # Check trait alignment
        primary_trait = report.primary_pattern
        if primary_trait in npc_profile.preferred_traits:
            # NPC respects this trait, more willing to trust
            return report.overall_coherence > 50
        
        elif primary_trait in npc_profile.uncomfortable_traits:
            # NPC uncomfortable with this trait, higher threshold
            return report.overall_coherence > 75
        
        else:
            # Neutral trait, standard threshold
            return report.overall_coherence > 60
    
    def get_npc_dialogue_depth(self, npc_name: str) -> str:
        """
        How deep should NPC dialogue go?
        
        Possible depths:
        - "surface": Small talk, basic information
        - "personal": Share feelings, backstory
        - "intimate": Reveal fears, motivations, secrets
        """
        report = self.calculator.get_coherence_report()
        
        if self.should_npc_trust_player(npc_name):
            if report.overall_coherence > 80:
                return "intimate"
            elif report.overall_coherence > 65:
                return "personal"
            else:
                return "surface"
        else:
            if report.overall_coherence > 50:
                return "surface"
            else:
                return "guarded"
    
    def get_npc_conflict_level(self, npc_name: str) -> str:
        """
        How much does this NPC conflict with player's traits?
        
        Possible levels:
        - "ally": NPC agrees with player
        - "neutral": NPC doesn't care
        - "skeptical": NPC disagrees but can work with player
        - "opposed": NPC fundamentally opposes player
        """
        if npc_name not in self.npc_profiles:
            return "neutral"
        
        npc_profile = self.npc_profiles[npc_name]
        report = self.calculator.get_coherence_report()
        primary_trait = report.primary_pattern
        
        if primary_trait in npc_profile.preferred_traits:
            return "ally"
        elif primary_trait in npc_profile.uncomfortable_traits:
            return "opposed"
        else:
            return "neutral"
    
    # ========== Private Methods ==========
    
    def _generate_response(
        self,
        npc_name: str,
        npc_profile: NPCDialogueProfile,
        player_primary_trait: TraitType,
        player_secondary_trait: Optional[TraitType],
        coherence_report,
        dialogue_prompt: str,
        context: Optional[Dict] = None,
    ) -> str:
        """
        Generate customized NPC response.
        
        This is a placeholder that will integrate with FirstPerson orchestrator
        for actual dialogue generation.
        """
        # Get trait comfort
        trait_comfort = self._get_trait_comfort(npc_profile, player_primary_trait)
        
        # Get dialogue depth
        depth = self.get_npc_dialogue_depth(npc_name)
        
        # Get conflict level
        conflict = self.get_npc_conflict_level(npc_name)
        
        # Build response descriptor (will be used by dialogue engine)
        response_descriptor = {
            "npc": npc_name,
            "player_trait": player_primary_trait.value,
            "trait_comfort": trait_comfort,
            "coherence": coherence_report.overall_coherence,
            "depth": depth,
            "conflict": conflict,
            "prompt": dialogue_prompt,
        }
        
        # For now, return a basic response
        # In production, this would call FirstPerson orchestrator
        if conflict == "opposed":
            return f"{npc_name} looks away, disagreeing with your fundamental approach."
        elif conflict == "ally":
            return f"{npc_name} nods. 'I see where you're coming from.'"
        else:
            return f"{npc_name} listens carefully."
    
    def _get_trait_comfort(
        self,
        npc_profile: NPCDialogueProfile,
        trait: TraitType
    ) -> float:
        """
        How comfortable is this NPC with this trait?
        
        Returns 0-1 score:
        - 0.9-1.0: NPC loves this trait
        - 0.5-0.7: NPC neutral about trait
        - 0.1-0.3: NPC dislikes trait
        """
        if trait in npc_profile.preferred_traits:
            return 0.9
        elif trait in npc_profile.uncomfortable_traits:
            return 0.2
        else:
            return 0.5
    
    def _initialize_npc_profiles(self) -> None:
        """
        Initialize dialogue profiles for all NPCs.
        
        This creates the mapping from NPC → how they respond to different traits.
        """
        # Saori - Integrator, values synthesis and awareness
        saori_profile = NPCDialogueProfile(
            personality_type=NPCPersonalityType.INTEGRATOR,
            preferred_traits=[TraitType.INTEGRATION, TraitType.AWARENESS],
            uncomfortable_traits=[],
        )
        self.npc_profiles["Saori"] = saori_profile
        
        # Ravi - Skeptical, values accountability
        ravi_profile = NPCDialogueProfile(
            personality_type=NPCPersonalityType.SKEPTICAL,
            preferred_traits=[TraitType.SKEPTICISM, TraitType.AWARENESS],
            uncomfortable_traits=[],
        )
        self.npc_profiles["Ravi"] = ravi_profile
        
        # Nima - Empathetic, values understanding
        nima_profile = NPCDialogueProfile(
            personality_type=NPCPersonalityType.EMPATHETIC,
            preferred_traits=[TraitType.EMPATHY, TraitType.INTEGRATION],
            uncomfortable_traits=[],
        )
        self.npc_profiles["Nima"] = nima_profile
        
        # Malrik - Mixed (merchant, pragmatist)
        malrik_profile = NPCDialogueProfile(
            personality_type=NPCPersonalityType.SKEPTICAL,
            preferred_traits=[TraitType.SKEPTICISM, TraitType.AWARENESS],
            uncomfortable_traits=[TraitType.EMPATHY],  # Softness threatens his worldview
        )
        self.npc_profiles["Malrik"] = malrik_profile
        
        # Elenya - Empathetic with integration tendency
        elenya_profile = NPCDialogueProfile(
            personality_type=NPCPersonalityType.EMPATHETIC,
            preferred_traits=[TraitType.EMPATHY, TraitType.INTEGRATION],
            uncomfortable_traits=[],
        )
        self.npc_profiles["Elenya"] = elenya_profile
        
        # Coren - Aware, pattern-seeker
        coren_profile = NPCDialogueProfile(
            personality_type=NPCPersonalityType.AWARE,
            preferred_traits=[TraitType.AWARENESS, TraitType.INTEGRATION],
            uncomfortable_traits=[],
        )
        self.npc_profiles["Coren"] = coren_profile


def get_npc_response_for_trait(
    profiler: TraitProfiler,
    npc_name: str,
    trait: TraitType,
) -> str:
    """
    Quick helper: Get NPC response to specific trait.
    
    Used for quick dialogue lookups in choice selection.
    """
    engine = NPCResponseEngine(profiler)
    return engine.get_npc_reaction_to_choice(npc_name, trait)


def should_npc_reveal_hidden_goal(profiler: TraitProfiler, npc_name: str) -> bool:
    """
    Should NPC reveal their true agenda to player?
    
    Requires:
    - High trust (coherence > 70)
    - NPC's personality aligns with player's traits
    """
    engine = NPCResponseEngine(profiler)
    
    if not engine.should_npc_trust_player(npc_name):
        return False
    
    report = engine.calculator.get_coherence_report()
    return report.overall_coherence > 70
