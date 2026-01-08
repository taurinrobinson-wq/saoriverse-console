# Quick Reference: Story Definitions API

## Add a Passage

```python
story.add_passage(
    name="scene_name",              # Required: unique identifier
    text="Story text...",           # Required: what player reads
    background="market_ruins",      # Optional: location visual
    npcs=["Ravi", "Nima"],         # Optional: characters in scene
    is_start=True,                  # Optional: first passage only
    tags=["act1", "marketplace"]    # Optional: organization
)
```


## Add a Choice

```python
story.add_choice(
    from_passage_name="current_scene",
    choice_text="What player clicks",
    to_passage_name="next_scene"
)
```


## Complete Example

```python
def build_velinor_story():
    story = StoryBuilder("Velinor: Remnants of the Tone")

    # Opening scene
    story.add_passage(
        name="market_arrival",
        text="You emerge into the Market District...",
        background="market_ruins",
        is_start=True,
        tags=["act1"]
    )

    # NPC encounter
    story.add_passage(
        name="meet_ravi",
        text="A figure approaches from the shadows...",
        background="market_ruins",
        npcs=["Ravi"],
        tags=["act1", "ravi_path"]
    )

    # Connect them
    story.add_choice(
        from_passage_name="market_arrival",
        choice_text="Greet the figure",
        to_passage_name="meet_ravi"
    )

    return story
```


## Key Parameters

| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `name` | string | Yes | `"market_arrival"` |
| `text` | string | Yes | `"You see..."` |
| `background` | string | No | `"market_ruins"` |
| `npcs` | list | No | `["Ravi", "Nima"]` |
| `is_start` | bool | No | `True` |
| `tags` | list | No | `["act1", "marketplace"]` |

## Common Backgrounds

- `market_ruins` - Market District
- `shelter_interior` - Safe rest area
- `shrine_ruins` - Temples
- `archive_entrance` - Library
- `underground_entrance` - Tunnels
- `thieves_cache` - Black market
- `bridge_ravine` - Crossing
- `temple_hall` - Ceremony space

## Main NPCs (Act 1)

- `Ravi` - Mentor, warm
- `Nima` - Guide, wise
- `Kaelen` - Thief, mysterious
- `Saori` - Shrine keeper

## Common Patterns

### Solo scene

```python
story.add_passage(
    name="alone",
    text="...",
    npcs=["Ravi"]  # Single NPC
)
```


### Group scene

```python
story.add_passage(
    name="group",
    text="...",
    npcs=["Ravi", "Nima"]  # Multiple
)
```


### Location only

```python
story.add_passage(
    name="explore",
    text="...",
    background="market_ruins"
    # no npcs - you're alone
)
```


### Branching

```python

# Choice point
story.add_choice(
    from_passage_name="fork",
    choice_text="Path A",
    to_passage_name="path_a"
)

# Alternative
story.add_choice(
    from_passage_name="fork",
    choice_text="Path B",
    to_passage_name="path_b"
)

# Reconverge
story.add_choice(
    from_passage_name="path_a",
    choice_text="Meet up",
    to_passage_name="convergence"
)
```


## Build Commands

```bash

# Build (Python → JSON)
python build_story.py

# Build + Validate
python build_story.py --validate

# Watch for changes
python build_story.py --watch

# Parse Markdown
python build_story.py --parse-markdown
```


## Tips

✓ Use snake_case for passage names (`market_arrival`, not `MarketArrival`) ✓ Use proper case for NPC
names (`Ravi`, not `ravi`) ✓ Use snake_case for backgrounds (`market_ruins`, not `MarketRuins`) ✓
Keep text short but descriptive ✓ Use tags for organization (act, location, npc_path, etc.) ✓
Multi-line text works fine in `"""..."""`

## Next Steps

1. Open `story_definitions.py` 2. Edit the story content 3. Add backgrounds/npcs to each scene 4.
Run `python build_story.py` 5. Run `python build_story.py --validate` 6. Test in game
## 

**Full Guides:**
- [README.md](README.md) - Complete story system guide
- [SCENE_COMPOSITION_GUIDE.md](SCENE_COMPOSITION_GUIDE.md) - Deep dive on backgrounds/NPCs
- [STORY_SYSTEM_IMPLEMENTATION.md](../STORY_SYSTEM_IMPLEMENTATION.md) - System overview
