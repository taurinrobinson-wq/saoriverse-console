"""
Velinor Twine Integration - Quick Start Guide
==============================================

This module shows how to initialize and run the complete Velinor system:
- Game Engine (state management, dice rolls, stats)
- Twine Story System (narrative flow, choices)
- FirstPerson Orchestrator (dynamic dialogue, emotional resonance)
"""

from velinor.engine import (
    VelinorEngine,
    VelinorTwineOrchestrator,
    TwineStoryLoader,
    NPCDialogueSystem,
)


def initialize_game(
    story_path: str = '/Volumes/My Passport for Mac/saoriverse-console/velinor/stories/sample_story.json',
    player_name: str = "Traveler",
    is_multiplayer: bool = False,
    player_ids: list = None
):
    """
    Initialize a complete Velinor game session.
    
    Args:
        story_path: Path to Twine story JSON file
        player_name: Name of the player character
        is_multiplayer: Enable multiplayer mode
        player_ids: List of player IDs for multiplayer
    
    Returns:
        VelinorTwineOrchestrator ready to play
    """
    
    # 1. Initialize game engine
    print("[*] Initializing game engine...")
    game_engine = VelinorEngine()
    game_engine.create_session(player_name=player_name)
    
    # 2. Initialize NPC dialogue system
    print("[*] Setting up NPC dialogue system...")
    npc_system = NPCDialogueSystem()
    
    # Note: FirstPerson orchestrator would be imported from your main system
    # from src.emotional_os.deploy.core.firstperson import FirstPersonOrchestrator
    # first_person = FirstPersonOrchestrator()
    first_person = None  # Optional - game works without it, just won't have dynamic dialogue
    
    # 3. Initialize Twine + game orchestrator
    print(f"[*] Loading story from: {story_path}")
    orchestrator = VelinorTwineOrchestrator(
        game_engine=game_engine,
        story_path=story_path,
        first_person_module=first_person,
        npc_system=npc_system
    )
    
    # 4. Start game
    print("[*] Starting game...")
    initial_state = orchestrator.start_game(
        is_multiplayer=is_multiplayer,
        player_ids=player_ids or []
    )
    
    print("\n" + "="*60)
    print("VELINOR: REMNANTS OF THE TONE")
    print("="*60 + "\n")
    
    return orchestrator, initial_state


def display_ui_state(state: dict) -> None:
    """Pretty-print game state for terminal UI."""
    print("\n" + "-"*60)
    
    # Background / location
    if state.get('background_image'):
        print(f"📍 Location: {state['background_image']}")
    
    # NPC info
    if state.get('npc_name'):
        print(f"👤 Speaking with: {state['npc_name']}")
    
    # Main dialogue
    print(f"\n{state.get('main_dialogue', '[No dialogue]')}\n")
    
    # NPC response (if generated)
    if state.get('npc_dialogue'):
        print(f"{state['npc_dialogue']}\n")
    
    # Clarifying question
    if state.get('has_clarifying_question') and state.get('clarifying_question'):
        print(f"💭 {state['clarifying_question']}\n")
    
    # Choices
    choices = state.get('choices', [])
    if choices:
        print("Options:")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice.get('text', 'Unknown')}")
    
    # Stats
    if state.get('game_state', {}).get('player_stats'):
        stats = state['game_state']['player_stats']
        print(f"\n📊 Stats:")
        print(f"   Courage: {stats.get('courage', 0)} | Wisdom: {stats.get('wisdom', 0)}")
        print(f"   Empathy: {stats.get('empathy', 0)} | Resolve: {stats.get('resolve', 0)}")
        print(f"   Resonance: {stats.get('resonance', 0)}")
    
    # Dice results if any
    if state.get('dice_roll'):
        roll = state['dice_roll']
        print(f"\n🎲 Dice Roll Result: {roll.get('raw_roll')} " +
              f"(DC {roll.get('difficulty', 'N/A')}) - " +
              f"{'✅ Success!' if roll.get('success') else '❌ Failure'}")
    
    print("-"*60)


