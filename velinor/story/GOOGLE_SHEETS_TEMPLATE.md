# Velinor Google Sheets Story Template

## Overview

Use this template to author Velinor stories in Google Sheets with zero technical barriers.  
Each row = one **passage** (scene). Columns define text, choices, and game mechanics.

**Template link:** [Velinor Story Template (Copy this)](https://docs.google.com/spreadsheets/d/TEMPLATE_ID)

---

## Column Reference

### Required Columns

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| **PassageID** | Text | `market_entry` | Unique identifier (no spaces, use underscores) |
| **Text** | Long Text | `You emerge from the collapsed underpass...` | Full passage text. **No Twine markup.** |

### Optional Columns (Story Metadata)

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| **Background** | Text | `market_ruins` | Background image/location |
| **NPC** | Text | `Keeper` | NPC name present in this scene |
| **Tags** | Comma-separated Text | `intro,market,tutorial` | For organization & filtering |
| **GlyphRewards** | Pipe-separated Text | `Courage\|Wisdom` | Glyphs player earns in this passage |
| **ToneOnEnter** | Key-Value Text | `courage:0.1,resolve:-0.05` | TONE stat changes on entering |

### Choice Columns (Repeating Sets)

For each choice (up to 6 per passage), include this set:

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| **Choice1_Text** | Text | `Approach the Keeper` | Choice text shown to player |
| **Choice1_Target** | Text | `keeper_dialogue_1` | Target passage ID |
| **Choice1_DiceCheck** | Text | `courage:12` | Skill check (stat:DC) or empty |
| **Choice1_ToneEffects** | Key-Value Text | `courage:0.2,empathy:-0.1` | TONE changes for this choice |
| **Choice1_NPCResonance** | Key-Value Text | `Keeper:0.3,Ravi:-0.1` | NPC relationship changes |
| **Choice1_StoryBeat** | Text | `first_contact_keeper` | Named story beat (optional) |

Then **Choice2_Text**, **Choice2_Target**, etc.

---

## Format Examples

### Simple Passage

```
PassageID: start
Text: You wake up in the market.
Background: market_ruins
NPC: Keeper
Tags: intro,opening
Choice1_Text: Greet the Keeper
Choice1_Target: greet_keeper
```

### Complex Passage with Dice Check & Effects

```
PassageID: monument_challenge
Text: The monument glows with ancient power. Test yourself?
Background: monuments
NPC: (leave empty)
GlyphRewards: Courage|Wisdom
ToneOnEnter: resolve:-0.2
Choice1_Text: Face the monument (Courage, DC 12)
Choice1_Target: monument_success
Choice1_DiceCheck: courage:12
Choice1_ToneEffects: courage:0.3
Choice1_NPCResonance: (leave empty)
Choice1_StoryBeat: monument_tested
Choice2_Text: Back away cautiously
Choice2_Target: market_alone
Choice2_ToneEffects: courage:-0.1
```

### Empty Passage (End of Branch)

```
PassageID: ending_alone
Text: You walk away. The city holds its secrets. [END]
Background: (leave empty)
NPC: (leave empty)
Tags: ending
Choice1_Text: (leave empty - no more choices)
```

---

## Data Entry Rules

### PassageID
- **Required** — must be unique
- Alphanumeric + underscores only (no spaces)
- Start with letter (e.g., `market_entry`, not `1_market`)

### Text
- **Required** — full passage displayed to player
- **No markup** — plain text only
- Can include line breaks

### Background / NPC
- Leave **blank** if not applicable (not empty string, just blank)
- Single value only

### Tags
- Comma-separated: `intro,market,tutorial`
- Used for filtering & organization

### GlyphRewards
- Pipe-separated: `Courage|Wisdom|Empathy`
- Leave blank if none

### ToneOnEnter / ToneEffects / NPCResonance
- **Format:** `key1:value1,key2:value2`
- **No spaces** around colons or commas
- Valid keys for TONE: `courage`, `wisdom`, `empathy`, `resolve`
- **Values:** small floats (±0.1 to ±0.3 typical)
- Examples:
  - `courage:0.2,empathy:-0.1`
  - `Keeper:0.3,Ravi:-0.15`

### DiceCheck
- **Format:** `stat:DC`
- **Stat:** `courage`, `wisdom`, `empathy`, `resolve`
- **DC:** integer (typically 8-15)
- Example: `courage:12`, `wisdom:14`
- Leave blank if no check needed

### Choice Text / Target
- **Text:** what player sees (e.g., "Ask about the Tone")
- **Target:** PassageID of next scene
- Leave **blank** to skip a choice slot
- If **Choice1_Text** is blank, no choices are added

### StoryBeat
- Optional label for story tracking
- Examples: `first_contact_keeper`, `monument_tested`, `ending_together`

---

## Workflow

### 1. Create Sheet
- Copy template or start fresh
- Name it something memorable (e.g., "Velinor_Market_Story")

### 2. Write Passages
- One row per scene
- Fill in PassageID, Text, and at least one choice

### 3. Link Passages
- Make sure each **Choice_Target** points to an existing **PassageID**
- First passage (top row) becomes the start automatically

### 4. Test Your Links
- Do passages form a connected story?
- Are there any dead ends (passages with no incoming links)?

### 5. Download as CSV
- **File → Download → Comma Separated Values (.csv)**
- Save to your computer

### 6. Convert to JSON
- Use the converter script:
  ```bash
  python sheets_to_json_converter.py --csv story.csv --output story.json
  ```
- Output is placed in `velinor/stories/`

### 7. Load in Game
- Pass JSON path to `StorySession`:
  ```python
  story_data = json.load(open("story.json"))
  session = StorySession(story_data)
  ```

---

## Tips & Tricks

### Start Multiple Branches
- Leave PassageID blank for passages you don't want as start (second row onward)
- First row is always start

### Empty Cells
- Blank cells = use defaults (None, empty list, etc.)
- Don't use "N/A" or "—" — just leave blank

### Naming Conventions
- PassageID: `snake_case` (e.g., `keeper_dialogue_1`, not `KeeperDialogue1`)
- NPC names: `PascalCase` (e.g., `Keeper`, `Ravi`, not `keeper`, `KEEPER`)

### Test Values
- TONE effects: ±0.1 to ±0.3 (small nudges)
- NPC resonance: ±0.1 to ±0.4
- Dice DC: 10-14 is typical

### Reuse Passages
- If multiple choices point to the same target, that's fine
- Creates choice variations with different outcomes

---

## Example Sheet Structure

| PassageID | Text | Background | NPC | Tags | Choice1_Text | Choice1_Target | Choice1_ToneEffects | Choice2_Text | Choice2_Target |
|-----------|------|-----------|-----|------|--------------|-----------------|-------------------|--------------|-----------------|
| market_entry | You emerge from... | market_ruins | Keeper | intro,market | Approach Keeper | keeper_dialogue_1 | courage:0.1 | Explore alone | market_exploration |
| keeper_dialogue_1 | The Keeper speaks... | market_ruins | Keeper | dialogue | Ask about glyphs | keeper_glyphs | courage:0.2 | Thank and leave | market_alone |
| keeper_glyphs | Glyphs are echoes... | market_ruins | Keeper | lore | Accept glyphs | keeper_guide |  | Decline | market_alone |
| market_exploration | The market sprawls... | market_ruins |  | exploration | Find archive | archive_entrance | wisdom:0.1 | Return to Keeper | market_entry |
| market_alone | You explore alone... | market_ruins |  | exploration | Enter underground | underground | courage:-0.1 | Cross bridge | bridge_crossing |
| archive_entrance | The archive beckons... | archive |  | archive | Go inside | archive_main |  |  |  |
| ending_alone | You fade into silence... | market_ruins |  | ending | [END] |  |  |  |  |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Unknown passage" error | Check that all `Choice_Target` values match existing `PassageID` values |
| Converter fails | Make sure CSV has headers matching column names exactly (case-sensitive) |
| Story doesn't start | First row **must** be a valid passage with PassageID |
| Numbers not parsing | Make sure tone effects use `:` not `=` (e.g., `courage:0.2` not `courage=0.2`) |
| Blank cells break converter | Leave truly blank, don't fill with spaces or "N/A" |

---

## Questions?

- Refer to [Velinor Story JSON Schema](VELINOR_JSON_SCHEMA.md) for technical details
- See [sheets_to_json_converter.py](sheets_to_json_converter.py) for code reference
