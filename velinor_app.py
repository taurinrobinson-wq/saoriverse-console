"""
Velinor Game UI - Streamlit Application
========================================

Interactive game frontend for Velinor: Remnants of the Tone

Features:
- Background images for locations
- NPC character displays
- Dialogue rendering in chat-style bubbles
- Dynamic choice buttons
- Free-text input
- Player stats display
- Dice roll visualization
- Multiplayer support
- Save/load functionality
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from velinor.engine import VelinorTwineOrchestrator, VelinorEngine

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Velinor: Remnants of the Tone",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    body { background-color: #0a0e27; color: #e0e0e0; }
    .stApp { background-color: #0a0e27; }
    
    /* Main dialogue container */
    .dialogue-container {
        background: linear-gradient(135deg, #1a1f3a 0%, #0f1523 100%);
        border-left: 4px solid #7c3aed;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* NPC dialogue bubble */
    .npc-dialogue {
        background: linear-gradient(135deg, #2d1b4e 0%, #1a0f2e 100%);
        border-left: 4px solid #a78bfa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-style: italic;
    }
    
    /* Clarifying question */
    .clarifying-question {
        background: linear-gradient(135deg, #1f3a3a 0%, #0f2626 100%);
        border-left: 4px solid #34d399;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 14px;
    }
    
    /* Stats panel */
    .stats-panel {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #374151;
    }
    
    /* Dice roll result */
    .dice-roll-success {
        background: linear-gradient(135deg, #065f46 0%, #034e3b 100%);
        color: #86efac;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #10b981;
        margin: 10px 0;
    }
    
    .dice-roll-failure {
        background: linear-gradient(135deg, #7c2d12 0%, #5a1e0a 100%);
        color: #fb7185;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #f87171;
        margin: 10px 0;
    }
    
    /* Title styling */
    .title-section {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1f3a5f 0%, #0a1f3f 100%);
        border-radius: 12px;
        border: 2px solid #3b82f6;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def initialize_session():
    """Initialize Streamlit session state."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.orchestrator = None
        st.session_state.game_state = None
        st.session_state.player_name = "Traveler"
        st.session_state.is_multiplayer = False
        st.session_state.player_ids = []
        st.session_state.game_log = []
        st.session_state.saves = []


initialize_session()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_asset_path(asset_type: str, name: str) -> str:
    """Get full path to asset file."""
    asset_dir = PROJECT_ROOT / "velinor" / asset_type
    return str(asset_dir / f"{name}.png")


def load_image_safe(path: str):
    """Load image safely, return None if not found."""
    try:
        from PIL import Image
        if Path(path).exists():
            return Image.open(path)
    except Exception as e:
        st.warning(f"Could not load image: {path}")
    return None


def display_background(background_name: str):
    """Display background image."""
    if background_name:
        # Map background names to filenames
        bg_map = {
            'market_ruins': 'city_market',
            'monuments': 'city_mountains',
            'archive_ruins': 'forest_city',
            'underground_ruins': 'swamp',
            'bridge_ravine': 'pass',
            'keeper_sanctuary': 'forest',
        }
        
        filename = bg_map.get(background_name, background_name)
        path = get_asset_path("backgrounds", filename)
        
        img = load_image_safe(path)
        if img:
            st.image(img, use_column_width=True)


def display_npc_character(npc_name: str):
    """Display NPC character portrait."""
    if npc_name:
        # Map NPC names to character files
        npc_map = {
            'Keeper': 'velinor_eyesclosed',
            'Saori': 'saori',
            'Sanor': 'sanor',
            'Irodora': 'irodora',
            'Tala': 'tala',
        }
        
        filename = npc_map.get(npc_name, npc_name.lower())
        path = get_asset_path("npcs", filename)
        
        img = load_image_safe(path)
        if img:
            return img
    return None


