# Velinor Streamlit Prototype

Full Streamlit implementation of **Velinor: Remnants of the Tone** - an emotionally-driven narrative game with:

- **Dynamic Scene Rendering** - Background + NPC overlay + dialogue
- **Button-Driven Interaction** - 2x2 button grid + optional fifth action button
- **Emotional OS Tracking** - TONE stats (Courage, Wisdom, Empathy, Resolve, Resonance)
- **REMNANTS System** - Deep emotional trait tracking (Truth, Deception, Competence, etc.)
- **Glyph Collection** - Unlock glyphs through story beats, use them to unlock chambers
- **Chamber Mechanics** - Simple click-based fight loop, obtain glyphs
- **NPC Perception** - Track how each NPC perceives player trust/affinity/understanding
- **Skills & Dialogue Banks** - Unlockable skills gate special dialogue branches

## Quick Start

### Install Dependencies

```bash
pip install -r velinor/requirements_streamlit.txt
```

### Run the App

```bash
streamlit run velinor/streamlit_app.py
```

The app will open at `http://localhost:8501`

## Architecture

### Files

- **`streamlit_app.py`** - Main Streamlit app entry point (session state, game loop)
- **`streamlit_state.py`** - Core game state management (TONE, glyphs, NPC perception)
- **`streamlit_ui.py`** - UI component rendering (sidebar, scene, buttons)
- **`stories/story_definitions.py`** - Story content (dialogue, choices, branching)
- **`engine/orchestrator.py`** - Game engine (Twine adapter, state transitions)
- **`engine/core.py`** - Core game mechanics (traits, dice rolls, NPCs)

### Data Flow

```
[Streamlit App]
    ↓
[Game State] ← manages → [UI Components]
    ↓
[Orchestrator] ← controls → [Story Engine]
    ↓
[Emotional OS] ← updates → [NPC System]
```

## Game Modes

The game switches between four main modes:

### 1. **Narrative Mode** (default)
- Player sees dialogue and 4 choice buttons
- Each choice updates TONE and NPC perception
- Choices can lead to chamber doors or story branches

### 2. **Glyph Input Mode** (at chamber doors)
- 4 buttons show available glyphs
- Player clicks glyphs in any order
- After 4 selections, buttons change to show next 4 glyphs
- After 8 glyphs, "Enter Chamber" button appears

### 3. **Chamber Mode** (inside glyph beast encounter)
- Single "Attack" button
- Increments fight counter
- At 15 attacks, "Obtain Glyph" button appears
- On obtain, glyph is added to player's collection

### 4. **Special Action Mode** (optional)
- Fifth button allows using a glyph on current NPC
- Updates dialogue and choice options
- Triggers new emotional branches

## UI Layout

### Main Area
```
┌─────────────────────────────────────────┐
│        📍 Location: Market Ruins         │
│        👥 Present: Ravi, Nima           │
│                                         │
│  *They're staring at me. What should I  │
│   do?*                                  │
│                                         │
│  [ Choice 1 ]  [ Choice 2 ]             │
│  [ Choice 3 ]  [ Choice 4 ]             │
│                                         │
│     [ Optional 5th Button ]             │
└─────────────────────────────────────────┘
```

### Sidebar
```
┌──────────────────────┐
│  📊 Emotional OS    │
│                     │
│  🎼 TONE           │
│  🟢 Courage: +0.15 │
│  🟡 Wisdom: -0.05  │
│  🟢 Empathy: +0.30 │
│                     │
│  👁️ REMNANTS        │
│  Truth: +0.20       │
│  Deception: -0.10   │
│                     │
│  ✨ GLYPHS         │
│  🟢 Sorrow - ...    │
│  ⚫ Presence - ...   │
│                     │
│  🎯 SKILLS         │
│  🟢 Empathic Listen │
│  ⚫ Tactical Aware   │
│                     │
│  👥 NPC PERCEPTION │
│  💚 Ravi (thoughtful)
│     Trust: +0.30    │
│  ❤️ Nima (cautious) │
│     Trust: +0.10    │
└──────────────────────┘
```

## Key Features

### Emotional OS (TONE)

Five core emotional dimensions track the player's emotional resonance:

- **Courage** - Willingness to act despite fear
- **Wisdom** - Understanding what truly matters
- **Empathy** - Connection with others' feelings
- **Resolve** - Commitment to chosen path
- **Resonance** - Overall harmonic balance

Each choice applies effects like `{"courage": +0.15, "empathy": -0.1}`, creating emergent emotional arcs.

### REMNANTS System

Deeper emotional tracking captures:

