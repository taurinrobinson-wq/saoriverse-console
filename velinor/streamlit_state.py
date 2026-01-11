"""
Streamlit Game State Management
===============================

Clean state machine for Velinor Streamlit prototype.

Tracks:
- Game mode (narrative, glyph_input, chamber, special)
- Glyphs (obtained, used, fusion state)
- TONE stats (courage, wisdom, empathy, resolve, resonance)
- REMNANTS traits
- NPC perception + emotional state
- Fight counter for chamber battles
- Skills unlocked
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ToneStats:
    """Player's emotional tone signature."""
    courage: float = 0.0
    wisdom: float = 0.0
    empathy: float = 0.0
    resolve: float = 0.0
    resonance: float = 0.0  # Overall harmonic balance

    def apply_effect(self, effect: Dict[str, float]):
        """Apply tone modifications from a choice."""
        for stat, value in effect.items():
            if hasattr(self, stat):
                setattr(self, stat, max(-1.0, min(1.0, getattr(self, stat) + value)))

    def to_dict(self) -> Dict[str, float]:
        return {
            "courage": round(self.courage, 2),
            "wisdom": round(self.wisdom, 2),
            "empathy": round(self.empathy, 2),
            "resolve": round(self.resolve, 2),
            "resonance": round(self.resonance, 2)
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
    """How an NPC perceives the player."""
    name: str
    trust: float = 0.0  # -1.0 to 1.0
    affinity: float = 0.0  # -1.0 to 1.0
    understanding: float = 0.0  # -1.0 to 1.0
    emotion: str = "neutral"  # emotional state
    last_interaction: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
            "Courage": Glyph(
                name="Courage",
                description="The glyph of moving forward despite fear",
                unlock_condition="first_choice",
                emotional_effect="courage",
                npc_resonance={"Ravi": 0.6, "Veynar": 0.7}
            ),
            "Wisdom": Glyph(
                name="Wisdom",
                description="The glyph of knowing what matters",
                unlock_condition="marketplace_visit",
                emotional_effect="wisdom",
                npc_resonance={"Kaelen": 0.8}
            ),
            "Transcendence": Glyph(
                name="Transcendence",
                description="The ultimate glyph of transformation",
                unlock_condition="chamber_victory",
                emotional_effect="resonance",
                npc_resonance={"all": 0.5}
            ),
            "Trust": Glyph(
                name="Trust",
                description="The glyph of believing in connection",
                unlock_condition="npc_bond",
                emotional_effect="empathy",
                npc_resonance={"Ravi": 0.9, "Nima": 0.7}
            ),
        }

    def _initialize_npc_perception(self) -> Dict[str, NPCPerception]:
        """Set up NPC perception tracks."""
        return {
            "Ravi": NPCPerception(name="Ravi", emotion="thoughtful"),
            "Nima": NPCPerception(name="Nima", emotion="cautious"),
            "Veynar": NPCPerception(name="Veynar", emotion="uncertain"),
            "Kaelen": NPCPerception(name="Kaelen", emotion="distant"),
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
