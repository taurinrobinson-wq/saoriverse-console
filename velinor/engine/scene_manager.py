"""Velinor Scene Manager - Modular Scene Implementation

Orchestrates scene rendering with:
- Background/foreground layering
- Glyph resonance triggers
- Dialogue progression
- Player choice branching
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import streamlit as st


class SceneState(Enum):
    """Scene progression states."""
    DISTANT = "distant"
    APPROACH = "approach"
    CLOSE = "close"
    DIALOGUE = "dialogue"
    CHOICES = "choices"
    COMPLETE = "complete"


@dataclass
class SceneAssets:
    """Container for scene visual assets."""
    background_distant: Optional[str] = None
    background_close: Optional[str] = None
    foreground_distant: Optional[str] = None
    foreground_close: Optional[str] = None
    ambient_sound: Optional[str] = None
    
    def get_background(self, state: SceneState) -> Optional[str]:
        """Get background asset for given scene state."""
        if state in (SceneState.DISTANT, SceneState.APPROACH):
            return self.background_distant or self.background_close
        return self.background_close or self.background_distant
    
    def get_foreground(self, state: SceneState) -> Optional[str]:
        """Get foreground asset for given scene state."""
        if state == SceneState.DISTANT:
            return self.foreground_distant
        elif state in (SceneState.APPROACH, SceneState.CLOSE, SceneState.DIALOGUE, SceneState.CHOICES):
            return self.foreground_close
        return None


@dataclass
class DialogueOption:
    """A single player dialogue choice."""
    text: str
    glyph_triggers: List[str] = field(default_factory=list)
    npc_response: str = ""
    next_scene: Optional[str] = None
    trust_modifier: float = 0.0
    
    def __hash__(self):
        return hash(self.text)
    
    def __eq__(self, other):
        return self.text == other.text if isinstance(other, DialogueOption) else False


@dataclass
class SceneModule:
    """Complete modular scene definition."""
    scene_id: str
    npc_name: str
    npc_archetype: str  # "mistrusting", "welcoming", "oracle"
    
    # Narrative content
    narration_distant: str
    narration_close: str
    npc_dialogue: str
    
    # Assets
    assets: SceneAssets
    
    # Dialogue branching
    player_options: List[DialogueOption] = field(default_factory=list)
    
    # Glyph resonance
    glyph_distant: List[str] = field(default_factory=list)
    glyph_close: List[str] = field(default_factory=list)
    
    # State management
    current_state: SceneState = SceneState.DISTANT
    completed: bool = False


class SceneRenderer:
    """Renders scenes with proper layering and progression."""
    
    def __init__(self):
        """Initialize scene renderer."""
        self.current_scene: Optional[SceneModule] = None
        self.scene_history: List[str] = []
    
    def render_background(self, scene: SceneModule) -> None:
        """Render background image for current scene state."""
        bg_path = scene.assets.get_background(scene.current_state)
        if bg_path:
            try:
                st.image(bg_path, use_column_width=True)
            except Exception as e:
                st.warning(f"Could not load background: {e}")
    
    def render_foreground(self, scene: SceneModule, width: Optional[int] = None) -> None:
        """Render foreground image (NPC) for current scene state."""
        fg_path = scene.assets.get_foreground(scene.current_state)
        if fg_path:
            try:
                if width:
                    st.image(fg_path, width=width)
                else:
                    st.image(fg_path, use_column_width=True)
            except Exception as e:
                st.warning(f"Could not load foreground: {e}")
    
    def render_narration(self, scene: SceneModule) -> None:
        """Render narration text for current scene state."""
        narration = ""
        if scene.current_state == SceneState.DISTANT:
            narration = scene.narration_distant
        elif scene.current_state in (SceneState.APPROACH, SceneState.CLOSE):
            narration = scene.narration_close
        
        if narration:
            st.markdown(f"""
            <div class="dialogue-container">
            {narration}
            </div>
            """, unsafe_allow_html=True)
    
    def render_glyph_resonance(self, scene: SceneModule) -> None:
        """Render glyph resonance indicators."""
        glyphs = []
        if scene.current_state == SceneState.DISTANT:
            glyphs = scene.glyph_distant
        elif scene.current_state in (SceneState.APPROACH, SceneState.CLOSE, SceneState.DIALOGUE):
            glyphs = scene.glyph_close
        
        if glyphs:
            glyph_str = " ".join(glyphs)
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; opacity: 0.8;">
            <small>Glyph Resonance: {glyph_str}</small>
            </div>
            """, unsafe_allow_html=True)
    
    def render_npc_dialogue(self, scene: SceneModule) -> None:
        """Render NPC dialogue bubble."""
        if scene.current_state in (SceneState.DIALOGUE, SceneState.CHOICES):
            st.markdown(f"""
            <div class="npc-dialogue">
            <strong>{scene.npc_name}:</strong><br/>
            {scene.npc_dialogue}
            </div>
            """, unsafe_allow_html=True)
    
    def render_player_options(self, scene: SceneModule) -> Optional[DialogueOption]:
        """Render player dialogue options and capture choice."""
        if not scene.player_options:
            return None
        
        st.markdown("### How do you respond?")
        
        # Create unique keys for buttons
        for i, option in enumerate(scene.player_options):
            if st.button(
                option.text,
                key=f"{scene.scene_id}_option_{i}",
                use_container_width=True
            ):
                return option
        
        return None
    
    def render_scene(
        self,
        scene: SceneModule,
        auto_advance: bool = True
    ) -> Optional[DialogueOption]:
        """Full scene render with state progression.
        
        Args:
            scene: SceneModule to render
            auto_advance: Whether to auto-advance through states
            
        Returns:
            Selected DialogueOption if player has chosen, else None
        """
        self.current_scene = scene
        
        # Layered rendering
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_background(scene)
        
        with col2:
            self.render_foreground(scene, width=300)
        
        # Narration
        st.markdown("---")
        self.render_narration(scene)
        
        # Glyph resonance
        self.render_glyph_resonance(scene)
        
        # NPC Dialogue
        if scene.current_state != SceneState.DISTANT:
            st.markdown("---")
            self.render_npc_dialogue(scene)
        
        # Player choices
        if scene.current_state == SceneState.CHOICES:
            st.markdown("---")
            return self.render_player_options(scene)
        
        # Auto-advance button if not at choices yet
        if auto_advance and scene.current_state != SceneState.CHOICES:
            if st.button("Continue...", key=f"{scene.scene_id}_continue"):
                # Progress to next state
                if scene.current_state == SceneState.DISTANT:
                    scene.current_state = SceneState.APPROACH
                elif scene.current_state == SceneState.APPROACH:
                    scene.current_state = SceneState.CLOSE
                elif scene.current_state == SceneState.CLOSE:
                    scene.current_state = SceneState.DIALOGUE
                elif scene.current_state == SceneState.DIALOGUE:
                    scene.current_state = SceneState.CHOICES
                
                st.rerun()
        
        return None


