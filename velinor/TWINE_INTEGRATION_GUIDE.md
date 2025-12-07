# Velinor Twine/Ink Integration Guide

## Overview

Velinor uses **Twine 2** with **SugarCube** (or **Ink** as alternative) as the narrative framework, integrated with:
- **Game Engine** (`core.py`) - State management, dice rolls, player stats
- **NPC System** (`npc_system.py`) - Dialogue generation using FirstPerson orchestrator
- **Twine Adapter** (`twine_adapter.py`) - Bridges narrative and game mechanics
- **Orchestrator** (`orchestrator.py`) - Main game loop controller

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Velinor Twine Integration                   │
└─────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────┐    ┌──────────────┐    ┌────────────┐
    │ Twine  │    │ Game Engine  │    │  FirstPerson
    │ Story  │    │ - State      │    │  Orchestrator
    │ System │    │ - Dice Rolls │    │  - Dialogue
    └────────┘    │ - Stats      │    │  - Affect
        │         └──────────────┘    │  - Memory
        │                 │           └────────────┘
        └─────────────────┼─────────────────┐
                          │
                    ┌─────▼─────┐
                    │ Orchestrator
                    │ - Game Loop
                    │ - Input Processing
                    │ - State Sync
                    └─────┬─────┘
                          │
                    ┌─────▼─────────────┐
                    │ UI Layer (Streamlit,
                    │  Flask, Web, etc.)
                    └───────────────────┘
```

## Key Files

### 1. **twine_adapter.py** - Twine/Story System Bridge
Handles:
- Loading Twine JSON story files
- Parsing SugarCube markup (`[[text->target]]`)
- Extracting dialogue, choices, and special commands
- Managing story context and progression

**Key Classes:**
- `TwineStoryLoader` - Loads story JSON
- `DialogueParser` - Parses Twine markup
- `TwineGameSession` - Session management
- `StoryBuilder` - Programmatic story creation

### 2. **orchestrator.py** - Game Loop Controller
Handles:
- Processing player input (typed or choices)
- Applying game mechanics (dice rolls, stat changes)
- Triggering NPC dialogue generation
- Formatting state for UI consumption
- Save/load functionality

**Key Classes:**
- `VelinorTwineOrchestrator` - Main controller
- `MultiplayerState` - Multiplayer session tracking

### 3. **core.py** - Game Engine
Manages:
- Game state (MENU, IN_GAME, DIALOGUE, CHOICE, etc.)
- Player stats (Courage, Wisdom, Empathy, Resolve, Resonance)
- Dice rolling with stat modifiers
- Location tracking
- Event system for UI callbacks

### 4. **npc_system.py** - NPC Dialogue
Manages:
- NPC personalities and dialogue templates
- Integration with FirstPerson orchestrator
- Dialogue history and relationships
- Solo vs. multiplayer dialogue adaptation

## Twine Story Markup

### Story File Format (JSON)
Velinor uses Twine 2 JSON export format:

```json
{
  "name": "Velinor: Remnants of the Tone",
  "startnode": "1",
  "passages": [
    {
      "pid": "1",
      "name": "market_entry",
      "text": "You emerge into the ruins...",
      "tags": [],
      "position": [0, 0],
      "size": [100, 100]
    }
  ]
}
```

### Twine Markup Syntax (SugarCube)

**Choices (Links):**
```
[[Choice text->target_passage]]
[[Talk to them|meeting]]  (alternative syntax)
```

**Skill Checks:**
```
[[Persuade the guard (Courage, DC 12)->success_path]]
```

**Commands (Special Markers):**
```
{background: location_name}      # Change background image
{npc: NPC_Name}                 # NPC speaking in scene
{dice: d20+courage}              # Trigger dice roll
{multiplayer: true}              # Enable multiplayer mode
```

**Example Passage:**
```
{background: market_ruins}
{npc: Keeper}

You emerge from the underpass into the Market District.
A figure approaches: "Welcome, Traveler."

[[Ask about the Tone->keeper_dialogue]]
[[Explore alone->market_exploration]]
[[Keep distance (Wisdom, DC 11)->observer_path]]
```

## Creating Stories

### Option 1: Build Programmatically

```python
from velinor.engine import StoryBuilder

story = StoryBuilder("My Story Title")

