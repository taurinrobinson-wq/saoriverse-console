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

        return {
            "orchestrator": orchestrator,
            "engine": game_engine,
            "npc_system": npc_system,
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

    # Initialize game state if not already done
    if "game_state" not in st.session_state:
        st.session_state.game_state = StreamlitGameState()

    systems = st.session_state.game_systems
    game_state = st.session_state.game_state
    orchestrator = systems["orchestrator"]

    # Display basic game info
    st.title("🌙 Velinor: Remnants of the Tone")
    st.write("Game engine initialized successfully!")

    # Show basic game state
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Game State")
        st.write(f"**Mode:** {game_state.mode}")
        st.write(f"**Current Scene:** {game_state.current_scene}")
        st.write(f"**Player:** {game_state.player_name}")

    with col2:
        st.subheader("🎼 TONE Stats")
        tone_dict = game_state.tone.to_dict()
        for stat, value in tone_dict.items():
            st.write(f"**{stat}:** {value}")

    # Show available glyphs
    st.subheader("✨ Glyphs")
    glyphs = game_state.glyphs
    for glyph_name, glyph_obj in glyphs.items():
        st.write(f"- **{glyph_name}**: {glyph_obj.description}")


if __name__ == "__main__":
    main()