class SceneBuilder:
    """Helper for building modular scenes."""
    
    @staticmethod
    def build_marketplace_arrival() -> SceneModule:
        """Build the marketplace arrival scene - player's first encounter."""
        return SceneModule(
            scene_id="market_arrival_01",
            npc_name="Velinor",
            npc_archetype="oracle",
            
            narration_distant="""
You notice someone in the distance.
She stands still amid the ruins, as if she's been waiting.
She appears to be some kind of priestess… or something older.
            """.strip(),
            
            narration_close="""
She comes closer to you.
Her eyes are transfixed on you — unblinking, unreadable.
You are intrigued. And a little intimidated.
Before you have a chance to speak, she does.
            """.strip(),
            
            npc_dialogue="""
"I see you. Not just your shape… but your ache."
"I am Velinor. And you are not lost — only unremembered."
            """.strip(),
            
            assets=SceneAssets(
                background_distant="velinor/backgrounds/marketplace_intact.png",
                background_close="velinor/backgrounds/marketplace_intact.png",
                foreground_distant="velinor/backgrounds/velinor_distant.png",
                foreground_close="velinor/backgrounds/velinor_close.png",
                ambient_sound="velinor/audio/wind_through_ruins.mp3"
            ),
            
            player_options=[
                DialogueOption(
                    text="Who are you really?",
                    glyph_triggers=["Querrä"],
                    npc_response="A question for another day. First, you must listen.",
                    trust_modifier=0.1
                ),
                DialogueOption(
                    text="What do you mean, 'unremembered'?",
                    glyph_triggers=["Thalen̈"],
                    npc_response="The glyphs will show you. But you must be ready to see.",
                    trust_modifier=0.15
                ),
                DialogueOption(
                    text="[Remain silent]",
                    glyph_triggers=["Aelitḧ"],
                    npc_response="Good. You know when to listen. That is rare.",
                    trust_modifier=0.2
                ),
            ],
            
            glyph_distant=["Esḧ"],
            glyph_close=["Cinarä̈", "Brethielï̈"],
        )
    
    @staticmethod
    def build_ravi_encounter() -> SceneModule:
        """Build first welcoming NPC encounter."""
        return SceneModule(
            scene_id="market_ravi_01",
            npc_name="Ravi",
            npc_archetype="welcoming",
            
            narration_distant="""
A figure emerges from behind a market stall.
He waves, a cautious smile crossing his weathered face.
He seems to be trying to place where he knows you from.
            """.strip(),
            
            narration_close="""
He approaches with genuine warmth, though his eyes carry caution.
"Welcome to the marketplace. You're new here, I can tell."
"Don't worry — most of us are just trying to survive."
            """.strip(),
            
            npc_dialogue="""
"I'd welcome you with open arms, but too many hands here have stolen lately."
"Still, I see something in you. You carry loss, but you're not here to take."
            """.strip(),
            
            assets=SceneAssets(
                background_distant="velinor/backgrounds/marketplace_intact.png",
                background_close="velinor/backgrounds/marketplace_intact.png",
                foreground_distant="velinor/backgrounds/ravi_distant.png",
                foreground_close="velinor/backgrounds/ravi_close.png",
            ),
            
            player_options=[
                DialogueOption(
                    text="I'm not here to steal. I'm here to listen.",
                    glyph_triggers=["Cinarä̈"],
                    npc_response="That's rare in these times. I think we can be friends.",
                    trust_modifier=0.25
                ),
                DialogueOption(
                    text="I know what it's like to lose trust.",
                    glyph_triggers=["Thalen̈"],
                    npc_response="Then you understand our fear. Stay close. I'll help you learn.",
                    trust_modifier=0.2
                ),
                DialogueOption(
                    text="Then let me earn it, slowly.",
                    glyph_triggers=["Aelitḧ"],
                    npc_response="Patience. Wisdom. You might do well here after all.",
                    trust_modifier=0.15
                ),
            ],
            
            glyph_distant=["Esḧ"],
            glyph_close=["Cinarä̈", "Brethielï̈"],
        )


# Session-based scene manager
def get_scene_renderer() -> SceneRenderer:
    """Get or create scene renderer in session state."""
    if "scene_renderer" not in st.session_state:
        st.session_state.scene_renderer = SceneRenderer()
    return st.session_state.scene_renderer


def get_current_scene() -> Optional[SceneModule]:
    """Get current active scene from session state."""
    return st.session_state.get("current_scene")


def set_current_scene(scene: SceneModule) -> None:
    """Set current active scene in session state."""
    st.session_state.current_scene = scene
