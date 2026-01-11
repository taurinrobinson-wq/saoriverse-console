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

from engine import VelinorTwineOrchestrator, VelinorEngine
from pathlib import Path
import json
from datetime import datetime
import sys
import io
import time
import random
from PIL import Image
import streamlit as st

# Define project root FIRST
PROJECT_ROOT = Path(__file__).parent.parent

# Add project root to path for imports
sys.path.insert(0, str(PROJECT_ROOT))

# Import optional modules
try:
    from emotional_os.deploy.core.firstperson import FirstPersonOrchestrator, AffectParser
    HAS_EMOTIONAL_OS = True
except ImportError:
    HAS_EMOTIONAL_OS = False
    FirstPersonOrchestrator = None
    AffectParser = None


# Import new modular components (if available)
try:
    from streamlit_state import StreamlitGameState
    from streamlit_ui import StreamlitUI
    HAS_NEW_COMPONENTS = True
except ImportError:
    HAS_NEW_COMPONENTS = False

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
# NOTE: Commented out - Velinor uses its own orchestrator
# if 'firstperson_orchestrator' not in st.session_state:
#     st.session_state.firstperson_orchestrator = FirstPersonOrchestrator(
#         user_id='velinor_player',
#         conversation_id='velinor_game'
#     )
#     st.session_state.firstperson_orchestrator.initialize_session()

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

        # New modular components
        if HAS_NEW_COMPONENTS:
            st.session_state.game_systems = None
            st.session_state.current_state = None
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


