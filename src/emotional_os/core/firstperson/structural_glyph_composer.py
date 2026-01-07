"""Enhanced Glyph Response Composer (Phase 4).

Refactors glyph integration to make glyphs structural rather than decorative.

OLD APPROACH (Phase 2.2.2):
  Response generated → glyph lookup → glyph name appended at end
  Result: Glyph feels tacked on, decorative

NEW APPROACH (Phase 4):
  Affect analyzed → glyph selected as meaning anchor → response structured AROUND glyph
  Result: Glyph drives emotional logic and metaphorical structure

Integration points:
- Works with AgentStateManager for mood-aware glyph selection
- Uses glyph meaning to structure response
- Glyph becomes central to emotional coherence
"""

from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

try:
    from emotional_os.core.firstperson.glyph_modernizer import get_glyph_for_affect
except ImportError:
    # Fallback if glyph_modernizer not available
    def get_glyph_for_affect(tone: str) -> Dict[str, Any]:
        """Fallback glyph lookup."""
        glyph_map = {
            "sad": {"name": "Loss", "description": "the weight of absence"},
            "anxious": {"name": "Spiraling", "description": "circular thoughts"},
            "angry": {"name": "Fire", "description": "intense heat"},
            "grateful": {"name": "Warmth", "description": "connection and gratitude"},
            "overwhelmed": {"name": "Overwhelm", "description": "too much at once"},
            "reflective": {"name": "Stillness", "description": "deep thought"},
        }
        return glyph_map.get(tone, {"name": "Echo", "description": "resonance"})


@dataclass
class GlyphStructure:
    """A glyph used as meaning anchor for response structure."""
    glyph_name: str
    description: str
    meaning: str  # What this glyph means in context
    intensity: float  # 0-1, how strongly to emphasize


