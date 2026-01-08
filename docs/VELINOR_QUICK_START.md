# 🎮 Velinor Game - Quick Start Guide

## Installation (Quick)

### macOS/Linux

```bash
bash setup.sh
source venv/bin/activate
```text

```text
```


### Windows

```cmd

python -m venv venv
venv\Scripts\activate.bat
pip install streamlit pillow

```text

```

The game will open at: **<http://localhost:8501>**

##

## What's New

### ✨ Graphics Integration

Your graphics files are fully integrated:

**Backgrounds** (15 locations):

- City Market, Mountains, Forest, Desert, Lake, Swamp, Underground, Bridge Pass
- 5 unique desert variations for different moments

**NPC Characters** (7 NPCs):

- Keeper, Saori, Sanor, Irodora, Tala, Safi & Rumi, Velinor (2 poses)

**UI Elements**:

- Transparent Velinor title logo for welcome screen

### 🎮 Streamlit UI Features

- **Full-screen backgrounds** for immersion
- **NPC portraits** that appear during conversations
- **Chat-style dialogue** with npc/player distinction
- **Dynamic stat display** showing Courage, Wisdom, Empathy, Resolve, Resonance
- **Dice roll results** with success/failure visualization
- **Save/Load system** with timestamped saves
- **Multiplayer support** with player customization
- **Responsive layout** - main story area + sidebar stats

##

## How to Play

1. **Click "Start New Game"** on the welcome screen
2. **Read the dialogue** - Story updates after each action
3. **Make choices** - Click buttons or type free-form responses
4. **Check your stats** - Right sidebar shows current values
5. **Watch dice rolls** - Skill checks show results
6. **Save your progress** - Use Save/Load from menu

### Controls

| Action | How |
|--------|-----|
| Select choice | Click button |
| Free-form input | Type in text box, click Submit |
| Save game | Menu → Save/Load → Save |
| Load game | Menu → Save/Load → Load |
| New game | Menu → Settings → Start New Game |
| Multiplayer | Menu → Settings → Enable, set player names |

##

## File Structure

```

saoriverse-console/
├── velinor_app.py              ← START HERE! Main game UI
├── setup.sh                    ← Run once: bash setup.sh
├── run.sh                      ← Run game: bash run.sh
├── requirements.txt            ← Python dependencies
│
└── velinor/
    ├── engine/
    │   ├── core.py             # Game engine
    │   ├── npc_system.py       # NPC dialogue
    │   ├── twine_adapter.py    # Story loader
    │   ├── orchestrator.py     # Game loop
    │   ├── assets_config.py    # Asset mapping
    │   └── __init__.py
    │
    ├── stories/
    │   └── sample_story.json   # Twine story
    │
    ├── backgrounds/            # 15 location images
    │   ├── city_market.png
    │   ├── forest.png
    │   ├── desert.png
    │   └── ...
    │
    ├── npcs/                   # 7 character images
    │   ├── velinor_eyesclosed.png
    │   ├── keeper.png
    │   ├── saori.png
    │   └── ...
    │
    ├── saves/                  # Auto-created for saves
    │
    ├── README.md               # Project overview
    ├── STATUS.md               # Current status
    ├── TWINE_INTEGRATION_GUIDE.md

```text
```text

```

##

## Creating Custom Stories

### Option 1: Twine 2 Editor (Recommended)

1. Download [Twine 2](https://twinery.org/)
2. Create story with visual editor
3. Export as JSON
4. Place in `velinor/stories/`
5. Update story path in `velinor_app.py`

### Option 2: Programmatically

```python


from velinor.engine import StoryBuilder