def render_dialogue_bubble(speaker: str, text: str, is_npc: bool = False):
    """Render dialogue in bubble format."""
    css_class = "npc-dialogue" if is_npc else "dialogue-container"
    
    if speaker:
        header = f"**{speaker}**"
        st.markdown(f"<div class='{css_class}'>{header}\n\n{text}</div>", 
                   unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='{css_class}'>{text}</div>", 
                   unsafe_allow_html=True)


def render_stats(stats: dict):
    """Render player stats panel."""
    st.markdown("<div class='stats-panel'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Courage", stats.get('courage', 0), delta=None)
        st.metric("Wisdom", stats.get('wisdom', 0), delta=None)
    
    with col2:
        st.metric("Empathy", stats.get('empathy', 0), delta=None)
        st.metric("Resolve", stats.get('resolve', 0), delta=None)
    
    with col3:
        st.metric("Resonance", stats.get('resonance', 0), delta=None)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_dice_roll(roll_data: dict):
    """Render dice roll result."""
    if not roll_data:
        return
    
    success = roll_data.get('success', False)
    css_class = "dice-roll-success" if success else "dice-roll-failure"
    
    result_text = "✅ SUCCESS" if success else "❌ FAILURE"
    
    st.markdown(
        f"""<div class='{css_class}'>
        🎲 Dice Roll: {roll_data.get('raw_roll', 0)} 
        (DC {roll_data.get('difficulty', 'N/A')}) 
        → {result_text}
        </div>""",
        unsafe_allow_html=True
    )


def save_game(orchestrator, name: str):
    """Save current game state."""
    save_dir = PROJECT_ROOT / "velinor" / "saves"
    save_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.json"
    save_path = save_dir / filename
    
    orchestrator.save_game(str(save_path))
    st.success(f"Game saved: {filename}")
    return filename


def list_saves():
    """List available saves."""
    save_dir = PROJECT_ROOT / "velinor" / "saves"
    if not save_dir.exists():
        return []
    
    return sorted([f.name for f in save_dir.glob("*.json")], reverse=True)


# ============================================================================
# MAIN GAME UI
# ============================================================================

def render_game_screen():
    """Render main game play screen."""
    if not st.session_state.orchestrator or not st.session_state.game_state:
        st.error("Game not initialized. Please start a new game.")
        return
    
    state = st.session_state.game_state
    
    # Display background
    col_bg = st.columns(1)[0]
    with col_bg:
        display_background(state.get('background_image'))
    
    # Main content area
    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        # NPC Character
        if state.get('npc_name'):
            st.subheader(f"👤 {state['npc_name']}")
            npc_img = display_npc_character(state['npc_name'])
            if npc_img:
                st.image(npc_img, width=200)
        
        # Main dialogue
        if state.get('main_dialogue'):
            render_dialogue_bubble(
                speaker=None,
                text=state['main_dialogue'],
                is_npc=False
            )
        
        # NPC response (if generated)
        if state.get('npc_dialogue'):
            render_dialogue_bubble(
                speaker=state.get('npc_name', 'NPC'),
                text=state['npc_dialogue'],
                is_npc=True
            )
        
        # Clarifying question
        if state.get('has_clarifying_question') and state.get('clarifying_question'):
            st.markdown(
                f"<div class='clarifying-question'>💭 {state['clarifying_question']}</div>",
                unsafe_allow_html=True
            )
        
        # Dice roll result
        if state.get('dice_roll'):
            render_dice_roll(state['dice_roll'])
        
        st.divider()
        
        # Player choices
        choices = state.get('choices', [])
        if choices:
            st.markdown("### Your Options:")
            
            # Display as buttons
            choice_cols = st.columns(len(choices)) if len(choices) <= 3 else None
            
            for i, choice in enumerate(choices):
                if choice_cols:
                    with choice_cols[i]:
                        if st.button(choice['text'], key=f"choice_{i}", use_container_width=True):
                            process_choice(i)
                else:
                    if st.button(choice['text'], key=f"choice_{i}", use_container_width=True):
                        process_choice(i)
        
        # Free-text input (optional)
        st.markdown("### Or type your response:")
        player_input = st.text_input(
            "Your response:",
            key="player_input",
            placeholder="Type what you'd like to do..."
        )
        
        if st.button("Submit Response", use_container_width=True):
            if player_input:
                process_free_text(player_input)
            else:
                st.warning("Please enter a response or choose an option.")
    
    with col_side:
        # Stats panel
        if state.get('game_state', {}).get('player_stats'):
            st.markdown("### 📊 Stats")
            render_stats(state['game_state']['player_stats'])
        
        # Passage info
        st.markdown("### 📍 Location")
        st.text(state.get('passage_name', 'Unknown'))


