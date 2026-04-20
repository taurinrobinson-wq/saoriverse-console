## Velinor resonance engine

This folder contains a small, testable resonance engine prototype used to map player `tone` vectors
into NPC `remnants` updates. Files added:

- `data/npc_profiles.json` — example NPC profiles with initial remnants.
- `data/influence_map.json` — simple mapping from tone dimensions to remnants.
- `engine/resonance.py` — implementation with `apply_tone_to_remnants`, `apply_tone_to_all_npcs`, and `simulate_encounter`.
- `tests/test_resonance.py` — pytest unit tests.

Run the tests with:

```bash
```text

```text
```


# 🎮 Velinor: Remnants of the Tone

A text-based narrative game with emotional resonance, dice mechanics, and multiplayer support.

**Status:** 🟢 Core engine complete | 🔄 UI layer pending

##

## What is Velinor?

Velinor is an innovative interactive fiction experience built with:

- **Hybrid Dialogue System** - Players can type free-form responses OR select from structured choices
- **Dice Roll Mechanics** - D&D-inspired stat-based outcomes with hidden/visible rolls
- **Emotional Resonance** - Glyphs (Courage, Wisdom, Empathy, Resolve) drive story progression
- **Dynamic Narration** - NPC responses adapt to player personality and group composition
- **Multiplayer Storytelling** - 2-4 players experience the story together
- **Living World** - Nature-reclaimed ruins of Saonyx with layered history

##

## Quick Start

### Installation

```bash


## Clone repo and navigate
cd saoriverse-console

## Install dependencies

```text

```

### Run Sample Game

```python

from velinor.engine import VelinorTwineOrchestrator, VelinorEngine

## Initialize
engine = VelinorEngine(player_name="Traveler") orchestrator = VelinorTwineOrchestrator(
game_engine=engine, story_path="velinor/stories/sample_story.json" )

## Start game
state = orchestrator.start_game()