def play_turn(orchestrator: VelinorTwineOrchestrator, player_input: str = None, choice_index: int = None):
    """
    Execute one game turn.
    
    Args:
        orchestrator: Game orchestrator instance
        player_input: Free-text player response
        choice_index: Selected choice index (0-based)
    
    Returns:
        Updated game state
    """
    if player_input is None and choice_index is None:
        return None
    
    state = orchestrator.process_player_action(
        player_input=player_input or "",
        choice_index=choice_index,
        player_id="player_1"
    )
    
    return state


# ============================================================================
# EXAMPLE: How to use in a Streamlit app or web UI
# ============================================================================

EXAMPLE_STREAMLIT_CODE = """
import streamlit as st
from velinor_quickstart import initialize_game, display_ui_state, play_turn

# Initialize session state
if 'orchestrator' not in st.session_state:
    orchestrator, initial_state = initialize_game()
    st.session_state.orchestrator = orchestrator
    st.session_state.current_state = initial_state
else:
    orchestrator = st.session_state.orchestrator
    initial_state = st.session_state.current_state

# Display current game state
display_ui_state(st.session_state.current_state)

# Get player input
col1, col2 = st.columns([2, 1])

with col1:
    player_text = st.text_input("Your response:", key="player_input")

# Display choice buttons
current_state = st.session_state.current_state
for i, choice in enumerate(current_state.get('choices', [])):
    if st.button(choice['text'], key=f"choice_{i}"):
        # Process choice
        new_state = play_turn(orchestrator, choice_index=i)
        st.session_state.current_state = new_state
        st.rerun()

# Process free text
if st.button("Submit Response"):
    if player_text:
        new_state = play_turn(orchestrator, player_input=player_text)
        st.session_state.current_state = new_state
        st.rerun()

# Save/Load buttons
if st.button("Save Game"):
    orchestrator.save_game('velinor_save.json')
    st.success("Game saved!")

if st.button("Load Game"):
    new_state = orchestrator.load_game('velinor_save.json')
    st.session_state.current_state = new_state
    st.rerun()
"""


# ============================================================================
# EXAMPLE: How to use in a web framework (Flask/FastAPI)
# ============================================================================

EXAMPLE_WEB_CODE = """
from flask import Flask, jsonify, request
from velinor_quickstart import initialize_game, play_turn

app = Flask(__name__)
game_sessions = {}  # In production, use Redis or database

@app.route('/api/game/start', methods=['POST'])
def start_game():
    player_name = request.json.get('player_name', 'Traveler')
    session_id = str(uuid.uuid4())
    
    orchestrator, initial_state = initialize_game(player_name=player_name)
    game_sessions[session_id] = orchestrator
    
    return jsonify({
        'session_id': session_id,
        'game_state': initial_state
    })

@app.route('/api/game/<session_id>/action', methods=['POST'])
def take_action(session_id):
    orchestrator = game_sessions.get(session_id)
    if not orchestrator:
        return jsonify({'error': 'Session not found'}), 404
    
    player_input = request.json.get('player_input')
    choice_index = request.json.get('choice_index')
    
    new_state = play_turn(orchestrator, player_input, choice_index)
    
    return jsonify(new_state)

@app.route('/api/game/<session_id>/save', methods=['POST'])
def save_game(session_id):
    orchestrator = game_sessions.get(session_id)
    if orchestrator:
        orchestrator.save_game(f'saves/{session_id}.json')
    return jsonify({'status': 'saved'})
"""


if __name__ == "__main__":
    # Quick test
    try:
        orchestrator, initial_state = initialize_game()
        display_ui_state(initial_state)
        
        print("\n✅ Velinor system initialized successfully!")
        print("To run a full game, integrate with Streamlit or web framework.")
        print("\nExample code snippets above show integration patterns.")
    
    except Exception as e:
        print(f"❌ Error initializing game: {e}")
        import traceback
        traceback.print_exc()