def process_choice(choice_index: int):
    """Process player choice selection."""
    orchestrator = st.session_state.orchestrator
    player_id = st.session_state.player_ids[0] if st.session_state.player_ids else "player_1"
    
    try:
        new_state = orchestrator.process_player_action(
            choice_index=choice_index,
            player_id=player_id
        )
        st.session_state.game_state = new_state
        st.session_state.game_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'choice',
            'choice_index': choice_index
        })
        st.rerun()
    except Exception as e:
        st.error(f"Error processing choice: {e}")


def process_free_text(player_input: str):
    """Process free-text player input."""
    orchestrator = st.session_state.orchestrator
    player_id = st.session_state.player_ids[0] if st.session_state.player_ids else "player_1"
    
    try:
        new_state = orchestrator.process_player_action(
            player_input=player_input,
            player_id=player_id
        )
        st.session_state.game_state = new_state
        st.session_state.game_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'free_text',
            'input': player_input
        })
        st.rerun()
    except Exception as e:
        st.error(f"Error processing input: {e}")


# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

def render_sidebar():
    """Render sidebar with game controls."""
    st.sidebar.title("⚙️ Game Menu")
    
    # Game status
    if st.session_state.orchestrator:
        st.sidebar.success("✅ Game Running")
    else:
        st.sidebar.info("⏹️ No Active Game")
    
    st.sidebar.divider()
    
    # Main menu tabs
    menu_choice = st.sidebar.radio(
        "Menu",
        ["Play", "Save/Load", "Settings", "About"],
        label_visibility="collapsed"
    )
    
    if menu_choice == "Play":
        if st.session_state.orchestrator:
            if st.sidebar.button("🔄 New Game", use_container_width=True):
                start_new_game()
    
    elif menu_choice == "Save/Load":
        render_save_load_menu()
    
    elif menu_choice == "Settings":
        render_settings_menu()
    
    elif menu_choice == "About":
        render_about_menu()


def start_new_game():
    """Initialize and start a new game."""
    try:
        engine = VelinorEngine()
        engine.create_session(
            player_name=st.session_state.player_name,
            multiplayer=st.session_state.is_multiplayer
        )
        
        story_path = PROJECT_ROOT / "velinor" / "stories" / "sample_story.json"
        if not story_path.exists():
            st.error(f"Story file not found: {story_path}")
            return
        
        orchestrator = VelinorTwineOrchestrator(
            game_engine=engine,
            story_path=str(story_path),
            first_person_module=None,  # Optional: connect FirstPerson here
            npc_system=None  # Optional: connect NPC system here
        )
        
        initial_state = orchestrator.start_game(
            is_multiplayer=st.session_state.is_multiplayer,
            player_ids=st.session_state.player_ids if st.session_state.is_multiplayer else []
        )
        
        st.session_state.orchestrator = orchestrator
        st.session_state.game_state = initial_state
        st.session_state.game_log = []
        
        st.success("✅ New game started!")
        st.rerun()
    
    except Exception as e:
        st.error(f"Error starting game: {e}")