def add_button_overlay(image: Image.Image, button_text: str, position: str = "bottom") -> Image.Image:
    """Draw a button on an image using PIL.

    Args:
        image: PIL Image to draw on
        button_text: Text for the button
        position: "bottom", "center", or "top"

    Returns:
        Image with button drawn on it
    """
    from PIL import ImageDraw, ImageFont

    # Convert to RGBA if needed
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Create a copy to draw on
    img_with_button = image.copy()
    draw = ImageDraw.Draw(img_with_button)

    # Button dimensions
    button_width = 200
    button_height = 50
    button_color = (70, 130, 180)  # Steel blue
    button_text_color = (255, 255, 255)  # White

    # Calculate position
    img_width, img_height = img_with_button.size
    x_center = (img_width - button_width) // 2

    if position == "bottom":
        y_pos = img_height - button_height - 30
    elif position == "center":
        y_pos = (img_height - button_height) // 2
    else:  # top
        y_pos = 30

    # Draw button rectangle
    button_box = [x_center, y_pos, x_center +
                  button_width, y_pos + button_height]
    draw.rectangle(button_box, fill=button_color,
                   outline=(255, 255, 255), width=2)

    # Draw button text (simple, centered)
    try:
        # Try to use a larger font, fall back to default
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    # Center text in button
    text_bbox = draw.textbbox((0, 0), button_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = x_center + (button_width - text_width) // 2
    text_y = y_pos + (button_height - text_height) // 2

    draw.text((text_x, text_y), button_text, fill=button_text_color, font=font)

    return img_with_button


def init_boss_fight_session():
    """Initialize session state for boss fight test."""
    if 'boss_fight' not in st.session_state:
        st.session_state.boss_fight = {
            'initialized': True,
            'x': 0.05,  # horizontal position (0..1)
            'direction': 1,  # 1 = left->right, -1 = right->left
            'speed': 0.15,  # fraction per second across screen
            'frame': 'right',  # 'left'|'right'|'forward'
            'forward_timer': 0.0,
            'overlay_fill': 0.0,  # 0..1
            'last_time': time.time(),
            'hit_count': 0,
            'shudder_ticks': 0,
        }


def update_boss_state(delta: float):
    """Advance boss state by delta seconds."""
    s = st.session_state.boss_fight
    # Move
    s['x'] += s['direction'] * s['speed'] * delta
    # Bounce and toggle frame
    if s['x'] >= 0.95:
        s['x'] = 0.95
        s['direction'] = -1
        s['frame'] = 'left'
    elif s['x'] <= 0.05:
        s['x'] = 0.05
        s['direction'] = 1
        s['frame'] = 'right'

    # Randomly trigger a forward-facing window while pacing
    if s['forward_timer'] <= 0:
        # small chance per second to become forward for 0.6s
        if random.random() < 0.6 * delta:
            s['frame'] = 'forward'
            s['forward_timer'] = 0.6
    else:
        s['forward_timer'] -= delta
        if s['forward_timer'] <= 0:
            # return to pacing image matching direction
            s['frame'] = 'right' if s['direction'] == 1 else 'left'

    # Overlay fills slowly during fight
    s['overlay_fill'] = min(1.0, s['overlay_fill'] + 0.02 * delta)

    # Handle shudder ticks (reduce over time)
    if s['shudder_ticks'] > 0:
        s['shudder_ticks'] -= max(1, int(8 * delta))


def composite_boss_scene(bg_img: Image.Image, boss_img: Image.Image, overlay_img: Image.Image, x_frac: float, shudder: int, width: int = 800) -> Image.Image:
    """Compose background + boss at horizontal fraction x_frac and overlay fill.

    Returns a PIL Image resized to `width` px wide for display.
    """
    # Work on a copy
    bg = bg_img.convert('RGBA').copy()
    canvas_w, canvas_h = bg.size

    # Boss scale: height about 45% of background
    boss_h = int(canvas_h * 0.45)
    boss_aspect = boss_img.width / boss_img.height
    boss_w = int(boss_h * boss_aspect)
    boss_resized = boss_img.resize(
        (boss_w, boss_h), Image.Resampling.LANCZOS).convert('RGBA')

    # Compute position
    x_px = int((canvas_w - boss_w) * x_frac)
    y_px = canvas_h - boss_h - 20

    # Apply shudder by small random offset when shuddering
    if shudder > 0:
        jitter = random.randint(-6, 6)
        x_px = max(0, min(canvas_w - boss_w, x_px + jitter))
        y_px = max(0, min(canvas_h - boss_h, y_px + random.randint(-3, 3)))

    # Paste boss
    composite = bg.copy()
    composite.paste(boss_resized, (x_px, y_px), boss_resized)

    # Apply semi-transparent overlay fill from bottom using supplied overlay_img as pattern
    if overlay_img:
        ov = overlay_img.convert('RGBA')
        ov = ov.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        # overlay alpha proportional to overlay_fill stored in session
        alpha = int(180 * st.session_state.boss_fight.get('overlay_fill', 0.0))
        mask = Image.new('L', (canvas_w, canvas_h), color=alpha)
        composite = Image.alpha_composite(composite, Image.composite(
            ov, Image.new('RGBA', (canvas_w, canvas_h)), mask))

    # Resize to fixed display width
    ratio = width / composite.width
    new_size = (width, int(composite.height * ratio))
    return composite.resize(new_size, Image.Resampling.LANCZOS).convert('RGB')


def render_boss_fight():
    """Render boss fight test UI.

    Uses session state `boss_fight` dict and image assets under `velinor/backgrounds` and `velinor/bosses`.
    """
    # Ensure session
    init_boss_fight_session()
    s = st.session_state.boss_fight

    # Load assets once into session for performance
    if 'assets_loaded' not in s:
        PROJECT_ROOT = Path(__file__).parent

        def load(path):
            try:
                return Image.open(path)
            except Exception:
                return None

        s['bg_img'] = load(str(PROJECT_ROOT / 'velinor' /
                           'backgrounds' / 'boss_chamber01.png'))
        s['boss_left'] = load(
            str(PROJECT_ROOT / 'velinor' / 'bosses' / 'triglyph_boss_nobg_left.png'))
        s['boss_right'] = load(
            str(PROJECT_ROOT / 'velinor' / 'bosses' / 'triglyph_boss_nobg_right.png'))
        s['boss_forward'] = load(
            str(PROJECT_ROOT / 'velinor' / 'bosses' / 'triglyph_boss_nobg_forward2.png'))
        s['overlay_img'] = load(
            str(PROJECT_ROOT / 'velinor' / 'backgrounds' / 'boss_chamber01.png'))
        s['assets_loaded'] = True

    now = time.time()
    delta = max(0.01, now - s.get('last_time', now))
    s['last_time'] = now

    # Update state
    update_boss_state(delta)

    # Determine current boss image
    frame = s['frame']
    if frame == 'left':
        boss_img = s.get('boss_left') or s.get('boss_right')
    elif frame == 'right':
        boss_img = s.get('boss_right') or s.get('boss_left')
    else:
        boss_img = s.get('boss_forward') or s.get('boss_right')

    # If shudder requested, keep shudder_ticks > 0 to jitter
    shudder = s.get('shudder_ticks', 0)

    # Composite scene image
    if not s.get('bg_img') or not boss_img:
        st.error('Missing boss or background assets for boss test.')
        return

    display_img = composite_boss_scene(s['bg_img'], boss_img, s.get(
        'overlay_img'), s['x'], shudder, width=800)

    # Display composite image at fixed width so we can place an overlay button by pixel
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(display_img, use_column_width=False, width=800)

    # Click handling: only respond when forward frame is visible
    can_hit = (frame == 'forward')

    # Compute button horizontal pixel (approx) to overlay on top of boss
    img_w = 800
    boss_px_w = int(display_img.width * 0.25)
    boss_center_px = int(img_w * s['x'])
    # Constrain
    boss_center_px = max(40, min(img_w - 40, boss_center_px))

    # Invisible button style positioned over boss
    left_margin = boss_center_px - (boss_px_w // 2)
    if left_margin < 0:
        left_margin = 0

    st.markdown(f"""
        <style>
        .stButton button {{
            background-color: transparent !important;
            border: none !important;
            color: transparent !important;
            padding: 0 !important;
            margin: -{int(display_img.height*0.45)}px 0 0 {left_margin}px !important;
            width: {boss_px_w}px !important;
            height: {int(display_img.height*0.5)}px !important;
            cursor: pointer;
        }}
        .stButton button:hover {{ background-color: rgba(255,255,255,0.02) !important; }}
        </style>
    """, unsafe_allow_html=True)

    hit = False
    if st.button('Hit Boss', key='boss_hit_btn', help='Click when boss faces you', args=None):
        if can_hit:
            hit = True
        else:
            st.warning('That was not a hit window!')

    if hit:
        # Register hit effects: shudder and speed up and overlay surge
        s['hit_count'] += 1
        s['shudder_ticks'] = max(s.get('shudder_ticks', 0), 8)
        s['speed'] = s.get('speed', 0.15) * 1.25
        s['overlay_fill'] = min(1.0, s['overlay_fill'] + 0.08)
        st.success('Hit! The triglyph reels.')

    # Show basic HUD below
    st.markdown(
        f"**Overlay**: {s['overlay_fill']:.2f} • **Speed**: {s['speed']:.3f} • **Hits**: {s['hit_count']}")

    # Auto-rerun to animate
    st.experimental_rerun()


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
    result.paste(npc_resized, (x_pos, y_pos),
                 npc_resized)  # Use NPC alpha as mask

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
            npc_resized = npc_img.resize(
                (npc_width, npc_height), Image.Resampling.LANCZOS)

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
        st.markdown(
            "<div style='margin: 30px 0;'><h4 style='color: #666666;'>What do you do?</h4></div>", unsafe_allow_html=True)

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
                        player_id = st.session_state.get(
                            'player_ids', ['player_1'])[0]
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
    st.markdown("<div style='margin-top: 30px;'><h4 style='color: #666666;'>Or type your response:</h4></div>",
                unsafe_allow_html=True)
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

    # Check if using new modular system
    if HAS_NEW_COMPONENTS and st.session_state.game_systems and st.session_state.game_state and st.session_state.current_state:
        render_game_screen_modular()
        return

    # Fall back to legacy system
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
    narration = " ".join(
        narration_parts) if narration_parts else "What will you do?"

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
        npc_filename = npc_map.get(
            state.get('npc_name'), state.get('npc_name').lower())
        npc_path = str(PROJECT_ROOT / "velinor" /
                       "npcs" / f"{npc_filename}.png")

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


def render_game_screen_modular():
    """Render game using new modular UI system."""
    if not HAS_NEW_COMPONENTS:
        return

    systems = st.session_state.game_systems
    game_state = st.session_state.game_state
    ui = systems.get("ui")

    if not ui:
        st.error("UI system not initialized")
        return

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
                    systems["orchestrator"].save_game("velinor_save.json")
                    st.success("Game saved!")
                except Exception:
                    st.info("Save system not yet available")
        with col2:
            if st.button("Load Game"):
                try:
                    new_state = systems["orchestrator"].load_game(
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
        st.write("**Mode:**", game_state.mode if hasattr(game_state,
                 'mode') else "unknown")
        if hasattr(game_state, 'tone'):
            st.write("**TONE Stats:**", game_state.tone.to_dict()
                     if hasattr(game_state.tone, 'to_dict') else {})


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


# ============================================================================
# NEW GAME HANDLERS (Modular Button Layout System)
# ============================================================================

def handle_choice(choice_index: int):
    """Handle player selecting a dialogue choice."""
    if not HAS_NEW_COMPONENTS:
        return

    if "game_systems" not in st.session_state or not st.session_state.game_systems:
        return

    orchestrator = st.session_state.game_systems.get("orchestrator")
    if not orchestrator:
        return

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
            # Apply choice consequences to TONE if available
            if HAS_NEW_COMPONENTS and "game_state" in st.session_state:
                if "consequence" in choice and hasattr(st.session_state.game_state, 'tone'):
                    st.session_state.game_state.tone.apply_effect(
                        choice["consequence"])
            # Simple state advancement
            st.session_state.current_state["main_dialogue"] = f"You chose: {choice['text']}"

    st.rerun()


def handle_glyph_input(glyph_name: str):
    """Handle player selecting a glyph at chamber door."""
    if not HAS_NEW_COMPONENTS or "game_state" not in st.session_state:
        return

    game_state = st.session_state.game_state
    if hasattr(game_state, 'use_glyph_at_door'):
        game_state.use_glyph_at_door(glyph_name)

        # Check if all glyphs used
        if hasattr(game_state, 'glyphs_used_count') and hasattr(game_state, 'glyph_page'):
            if game_state.glyphs_used_count >= 4:
                if game_state.glyph_page == 1:
                    game_state.glyph_page = 2
                else:
                    # Ready to enter chamber
                    if hasattr(game_state, 'mode'):
                        game_state.mode = "chamber"

    st.rerun()


def handle_attack():
    """Handle attack button in chamber fight."""
    if not HAS_NEW_COMPONENTS or "game_state" not in st.session_state:
        return

    game_state = st.session_state.game_state
    if hasattr(game_state, 'fight_counter'):
        game_state.fight_counter += 1

        if game_state.fight_counter >= 15:
            if hasattr(game_state, 'mode'):
                game_state.mode = "chamber_complete"

    st.rerun()


def handle_special_action(action: str):
    """Handle special glyph action."""
    if not HAS_NEW_COMPONENTS or "game_state" not in st.session_state:
        return

    game_state = st.session_state.game_state

    if action.startswith("use_glyph_"):
        glyph_name = action.replace("use_glyph_", "")
        if hasattr(game_state, 'use_glyph_on_npc'):
            game_state.use_glyph_on_npc(glyph_name)
        st.rerun()


def start_new_game():
    """Initialize and start a new game."""
    try:
        # Try to initialize new modular system first
        if HAS_NEW_COMPONENTS:
            try:
                story_path = str(PROJECT_ROOT / "velinor" /
                                 "stories" / "sample_story.json")

                # Initialize systems for new modular UI
                game_engine = VelinorEngine()
                game_engine.create_session(
                    player_name=st.session_state.player_name)

                from velinor.engine.npc_system import NPCDialogueSystem
                npc_system = NPCDialogueSystem()

                # Initialize orchestrator with story path
                orchestrator = VelinorTwineOrchestrator(
                    game_engine=game_engine,
                    story_path=story_path,
                    npc_system=npc_system,
                    player_name=st.session_state.player_name
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
                            {"text": "Observe quietly",
                                "consequence": {"observation": 0.1}},
                            {"text": "Wander the market", "consequence": {
                                "narrative_presence": 0.1}},
                            {"text": "Listen to the songs",
                                "consequence": {"empathy": 0.1}}
                        ]
                    }

                # Store new modular systems
                st.session_state.game_systems = {
                    "orchestrator": orchestrator,
                    "engine": game_engine,
                    "npc_system": npc_system,
                    "initial_state": initial_state,
                    "ui": StreamlitUI()
                }
                st.session_state.game_state = StreamlitGameState()
                st.session_state.current_state = initial_state

                st.success("✅ New game started with enhanced UI!")
                st.rerun()
                return
            except Exception as e:
                # Fall through to legacy system if new system fails
                st.warning(
                    f"Enhanced UI not available, using legacy mode: {str(e)}")

        # Legacy system initialization
        engine = VelinorEngine()
        engine.create_session(
            player_name=st.session_state.player_name,
            multiplayer=st.session_state.is_multiplayer
        )

        story_path = PROJECT_ROOT / "velinor" / "stories" / "sample_story.json"
        if not story_path.exists():
            st.error(f"Story file not found: {story_path}")
            return

        # Get or reinitialize FirstPerson for emotionally-aware NPC responses (if available)
        firstperson_orchestrator = None
        if HAS_EMOTIONAL_OS:
            firstperson_orchestrator = st.session_state.get(
                'firstperson_orchestrator')
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
            # Connected: FirstPerson for nuanced responses
            first_person_module=firstperson_orchestrator,
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
                        engine.create_session(
                            player_name=st.session_state.player_name)
                        story_path = PROJECT_ROOT / "velinor" / "stories" / "sample_story.json"
                        st.session_state.orchestrator = VelinorTwineOrchestrator(
                            game_engine=engine,
                            story_path=str(story_path)
                        )

                    state = st.session_state.orchestrator.load_game(
                        str(save_path))
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
        # Welcome splash screen - image with button drawn on it
        splash_img_path = str(PROJECT_ROOT / "velinor" /
                              "backgrounds" / "velinor_title_eyes_closed.png")
        splash_img = load_image_safe(splash_img_path)

        if splash_img:
            # Add button overlay to image using PIL
            splash_with_button = add_button_overlay(
                splash_img, "Start New Game", position="bottom")

            # Display image centered
            col_left, col_img, col_right = st.columns([1, 2, 1])
            with col_img:
                st.image(splash_with_button, use_column_width=True)

                # Invisible clickable button that overlaps the drawn button
                st.markdown("""
                    <style>
                    .stButton button {
                        background-color: transparent !important;
                        border: none !important;
                        color: transparent !important;
                        padding: 0 !important;
                        margin: -55px auto 0 auto !important;
                        width: 200px !important;
                    }
                    .stButton button:hover {
                        background-color: transparent !important;
                    }
                    </style>
                """, unsafe_allow_html=True)

                if st.button("Start New Game", use_container_width=False, key="welcome_start"):
                    start_new_game()
                # Test Boss Fight button
                if st.button("Test Boss Fight", use_container_width=False, key="welcome_boss_test"):
                    st.session_state.boss_test = True
                    # initialize boss session
                    init_boss_fight_session()
                    st.experimental_rerun()

    # If boss test was requested, render boss fight UI
    if st.session_state.get('boss_test'):
        render_boss_fight()


if __name__ == "__main__":
    main()
