#!/usr/bin/env python3
"""
Velinor Streamlit Game Launcher
================================
Runs the Streamlit game with proper path setup from project root.

Usage:
    python run_streamlit_game.py
    
OR from command line:
    streamlit run run_streamlit_game.py
"""

import streamlit as st
from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.engine.core import VelinorEngine
from velinor.engine.npc_system import NPCDialogueSystem
from velinor.stories.story_definitions import build_velinor_story
from velinor.streamlit_state import StreamlitGameState
from velinor.streamlit_ui import StreamlitUI
import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now we can safely import and run the game


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
            story=story_data,
            engine=game_engine,
            npc_system=npc_system
        )

        return {
            "orchestrator": orchestrator,
            "engine": game_engine,
            "npc_system": npc_system,
            "story": story_data,
            "ui": StreamlitUI()
        }
    except Exception as e:
        st.error(f"Failed to initialize game: {str(e)}")
        st.stop()


def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="Velinor: Remnants of the Tone",
        page_icon="🌙",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize game systems
    if "game_systems" not in st.session_state:
        st.session_state.game_systems = initialize_game()

    systems = st.session_state.game_systems
    orchestrator = systems["orchestrator"]
    ui = systems["ui"]

    # Render UI
    ui.render_sidebar(st.session_state)
    ui.render_scene(orchestrator, st.session_state)
    ui.render_button_grid(orchestrator, st.session_state)


if __name__ == "__main__":
    main()