story = StoryBuilder("My Adventure") story.add_passage("start", "You awake in a strange place...",
is_start=True) story.add_choice("start", "Look around", "examine") story.add_choice("start", "Move
forward", "walk")

```text
```


### Story Markup Syntax

```
{background: location}    # Set background image
{npc: NPCName}           # NPC is speaking
{dice: d20+courage}      # Trigger dice roll
{multiplayer: true}      # Adapt for group
[[Choice text->passage]] # Link to next passage
```text

```text
```


##

## Troubleshooting

### "ModuleNotFoundError: No module named 'velinor'"

**Fix:** Run from project root:

```bash

cd /path/to/saoriverse-console

```text

```

### Images not loading

**Check paths:**

```bash

ls velinor/backgrounds/    # Should see 15+ images ls velinor/npcs/           # Should see 7+ images

```text
```text

```

### Port 8501 already in use

**Try different port:**

```bash


```text
```


### Virtual environment issues

**Fresh start:**

```bash
deactivate  # if in a venv
rm -rf venv/
```text

```text
```


##

## Advanced Setup

### Conda Environment (Alternative)

```bash

conda create -n velinor python=3.11
conda activate velinor

```text

```

### Docker (Optional)

```dockerfile

FROM python:3.12-slim WORKDIR /app COPY . . RUN pip install streamlit pillow

```text
```text

```

```bash


docker build -t velinor .

```text
```


### Cloud Deployment

**Streamlit Cloud (Free):**

1. Push to GitHub 2. Go to share.streamlit.io 3. Deploy from repo 4. Select `velinor_app.py`

**Heroku:**

```bash
git push heroku main
```


##

## Stats System

| Stat | Meaning | Use |
|------|---------|-----|
| **Courage** | Bravery, facing danger | Intimidate, confront, attack |
| **Wisdom** | Perception, understanding | Investigate, understand, sense |
| **Empathy** | Connection, emotion | Persuade, comfort, understand others |
| **Resolve** | Determination, persistence | Endure, resist, maintain focus |
| **Resonance** | Connection to the Tone | Find glyphs, hear echoes, understand story |

All stats start at 50 (neutral) and can go 0-100.

##

## Multiplayer

### Enable Multiplayer

1. Menu → Settings 2. Check "Multiplayer Mode" 3. Set number of players (2-4) 4. Enter each player's
name/ID 5. Start game

### How It Works

- Each player contributes to dialogue
- NPCs address the group collectively
- Responses adapt to group composition
- See other players' choices in sidebar
- Shared story progression

##

## First Session Tips

1. **Read everything** - Story has depth 2. **Try different choices** - Same choice changes dialogue
3. **Pay attention to stats** - They affect dice rolls 4. **Save often** - Especially before major
choices 5. **Play with multiplayer** - Different story with friends

##

## Next Steps

### For Players

1. ✅ Install and play sample story 2. Create custom stories in Twine 2 3. Invite friends for
multiplayer 4. Deploy game online

### For Developers

1. Connect FirstPerson orchestrator for dynamic dialogue 2. Implement inventory system 3. Add quest
tracking UI 4. Create achievement system 5. Build community features

##

## Important Files

| File | Purpose |
|------|---------|
| `velinor_app.py` | 🎮 Main game UI - START HERE |
| `setup.sh` | Installation script |
| `run.sh` | Launch game |
| `velinor/engine/core.py` | Game engine |
| `velinor/engine/twine_adapter.py` | Story loader |
| `velinor/engine/orchestrator.py` | Game loop |
| `velinor/stories/sample_story.json` | Example story |

##

## Support & Documentation

- 📖 **Full Guide:** `velinor/TWINE_INTEGRATION_GUIDE.md`
- 🏗️ **Architecture:** `velinor/TWINE_IMPLEMENTATION_COMPLETE.md`
- 📊 **Project Status:** `velinor/STATUS.md`
- 🎮 **Game Overview:** `velinor/README.md`

##

## System Requirements

- **Python:** 3.8+ (3.10+ recommended)
- **OS:** Windows, macOS, Linux
- **RAM:** 512MB minimum
- **Disk:** 100MB for installation + saves
- **Browser:** Any modern browser (Chrome, Firefox, Safari, Edge)

##

## Performance Notes

- First load: Graphics cache after initial load
- Session state: Game state persists during session
- Save files: Stored as JSON in `velinor/saves/`
- Large stories: 100+ passages work fine

##

## License

[Your License Here]

##

**Created:** December 6, 2025
**Status:** 🟢 Ready to Play!
**Version:** 1.0 - Streamlit UI Edition

##

## Enjoy

Welcome to Velinor. May you find truth in the Tone. ✨
