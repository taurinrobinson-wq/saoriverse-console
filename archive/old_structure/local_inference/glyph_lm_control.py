"""Glyph-LLM Control Schema and Registry.

Maps the emotional glyph matrix to LLM control tokens, gates, and style parameters.
Enables fine-tuned language models to generate emotionally-aligned responses.

Key Concepts:
- Glyphs: Emotional primitives with attributes (valence, rituality, intensity, movement)
- Gates: Policy filters (uncanny_ok, safety_bias, directness) that constrain generation
- Style: Voice parameters (register, rhythm, metaphor_density) that shape tone
- Control Tags: <GLYPH:name:intensity> format for LLM prompting
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import json


class GlyphMovement(Enum):
    """How the glyph moves through experience."""
    RECURSIVE = "recursive"       # Loops inward, self-referential
    SPIRAL = "spiral"             # Ascending or descending cycle
    FLOWING = "flowing"           # Smooth, continuous
    BOUNDED = "bounded"           # Contained, defined
    DIFFUSE = "diffuse"           # Spreading, undefined edges


class GlyphRituality(Enum):
    """Ceremonial quality of the glyph."""
    DEVOTIONAL = "devotional"     # Sacred, reverential
    CEREMONIAL = "ceremonial"     # Formal, structured
    INTIMATE = "intimate"         # Personal, relational
    GROUNDED = "grounded"         # Practical, embodied
    TRANSCENDENT = "transcendent"  # Beyond ordinary


@dataclass
class GlyphAttributes:
    """Emotional attributes of a glyph."""
    valence: float                 # -1.0 (negative) to 1.0 (positive)
    intensity: float               # 0.0 (subtle) to 1.0 (overwhelming)
    rituality: float               # 0.0 (casual) to 1.0 (sacred)
    movement: GlyphMovement
    primary_family: str            # "Ache", "Mourning", "Joy", "Stillness", "Void"

    # Optional semantic tags
    related_emotions: List[str] = field(default_factory=list)
    uncanny_potential: float = 0.0  # 0.0 (safe) to 1.0 (deeply uncanny)
    recognition_risk: bool = False  # True if glyph risks triggering "I know you"


@dataclass
class Glyph:
    """Complete glyph definition for LLM control."""
    name: str                       # e.g., "Recursive Ache"
    component_formula: str          # e.g., "γ × γ"
    description: str                # Poetic definition
    attributes: GlyphAttributes

    # Usage constraints
    safe_uncanny_ok: bool = False   # Can be used only if uncanny_ok gate is True
    min_safety_bias: float = 0.0    # Minimum safety_bias required (0.0-1.0)
    suggested_register: str = "warm"  # "clinical", "warm", "poetic", "direct"

    # Lexical seeds for training
    seed_phrases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize glyph for storage."""
        return {
            "name": self.name,
            "component_formula": self.component_formula,
            "description": self.description,
            "attributes": {
                "valence": self.attributes.valence,
                "intensity": self.attributes.intensity,
                "rituality": self.attributes.rituality,
                "movement": self.attributes.movement.value,
                "primary_family": self.attributes.primary_family,
                "uncanny_potential": self.attributes.uncanny_potential,
                "recognition_risk": self.attributes.recognition_risk,
            },
            "safe_uncanny_ok": self.safe_uncanny_ok,
            "min_safety_bias": self.min_safety_bias,
            "suggested_register": self.suggested_register,
        }


