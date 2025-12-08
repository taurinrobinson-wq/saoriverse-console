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
from PIL import Image
import io

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from velinor.engine import VelinorTwineOrchestrator, VelinorEngine
from emotional_os.deploy.core.firstperson import FirstPersonOrchestrator, AffectParser

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Velinor: Remnants of the Tone",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize FirstPerson orchestrator for emotionally-aware responses
if 'firstperson_orchestrator' not in st.session_state:
    st.session_state.firstperson_orchestrator = FirstPersonOrchestrator(
        user_id='velinor_player',
        conversation_id='velinor_game'
    )
    st.session_state.firstperson_orchestrator.initialize_session()

# Custom CSS - Light Theme
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
        line-height: 1.6;
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
    
    /* Clarifying question */
    .clarifying-question {
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
        border-left: 4px solid #34d399;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 14px;
        color: #065f46;
    }
    
    /* Stats panel */
    .stats-panel {
        background: linear-gradient(135deg, #f3f4f6 0%, #f9fafb 100%);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        color: #1f2937;
    }
    
    /* Dice roll result */
    .dice-roll-success {
        background: linear-gradient(135deg, #dcfce7 0%, #dcfce7 100%);
        color: #15803d;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #86efac;
        margin: 10px 0;
    }
    
    .dice-roll-failure {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #fca5a5;
        margin: 10px 0;
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
    """Display background image with height constraint for single-page fit."""
    if background_name:
        # Map background names to filenames
        bg_map = {
            'market_ruins': 'city_market(16-9)',
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
            # Display with height constraint to fit on one page
            st.image(img, use_column_width=True, width=800)


def composite_background_with_npc(background_name: str, npc_name: str):
    """Composite NPC character on top of background image.
    
    Args:
        background_name: Name of the background image
        npc_name: Name of the NPC character
    
    Returns:
        PIL Image with NPC composited on background, or None if either image not found
    """
    if not background_name or not npc_name:
        return None
    
    # Load background
    bg_map = {
        'market_ruins': 'city_market',
        'monuments': 'city_mountains',
        'archive_ruins': 'forest_city',
        'underground_ruins': 'swamp',
        'bridge_ravine': 'pass',
        'keeper_sanctuary': 'forest',
    }
    
    bg_filename = bg_map.get(background_name, background_name)
    bg_path = get_asset_path("backgrounds", bg_filename)
    background = load_image_safe(bg_path)
    
    if not background:
        return None
    
    # Load NPC
    npc_map = {
        'Keeper': 'velinor_eyesclosed',
        'Saori': 'saori',
        'Sanor': 'sanor',
        'Irodora': 'irodora',
        'Tala': 'tala',
    }
    
    npc_filename = npc_map.get(npc_name, npc_name.lower())
    npc_path = get_asset_path("npcs", npc_filename)
    npc = load_image_safe(npc_path)
    
    if not npc:
        return None
    
    # Convert to RGBA if needed for transparency support
    if background.mode != 'RGBA':
        background = background.convert('RGBA')
    if npc.mode != 'RGBA':
        npc = npc.convert('RGBA')
    
    # Scale NPC to fit on background
    # NPC should be about 40% of background height, positioned lower-right
    bg_height = background.height
    npc_height = int(bg_height * 0.5)  # 50% of background height
    npc_aspect = npc.width / npc.height
    npc_width = int(npc_height * npc_aspect)
    
    # Resize NPC
    npc_resized = npc.resize((npc_width, npc_height), Image.Resampling.LANCZOS)
    
    # Position NPC on background (right side, lower portion)
    x_pos = background.width - npc_width - 20  # 20px from right edge
    y_pos = background.height - npc_height - 10  # 10px from bottom
    
    # Composite the images
    result = background.copy()
    result.paste(npc_resized, (x_pos, y_pos), npc_resized)  # Use NPC alpha as mask
    
    return result.convert('RGB')  # Convert back to RGB for display
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


def render_background_with_overlay(background_name: str, npc_path: str, narration: str, choices: list):
    """Render background image with NPC overlay, narration, and choice buttons.
    
    Args:
        background_name: Name of the background image file
        npc_path: Full path to NPC character image
        narration: Italicized narration text
        choices: List of choice dictionaries with 'text' keys
    """
    # Load background image
    if background_name:
        bg_map = {
            'market_ruins': 'city_market(16-9)',
            'monuments': 'city_mountains',
            'archive_ruins': 'forest_city',
            'underground_ruins': 'swamp',
            'bridge_ravine': 'pass',
            'keeper_sanctuary': 'forest',
        }
        filename = bg_map.get(background_name, background_name)
        path = get_asset_path("backgrounds", filename)
        bg_img = load_image_safe(path)
    else:
        bg_img = None
    
    # Load NPC image
    npc_img = None
    if npc_path:
        npc_img = load_image_safe(npc_path)
    
    # Create composite image with background and NPC
    if bg_img:
        if npc_img:
            # Composite NPC onto background (center-bottom)
            composite = bg_img.copy()
            if composite.mode != 'RGBA':
                composite = composite.convert('RGBA')
            if npc_img.mode != 'RGBA':
                npc_img = npc_img.convert('RGBA')
            
            # Scale NPC to fit (50% of background height, reduced by 10%)
            bg_height = composite.height
            npc_height = int(bg_height * 0.54)  # 0.6 * 0.9 = 0.54
            npc_aspect = npc_img.width / npc_img.height
            npc_width = int(npc_height * npc_aspect)
            npc_resized = npc_img.resize((npc_width, npc_height), Image.Resampling.LANCZOS)
            
            # Center horizontally, position at bottom
            x_pos = (composite.width - npc_width) // 2
            y_pos = composite.height - npc_height - 10
            
            composite.paste(npc_resized, (x_pos, y_pos), npc_resized)
            display_img = composite.convert('RGB')
        else:
            display_img = bg_img
        
        # Display the composite image
        st.image(display_img, use_column_width=True)
    
    # Narration text (light gray, italicized)
    st.markdown(
        f"""<div style='text-align: center; color: #999999; font-style: italic; margin: 20px 0; font-size: 16px;'>
        {narration}
        </div>""",
        unsafe_allow_html=True
    )
    
    # Choice buttons in 2x2 grid
    if choices:
        st.markdown("<div style='margin: 30px 0;'><h4 style='color: #666666;'>What do you do?</h4></div>", unsafe_allow_html=True)
        
        # Create 2x2 grid (4 buttons)
        cols = st.columns(2)
        for i, choice in enumerate(choices[:4]):
            col_idx = i % 2
            with cols[col_idx]:
                btn_text = choice.get('text', f'Option {i+1}')
                if st.button(
                    btn_text,
                    key=f"choice_{i}",
                    use_container_width=True,
                    help=choice.get('description', '')
                ):
                    # Process choice
                    orchestrator = st.session_state.get('orchestrator')
                    if orchestrator:
                        player_id = st.session_state.get('player_ids', ['player_1'])[0]
                        try:
                            new_state = orchestrator.process_player_action(
                                player_input=btn_text,
                                choice_index=i,
                                player_id=player_id
                            )
                            st.session_state.game_state = new_state
                            st.session_state.game_log.append({
                                'timestamp': datetime.now().isoformat(),
                                'action': 'choice',
                                'choice_index': i,
                                'choice_text': btn_text
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error processing choice: {e}")
    
    # Free-text input
    st.markdown("<div style='margin-top: 30px;'><h4 style='color: #666666;'>Or type your response:</h4></div>", unsafe_allow_html=True)
    player_input = st.text_input(
        "Your action:",
        key="player_input_overlay",
        placeholder="Type what you'd like to do...",
        label_visibility="collapsed"
    )
    
    if st.button("Submit Response", use_container_width=True):
        if player_input:
            orchestrator = st.session_state.get('orchestrator')
            if orchestrator:
                player_id = st.session_state.get('player_ids', ['player_1'])[0]
                try:
                    new_state = orchestrator.process_player_action(
                        player_input=player_input,
                        player_id=player_id
                    )
                    st.session_state.game_state = new_state
                    st.session_state.game_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'free_text',
                        'text': player_input
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing input: {e}")
        else:
            st.warning("Please enter a response or choose an option.")


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
    """Render main game play screen with background overlay."""
    if not st.session_state.orchestrator or not st.session_state.game_state:
        st.error("Game not initialized. Please start a new game.")
        return
    
    state = st.session_state.game_state
    
    # Build the narration/dialogue for display
    narration_parts = []
    if state.get('main_dialogue'):
        narration_parts.append(state['main_dialogue'])
    if state.get('npc_dialogue'):
        narration_parts.append(state['npc_dialogue'])
    narration = " ".join(narration_parts) if narration_parts else "What will you do?"
    
    # Get NPC image path if NPC exists
    npc_path = None
    if state.get('npc_name'):
        npc_map = {
            'Keeper': 'velinor_eyesclosed',
            'Saori': 'saori',
            'Sanor': 'sanor',
            'Irodora': 'irodora',
            'Tala': 'tala',
            'Ravi': 'Ravi_Nima',
        }
        npc_filename = npc_map.get(state.get('npc_name'), state.get('npc_name').lower())
        npc_path = str(PROJECT_ROOT / "velinor" / "npcs" / f"{npc_filename}.png")
    
    # Get choices
    choices = state.get('choices', [])
    
    # Use the overlay component
    render_background_with_overlay(
        background_name=state.get('background_image', ''),
        npc_path=npc_path,
        narration=narration,
        choices=choices
    )
    
    # Additional info sections below overlay
    if state.get('has_clarifying_question') and state.get('clarifying_question'):
        st.markdown(
            f"<div class='clarifying-question'>💭 {state['clarifying_question']}</div>",
            unsafe_allow_html=True
        )
    
    if state.get('dice_roll'):
        render_dice_roll(state['dice_roll'])
    
    # Stats panel
    if state.get('stats'):
        st.divider()
        render_stats(state['stats'])


def process_choice(choice_index: int):
    """Process player choice selection."""
    orchestrator = st.session_state.orchestrator
    player_id = st.session_state.player_ids[0] if st.session_state.player_ids else "player_1"
    
    try:
        # Get the choice text from game state
        choices = st.session_state.game_state.get('choices', [])
        if choice_index < len(choices):
            choice_text = choices[choice_index].get('text', '')
        else:
            choice_text = ''
        
        new_state = orchestrator.process_player_action(
            player_input=choice_text,
            choice_index=choice_index,
            player_id=player_id
        )
        st.session_state.game_state = new_state
        st.session_state.game_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'choice',
            'choice_index': choice_index,
            'choice_text': choice_text
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
    
    # Stats and location in sidebar expanders
    st.sidebar.divider()
    state = st.session_state.game_state
    if state:
        # Stats panel in collapsible expander
        if state.get('game_state', {}).get('player_stats'):
            with st.sidebar.expander("📊 Player Stats", expanded=True):
                render_stats(state['game_state']['player_stats'])
        
        # Location info in collapsible expander
        with st.sidebar.expander("📍 Location", expanded=True):
            st.text(state.get('passage_name', 'Unknown'))


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
        
        # Get or reinitialize FirstPerson for emotionally-aware NPC responses
        firstperson_orchestrator = st.session_state.get('firstperson_orchestrator')
        if not firstperson_orchestrator:
            firstperson_orchestrator = FirstPersonOrchestrator(
                user_id=st.session_state.player_name,
                conversation_id='velinor_game'
            )
            firstperson_orchestrator.initialize_session()
            st.session_state.firstperson_orchestrator = firstperson_orchestrator
        
        orchestrator = VelinorTwineOrchestrator(
            game_engine=engine,
            story_path=str(story_path),
            first_person_module=firstperson_orchestrator,  # Connected: FirstPerson for nuanced responses
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
    
    # Sidebar
    render_sidebar()
    
    # Main content
    if st.session_state.orchestrator and st.session_state.game_state:
        render_game_screen()
    else:
        # Welcome splash screen - just image with overlay button
        splash_img_path = str(PROJECT_ROOT / "velinor" / "npcs" / "photo-output.PNG")
        splash_img = load_image_safe(splash_img_path)
        
        if splash_img:
            st.image(splash_img, use_column_width=True)
        
        # Centered button overlay at bottom
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Start New Game", use_container_width=True, key="welcome_start"):
                start_new_game()


if __name__ == "__main__":
    main()