## Process player input
state = orchestrator.process_player_action( choice_index=0,  # Select first choice
player_id="player_1"

```text
```text

```

See `velinor/engine/quickstart.py` for complete examples (Streamlit, FastAPI, etc.)

##

## Architecture

```


TWINE STORY (JSON) ↓ [TwineAdapter] → Loads passages, parses markup ↓ [Orchestrator] → Main game
loop
    ├─ Process Input
    ├─ Apply Mechanics (Dice, Stats)
    ├─ Generate NPC Dialogue
    └─ Format UI State
↓ [UI Layer] → Display to Player
    ├─ Streamlit (Desktop)
    ├─ Web Framework (Online)
    ├─ CLI Terminal (Local)

```text
```


### Key Components

| Component | Purpose | Status |
|-----------|---------|--------|
| `engine/core.py` | Game state, dice, events | ✅ Complete |
| `engine/npc_system.py` | NPC dialogue, personalities | ✅ Complete |
| `engine/twine_adapter.py` | Twine story loading | ✅ Complete |
| `engine/orchestrator.py` | Game loop controller | ✅ Complete |
| Streamlit UI | Visual game frontend | 🔄 Next |
| Web API | Online multiplayer | 🔄 Planned |

##

## Story System

Velinor uses **Twine 2** with **SugarCube** markup:

### Story Markup

```
{background: market_ruins}
{npc: Keeper}

You emerge into the Market District...

[[Ask about the Tone->keeper_dialogue]]
[[Explore alone->market_exploration]]
```text

```text
```


**Syntax:**

- `[[text->target]]` - Choice link
- `{background: name}` - Change background image
- `{npc: Name}` - NPC speaking
- `{dice: d20+courage}` - Trigger dice roll
- `{multiplayer: true}` - Group mode

### Story Structure

Current sample story includes:

- **Market District** - Opening scene with Keeper NPC
- **Monument Encounters** - Skill check choices (Courage, Wisdom, Empathy)
- **Branching Paths** - Multiple routes through story
- **20+ Passages** - Scaffolding ready for expansion

See `velinor/TWINE_INTEGRATION_GUIDE.md` for complete markup reference.

##

## Game Mechanics

### Player Stats

```python

{
    'courage': 50,     # Face danger, stand firm
    'wisdom': 55,      # Understand patterns, observe
    'empathy': 60,     # Connect with others, feel
    'resolve': 50,     # Persist despite difficulty
    'resonance': 100,  # Hear the Tone, collect glyphs

```text

```

### Dice Rolls

- **D20 + Modifier** - Stat-based difficulty checks
- **Hidden Rolls** - GM decides outcome behind scenes
- **Visible Rolls** - Show player the result for transparency
- **Success/Failure Routing** - Story branches based on roll

Example:

```

Player chooses: "Persuade the guard" DC: 12, Player Courage: +3 Roll: 14 + 3 = 17 ✅ Success

```text
```text

```

### Glyphs

- Collect emotional resonance tokens
- Each glyph represents a value (Courage, Wisdom, etc.)
- Strengthen player's resonance
- Unlock hidden story paths

##

## Multiplayer Features

### How It Works

1. **Multiple Players** - 2-4 players join same session
2. **Shared Dialogue** - All contribute to decisions
3. **Adaptive Responses** - NPCs adapt to group composition
4. **Sidebar Tracking** - See other players' inputs

### Example

**Solo Mode:**

```


```text
```


**Multiplayer Mode:**

```
NPC: "Together, your courage strengthens. The mist bends
```text

```text
```


##

## Integration with FirstPerson Orchestrator

When FirstPerson is available:

- **Dynamic Dialogue** - NPCs generate fresh responses each turn
- **Affect Parsing** - Understand player emotional state
- **Clarifying Questions** - Companionable follow-ups
- **Memory Tracking** - Remember previous choices

Without FirstPerson: Game still works with template-based dialogue.

##

## File Structure

```

velinor/
├── engine/
│   ├── core.py                 # Game engine (state, dice)
│   ├── npc_system.py           # NPC dialogue
│   ├── twine_adapter.py        # Twine bridge
│   ├── orchestrator.py         # Game loop
│   ├── quickstart.py           # UI examples
│   └── __init__.py
├── stories/
│   └── sample_story.json       # Twine story
├── assets/
│   └── backgrounds/            # Location images
├── markdowngameinstructions/   # Design docs

```text

```

##

## Next Steps

### Phase 2: UI Implementation

1. **Streamlit App** (`app.py`)
   - Display backgrounds
   - Render dialogue bubbles
   - Handle input (buttons, text box)
   - Show stats and dice rolls

2. **Test Full Loop**
   - Play through sample story
   - Verify skill checks
   - Test multiplayer

### Phase 3: Content Expansion

1. Flesh out story (20 → 50+ passages)
2. Create background images
3. Refine NPC personalities
4. Test FirstPerson integration

### Phase 4: Polish & Deploy

1. Inventory system
2. Quest tracking
3. Achievement system
4. Deploy to cloud (Heroku, AWS)

##

## Documentation

- **`TWINE_INTEGRATION_GUIDE.md`** - Complete API reference
- **`TWINE_IMPLEMENTATION_COMPLETE.md`** - Architecture details
- **`STATUS.md`** - Current project status
- **`engine/quickstart.py`** - Code examples

##

## Example: Playing the Game

```python


## Initialize (2)
orchestrator = VelinorTwineOrchestrator( game_engine=engine,
story_path="velinor/stories/sample_story.json" )

## Start
state = orchestrator.start_game() print(state['main_dialogue']) print("Choices:", state['choices'])

## Player chooses
state = orchestrator.process_player_action(choice_index=0)

## Or player types
state = orchestrator.process_player_action( player_input="I approach cautiously" )

## Get result
print(state['npc_dialogue']) print("New location:", state['game_state']['current_location'])

## Save
orchestrator.save_game("saves/game_001.json")

## Load

```text
```text

```

##

## Technical Details

### Twine JSON Format

Velinor loads Twine 2 JSON export format:

```json


{ "name": "Story Title", "startnode": "1", "passages": [ { "pid": "1", "name": "start", "text":
"Story content...", "tags": [], "position": [0, 0], "size": [100, 100] } ]

```text
```


### Game State Structure

```python
{
  'passage_id': 'keeper_dialogue',
  'passage_name': 'Meeting the Keeper',
  'main_dialogue': 'The Keeper greets you...',
  'npc_name': 'Keeper',
  'npc_dialogue': '[AI-generated response]',
  'background_image': 'market_ruins',
  'choices': [
    {'text': 'Ask about the Tone', 'target': 'keeper_dialogue_1'},
    {'text': 'Explore alone', 'target': 'market_alone'}
  ],
  'clarifying_question': 'Are you sure about this?',
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


##

## Support & Resources

- **Twine 2**: <https://twinery.org/>
- **SugarCube Manual**: <https://www.motoslave.net/sugarcube/2/docs/>
- **Game Design**: See `/velinor/markdowngameinstructions/`

##

## License

[Your License Here]

##

**Created:** December 6, 2025
**Branch:** `feature/velinor-remnants-of-tone`
**Status:** 🟢 Core complete | Ready for UI integration
