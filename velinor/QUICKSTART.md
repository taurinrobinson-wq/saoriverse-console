# Velinor Marketplace Scenes - Quick Start Guide

## 🚀 Running the Test Interface

```bash
cd /workspaces/saoriverse-console
```text

```text
```


Then open your browser to the provided URL (usually `http://localhost:8501`).

##

## 📖 What You'll See

1. **Welcome Screen** (first load)
   - Enter your character name
   - Click "🚀 Start the Sequence"

2. **Scene 1: Marketplace Arrival**
   - Ambient intro to the city
   - Auto-advances with Continue button
   - Shows glyph resonance

3. **Scene 2: Ravi Encounter**
   - Welcoming NPC appears
   - Choose dialogue response
   - Watch trust increase (0-25%)

4. **Scene 3: Nima Encounter**
   - Mistrusting NPC challenges you
   - Different dialogue options
   - Trust increases slower (5-15%)

5. **Scene 4: Collapse Event**
   - Background changes to show destruction
   - NPCs react (or don't react)
   - Player responds to chaos

6. **Scene 5: Map Introduction**
   - Learn to navigate the marketplace
   - Map mechanics explained
   - Final dialogue choice

##

## 🎮 Controls

**In-Scene:**

- **Continue** button: advances through scene states
- **Dialogue Option buttons**: select your response
- **Next/Previous buttons** (sidebar): skip between scenes

**Sidebar:**

- **Player Stats**: name and NPC trust percentages
- **Scene Navigation**: current position in sequence
- **Dialogue History**: expandable, shows all choices made

##

## 📊 Understanding the System

### Scene States

Each scene progresses through: **DISTANT** → **APPROACH** → **CLOSE** → **DIALOGUE** → **CHOICES**

### Trust System

- **Initial**: Ravi starts at 0%, Nima at 0%
- **Per Choice**: +5% to +25% depending on option
- **Maximum**: 100%
- **Effect**: (Higher trust unlocks deeper dialogue later)

### Glyphs

Emotional resonance indicators that appear below narration:

- `[Esḧ]` = Sacred witness
- `[Cinarä̈]` = Invoked beloved
- `[Brethielï̈]` = Breath as guide
- `[Thalen̈]` = Longing
- `[Aelitḧ]` = Stillness/Witness
- `[Querrä]` = Inquiry
- `[Ruuñ]` = Collapse
- `[Sha'rú]` = Repair/Adaptation

##

## 🖼️ What You Need to Add

### Background Images

Create these in `velinor/backgrounds/`:

- `marketplace_intact_distant.png` - Far view of marketplace
- `marketplace_intact_close.png` - Close-up of marketplace
- `marketplace_collapsed_close.png` - After collapse

### Foreground Images (NPCs)

- `ravi_distant.png` - Ravi far away (small, low opacity)
- `ravi_close.png` - Ravi nearby (larger, full opacity)
- `nima_distant.png` - Nima far away
- `nima_close.png` - Nima nearby

**Note:** Right now the app uses placeholder paths. Images are optional for testing the flow.

##

## 🔧 Adding New Scenes

Edit `velinor/engine/marketplace_scenes.py`:

```python

@staticmethod
def build_my_new_scene() -> SceneModule:
    return SceneModule(
        scene_id="marketplace_my_scene_01",
        npc_name="Some NPC",
        npc_archetype="welcoming",  # or "mistrusting", "oracle"

        narration_distant="What they see from far away...",
        narration_close="What they see up close...",
        npc_dialogue="What the NPC says...",

        assets=SceneAssets(
            background_distant="velinor/backgrounds/bg_distant.png",
            background_close="velinor/backgrounds/bg_close.png",
            foreground_distant="velinor/backgrounds/npc_distant.png",
            foreground_close="velinor/backgrounds/npc_close.png",
        ),

        player_options=[
            DialogueOption(
                text="First choice",
                glyph_triggers=["Querrä"],
                npc_response="NPC's response to this choice",
                trust_modifier=0.1
            ),
            DialogueOption(
                text="Second choice",
                glyph_triggers=["Thalen̈"],
                npc_response="Different response",
                trust_modifier=0.15
            ),
        ],

        glyph_distant=["Esḧ"],
        glyph_close=["Querrä", "Cinarä̈"],
    )

# Add to sequence at bottom:
@staticmethod
def get_sequence() -> List[SceneModule]:
    return [
        # ... existing scenes
        MarketplaceSceneSequence.build_my_new_scene(),  # ADD HERE

```text

```

Then restart the test app and navigate to your new scene!

##

## 📚 Documentation Files

After running scenes, check these design docs to understand the system deeper:

- **01_player_backstory.md** - Who the player is, why they're here
- **02_marketplace_npc_system.md** - How NPCs work, trust mechanics
- **03_scene_modules.md** - Architecture and template reference
- **04_collapse_mechanics.md** - How dynamic events work
- **05_npc_reaction_library.md** - Reusable dialogue banks

Location: `/workspaces/saoriverse-console/velinor/markdowngameinstructions/`

##

## 🐛 Troubleshooting

**"Image not found" warnings:**

- This is normal if you haven't created the PNG assets yet
- The app still works; it just shows text

**Scenes not advancing:**

- Click "Continue" button to move between states
- Once at "CHOICES" state, click a dialogue option

**Trust not updating:**

- Trust only updates when you select a dialogue option
- Check sidebar stats after making a choice
- Different NPCs have different trust modifiers

**Dialogue history empty:**

- History only records choices from dialogue options
- Auto-advance scenes (intro) don't add to history

##

## 📖 Next Steps

1. **Test the flow** (now!)
   - Run `streamlit run velinor_scenes_test.py`
   - Make different choices, see trust change
   - Review dialogue history

2. **Create background images**
   - Design marketplace from distance and close-up
   - Create collapsed version showing destruction
   - Ensure consistent perspective/vanishing points

3. **Create NPC foreground images**
   - Design Ravi and Nima characters
   - Create "distant" and "close" variants
   - Size for proper layering (distant smaller, close larger)

4. **Add new scenes**
   - Follow template above
   - Build NPCs you designed in documentation
   - Add to sequence and test

5. **Integrate with main app**
   - Import scene system into `velinor_app.py`
   - Create marketplace chapter/quest that uses scenes
   - Display player choices' effects on later story

##

## 💡 Pro Tips

**For Quick Testing:**

- Use `Previous/Next` buttons in sidebar to jump between scenes
- Check sidebar stats to see real-time trust changes
- Review dialogue history to see all your choices

**For Content Development:**

- Write multiple dialogue variants for each NPC response
- Use trust modifiers strategically (high trust for insight, low for testing)
- Glyphs should match emotional tone of the scene

**For Visual Design:**

- Keep background perspectives consistent between distant/close
- Show clear depth (distance) in distant images, detail in close
- Use lighting/atmosphere to set mood

**For Story Design:**

- Each scene should have 2-4 player options (not 1, too linear; not 5+, overwhelming)
- Options should feel meaningfully different
- Consequences (trust changes) should be visible and matter

##

## 🎯 Quick Reference

| File | Purpose |
|------|---------|
| `velinor_scenes_test.py` | Main test app - run this |
| `velinor/engine/scene_manager.py` | Core scene engine (SceneRenderer, SceneModule) |
| `velinor/engine/marketplace_scenes.py` | 5-scene marketplace sequence |
| `velinor/markdowngameinstructions/01-05_*.md` | Design documentation |
| `velinor/IMPLEMENTATION_SUMMARY.md` | Full technical documentation |

##

## ✨ You're Ready

Everything is built and committed to git. Just:

```bash

streamlit run velinor_scenes_test.py

```

Have fun exploring the marketplace! 🎮

---

# 🌒 Velinor Streamlit Prototype - Full Game Implementation

## New: Complete Streamlit Implementation

A fully functional Streamlit version of **Velinor: Remnants of the Tone** with:

- **Dynamic Scene Rendering** - Background + NPC overlay + dialogue
- **Emotional OS (TONE)** - Track Courage, Wisdom, Empathy, Resolve, Resonance
- **Glyph System** - Collect and use glyphs to unlock emotional chambers
- **Chamber Mechanics** - Simple click-based battles and glyph acquisition
- **NPC Perception** - Track trust, affinity, understanding for each NPC
- **Skills & Dialogue** - Unlockable abilities that gate special branches

## Quick Start

### 1. Install Dependencies

```bash
pip install -r velinor/requirements_streamlit.txt
```

### 2. Run the Game

```bash
streamlit run velinor/streamlit_app.py
```

Opens at `http://localhost:8501`

### 3. Validate Everything Works

```bash
python -m pytest velinor/test_streamlit_integration.py -v
```

All 8 tests should pass ✅

## Game Modes

### Narrative Mode (default)
- Read dialogue and make choices
- Each choice updates TONE and NPC perception
- Progress through story arcs

### Glyph Input Mode (at chamber doors)
- Select 4 glyphs from your collection
- See next set of 4 glyphs
- Enter the chamber

### Chamber Mode (glyph beast encounter)
- Click "Attack" button repeatedly
- At 15 attacks, obtain the glyph
- Return to narrative

### Special Action (fifth button)
- Invoke glyphs on NPCs to unlock emotional dialogue
- Update NPC perception deeply
- Discover hidden story branches

## Sidebar Dashboard

Always visible on the right:

**🎼 TONE** - Five emotional stats
- 🟢 Courage, Wisdom, Empathy, Resolve, Resonance

**👁️ REMNANTS** - Deep trait tracking
- Truth vs Deception, Competence, Emotional Inference

**✨ GLYPHS** - Emotional stances
- 🟢 obtained (green), ⚫ locked (gray)

**🎯 SKILLS** - Unlockable abilities
- Gate special dialogue branches

**👥 NPC PERCEPTION** - Trust/Affinity/Understanding
- How each NPC perceives you

## Files

- **`streamlit_app.py`** - Main game loop (150 lines)
- **`streamlit_state.py`** - Game state management (450 lines)
- **`streamlit_ui.py`** - UI rendering (350 lines)
- **`STREAMLIT_README.md`** - Complete architecture guide
- **`test_streamlit_integration.py`** - Integration tests (150 lines)

## Key Features

### TONE System

Five dimensions of emotional resonance:

| Stat | Meaning |
|------|---------|
| Courage | Acting despite fear |
| Wisdom | Knowing what matters |
| Empathy | Feeling with others |
| Resolve | Commitment to path |
| Resonance | Harmonic balance |

Each choice applies effects like `{"courage": +0.15, "empathy": -0.1}`

### Glyphs as Emotional Verbs

Glyphs aren't items—they're stances you can invoke:

- **Sorrow** - Open vulnerability
- **Presence** - Be fully aware
- **Courage** - Move boldly
- **Wisdom** - Choose wisely
- **Trust** - Believe in connection
- **Transcendence** - Ultimate victory

### NPC Perception

Three dimensions per NPC (-1.0 to +1.0):

- **Trust** - Safety and reliability
- **Affinity** - Liking and comfort
- **Understanding** - Being known

Use glyphs and skills to shift perception, unlock special dialogue.

## Extending

### Add Story Scenes

In `stories/story_definitions.py`:

```python
story.add_passage(
    name="my_scene",
    text="*Dialogue here*",
    background="location",
    npcs=["Ravi"]
)

story.add_choice(
    from_passage_name="my_scene",
    choice_text="Choice text",
    to_passage_name="next_scene",
    tone_effects={"courage": 0.2},
    npc_resonance={"Ravi": 0.1}
)
```

### Add Glyphs

In `streamlit_state.py`:

```python
"MyGlyph": Glyph(
    name="MyGlyph",
    description="Does X",
    unlock_condition="scene_name",
    emotional_effect="courage",
    npc_resonance={"Ravi": 0.8}
)
```

### Add Skills

In `streamlit_state.py`:

```python
"My Skill": Skill(
    name="My Skill",
    description="Unlocks special dialogue",
    dialogue_banks=["scene1", "scene2"]
)
```

## Architecture

```
Streamlit App
    ↓
[Session State] ← [Game State] ← [UI Components]
    ↓                  ↓
[Orchestrator] ← [Story Engine]
    ↓
[Emotional OS] → [NPC System]
```

**Data Flow:**
1. Player clicks button
2. Handler updates `game_state` (TONE, glyphs, NPC perception)
3. UI re-renders with new state
4. Sidebar shows live updates

## Testing

Run integration tests:

```bash
python -m pytest velinor/test_streamlit_integration.py -v
```

Validates:
- ✅ Story building (14 passages)
- ✅ Game state initialization
- ✅ Tone effects
- ✅ Glyph operations
- ✅ NPC perception
- ✅ UI components
- ✅ Game engine
- ✅ Serialization

## Limitations (By Design)

- **No animations** - Fight loop is click-based (fast prototyping)
- **No images** - Placeholders for backgrounds/overlays
- **Text-based UI** - Upgrade to React later
- **Single-player** - Multiplayer in future version
- **5-button limit** - Forces clear UI design
- **Gray/green glyphs** - Instant feedback without rendering

## Next Steps

1. **Play through story** - Test all branches
2. **Tune fight mechanics** - Adjust attack count
3. **Add more scenes** - Expand Act 2 & 3
4. **Implement saving** - Wire up persistence
5. **Port to React** - Build final cinematic version

See `STREAMLIT_README.md` for complete documentation.