# Add passages
intro = story.add_passage(
    name="intro",
    text="{background: forest}\n{npc: Guide}\n\nYou arrive at a forest crossing...",
    is_start=True
)

# Add choices
story.add_choice("intro", "Follow the Guide", "guide_path")
story.add_choice("intro", "Go alone", "alone_path")

# Export as JSON
story.export_json("my_story.json")
```

### Option 2: Create in Twine 2 UI

1. Download [Twine 2](https://twinery.org/)
2. Create story with visual passage editor
3. Export as JSON via menu
4. Load with `TwineStoryLoader()`

### Option 3: Edit Sample Story

See `/velinor/stories/sample_story.json` for a working example with:
- Market District opening
- Multiple dialogue paths
- Skill check choices
- NPC interactions
- Story branching

## Running a Game

### Basic Initialization

```python
from velinor.engine import VelinorTwineOrchestrator, VelinorEngine

# Create game engine
engine = VelinorEngine(player_name="Traveler")

# Create orchestrator
orchestrator = VelinorTwineOrchestrator(
    game_engine=engine,
    story_path="path/to/story.json"
)

# Start game
initial_state = orchestrator.start_game()
```

### Process Player Input

```python
# Player chooses option 1
next_state = orchestrator.process_player_action(
    choice_index=0,
    player_id="player_1"
)

# Player types response
next_state = orchestrator.process_player_action(
    player_input="I approach cautiously",
    player_id="player_1"
)
```

### Game State Structure

```python
{
    'passage_id': 'keeper_dialogue',
    'passage_name': 'Meeting the Keeper',
    'main_dialogue': 'The Keeper greets you...',
    'npc_name': 'Keeper',
    'npc_dialogue': '[Generated by FirstPerson]',
    'background_image': 'market_ruins',
    'choices': [
        {'text': 'Ask about the Tone', 'target': 'keeper_dialogue_1'},
        {'text': 'Explore alone', 'target': 'market_alone'}
    ],
    'clarifying_question': 'Are you sure this is the path you want?',
    'has_clarifying_question': True,
    'is_multiplayer': False,
    'game_state': {
        'current_location': 'MARKET_DISTRICT',
        'player_stats': {
            'courage': 50,
            'wisdom': 55,
            'empathy': 60,
            'resolve': 50,
            'resonance': 100
        }
    }
}
```

## UI Integration Examples

### Streamlit UI

```python
import streamlit as st
from velinor.engine import VelinorTwineOrchestrator, VelinorEngine

# Session initialization
if 'orchestrator' not in st.session_state:
    engine = VelinorEngine(player_name="Traveler")
    st.session_state.orchestrator = VelinorTwineOrchestrator(
        game_engine=engine,
        story_path="velinor/stories/sample_story.json"
    )
    st.session_state.state = st.session_state.orchestrator.start_game()

# Display
state = st.session_state.state
st.image(f"images/{state['background_image']}.png")
st.markdown(f"## {state['npc_name']}")
st.write(state['main_dialogue'])

# Choices
for i, choice in enumerate(state['choices']):
    if st.button(choice['text'], key=f"choice_{i}"):
        new_state = st.session_state.orchestrator.process_player_action(
            choice_index=i, player_id="solo"
        )
        st.session_state.state = new_state
        st.rerun()

# Free text (optional)
player_input = st.text_input("Your response:")
if st.button("Submit"):
    new_state = st.session_state.orchestrator.process_player_action(
        player_input=player_input, player_id="solo"
    )
    st.session_state.state = new_state
    st.rerun()
```

### FastAPI Web Backend

```python
from fastapi import FastAPI
from velinor.engine import VelinorTwineOrchestrator, VelinorEngine

app = FastAPI()
sessions = {}  # In production, use Redis/database

@app.post("/api/game/start")
def start_game(player_name: str = "Traveler"):
    session_id = str(uuid.uuid4())
    engine = VelinorEngine(player_name=player_name)
    orchestrator = VelinorTwineOrchestrator(
        game_engine=engine,
        story_path="velinor/stories/sample_story.json"
    )
    sessions[session_id] = orchestrator
    return {
        "session_id": session_id,
        "state": orchestrator.start_game()
    }

