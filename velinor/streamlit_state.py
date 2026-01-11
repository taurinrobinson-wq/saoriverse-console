"""
Streamlit Game State Management
===============================

Clean state machine for Velinor Streamlit prototype.

Tracks:
- Game mode (narrative, glyph_input, chamber, special)
- Glyphs (obtained, used, fusion state)
- TONE stats (trust, observation, narrative_presence, empathy, resonance)
- REMNANTS traits (resolve, empathy, memory, nuance, authority, need, trust, skepticism)
- NPC perception + emotional state
- Fight counter for chamber battles
- Skills unlocked
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ToneStats:
    """Player's emotional TONE signature.

    TONE = Trust, Observation, Narrative Presence, Empathy
    Plus Resonance (overarching harmonic balance)
    """
    trust: float = 0.0  # T: Reliability to NPCs
    observation: float = 0.0  # O: Perception and wisdom
    narrative_presence: float = 0.0  # N: Charisma and agency
    empathy: float = 0.0  # E: Heart and vulnerability
    resonance: float = 0.0  # Overarching harmonic balance

    def apply_effect(self, effect: Dict[str, float]):
        """Apply tone modifications from a choice."""
        for stat, value in effect.items():
            if hasattr(self, stat):
                setattr(self, stat, max(-1.0, min(1.0, getattr(self, stat) + value)))

    def to_dict(self) -> Dict[str, float]:
        return {
            "trust": round(self.trust, 2),
            "observation": round(self.observation, 2),
            "narrative_presence": round(self.narrative_presence, 2),
            "empathy": round(self.empathy, 2),
            "resonance": round(self.resonance, 2)
        }


@dataclass
class RemnantTraits:
    """NPC Personality System - REMNANTS traits.

    REMNANTS = Resolve, Empathy, Memory, Nuance, Authority, Need, Trust, Skepticism
    These describe NPC personalities and how they respond to player TONE stats.
    """
    resolve: float = 0.5  # R: How firm or principled
    empathy: float = 0.5  # E: Capacity to care and connect
    memory: float = 0.5  # M: How past shapes choices
    nuance: float = 0.5  # N: Subtlety and complexity
    authority: float = 0.5  # A: Relationship to boundaries and control
    need: float = 0.5  # N: What they seek from player
    trust: float = 0.5  # T: Baseline openness or suspicion
    skepticism: float = 0.5  # S: Tendency to doubt and withhold

    def apply_effect(self, effect: Dict[str, float]):
        """Apply modifications to remnant traits."""
        for stat, value in effect.items():
            if hasattr(self, stat):
                setattr(self, stat, max(
                    0.0, min(1.0, getattr(self, stat) + value)))

    def to_dict(self) -> Dict[str, float]:
        return {
            "resolve": round(self.resolve, 2),
            "empathy": round(self.empathy, 2),
            "memory": round(self.memory, 2),
            "nuance": round(self.nuance, 2),
            "authority": round(self.authority, 2),
            "need": round(self.need, 2),
            "trust": round(self.trust, 2),
            "skepticism": round(self.skepticism, 2)
        }


@dataclass
class Glyph:
    """Represents a glyph the player can obtain."""
    name: str
    description: str = ""
    obtained: bool = False
    unlock_condition: str = ""  # What story beat/condition unlocks it
    emotional_effect: str = ""  # What tone it affects
    npc_resonance: Dict[str, float] = field(
        default_factory=dict)  # Which NPCs resonate with it

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NPCPerception:
    """How an NPC perceives the player, plus their REMNANTS profile."""
    name: str
    trust: float = 0.0  # -1.0 to 1.0: How much they trust the player
    affinity: float = 0.0  # -1.0 to 1.0: How much they like the player
    understanding: float = 0.0  # -1.0 to 1.0: How well they understand the player
    emotion: str = "neutral"  # Current emotional state
    last_interaction: Optional[str] = None
    remnants_profile: RemnantTraits = field(
        default_factory=RemnantTraits)  # Their personality

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['remnants_profile'] = self.remnants_profile.to_dict()
        return data


@dataclass
class Skill:
    """A learnable skill that unlocks dialogue options."""
    name: str
    description: str = ""
    unlocked: bool = False
    prerequisites: List[str] = field(default_factory=list)
    dialogue_banks: List[str] = field(
        default_factory=list)  # Which dialogues it unlocks

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StreamlitGameState:
    """
    Central game state for Streamlit prototype.

    Manages all narrative, emotional, and mechanical state.
    """

    def __init__(self):
        # Metadata
        self.player_name: str = "Traveler"
        self.start_time: datetime = datetime.now()

        # Mode tracking
        self.mode: str = "narrative"  # narrative | glyph_input | chamber | special
        self.current_scene: str = "market_arrival"

        # Emotional OS
        self.tone = ToneStats()
        self.remnants_traits: Dict[str, float] = {
            "truth": 0.0,
            "deception": 0.0,
            "competence": 0.0,
            "incompetence": 0.0,
            "social_consequence": 0.0,
            "emotional_inference": 0.0
        }

        # Glyphs
        self.glyphs: Dict[str, Glyph] = self._initialize_glyphs()
        # For chamber door glyph input
        self.glyphs_used_at_door: List[str] = []
        self.glyphs_used_on_npc: List[str] = []  # For emotional actions
        # For 8-glyph doors (page 1 = glyphs 0-3, page 2 = glyphs 4-7)
        self.glyph_page: int = 1
        self.glyphs_used_count: int = 0  # Counter for current page

        # Chamber mechanics
        self.mode_chamber: str = ""  # Which glyph beast we're facing
        self.fight_counter: int = 0  # Number of attacks
        self.fight_max: int = 15  # Threshold to obtain glyph

        # NPC perception
        self.npc_perception: Dict[str,
                                  NPCPerception] = self._initialize_npc_perception()

        # Skills
        self.skills: Dict[str, Skill] = self._initialize_skills()

        # Dialogue history
        self.dialogue_history: List[Dict[str, str]] = []

        # Choices made
        self.choices_made: List[Dict[str, Any]] = []

    def _initialize_glyphs(self) -> Dict[str, Glyph]:
        """Set up all available glyphs."""
        return {
            "Sorrow": Glyph(
                name="Sorrow",
                description="The glyph of deep understanding through loss",
                unlock_condition="marketplace_visit",
                emotional_effect="empathy",
                npc_resonance={"Ravi": 0.8}
            ),
            "Presence": Glyph(
                name="Presence",
                description="The glyph of being fully here",
                unlock_condition="npc_encounter",
                emotional_effect="resonance",
                npc_resonance={"Nima": 0.8}
            ),
            "Trust": Glyph(
                name="Trust",
                description="The glyph of belief in connection",
                unlock_condition="first_choice",
                emotional_effect="trust",
                npc_resonance={"Ravi": 0.6, "Veynar": 0.7}
            ),
            "Observation": Glyph(
                name="Observation",
                description="The glyph of knowing what matters",
                unlock_condition="marketplace_visit",
                emotional_effect="observation",
                npc_resonance={"Kaelen": 0.8}
            ),
            "Narrative Presence": Glyph(
                name="Narrative Presence",
                description="The glyph of charisma and agency",
                unlock_condition="first_dialogue",
                emotional_effect="narrative_presence",
                npc_resonance={"Ravi": 0.9, "Drossel": 0.8}
            ),
            "Transcendence": Glyph(
                name="Transcendence",
                description="The ultimate glyph of transformation",
                unlock_condition="chamber_victory",
                emotional_effect="resonance",
                npc_resonance={"all": 0.5}
            ),
        }

    def _initialize_npc_perception(self) -> Dict[str, NPCPerception]:
        """Set up NPC perception tracks with REMNANTS profiles."""
        return {
            "Ravi": NPCPerception(
                name="Ravi",
                emotion="thoughtful",
                remnants_profile=RemnantTraits(
                    resolve=0.7,  # Firm principles
                    empathy=0.8,  # Caring
                    memory=0.9,   # Bound to legacy
                    nuance=0.8,   # Complex thinker
                    authority=0.6,  # Moderate authority
                    need=0.7,     # Seeks understanding
                    trust=0.6,    # Cautious but fair
                    skepticism=0.5  # Balanced doubt
                )
            ),
            "Nima": NPCPerception(
                name="Nima",
                emotion="cautious",
                remnants_profile=RemnantTraits(
                    resolve=0.5,  # Flexible
                    empathy=0.9,  # High emotional capacity
                    memory=0.6,   # Some tradition
                    nuance=0.9,   # Subtle observer
                    authority=0.3,  # Low authority, respects others'
                    need=0.8,     # Seeks trust
                    trust=0.4,    # Skeptical baseline
                    skepticism=0.8  # High skepticism
                )
            ),
            "Veynar": NPCPerception(
                name="Veynar",
                emotion="uncertain",
                remnants_profile=RemnantTraits(
                    resolve=0.8,  # Very firm
                    empathy=0.4,  # Lower capacity
                    memory=0.7,   # Values tradition
                    nuance=0.5,   # Straightforward
                    authority=0.9,  # High authority
                    need=0.6,     # Seeks respect
                    trust=0.5,    # Neutral baseline
                    skepticism=0.7  # Somewhat skeptical
                )
            ),
            "Kaelen": NPCPerception(
                name="Kaelen",
                emotion="distant",
                remnants_profile=RemnantTraits(
                    resolve=0.6,  # Moderately firm
                    empathy=0.3,  # Low capacity
                    memory=0.4,   # Lives in present
                    nuance=0.4,   # Blunt
                    authority=0.5,  # Balanced
                    need=0.9,     # Seeks survival/resources
                    trust=0.2,    # Very skeptical
                    skepticism=0.9  # High skepticism
                )
            ),
        }

    def _initialize_skills(self) -> Dict[str, Skill]:
        """Set up learnable skills."""
        return {
            "Empathic Listening": Skill(
                name="Empathic Listening",
                description="Listen deeply to understand true needs",
                dialogue_banks=["ravi_vulnerable", "nima_trust"]
            ),
            "Tactical Awareness": Skill(
                name="Tactical Awareness",
                description="Assess situations with strategic clarity",
                dialogue_banks=["kaelen_strategy", "veynar_plans"]
            ),
            "Emotional Resonance": Skill(
                name="Emotional Resonance",
                description="Harmonize with others' emotional states",
                dialogue_banks=["glyph_fusion", "emotional_echo"]
            ),
        }

    # ========================================================================
    # GLYPH MANAGEMENT
    # ========================================================================

    def obtain_glyph(self, glyph_name: str) -> bool:
        """Mark a glyph as obtained."""
        if glyph_name in self.glyphs:
            self.glyphs[glyph_name].obtained = True
            return True
        return False

    def use_glyph_at_door(self, glyph_name: str) -> bool:
        """Use a glyph to unlock a chamber door."""
        if (glyph_name in self.glyphs and
            self.glyphs[glyph_name].obtained and
                glyph_name not in self.glyphs_used_at_door):
            self.glyphs_used_at_door.append(glyph_name)
            self.glyphs_used_count += 1
            return True
        return False

    def use_glyph_on_npc(self, glyph_name: str) -> bool:
        """Use a glyph to invoke special dialogue with an NPC."""
        if glyph_name in self.glyphs and self.glyphs[glyph_name].obtained:
            self.glyphs_used_on_npc.append(glyph_name)
            return True
        return False

    def reset_glyph_door_input(self) -> None:
        """Reset glyph input for new chamber door."""
        self.glyphs_used_at_door.clear()
        self.glyphs_used_count = 0
        self.glyph_page = 1

    def get_obtained_glyphs(self) -> List[str]:
        """Get list of obtained glyph names."""
        return [name for name, glyph in self.glyphs.items() if glyph.obtained]

    def get_usable_glyphs(self) -> List[str]:
        """Get glyphs that haven't been used at current door."""
        return [
            name for name in self.get_obtained_glyphs()
            if name not in self.glyphs_used_at_door
        ]

    # ========================================================================
    # TONE MANAGEMENT
    # ========================================================================

    def apply_tone_effect(self, effect: Dict[str, float]) -> None:
        """Apply tone modifications from a choice."""
        self.tone.apply_effect(effect)

    def get_tone_dict(self) -> Dict[str, float]:
        """Get current tone as dict."""
        return self.tone.to_dict()

    # ========================================================================
    # NPC PERCEPTION
    # ========================================================================

    def update_npc_perception(self, npc_name: str,
                              trust_delta: float = 0.0,
                              affinity_delta: float = 0.0,
                              understanding_delta: float = 0.0,
                              emotion: Optional[str] = None) -> None:
        """Update how an NPC perceives the player."""
        if npc_name not in self.npc_perception:
            return

        npc = self.npc_perception[npc_name]
        npc.trust = max(-1.0, min(1.0, npc.trust + trust_delta))
        npc.affinity = max(-1.0, min(1.0, npc.affinity + affinity_delta))
        npc.understanding = max(-1.0, min(1.0,
                                npc.understanding + understanding_delta))

        if emotion:
            npc.emotion = emotion

        npc.last_interaction = str(datetime.now())

    def get_npc_perception_dict(self) -> Dict[str, Dict[str, Any]]:
        """Get all NPC perceptions as dict."""
        return {
            name: npc.to_dict()
            for name, npc in self.npc_perception.items()
        }

    # ========================================================================
    # DIALOGUE TRACKING
    # ========================================================================

    def record_dialogue(self, npc_name: str, dialogue_text: str, is_player: bool = False) -> None:
        """Record a line of dialogue."""
        self.dialogue_history.append({
            "speaker": "Player" if is_player else npc_name,
            "text": dialogue_text,
            "timestamp": str(datetime.now())
        })

    def record_choice(self, choice_text: str, tone_effects: Dict[str, float] = None,
                      npc_resonance: Dict[str, float] = None) -> None:
        """Record a choice made by player."""
        self.choices_made.append({
            "text": choice_text,
            "timestamp": str(datetime.now()),
            "tone_effects": tone_effects or {},
            "npc_resonance": npc_resonance or {}
        })

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "player_name": self.player_name,
            "start_time": self.start_time.isoformat(),
            "mode": self.mode,
            "current_scene": self.current_scene,
            "tone": self.tone.to_dict(),
            "remnants_traits": self.remnants_traits,
            "glyphs": {
                name: glyph.to_dict()
                for name, glyph in self.glyphs.items()
            },
            "glyphs_used_at_door": self.glyphs_used_at_door,
            "glyphs_used_on_npc": self.glyphs_used_on_npc,
            "glyph_page": self.glyph_page,
            "fight_counter": self.fight_counter,
            "npc_perception": self.get_npc_perception_dict(),
            "skills": {
                name: skill.to_dict()
                for name, skill in self.skills.items()
            },
            "dialogue_history": self.dialogue_history[-10:],  # Last 10 lines
            "choices_made": len(self.choices_made)
        }
