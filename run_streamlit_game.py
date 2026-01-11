#!/usr/bin/env python3
"""
Velinor Streamlit Game Launcher
================================
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

Usage:
    streamlit run run_streamlit_game.py
"""

import streamlit as st
from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.engine.core import VelinorEngine
from velinor.engine.npc_system import NPCDialogueSystem
from velinor.streamlit_state import StreamlitGameState
from velinor.streamlit_ui import StreamlitUI
import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def initialize_game():
    """Initialize the Velinor game engine and orchestrator."""
    try:
        # Story path
        story_path = str(Path(__file__).parent / "velinor" /
                         "stories" / "sample_story.json")

        # Initialize systems
        game_engine = VelinorEngine()
        game_engine.create_session(
            player_name=st.session_state.get("player_name", "Traveler"))

        npc_system = NPCDialogueSystem()

        # Initialize orchestrator with story path
        orchestrator = VelinorTwineOrchestrator(
            game_engine=game_engine,
            story_path=story_path,
            npc_system=npc_system,
            player_name=st.session_state.get("player_name", "Traveler")
        )

        # Start game and get initial state
        try:
            initial_state = orchestrator.start_game()
        except Exception:
            # If start_game fails, create a default state
            initial_state = {
                "scene": "market_arrival",
                "background_image": "marketplace",
                "npcs": ["Ravi", "Nima"],
                "main_dialogue": "Welcome to the marketplace. The city hums with activity around you.",
                "npc_dialogue": None,
                "choices": [
                    {"text": "Approach Ravi", "consequence": {"trust": 0.1}},
                    {"text": "Observe quietly", "consequence": {"observation": 0.1}},
                    {"text": "Wander the market", "consequence": {
                        "narrative_presence": 0.1}},
                    {"text": "Listen to the songs", "consequence": {"empathy": 0.1}}
                ]
            }

        return {
            "orchestrator": orchestrator,
            "engine": game_engine,
            "npc_system": npc_system,
            "initial_state": initial_state,
            "ui": StreamlitUI()
        }
    except Exception as e:
        st.error(f"Failed to initialize game: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        st.stop()


def handle_choice(choice_index: int):
    """Handle player selecting a dialogue choice."""
    orchestrator = st.session_state.game_systems["orchestrator"]
    try:
        new_state = orchestrator.process_player_action(
            choice_index=choice_index,
            player_id="player_1"
        )
        if new_state:
            st.session_state.current_state = new_state
    except Exception:
        # If orchestrator action fails, advance narrative manually
        choices = st.session_state.current_state.get("choices", [])
        if choice_index < len(choices):
            choice = choices[choice_index]
            # Apply choice consequences to TONE
            if "consequence" in choice:
                st.session_state.game_state.tone.apply_effect(
                    choice["consequence"])
            # Simple state advancement
            st.session_state.current_state["main_dialogue"] = f"You chose: {choice['text']}"

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
        st.rerun()


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Velinor: Remnants of the Tone",
        page_icon="🌙",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize game systems
    if "game_systems" not in st.session_state:
        st.session_state.game_systems = initialize_game()

    # Initialize game state if not already done
    if "game_state" not in st.session_state:
        st.session_state.game_state = StreamlitGameState()

    # Set current state from initial state
    if "current_state" not in st.session_state:
        st.session_state.current_state = st.session_state.game_systems["initial_state"]

    systems = st.session_state.game_systems
    game_state = st.session_state.game_state
    ui = systems["ui"]

    # ========================================================================
    # LAYOUT: MAIN + SIDEBAR
    # ========================================================================

    # Render sidebar (TONE, REMNANTS, Glyphs, Skills)
    ui.render_sidebar(game_state)

    # Main content area
    st.title("🌙 Velinor: Remnants of the Tone")
    st.divider()

    # Render background + overlay + dialogue
    ui.render_scene(st.session_state.current_state)

    st.divider()

    # Render button grid + fifth action button
    ui.render_button_grid(
        current_state=st.session_state.current_state,
        game_state=game_state,
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
                try:
                    st.session_state.game_systems["orchestrator"].save_game(
                        "velinor_save.json")
                    st.success("Game saved!")
                except Exception:
                    st.info("Save system not yet available")
        with col2:
            if st.button("Load Game"):
                try:
                    new_state = st.session_state.game_systems["orchestrator"].load_game(
                        "velinor_save.json")
                    if new_state:
                        st.session_state.current_state = new_state
                        st.rerun()
                except Exception:
                    st.info("Load system not yet available")
        with col3:
            if st.button("Reset Game"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        st.write("**Current Scene:**",
                 st.session_state.current_state.get("scene", "unknown"))
        st.write("**Mode:**", game_state.mode)
        st.write("**TONE Stats:**", game_state.tone.to_dict())