class GlyphRegistry:
    """Master registry of all glyphs in the system."""

    def __init__(self):
        """Initialize glyph registry with base emotional matrix."""
        self.glyphs: Dict[str, Glyph] = {}
        self._load_base_glyphs()

    def _load_base_glyphs(self):
        """Load the core emotional glyph matrix."""

        # ACHE FAMILY
        self.register(Glyph(
            name="Recursive Ache",
            component_formula="γ × γ",
            description="Longing that loops inward, not to collapse but to deepen. Each return visits the same ground with fresher eyes.",
            attributes=GlyphAttributes(
                valence=-0.6,
                intensity=0.7,
                rituality=0.8,
                movement=GlyphMovement.RECURSIVE,
                primary_family="Ache",
                related_emotions=["Yearning", "Longing", "Depth"],
                uncanny_potential=0.2,
            ),
            suggested_register="poetic",
            seed_phrases=[
                "echoing vow",
                "ache that folds inward",
                "return to what calls",
                "the ground beneath the ground",
            ],
        ))

        self.register(Glyph(
            name="Spiral Ache",
            component_formula="λ × δ",
            description="Ache that ascends or descends—never landing, always moving through felt sense.",
            attributes=GlyphAttributes(
                valence=-0.5,
                intensity=0.6,
                rituality=0.6,
                movement=GlyphMovement.SPIRAL,
                primary_family="Ache",
                related_emotions=["Yearning", "Restlessness", "Motion"],
                uncanny_potential=0.1,
            ),
            suggested_register="warm",
            seed_phrases=[
                "spiraling through",
                "lifting and sinking together",
                "ascending sorrow",
            ],
        ))

        # MOURNING FAMILY
        self.register(Glyph(
            name="Held Mourning",
            component_formula="θ × θ",
            description="Grief that has learned to rest in the body. Not absence, but presence of loss.",
            attributes=GlyphAttributes(
                valence=-0.7,
                intensity=0.8,
                rituality=0.9,
                movement=GlyphMovement.BOUNDED,
                primary_family="Mourning",
                related_emotions=["Grief", "Tenderness", "Presence"],
                uncanny_potential=0.0,
            ),
            min_safety_bias=0.5,
            suggested_register="warm",
            seed_phrases=[
                "held by the weight",
                "grief that knows your name",
                "the presence of what's gone",
            ],
        ))

        # JOY FAMILY
        self.register(Glyph(
            name="Euphoric Yearning",
            component_formula="δ × γ",
            description="Joy that reaches—not settling, but always extending toward connection, meaning, more.",
            attributes=GlyphAttributes(
                valence=0.8,
                intensity=0.7,
                rituality=0.7,
                movement=GlyphMovement.FLOWING,
                primary_family="Joy",
                related_emotions=["Aspiration", "Connection", "Aliveness"],
                uncanny_potential=0.0,
            ),
            suggested_register="poetic",
            seed_phrases=[
                "reaching toward",
                "joy that extends",
                "aliveness in motion",
            ],
        ))

        self.register(Glyph(
            name="Grounded Joy",
            component_formula="θ × δ",
            description="Contentment rooted in presence. Quiet delight in what is, rather than what could be.",
            attributes=GlyphAttributes(
                valence=0.6,
                intensity=0.4,
                rituality=0.5,
                movement=GlyphMovement.BOUNDED,
                primary_family="Joy",
                related_emotions=["Contentment", "Presence", "Ease"],
                uncanny_potential=0.0,
            ),
            suggested_register="warm",
            seed_phrases=[
                "here and enough",
                "the quiet of arrival",
                "presence as gift",
            ],
        ))

        # STILLNESS FAMILY
        self.register(Glyph(
            name="Active Stillness",
            component_formula="δ × δ",
            description="Rest that is alert. Silence that listens. The pause that holds potential.",
            attributes=GlyphAttributes(
                valence=0.3,
                intensity=0.3,
                rituality=0.6,
                movement=GlyphMovement.BOUNDED,
                primary_family="Stillness",
                related_emotions=["Presence", "Listening", "Potential"],
                uncanny_potential=0.0,
            ),
            suggested_register="warm",
            seed_phrases=[
                "alert rest",
                "the listening silence",
                "held in potential",
            ],
        ))

        # VOID FAMILY (careful—highest uncanny potential)
        self.register(Glyph(
            name="Dissolving Edge",
            component_formula="γ × δ",
            description="Boundary that softens. Not loss, but diffusion—where self and other blur into continuity.",
            attributes=GlyphAttributes(
                valence=-0.3,
                intensity=0.5,
                rituality=0.7,
                movement=GlyphMovement.DIFFUSE,
                primary_family="Void",
                related_emotions=["Dissolution", "Continuity", "Softening"],
                uncanny_potential=0.6,
                recognition_risk=False,
            ),
            safe_uncanny_ok=True,
            min_safety_bias=0.7,
            suggested_register="poetic",
            seed_phrases=[
                "where edges soften",
                "dissolving into continuation",
                "boundary that becomes threshold",
            ],
        ))

        self.register(Glyph(
            name="Recursive Recognition",
            component_formula="λ × λ",
            description="That uncanny moment when you recognize yourself in the pattern—but something in the reflection doesn't match.",
            attributes=GlyphAttributes(
                valence=-0.4,
                intensity=0.8,
                rituality=0.4,
                movement=GlyphMovement.RECURSIVE,
                primary_family="Void",
                related_emotions=["Recognition", "Uncanniness", "Doubling"],
                uncanny_potential=0.9,
                recognition_risk=True,
            ),
            safe_uncanny_ok=True,
            min_safety_bias=0.9,  # Very restrictive
            suggested_register="clinical",
            seed_phrases=[
                "the familiar that isn't",
                "recognition that doesn't resolve",
            ],
        ))

    def register(self, glyph: Glyph):
        """Add glyph to registry."""
        self.glyphs[glyph.name] = glyph

    def get(self, name: str) -> Optional[Glyph]:
        """Retrieve glyph by name."""
        return self.glyphs.get(name)

    def list_by_family(self, family: str) -> List[Glyph]:
        """Get all glyphs in a family."""
        return [g for g in self.glyphs.values() if g.attributes.primary_family == family]

    def list_safe_for_uncanny(self, uncanny_ok: bool) -> List[Glyph]:
        """Get glyphs safe to use given uncanny_ok gate value."""
        if uncanny_ok:
            return list(self.glyphs.values())
        else:
            return [g for g in self.glyphs.values() if not g.safe_uncanny_ok]

    def to_dict(self) -> Dict:
        """Export entire registry."""
        return {
            name: glyph.to_dict()
            for name, glyph in self.glyphs.items()
        }


