"""
Velinor Streamlit Prototype
============================

Full Streamlit implementation of Velinor: Remnants of the Tone
with modular UI, state management, and emotional OS integration.

Features:
- 2x2 button grid + fifth action button (choices, glyph input, fight loop)
- Sidebar TONE/REMNANTS/Glyphs/Skills tracking
- Background + NPC overlay rendering
- Scene transitions with dialogue
- Glyph collection and usage
- Chamber fight mechanics
- NPC perception and emotional consequences

Run:
    streamlit run velinor/streamlit_app.py
"""

# CRITICAL: Set up path before ANY other imports
from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.engine.core import VelinorEngine
from velinor.engine.npc_system import NPCDialogueSystem
from velinor.stories.story_definitions import build_velinor_story
from velinor.streamlit_state import StreamlitGameState
from velinor.streamlit_ui import StreamlitUI
import streamlit as st
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# NOW import streamlit and game modules


def initialize_game():
    """Initialize the Velinor game engine and orchestrator."""
    try:
        # Build story
        story_builder = build_velinor_story()
        story_data = story_builder.story_data

        # Initialize systems
        game_engine = VelinorEngine()
        game_engine.create_session(
            player_name=st.session_state.get("player_name", "Traveler"))

        npc_system = NPCDialogueSystem()

        orchestrator = VelinorTwineOrchestrator(
            game_engine=game_engine,
            story_path="velinor_story.json",  # In-memory
            npc_system=npc_system,
            player_name=st.session_state.get("player_name", "Traveler")
        )

        # Start game
        initial_state = orchestrator.start_game()

        return orchestrator, initial_state, story_data

    except Exception as e:
        import traceback
        st.error(f"Failed to initialize game: {e}")
        st.error(traceback.format_exc())
        return None, None, None


def main():
    """Main Streamlit app loop."""
    st.set_page_config(
        page_title="Velinor: Remnants of the Tone",
        page_icon="🌒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # ========================================================================
    # SESSION STATE INITIALIZATION
    # ========================================================================

    if "initialized" not in st.session_state:
        st.session_state.initialized = False

    if not st.session_state.initialized:
        st.session_state.player_name = "Traveler"
        st.session_state.game_state = StreamlitGameState()
        orchestrator, initial_state, story_data = initialize_game()

        if orchestrator and initial_state:
            st.session_state.orchestrator = orchestrator
            st.session_state.current_state = initial_state
            st.session_state.story_data = story_data
            st.session_state.initialized = True
        else:
            st.error("Failed to initialize game engine")
            return

    # ========================================================================
    # LAYOUT: MAIN + SIDEBAR
    # ========================================================================

    ui = StreamlitUI()

    # Render sidebar (TONE, REMNANTS, Glyphs, Skills)
    ui.render_sidebar(st.session_state.game_state)

    # Main content area
    st.title("🌒 Velinor: Remnants of the Tone")
    st.divider()

    # Render background + overlay + dialogue
    ui.render_scene(st.session_state.current_state)

    st.divider()

    # Render button grid + fifth action button
    ui.render_button_grid(
        current_state=st.session_state.current_state,
        game_state=st.session_state.game_state,
        on_choice=handle_choice,
        on_glyph_input=handle_glyph_input,
        on_attack=handle_attack,
        on_special_action=handle_special_action
    )

    # Debug panel (optional)
    with st.expander("🔧 Debug Panel"):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Save Game"):
                st.session_state.orchestrator.save_game("velinor_save.json")
                st.success("Game saved!")
        with col2:
            if st.button("Load Game"):
                new_state = st.session_state.orchestrator.load_game(
                    "velinor_save.json")
                if new_state:
                    st.session_state.current_state = new_state
                    st.rerun()
        with col3:
            if st.button("Reset Game"):
                st.session_state.initialized = False
                st.rerun()

        st.write("**Current Scene:**",
                 st.session_state.current_state.get("scene", "unknown"))
        st.write("**Mode:**", st.session_state.game_state.mode)
        st.write("**Game State:**")
        st.json(st.session_state.game_state.to_dict())


def handle_choice(choice_index: int):
    """Handle player selecting a dialogue choice."""
    orchestrator = st.session_state.orchestrator
    new_state = orchestrator.process_player_action(
        choice_index=choice_index,
        player_id="player_1"
    )

    if new_state:
        st.session_state.current_state = new_state
        st.rerun()


def handle_glyph_input(glyph_name: str):
    """Handle player selecting a glyph at chamber door."""
    game_state = st.session_state.game_state
    game_state.use_glyph_at_door(glyph_name)

    # Check if all glyphs used
    if game_state.glyphs_used_count >= 4:
        if game_state.glyph_page == 1:
            game_state.glyph_page = 2
        else:
            # Ready to enter chamber
            game_state.mode = "chamber"
            st.rerun()
    else:
        st.rerun()


def handle_attack():
    """Handle attack button in chamber fight."""
    game_state = st.session_state.game_state
    game_state.fight_counter += 1

    if game_state.fight_counter >= 15:
        game_state.mode = "chamber_complete"

    st.rerun()


def handle_special_action(action: str):
    """Handle special glyph action."""
    game_state = st.session_state.game_state

    if action.startswith("use_glyph_"):
        glyph_name = action.replace("use_glyph_", "")
        game_state.use_glyph_on_npc(glyph_name)

        # Update dialogue/choices based on glyph use
        # This will be handled by the orchestrator's emotional OS
        st.rerun()


if __name__ == "__main__":
    main()