@app.post("/api/game/{session_id}/action")
def take_action(session_id: str, choice_index: int = None, input_text: str = None):
    orchestrator = sessions[session_id]
    return orchestrator.process_player_action(
        choice_index=choice_index,
        player_input=input_text,
        player_id="player_1"
    )

@app.post("/api/game/{session_id}/save")
def save_game(session_id: str):
    sessions[session_id].save_game(f"saves/{session_id}.json")
    return {"status": "saved"}
```

## Multiplayer Support

### Enabling Multiplayer

```python
# Start with multiple players
orchestrator.start_game(
    is_multiplayer=True,
    player_ids=["player_1", "player_2", "player_3"]
)

# Process input from individual players
orchestrator.process_player_action(
    player_input="I agree with them",
    player_id="player_2"
)
```

### Multiplayer Features

1. **Sidebar tracking** - See other players' inputs
2. **Adaptive dialogue** - NPCs address group vs. individual
3. **Group stat averaging** - Dice rolls consider all players
4. **Persona-aware responses** - Different tone per player type

**Multiplayer Dialogue Example:**
```
Solo: "You steady yourself as the mist parts."
Group: "Together, your resolve strengthens. The mist bends to your collective will."
```

## Dice Mechanics

### Automatic Skill Checks

If a choice includes skill check notation:
```
[[Persuade the guard (Courage, DC 12)->success]]
```

The system automatically:
1. Rolls d20
2. Applies player's Courage modifier
3. Compares against DC 12
4. Routes to success/failure passage

### Manual Dice Rolls

In passages:
```
{dice: d20+wisdom}

You attempt to solve the ancient puzzle...
```

System processes and determines outcome, potentially branching story.

## Save/Load

```python
# Save current game
orchestrator.save_game("saves/game_001.json")

# Load saved game
state = orchestrator.load_game("saves/game_001.json")
```

Save files contain:
- Current passage ID
- Visited passages list
- Dialogue history
- Player stats
- Complete game log

## FirstPerson Integration

When FirstPerson orchestrator is available, NPC responses become:

1. **Dynamic** - Same choice generates different dialogue each time
2. **Empathetic** - Adapted to player personality/choices
3. **Aware** - References player's previous actions
4. **Clarifying** - Asks open-ended follow-up questions

**Without FirstPerson:** Dialogue is static (template-based)
**With FirstPerson:** Dialogue is generated dynamically (AI-enhanced)

## Next Steps

1. **Build your story** using Twine or StoryBuilder
2. **Test game flow** with `quickstart.py`
3. **Integrate UI layer** (Streamlit, web, etc.)
4. **Connect FirstPerson** for dynamic dialogue
5. **Add background images** to `/velinor/assets/backgrounds/`
6. **Flesh out NPC personalities** in `npc_system.py`
7. **Deploy** to Heroku, AWS, or your hosting platform

## File Structure

```
velinor/
├── engine/
│   ├── core.py                      # Game engine
│   ├── npc_system.py                # NPC dialogue
│   ├── twine_adapter.py             # Twine/story bridge
│   ├── orchestrator.py              # Game loop controller
│   ├── quickstart.py                # Quick start guide
│   ├── sample_story.py              # Story builder example
│   └── __init__.py
├── stories/
│   └── sample_story.json            # Example Twine story
├── assets/
│   └── backgrounds/                 # Background images
└── Characters_Lexicon/              # Game design docs
```

## Troubleshooting

**Issue: Story not loading**
- Check JSON path is correct
- Verify JSON is valid (use `json -l` checker)
- Ensure passages have unique names

**Issue: Choices not appearing**
- Verify `[[text->target]]` syntax
- Ensure target passage exists
- Check for typos in passage names

**Issue: Dice rolls not working**
- Verify `{dice: d20+stat}` syntax
- Check player stat exists
- Ensure DC is reasonable (1-20)

**Issue: NPCs not generating dialogue**
- Verify FirstPerson module is available
- Check NPC registry has the NPC
- Ensure passage has `{npc: Name}` tag

## Resources

- **Twine 2**: https://twinery.org/
- **SugarCube Manual**: https://www.motoslave.net/sugarcube/2/docs/
- **Ink by Inkle**: https://github.com/inkle/ink
- **Velinor Game Docs**: `/velinor/markdowngameinstructions/`
