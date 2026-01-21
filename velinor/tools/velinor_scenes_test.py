"""
Velinor Scene Testing Interface - Streamlit Application
========================================================

Simplified interface for testing and building marketplace scenes
with the modular scene system.

This app demonstrates:
- Background/foreground layering
- NPC dialogue progression
- Glyph resonance triggers
- Player choice tracking
- Trust system integration
"""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from velinor.engine.scene_manager import (
    SceneRenderer,
    SceneBuilder,
    get_scene_renderer,
    get_current_scene,
    set_current_scene,
)
from velinor.engine.marketplace_scenes import MarketplaceSceneSequence

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Velinor: Marketplace Scenes",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    body { background-color: #ffffff; color: #1f2937; }
    .stApp { background-color: #ffffff; }
    
    /* Main dialogue container */
    .dialogue-container {
        background: linear-gradient(135deg, #f0f4ff 0%, #f5f8ff 100%);
        border-left: 4px solid #7c3aed;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 16px;
        line-height: 1.8;
        color: #1f2937;
    }
    
    /* NPC dialogue bubble */
    .npc-dialogue {
        background: linear-gradient(135deg, #ede9fe 0%, #faf5ff 100%);
        border-left: 4px solid #a78bfa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-style: italic;
        color: #5b21b6;
    }
    
    /* Stats panel */
    .stats-panel {
        background: linear-gradient(135deg, #f3f4f6 0%, #f9fafb 100%);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        color: #1f2937;
    }
    
    /* Title styling */
    .title-section {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%);
        border-radius: 12px;
        border: 2px solid #3b82f6;
        margin-bottom: 20px;
        color: #1e40af;
    }
    
    /* Glyph resonance */
    .glyph-resonance {
        text-align: center;
        padding: 10px;
        opacity: 0.8;
        color: #7c3aed;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def initialize_session():
    """Initialize session state for marketplace scenes."""
    if 'scene_session_initialized' not in st.session_state:
        st.session_state.scene_session_initialized = True
        st.session_state.current_scene_index = 0
        st.session_state.scenes = MarketplaceSceneSequence.get_sequence()
        st.session_state.scene_renderer = SceneRenderer()
        st.session_state.player_name = "Traveler"
        st.session_state.player_trust = {
            "ravi": 0.0,
            "nima": 0.0,
        }
        st.session_state.dialogue_history = []
        st.session_state.choices_made = []
        st.session_state.game_started = False


initialize_session()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def record_choice(scene_id: str, choice_text: str, trust_modifier: float) -> None:
    """Record player choice in session history."""
    st.session_state.choices_made.append({
        "scene_id": scene_id,
        "choice": choice_text,
        "timestamp": datetime.now().isoformat(),
        "trust_modifier": trust_modifier,
    })


def update_player_trust(npc_name: str, modifier: float) -> None:
    """Update trust value for an NPC."""
    if npc_name.lower() in st.session_state.player_trust:
        st.session_state.player_trust[npc_name.lower()] = min(
            1.0,
            max(0.0, st.session_state.player_trust[npc_name.lower()] + modifier)
        )


def render_player_stats() -> None:
    """Render player stats panel in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Player Stats")
    st.sidebar.markdown(f"**Name:** {st.session_state.player_name}")
    
    st.sidebar.markdown("**NPC Trust Levels:**")
    for npc, trust in st.session_state.player_trust.items():
        trust_pct = int(trust * 100)
        st.sidebar.metric(
            f"{npc.capitalize()}",
            f"{trust_pct}%",
            delta=None
        )


def render_scene_controls() -> None:
    """Render scene navigation controls in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎬 Scene Navigation")
    
    total_scenes = len(st.session_state.scenes)
    current_idx = st.session_state.current_scene_index
    
    st.sidebar.info(f"Scene {current_idx + 1} of {total_scenes}")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("← Previous", disabled=(current_idx == 0)):
            st.session_state.current_scene_index = max(0, current_idx - 1)
            st.rerun()
    
    with col2:
        if st.button("Next →", disabled=(current_idx >= total_scenes - 1)):
            st.session_state.current_scene_index = min(total_scenes - 1, current_idx + 1)
            st.rerun()


def render_dialogue_history() -> None:
    """Render dialogue history in expandable sidebar section."""
    if st.session_state.choices_made:
        with st.sidebar.expander("📝 Dialogue History"):
            for i, entry in enumerate(st.session_state.choices_made, 1):
                st.write(f"**Choice {i}:** {entry['choice']}")
                if entry['trust_modifier'] > 0:
                    st.caption(f"Trust +{int(entry['trust_modifier'] * 100)}%")


# ============================================================================
# MAIN RENDERING
# ============================================================================

def render_current_scene() -> None:
    """Render the current marketplace scene."""
    renderer = st.session_state.scene_renderer
    scenes = st.session_state.scenes
    current_idx = st.session_state.current_scene_index
    
    if current_idx >= len(scenes):
        st.error("Scene index out of range!")
        return
    
    scene = scenes[current_idx]
    set_current_scene(scene)
    
    # Render scene
    choice = renderer.render_scene(scene, auto_advance=True)
    
    # If player made a choice, update state and record it
    if choice:
        record_choice(scene.scene_id, choice.text, choice.trust_modifier)
        
        # Update trust based on NPC
        if scene.npc_archetype == "welcoming":
            update_player_trust("ravi", choice.trust_modifier)
        elif scene.npc_archetype == "mistrusting":
            update_player_trust("nima", choice.trust_modifier)
        
        # Show response
        st.markdown("---")
        st.success(f"✨ **{scene.npc_name}:** {choice.npc_response}")
        
        # Advance to next scene if available
        if current_idx + 1 < len(scenes):
            st.info(f"📍 Moving to next scene...")
            st.session_state.current_scene_index = current_idx + 1
            st.rerun()


def render_welcome_screen() -> None:
    """Render welcome/start screen."""
    st.markdown("""
    <div class='title-section'>
        <h1>🎭 Velinor: Marketplace Scenes</h1>
        <p>Interactive Scene Testing & Development</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ## Welcome to the Velinor Marketplace
    
    This is an interactive walkthrough of the marketplace arrival sequence.
    You'll encounter NPCs, make choices, and build trust as you explore.
    
    **Sequence includes:**
    1. **Marketplace Arrival** - Your first view of the city
    2. **Ravi's Encounter** - A welcoming NPC greets you
    3. **Nima's Encounter** - A mistrusting guard tests you
    4. **Collapse Event** - The city itself becomes dynamic
    5. **Map Introduction** - Learn to navigate the marketplace
    
    ---
    
    **Ready to begin?**
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        player_name = st.text_input("What is your name?", value="Traveler")
        if player_name:
            st.session_state.player_name = player_name
    
    with col2:
        if st.button("🚀 Start the Sequence", use_container_width=True):
            st.session_state.game_started = True
            st.session_state.current_scene_index = 0
            st.rerun()


def main():
    """Main application entry point."""
    
    # Render sidebar controls
    render_player_stats()
    render_scene_controls()
    render_dialogue_history()
    
    # Main content
    if not st.session_state.game_started:
        render_welcome_screen()
    else:
        render_current_scene()


if __name__ == "__main__":
    main()
