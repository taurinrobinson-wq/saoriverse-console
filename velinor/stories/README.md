# Story Building System Guide

## Overview

This system gives you **complete independence** to edit and manage the Velinor story without needing
an AI agent to modify JSON each time.

The pipeline works like this:

```
Your Edits (story_definitions.py)
    ↓
Python Code (readable, version-controllable)
    ↓
build_story.py (converts to JSON)
    ↓
sample_story.json (what the game engine reads)
    ↓
story_validator.py (catches errors before runtime)
```


## Quick Start

### 1. Edit the Story (story_definitions.py)

This is where you write the story. It reads like Python code but is designed to be **intuitive and
prose-like**:

```python
def build_velinor_story():
    story = StoryBuilder("Velinor: Remnants of the Tone")

    # Scene: Market Arrival
    story.add_passage(
        name="market_arrival",
        text="""
You emerge from the collapsed underpass into the Market District.
The air is thick with silence—not the silence of absence, but of waiting.
        """,
        is_start=True,
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1"]
    )

    # Player choice
    story.add_choice(
        from_passage_name="market_arrival",
        choice_text="Push forward boldly",
        to_passage_name="meet_ravi_nima"
    )

    return story
```


**Key Concepts:**

- **Passages**: Individual scenes or text nodes
  - `name`: Unique identifier (snake_case)
  - `text`: Story content (what player reads)
  - `background`: Background/location name (e.g., "market_ruins", "temple_hall")
  - `npcs`: List of NPCs present in this scene (e.g., `["Ravi", "Nima"]`)
  - `is_start`: Mark the first passage (only one)
  - `tags`: Organize by act, theme, NPC, etc.

- **Choices**: What players can do
  - `from_passage_name`: Which passage contains this choice
  - `choice_text`: What the player sees (e.g., "Ask about the glyphs")
  - `to_passage_name`: Where the choice leads

### 2. Build to JSON

```bash
python build_story.py
```


This converts your Python code to `sample_story.json`, which the game engine reads.

**Output:**

```
✓ Story exported to sample_story.json
```


### 3. Validate for Errors

```bash
python build_story.py --validate
```


This checks for:
- ✓ Broken links (choices pointing to non-existent passages)
- ✓ Missing start passage
- ✓ Dead ends (passages with no exit)
- ✓ Unreachable content
- ✓ Duplicate IDs or names
- ✓ Malformed passages

**Example output:**

```

# STORY VALIDATION REPORT

Story: Velinor: Remnants of the Tone
Total passages: 14

✓ No structural errors

⚠️  WARNINGS (1):
   • Passage 'shrine_visit_evening' has empty text

✓ No other warnings

✅ STORY IS VALID
```


### 4. Watch for Changes

```bash
python build_story.py --watch
```


This watches your `story_definitions.py` and automatically rebuilds + validates whenever you save.

```
👀 Watching for changes (Ctrl+C to stop)

Ready for changes...

[14:32:15] Changes detected
✓ Story exported to sample_story.json
✓ No structural errors
```


## Advanced Workflows

### Convert Markdown Story Map to Python Scaffold

If you have your story outlined in Markdown (your story_map_velinor.md), you can auto-generate a
Python skeleton:

```bash
python build_story.py --parse-markdown
```


This reads `story_map_velinor.md` and generates `story_definitions.py` with passage placeholders.
You then fill in the actual story text.

### Edit and Iterate

1. **Edit story_definitions.py** - add passages, refine text 2. **Save the file** 3. **Auto-rebuild
watches for changes** - JSON updates automatically 4. **Validation runs** - errors appear
immediately 5. **Test in game** - play through your changes

### Stats and Tone Effects

Each choice can affect player stats:

```python
story.add_choice(
    from_passage="market_arrival",
    text="Push forward boldly",
    to_passage="meet_ravi_nima",
    stat_effects={
        "narrative_presence": 0.2,    # +20% to presence
        "courage": 0.15,               # +15% to courage
        "empathy": -0.1                # -10% to empathy
    }
)
```


The game engine uses these to track the player's emotional arc.

### Backgrounds and NPCs

Specify what location and characters are in each scene:

```python
story.add_passage(
    name="market_arrival",
    text="...",
    background="market_ruins",        # Location/visual setting
    npcs=["Ravi", "Nima"],           # List of NPCs present
    tags=["marketplace", "act1"]
)
```


**Backgrounds** should match available assets in velinor-web (e.g., "market_ruins", "temple_hall", "shelter_interior")

**NPCs** are character names that the game engine will render (e.g., "Ravi", "Nima", "Kaelen")

Both are optional - use them to provide context to the game engine about scene composition.

### Organizing by Tags

Use tags to organize passages:

```python
story.add_passage(
    ...
    tags=["marketplace", "act1", "ravi_path", "npc_encounter"]
)
```