- **Truth vs Deception** - Honesty vs subterfuge
- **Competence vs Incompetence** - Capability spectrum
- **Social Consequence** - Relational impact
- **Emotional Inference** - Understanding others

### Glyphs as Verbs

Glyphs are not items—they're *emotional stances*. When you obtain Sorrow, you can:

1. **Invoke it in front of an NPC** (fifth button action)
   - Opens vulnerable dialogue branches
   - Updates NPC perception
   - Unlocks hidden story paths

2. **Use it to unlock chamber doors** (glyph input mode)
   - Combine specific glyphs to enter emotional chambers
   - Face glyph beasts that embody emotional concepts
   - Obtain transcendent glyphs through emotional victory

### NPC Perception

Each NPC tracks three dimensions of perception:

- **Trust** (-1.0 to +1.0) - Safety and reliability
- **Affinity** (-1.0 to +1.0) - Liking and comfort
- **Understanding** (-1.0 to +1.0) - Being known and seen

Player choices, glyph invocations, and skills update these dynamically, gating special dialogue.

## Configuration

### Adding New Story Content

Edit `velinor/stories/story_definitions.py`:

```python
story.add_passage(
    name="my_scene",
    text="*Player sees this dialogue*",
    background="marketplace",
    npcs=["Ravi", "Nima"],
    tags=["act1", "marketplace"]
)

story.add_choice(
    from_passage_name="my_scene",
    choice_text="What the player clicks",
    to_passage_name="next_scene",
    tone_effects={"courage": 0.2, "wisdom": -0.1},
    npc_resonance={"Ravi": 0.3, "Nima": -0.2}
)
```

### Adding Glyphs

Edit `velinor/streamlit_state.py` in `_initialize_glyphs()`:

```python
"MyGlyph": Glyph(
    name="MyGlyph",
    description="What it does",
    unlock_condition="story_beat_name",
    emotional_effect="courage",  # Which TONE stat it affects
    npc_resonance={"Ravi": 0.8}  # Which NPCs resonate with it
)
```

### Adding Skills

Edit `velinor/streamlit_state.py` in `_initialize_skills()`:

```python
"My Skill": Skill(
    name="My Skill",
    description="What it unlocks",
    dialogue_banks=["special_dialogue_1", "special_dialogue_2"]
)
```

## Testing

### Quick Test

```bash
python velinor/stories/build_story.py --validate
python velinor/stories/story_validator.py
```

### Interactive Testing

Run the Streamlit app and:

1. Make choices to see TONE updates
2. Reach a chamber door to test glyph input
3. Enter chamber and attack 15 times
4. Check sidebar to verify glyph added
5. Use glyph on NPC to see special dialogue

## Limitations & Design Choices

### Streamlit Constraints

- **No true z-index layering** - We fake overlays with markdown (upgrade to React later)
- **Full page rerun on button click** - Session state manages coherence
- **No real-time animation** - Fight loop is click-based, not animated
- **No audio/MIDI** - Text-based for prototype
- **No complex scene geometry** - Background descriptions instead of images

### By Design

- **Five-button limit** - Keeps choices simple, forces clear design
- **Simple fight mechanic** - 15 clicks validates story pacing, not combat depth
- **Gray/green glyph states** - Instant visual feedback without images
- **Sidebar-first emotional tracking** - TONE is always visible, informs choices

## Future: React Port

Once emotional logic is validated in Streamlit, port to React for:

- Real z-index layering and smooth overlays
- Animated NPC expressions and scene transitions
- Full MIDI/audio integration (ToneCore)
- Touch-friendly mobile UI
- Network multiplayer

All data structures stay the same—just swap the UI layer.

## Troubleshooting

### "Failed to initialize game"

Check that:
- `velinor/stories/story_definitions.py` builds correctly
- `velinor/engine/orchestrator.py` is importable
- No circular imports in velinor modules

```bash
python -c "from velinor.engine.orchestrator import VelinorTwineOrchestrator; print('OK')"
```

### Buttons not responding

- Clear Streamlit cache: `streamlit cache clear`
- Check that session state is initializing correctly
- Verify `st.rerun()` is being called

### Sidebar not updating

- Sidebar rendering happens every app rerun
- Make sure `game_state` is being modified in-place
- Check that `st.session_state.game_state` is persisting

## Contributing

To add features:

1. Add story content in `story_definitions.py`
2. Add state tracking in `streamlit_state.py`
3. Add UI components in `streamlit_ui.py`
4. Wire handlers in `streamlit_app.py`
5. Test with `streamlit run velinor/streamlit_app.py`

## License

This is part of the Saoriverse Console project.
