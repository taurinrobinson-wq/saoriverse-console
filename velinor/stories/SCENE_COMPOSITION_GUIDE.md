# Story Scene Composition Guide

When writing scenes in `story_definitions.py`, you can now specify the background and NPCs for each scene.

## Quick Example

```python
story.add_passage(
    name="market_arrival",
    text="You emerge into the Market District...",
    background="market_ruins",
    npcs=["Ravi", "Nima"],
    tags=["marketplace", "act1"]
)
```

## How It Works

### Backgrounds

The `background` parameter specifies the location/visual setting for a scene:

```python
background="market_ruins"      # Primary location
background="shelter_interior"  # Indoor shelter
background="shrine_ruins"      # Temple/shrine area
background="thieves_cache"     # Underground market
```

The game engine uses this to:
- Load background images/visuals
- Set the environmental mood
- Provide context for the player

**Common backgrounds for Velinor:**
- `market_ruins` - Market District (primary starting location)
- `shelter_interior` - Safe rest area
- `shrine_ruins` - Ancient temples/monuments
- `archive_entrance` - Library/knowledge hub
- `underground_entrance` - Tunnels and caves
- `thieves_cache` - Black market area
- `bridge_ravine` - Dangerous crossing
- `temple_hall` - Ceremonial space

### NPCs

The `npcs` parameter specifies which characters are present in the scene:

```python
npcs=["Ravi"]              # Single NPC
npcs=["Ravi", "Nima"]      # Multiple NPCs
npcs=["Ravi", "Nima", "Kaelen"]  # Even more
```

The game engine uses this to:
- Render character portraits/models
- Trigger dialogue from specific NPCs
- Track relationship progression
- Create scene composition

**Main NPCs for Act 1:**
- `Ravi` - Warm mentor figure, trusts quickly
- `Nima` - Cautious guide, wisdom-focused
- `Kaelen` - Thief character, underground contact
- `Saori` - Shrine NPC (Act 1 later encounters)

## Usage Patterns

### Scene with Multiple NPCs
```python
story.add_passage(
    name="marketplace_meeting",
    text="Both of them approach you...",
    background="market_ruins",
    npcs=["Ravi", "Nima"],
    tags=["marketplace", "act1", "group_scene"]
)
```

### Solo Dialogue Scene
```python
story.add_passage(
    name="ravi_alone",
    text="Ravi pulls you aside...",
    background="market_ruins",
    npcs=["Ravi"],
    tags=["marketplace", "act1", "ravi_path"]
)
```

### Location-Only Scene
```python
story.add_passage(
    name="shelter_rest",
    text="You enter the quiet shelter...",
    background="shelter_interior",
    npcs=[],  # Empty - you're alone
    tags=["rest", "shelter"]
)
```

### Optional Presence
```python
# If you want to skip specifying these:
story.add_passage(
    name="exploration",
    text="You wander through ruins...",
    tags=["exploration"]
    # background and npcs are optional
)
```

## Metadata Storage

Both background and NPCs are stored in two ways in the JSON:

**1. In the passage text (for parsing):**
```
{background: market_ruins}
{npc: Ravi}
{npc: Nima}

Your story text here...
```

**2. In _metadata field (for structured access):**
```json
"_metadata": {
  "background": "market_ruins",
  "npcs": ["Ravi", "Nima"]
}
```

This allows the game engine to use either the parsed text tags or the structured metadata, depending on its parsing strategy.

## Editing Examples

### Change the NPCs in a scene

Before:
```python
story.add_passage(
    name="meeting",
    text="The Keeper approaches...",
    npcs=["Keeper"],
)
```

After:
```python
story.add_passage(
    name="meeting",
    text="Ravi approaches...",
    npcs=["Ravi"],
)
```

### Add a background to a placeholder

Before:
```python
story.add_passage(
    name="shrine_visit",
    text="[PLACEHOLDER]",
)
```

After:
```python
story.add_passage(
    name="shrine_visit",
    text="The ancient shrine glows with bioluminescence...",
    background="shrine_ruins",
    npcs=["Saori"],
)
```

### Multi-location story branch

```python
# Market scene
story.add_passage(
    name="market_decision",
    text="You stand at a crossroads...",
    background="market_ruins",
    npcs=["Ravi", "Nima"]
)

# Branch 1: Follow underground
story.add_passage(
    name="underground_path",
    text="You descend into darkness...",
    background="underground_entrance",
    npcs=["Kaelen"]
)

# Branch 2: Go to shrine
story.add_passage(
    name="shrine_path",
    text="You climb toward the shrine...",
    background="shrine_ruins",
    npcs=["Saori"]
)
```

## Naming Conventions

### Backgrounds

Use snake_case with descriptive location names:
- `market_ruins` (not `MarketRuins` or `market-ruins`)
- `shelter_interior` (not `ShelterInterior`)
- `shrine_ruins` (not `templeRuins`)

### NPCs

Use proper case (as characters would be named):
- `Ravi` (not `ravi` or `RAVI`)
- `Nima` (not `nima`)
- `Kaelen` (not `kaelen`)

## Integration with Game Engine

The game engine (velinor-web) reads these fields to:

1. **Load visuals**
   - Background image from `velinor-web/public/assets/backgrounds/{background}.png`
   - NPC sprite from `velinor-web/public/assets/npcs/{npc}.png`

2. **Render UI**
   - Display background as scene backdrop
   - Show NPC portraits or character models
   - Position dialogue bubbles near the speaker

3. **Track relationships**
   - Record which NPCs player has met
   - Track dialogue history per NPC
   - Build relationship scores

4. **Enable features**
   - Some choices only appear if specific NPCs are present
   - Some scenes can't be entered without meeting an NPC first
   - Relationship-gated content

## Workflow

1. **Write your story** in `story_definitions.py`
2. **Add background/npcs** for each scene
3. **Run build**: `python build_story.py`
4. **Validate**: `python build_story.py --validate`
5. **Test in game**: Play through to verify characters/locations load correctly
6. **Iterate**: Edit, rebuild, test

## Next Steps

- [ ] Add all background assets to velinor-web
- [ ] Add NPC character portraits/models
- [ ] Test scene composition in game
- [ ] Verify NPC dialogue triggers correctly
- [ ] Expand to Acts 2-4 with new locations/NPCs

---

**Example: Complete Market Scene**

```python
# Marketplace opening
story.add_passage(
    name="market_arrival",
    text="""You emerge from the collapsed underpass into the Market District.
    The air is thick with silence. Dust hangs in the air as two figures 
    move across the plaza.""",
    is_start=True,
    background="market_ruins",
    npcs=[],  # No NPCs yet - you see them from afar
    tags=["marketplace", "act1"]
)

# NPC encounter
story.add_passage(
    name="meet_ravi_nima",
    text="""The dust clears. Two figures emerge: Ravi, warm-eyed and calm.
    Nima, sharp-gazed and cautious. "You carry something," Nima says.
    "A resonance. We felt it.\"""",
    background="market_ruins",
    npcs=["Ravi", "Nima"],
    tags=["marketplace", "act1", "npc_encounter"]
)

# Ravi path
story.add_passage(
    name="ravi_dialogue",
    text="""You move toward Ravi. His expression softens. "I've learned to 
    recognize it. People who listen." He extends a weathered hand.""",
    background="market_ruins",
    npcs=["Ravi", "Nima"],
    tags=["marketplace", "act1", "ravi_path"]
)
```

This gives the game engine everything it needs to render a complete, immersive scene composition!