def render_save_load_menu():
    """Render save/load menu."""
    st.sidebar.subheader("💾 Save/Load")
    
    tab1, tab2 = st.sidebar.tabs(["Save", "Load"])
    
    with tab1:
        if st.session_state.orchestrator:
            save_name = st.text_input("Save name:", value="velinor_save")
            if st.button("Save Game", use_container_width=True):
                save_game(st.session_state.orchestrator, save_name)
        else:
            st.info("No active game to save")
    
    with tab2:
        saves = list_saves()
        if saves:
            selected_save = st.selectbox("Load save:", saves)
            if st.button("Load Game", use_container_width=True):
                try:
                    save_path = PROJECT_ROOT / "velinor" / "saves" / selected_save
                    # Create orchestrator if needed
                    if not st.session_state.orchestrator:
                        engine = VelinorEngine()
                        engine.create_session(player_name=st.session_state.player_name)
                        story_path = PROJECT_ROOT / "velinor" / "stories" / "sample_story.json"
                        st.session_state.orchestrator = VelinorTwineOrchestrator(
                            game_engine=engine,
                            story_path=str(story_path)
                        )
                    
                    state = st.session_state.orchestrator.load_game(str(save_path))
                    st.session_state.game_state = state
                    st.success("✅ Game loaded!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading game: {e}")
        else:
            st.info("No saved games found")


def render_settings_menu():
    """Render settings menu."""
    st.sidebar.subheader("⚙️ Settings")
    
    # Player name
    player_name = st.text_input(
        "Player Name:",
        value=st.session_state.player_name,
        key="settings_player_name"
    )
    st.session_state.player_name = player_name
    
    # Multiplayer toggle
    is_multiplayer = st.checkbox(
        "Multiplayer Mode",
        value=st.session_state.is_multiplayer,
        key="settings_multiplayer"
    )
    st.session_state.is_multiplayer = is_multiplayer
    
    if is_multiplayer:
        num_players = st.number_input(
            "Number of Players:",
            min_value=2,
            max_value=4,
            value=len(st.session_state.player_ids) or 2
        )
        
        player_ids = []
        for i in range(num_players):
            pid = st.text_input(
                f"Player {i+1} ID:",
                value=f"player_{i+1}",
                key=f"player_id_{i}"
            )
            player_ids.append(pid)
        
        st.session_state.player_ids = player_ids
    
    st.divider()
    
    if st.button("Start New Game with Settings", use_container_width=True):
        start_new_game()


def render_about_menu():
    """Render about menu."""
    st.sidebar.subheader("ℹ️ About")
    
    st.sidebar.markdown("""
    ## Velinor: Remnants of the Tone
    
    A text-based narrative game with:
    - **Emotional Resonance** - Glyphs and the Tone
    - **Dice Mechanics** - D&D-inspired rolls
    - **Dynamic Dialogue** - NPC responses adapt to you
    - **Multiplayer** - Share the story with friends
    - **Free-form Input** - Type or choose your path
    
    **Created:** December 2025
    
    ---
    
    [📖 Full Documentation](./velinor/TWINE_INTEGRATION_GUIDE.md)
    """)


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point."""
    
    # Title section
    st.markdown("""
    <div class='title-section'>
        <h1>🎮 Velinor: Remnants of the Tone</h1>
        <p>A Living Narrative Adventure</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # Main content
    if st.session_state.orchestrator and st.session_state.game_state:
        render_game_screen()
    else:
        # Welcome screen
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            # Welcome to Velinor
            
            You stand at the threshold of a shattered civilization.
            
            The city of Saonyx lies in ruins, reclaimed by nature and time.
            But within these remnants pulses something ancient: **the Tone**.
            
            A faint resonance, a memory of collective emotion still waiting to be heard.
            
            Your choices will echo through the ruins.
            Your courage, wisdom, empathy, and resolve will be tested.
            And somewhere in the glyphs that remain, the truth of what was lost waits for you.
            
            ---
            
            **Ready to begin?**
            """)
            
            if st.button("🚀 Start New Game", use_container_width=True, key="welcome_start"):
                start_new_game()
        
        with col2:
            title_img_path = PROJECT_ROOT / "velinor" / "velinor_title_transparent.png"
            title_img = load_image_safe(str(title_img_path))
            if title_img:
                st.image(title_img, use_column_width=True)


if __name__ == "__main__":
    main()