This helps you:
- Group related scenes
- Track which NPC paths are incomplete
- Build separate acts
- Ensure every scene is tagged

**Recommended tags:**
- Act: `act1`, `act2`, `act3`, `act4`
- Location: `marketplace`, `archive`, `temple`, `underground`
- NPC: `ravi_path`, `nima_path`, `kaelen_encounter`
- Type: `dialogue`, `exploration`, `choice_point`, `ending`

## File Structure

```
velinor/stories/
├── story_definitions.py        ← EDIT THIS (your story)
├── sample_story.json           ← AUTO-GENERATED (don't edit)
├── build_story.py              ← Use this to build
├── story_validator.py          ← Use this to validate
├── story_map_parser.py         ← Use this to parse Markdown
└── README.md                   ← This file
```


## Version Control

Since `story_definitions.py` is pure Python, Git diffs are clean and meaningful:

```diff
- story.add_passage(
-     name="keeper_dialogue_1",
-     text="The Keeper's eyes soften...",
- )
+ story.add_passage(
+     name="ravi_dialogue",
+     text="Ravi's expression softens...",
+ )
```


Unlike JSON diffs, you can easily see what changed.

## Common Tasks

### Add a New Passage

```python
story.add_passage(
    name="new_scene",
    text="""
Your new story text here.
Multiple lines work fine.
    """,
    background="location_name",
    npcs=["NPC1"],
    tags=["act2"]
)
```


### Connect Two Passages

```python
story.add_choice(
    from_passage="current_scene",
    text="Where you want to go",
    to_passage="next_scene"
)
```


### Edit Existing Passage

Just update the `text` field in `story_definitions.py`:

```python
story.add_passage(
    pid="1",
    name="market_arrival",
    text="""
[Updated story text here]
    """,
    is_start=True
)
```


Save, and it auto-rebuilds.

### Create a Branching Path

```python

# Main path
story.add_choice(
    from_passage="decision_point",
    text="Go with Ravi",
    to_passage="ravi_path_1"
)

# Alternative path
story.add_choice(
    from_passage="decision_point",
    text="Go with Nima",
    to_passage="nima_path_1"
)

# Both paths can reconverge later
story.add_choice(
    from_passage="ravi_path_1",
    text="Meet up with Nima",
    to_passage="reconvergence"
)
```


## Troubleshooting

### Error: "Passage 'X' (pid=Y) has broken link to non-existent passage 'Z'"

You have a choice pointing to a passage that doesn't exist.

**Fix:**
1. Check the passage name: `to_passage="correct_name"` 2. Make sure the target passage exists 3. Run
validation again: `python build_story.py --validate`

### Error: "Start passage (pid=1) does not exist"

The game is looking for a passage with `pid="1"` but can't find it.

**Fix:**
1. Make sure your first passage has `pid="1"` 2. Make sure `is_start=True` on that passage

### Warning: "Passage 'X' is a dead end"

A passage has no choices leading out of it (and isn't marked as an ending).

**Fix (choose one):**
- Add choices to continue the story
- Mark it as an ending: `story.add_passage(..., is_end=True)`
- Add choices that lead back: `story.add_choice(..., to_passage="somewhere")`

### Error: "Duplicate pid: '1'"

Two passages have the same ID.

**Fix:**
- Each passage needs a unique `pid`
- Increment: `pid="1"`, `pid="2"`, `pid="3"`, etc.

## Workflow Tips

1. **Start with outline** - add passage names and basic structure 2. **Fill in dialogue** - add the
actual story text passage by passage 3. **Validate frequently** - catch errors early with `python
build_story.py --validate` 4. **Use watch mode** - `python build_story.py --watch` while editing 5.
**Test in game** - play through to ensure choices work 6. **Commit to Git** - your Python story
definitions are safe and version-tracked

## Integration with Game Engine

The game engine loads `sample_story.json` and:
- Starts at passage with `startnode` ID
- Displays passage `text`
- Provides buttons for each choice
- Applies `stat_effects` when choices are made
- Navigates to next passage when choice is clicked

You don't need to touch JSON directly—just edit `story_definitions.py`, build, validate, and play.

## Next Steps

1. **Review current story** - Open `story_definitions.py` to see the existing structure 2. **Update
NPC names** - Replace "Keeper" with "Ravi" and "Nima" throughout 3. **Add more passages** - Flesh
out Act 2-4 based on your story map 4. **Test in game** - Run the Velinor engine and play through
your story 5. **Iterate** - Edit, build, validate, test, repeat

Your story map (`story_map_velinor.md`) is the source of truth for outline and structure.
`story_definitions.py` is where you write the actual prose. JSON is generated automatically.

You're now in control of your narrative. Happy writing! 📖
