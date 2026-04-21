# Velinor Story System Architecture

## End-to-End Pipeline

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAY AUTHORS / WRITERS / YOU                                                 │
│ (No coding required)                                                        │
└────────────────────┬────────────────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Google Sheets             │
        │  Story Template            │
        │                            │
        │  • PassageID               │
        │  • Text                    │
        │  • Background/NPC          │
        │  • Choices + Effects       │
        │  • Dice checks             │
        └────────────────┬───────────┘
                         │
         (Export as CSV) │
                         ▼
        ┌────────────────────────────────────┐
        │ sheets_to_json_converter.py        │
        │                                    │
        │ • Parse CSV rows                   │
        │ • Validate PassageIDs              │
        │ • Convert to canonical JSON        │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │ Velinor Story JSON File                  │
        │ (velinor/stories/market.json)            │
        │                                          │
        │ {                                        │
        │   "title": "...",                        │
        │   "start": "market_entry",               │
        │   "passages": {                          │
        │     "market_entry": {...},               │
        │     "keeper_dialogue_1": {...}           │
        │   }                                      │
        │ }                                        │
        └──────────────┬───────────────────────────┘
                       │
                       │ (Loaded by game engine)
                       ▼
        ┌────────────────────────────────────────────┐
        │ StorySession(story_data)                   │
        │                                            │
        │ • get_current_passage()                    │
        │ • get_choices()                            │
        │ • choose(choice_index)                     │
        │ • get_choice_metadata()                    │
        └──────────────┬──────────────────────────────┘
                       │
                       │ (Wrapped by orchestrator)
                       ▼
        ┌──────────────────────────────────────────────────────┐
        │ VelinorOrchestrator                                  │
        │                                                      │
        │ • story_session: StorySession                        │
        │ • process_player_action(input)                       │
        │ • render_passage()                                   │
        │ • apply_tone_effects()                               │
        │ • apply_npc_resonance()                              │
        └───────────────┬────────────────────────────────────┬─┘
                        │                                    │
                        ▼                                    ▼
        ┌──────────────────────────────┐    ┌─────────────────────────────┐
        │ Emotional OS                 │    │ Game Engine Systems         │
        │                              │    │                             │
        │ • TraitProfiler              │    │ • Dice rolls                │
        │ • CoherenceCalculator        │    │ • Stat updates              │
        │ • NPCResponseEngine          │    │ • Story beat markers        │
        │ • REMNANTS NPCManager        │    │ • Save/load game state      │
        │                              │    │                             │
        │ → Computes player coherence  │    │ → Executes game mechanics   │
        │ → Generates NPC responses    │    │ → Updates world state       │
        │ → Tracks trait patterns      │    │                             │
        └──────────────┬───────────────┘    └──────────┬──────────────────┘
                       │                               │
                       └───────────────┬────────────────┘
                                       │
                                       ▼
        ┌───────────────────────────────────────────────┐
        │ Game State                                    │
        │ (Updated with each choice)                    │
        │                                               │
        │ • current_passage_id                          │
        │ • player traits (courage, wisdom, etc.)       │
        │ • npc_relationships                           │
        │ • story_beats_hit                             │
        │ • dialogue_log                                │
        └───────────────┬─────────────────────────────┘
                        │
                        ▼
        ┌──────────────────────────────────────┐
        │ UI / Frontend                        │
        │ (React, console, etc.)               │
        │                                      │
        │ • Render passage text                │
        │ • Display background image           │
        │ • Show NPC dialogue                  │
        │ • Present choices to player          │
        │ • Show player stats/coherence        │
        └──────────────────────────────────────┘
```

---

## Component Breakdown

### 1. **Google Sheets Template**
- **Purpose:** Human-readable story authoring for lay writers
- **Format:** CSV rows (downloadable from Sheets)
- **No technical barrier:** Plain text + simple key-value pairs

### 2. **Converter Script** (`sheets_to_json_converter.py`)
- **Input:** CSV export from Sheets
- **Output:** Velinor story JSON (canonical format)
- **Validation:** Checks PassageID uniqueness, choice targets exist
- **CLI:** `python sheets_to_json_converter.py --csv story.csv --output story.json`

### 3. **Velinor Story JSON** 
- **Format:** Single source of truth for all stories
- **Schema:** Defined in `VELINOR_JSON_SCHEMA.md`
- **Structure:** Flat passages (no nesting), choices embedded in passages
- **Metadata:** Title, author, region, creation date

### 4. **StorySession** (Runtime Engine)
- **Loads:** Velinor story JSON
- **State:** Current passage, history of visited passages
- **Methods:**
  - `get_current_passage()` — Returns passage object
  - `get_choices()` — Available choices in current passage
  - `choose(index)` — Select choice, advance to next passage
  - `get_choice_metadata(index)` — Inspect choice effects without selecting
- **No external dependencies:** Pure story navigation

### 5. **Velinor Orchestrator**
- **Wrapper:** StorySession + game mechanics
- **Responsibilities:**
  - Render passages for UI
  - Apply tone/TONE effects from choices
  - Update NPC resonance
  - Track story beats
  - Integrate with Emotional OS
  - Handle dice rolls (if present)
  - Manage save/load

### 6. **Emotional OS Integration**
- **TraitProfiler:** Tracks player TONE choices
- **CoherenceCalculator:** Computes coherence level (consistency)
- **NPCResponseEngine:** Generates contextual NPC dialogue based on traits
- **REMNANTS Manager:** Simulates NPC state evolution through story
- **Connection:** Choice metadata (`tone_effects`, `npc_resonance`, `mark_story_beat`) feeds directly into these systems

### 7. **Frontend / UI**
- **Receives:** Rendered passage state from orchestrator
- **Displays:**
  - Background image (from passage `background` field)
  - Passage text
  - NPC name & dialogue
  - Player choices
  - Current player stats (coherence, traits)
- **Sends back:** Player choice selection (index) or free-text input

---

## Data Flow Example

**Scenario:** Player chooses "Approach the Keeper" at market_entry

```
1. UI shows: choices = ["Approach the Keeper", "Explore alone", ...]
   Player clicks: choice_index = 0