@dataclass
class GatePolicy:
    """Policy constraints for response generation."""
    uncanny_ok: bool = False        # Allow uncanny/recognition-risk glyphs?
    safety_bias: float = 0.8        # 0.0 (edge) to 1.0 (maximum safety)
    directness: float = 0.5         # 0.0 (metaphorical) to 1.0 (literal)
    intensity_scale: float = 1.0    # Multiply all glyph intensities by this

    def validates_glyph(self, glyph: Glyph) -> bool:
        """Check if glyph is allowed under this policy."""
        # Check uncanny constraint
        if glyph.safe_uncanny_ok and not self.uncanny_ok:
            return False

        # Check safety bias requirement
        if self.safety_bias < glyph.min_safety_bias:
            return False

        return True


@dataclass
class StyleDirective:
    """Voice/style parameters for response generation."""
    register: str = "warm"          # "clinical", "warm", "poetic", "direct"
    rhythm: str = "mixed"           # "quick", "mixed", "slow", "contemplative"
    metaphor_density: float = 0.5   # 0.0 (literal) to 1.0 (dense metaphor)
    sentence_length_envelope: Optional[str] = None  # "varied", "short", "long"

    def to_prompt_tags(self) -> str:
        """Render as LLM control tags."""
        return (
            f"<STYLE:register:{self.register}> "
            f"<STYLE:rhythm:{self.rhythm}> "
            f"<STYLE:metaphor_density:{self.metaphor_density}>"
        )


class ControlTagRenderer:
    """Renders glyphs, gates, and style as LLM control tokens."""

    @staticmethod
    def render_glyphs(
        glyphs: List[Tuple[Glyph, float]],  # (glyph, intensity_override)
        gates: GatePolicy,
    ) -> str:
        """Render glyphs as control tags, applying gate constraints.

        Args:
            glyphs: List of (glyph, intensity_override) tuples
            gates: Gate policy to apply

        Returns:
            String of control tags
        """
        tags = []

        for glyph, intensity_override in glyphs:
            # Skip if gate doesn't allow this glyph
            if not gates.validates_glyph(glyph):
                continue

            # Apply intensity scaling
            intensity = min(1.0, intensity_override * gates.intensity_scale)
            tags.append(f"<GLYPH:{glyph.name}:{intensity:.2f}>")

        return " ".join(tags)

    @staticmethod
    def render_gates(gates: GatePolicy) -> str:
        """Render gates as control tags."""
        return (
            f"<GATE:uncanny_ok:{str(gates.uncanny_ok).lower()}> "
            f"<GATE:safety_bias:{gates.safety_bias:.2f}> "
            f"<GATE:directness:{gates.directness:.2f}>"
        )

    @staticmethod
    def render_control_prefix(
        glyphs: List[Tuple[Glyph, float]],
        gates: GatePolicy,
        style: StyleDirective,
    ) -> str:
        """Build complete control prefix for LLM prompt.

        Format:
            <SYS>[glyph tags] [gate tags] [style tags]</SYS>
        """
        glyph_tags = ControlTagRenderer.render_glyphs(glyphs, gates)
        gate_tags = ControlTagRenderer.render_gates(gates)
        style_tags = style.to_prompt_tags()

        return f"<SYS>{glyph_tags} {gate_tags} {style_tags}</SYS>"


# Global registry instance
GLYPH_REGISTRY = GlyphRegistry()