class StructuralGlyphComposer:
    """Composes responses where glyph is structural, not decorative."""
    
    def __init__(self):
        """Initialize composer."""
        self.recent_glyphs = []  # Track recent glyphs to avoid repetition
    
    def compose_with_structural_glyph(
        self,
        user_input: str,
        user_affect: Any,
        agent_state: Any,
        hypothesis: Optional[str] = None,
    ) -> str:
        """Compose response where glyph drives structure.
        
        Args:
            user_input: User's text
            user_affect: AffectAnalysis with tone, valence, arousal
            agent_state: AgentStateManager with mood
            hypothesis: Agent's emotional hypothesis about user
        
        Returns:
            Response where glyph is central
        """
        tone = getattr(user_affect, "tone", "neutral")
        arousal = getattr(user_affect, "arousal", 0.5)
        valence = getattr(user_affect, "valence", 0)
        
        # Step 1: Select glyph as meaning anchor
        glyph_dict = get_glyph_for_affect(tone)
        glyph = GlyphStructure(
            glyph_name=glyph_dict.get("name", "Echo"),
            description=glyph_dict.get("description", "resonance"),
            meaning=self._infer_glyph_meaning(tone, user_input),
            intensity=min(1.0, arousal),
        )
        
        # Step 2: Structure response around glyph
        response = self._structure_around_glyph(
            glyph=glyph,
            user_input=user_input,
            agent_mood=getattr(agent_state, "primary_mood", None) if agent_state else None,
            hypothesis=hypothesis,
            arousal=arousal,
        )
        
        # Track glyph usage
        self.recent_glyphs.append(glyph.glyph_name)
        if len(self.recent_glyphs) > 10:
            self.recent_glyphs = self.recent_glyphs[-10:]
        
        return response
    
    def _infer_glyph_meaning(self, tone: str, user_input: str) -> str:
        """Infer what the glyph means in this specific context.
        
        Args:
            tone: User's tone
            user_input: User's text
        
        Returns:
            Meaning description
        """
        # Map tone to meaning
        tone_meanings = {
            "sad": "the heaviness of what you're carrying",
            "anxious": "the thoughts that keep looping",
            "angry": "the intensity that needs expression",
            "frustrated": "the thing that won't move",
            "grateful": "the warmth of connection",
            "overwhelmed": "too much converging",
            "reflective": "the space you're holding",
            "uncertain": "the not-knowing",
            "vulnerable": "the openness of being seen",
        }
        
        meaning = tone_meanings.get(tone, "what you're experiencing")
        
        # Add detail from user input if possible
        if "can't" in user_input.lower() or "won't" in user_input.lower():
            meaning = f"{meaning} —something stuck"
        elif "too much" in user_input.lower():
            meaning = f"{meaning} —convergence"
        elif "alone" in user_input.lower():
            meaning = f"{meaning} —isolation"
        
        return meaning
    
    def _structure_around_glyph(
        self,
        glyph: GlyphStructure,
        user_input: str,
        agent_mood: Optional[str] = None,
        hypothesis: Optional[str] = None,
        arousal: float = 0.5,
    ) -> str:
        """Structure response around glyph as central element.
        
        Args:
            glyph: The glyph structure
            user_input: User's text
            agent_mood: Agent's current mood
            hypothesis: Agent's hypothesis about user
            arousal: User's arousal level
        
        Returns:
            Response structured around glyph
        """
        # Response structure:
        # 1. Acknowledge and name the glyph
        # 2. Explore what the glyph means
        # 3. Connect it to what user said
        # 4. Offer presence/next step
        
        lines = []
        
        # Line 1: Name the glyph with agency
        if arousal > 0.7:
            # High intensity: more direct
            lines.append(f"I'm hearing [{glyph.glyph_name}] in this.")
        else:
            # Lower intensity: more gentle
            lines.append(f"I'm sitting with [{glyph.glyph_name}] here.")
        
        # Line 2: Explore glyph meaning
        if agent_mood and agent_mood.value in ["moved", "protective", "concerned"]:
            # Agent is emotionally engaged: explore deeply
            lines.append(
                f"[{glyph.glyph_name}] is {glyph.meaning}."
            )
            lines.append(f"And when I sit with what you just said, I feel that too.")
        else:
            # Agent is listening: reflect back
            lines.append(f"[{glyph.glyph_name}] is {glyph.meaning}.")
        
        # Line 3: Connect to user's specific situation
        if hypothesis:
            lines.append(f"I think you're processing {hypothesis}.")
        else:
            # Extract something specific from user input
            if "can't stop" in user_input.lower():
                lines.append("And something keeps you here, won't let go.")
            elif "alone" in user_input.lower():
                lines.append("And you're feeling like you're carrying this alone.")
            elif "don't understand" in user_input.lower():
                lines.append("And you're trying to make sense of it.")
        
        # Line 4: Offer presence
        if agent_mood and agent_mood.value in ["protective", "moved"]:
            lines.append(f"I'm with you in the [{glyph.glyph_name.lower()}].")
        else:
            lines.append(f"I'm here with this.")
        
        # Join lines with appropriate spacing
        response = " ".join(lines)
        
        return response
    
    def should_avoid_glyph(self, glyph_name: str) -> bool:
        """Check if we've used this glyph recently.
        
        Args:
            glyph_name: Name of glyph
        
        Returns:
            True if we should avoid it
        """
        # Don't repeat glyphs within last 5 turns
        if len(self.recent_glyphs) < 5:
            return glyph_name in self.recent_glyphs
        
        recent = self.recent_glyphs[-5:]
        return glyph_name in recent


# Module-level singleton for integration

_composer = StructuralGlyphComposer()


def compose_structural_glyph_response(
    user_input: str,
    user_affect: Any,
    agent_state: Optional[Any] = None,
    hypothesis: Optional[str] = None,
) -> str:
    """Module-level function for structural glyph composition.
    
    Args:
        user_input: User's input
        user_affect: Affect analysis
        agent_state: Agent state manager (optional)
        hypothesis: Agent's hypothesis (optional)
    
    Returns:
        Response with structural glyph
    """
    return _composer.compose_with_structural_glyph(
        user_input, user_affect, agent_state, hypothesis
    )