2. Orchestrator.process_player_action(choice_index=0)
   
3. StorySession.choose(0)
   - Gets choice object from current passage
   - Reads target: "keeper_dialogue_1"
   - Advances to new passage
   
4. Orchestrator.apply_game_mechanics()
   - Extracts choice.metadata:
     { "tone_effects": {"courage": 0.1},
       "npc_resonance": {"Keeper": 0.2},
       "mark_story_beat": "first_contact_keeper" }
   
5. TraitProfiler.record_choice()
   - Marks "courage" trait (+0.1)
   
6. REMNANTS.update_npc()
   - Keeper resonance +0.2
   
7. CoherenceCalculator.get_report()
   - Recalculates coherence with new choices
   - Determines pattern (e.g., "Resolute Diplomat")
   
8. NPCResponseEngine.generate_dialogue()
   - Reads current pattern
   - Generates context-aware Keeper response
   
9. Orchestrator renders new state:
   { "passage_text": "The Keeper's eyes soften...",
     "background": "market_ruins",
     "npc_name": "Keeper",
     "npc_dialogue": "[Generated emotionally-aware response]",
     "choices": [...],
     "player_coherence": 0.67,
     "player_traits": {...} }
   
10. UI displays everything
    
11. Loop back to step 1
```

---

## API Reference

### StorySession

```python
from velinor.story.story_session import StorySession
import json

# Load story
story_data = json.load(open("story.json"))
session = StorySession(story_data)

# Navigate
passage = session.get_current_passage()  # Dict with passage data
choices = session.get_choices()          # List of choice dicts

# Select choice
next_passage = session.choose(0)         # Advances & returns new passage

# Inspect without selecting
metadata = session.get_choice_metadata(0)  # {"tone_effects": {...}, ...}

# Track
history = session.get_history()          # List of visited passage IDs
```

### StoryBuilder (Programmatic)

```python
from velinor.story.story_builder import StoryBuilder

# Build story
builder = StoryBuilder("My Story", author="Me", region="Marketplace")

# Add passages
builder.add_passage(
    passage_id="start",
    text="You wake up.",
    background="bedroom",
    npc="Cat",
    is_start=True
)

# Add choices
builder.add_choice(
    from_passage_id="start",
    text="Get out of bed",
    target_id="standing",
    tone_effects={"courage": 0.1},
    npc_resonance={"Cat": 0.2},
    mark_story_beat="morning_awakening"
)

# Export
builder.export_json("story.json")

# Validate
errors = builder.validate()  # Returns list of issues
```

### Converter

```python
from velinor.story.sheets_to_json_converter import convert_rows_to_story

# From CSV rows
rows = [...]  # List of dicts from CSV reader
story = convert_rows_to_story(rows, title="Market Quest")

# CLI
# python sheets_to_json_converter.py --csv story.csv --output story.json
```

---

## Integration with Orchestrator

The orchestrator was refactored to use the new story system:

```python
from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.story.story_session import StorySession
import json

# In orchestrator.__init__():
story_data = json.load(open("story.json"))
self.story_session = StorySession(story_data)

# In orchestrator.process_player_action():
next_state = self.story_session.choose(choice_index)
metadata = self.story_session.get_choice_metadata(choice_index)

# Apply effects through game systems
self.trait_profiler.record_choice(...)
self.npc_manager.update_npc(...)
```

---

## Key Departures from Twine

| Aspect | Twine | Velinor |
|--------|-------|---------|
| **Format** | `.tw` or Twine JSON | Flat JSON schema |
| **Editing** | Visual editor | Google Sheets or code |
| **Markup** | `[[link->target]]` | Clean JSON fields |
| **Passages** | Nested with position | Flat dict by ID |
| **Metadata** | In story tags | Explicit choice objects |
| **Tooling** | Twine app | Python + Sheets |
| **Accessibility** | Requires app download | Web-based (Sheets) |

---

## Workflow Summary

**For Writers:**
```
1. Open Google Sheets template
2. Fill in PassageID, Text, Choices
3. Download as CSV
4. Run converter: sheets_to_json_converter.py
5. Done! JSON is ready for game
```

**For Developers:**
```
1. Load story JSON into StorySession
2. Call session.get_current_passage() to render
3. Hook session.choose() to player input
4. Apply metadata through game systems
5. Loop until end
```

**For Game:**
```
JSON → StorySession → Orchestrator → Emotional OS → UI
```

---

## Files & Locations

- **Schema:** `velinor/story/VELINOR_JSON_SCHEMA.md`
- **Sheets Guide:** `velinor/story/GOOGLE_SHEETS_TEMPLATE.md`
- **Converter:** `velinor/story/sheets_to_json_converter.py`
- **StoryBuilder:** `velinor/story/story_builder.py`
- **StorySession:** `velinor/story/story_session.py`
- **Stories:** `velinor/stories/*.json`
- **Orchestrator:** `velinor/engine/orchestrator.py` (uses StorySession)
