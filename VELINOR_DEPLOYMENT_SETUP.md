# 🎮 Velinor Game - Deployment & Setup Guide

## Quick Local Setup

### Option 1: Automated Setup (Recommended)
```bash
cd /Volumes/My\ Passport\ for\ Mac/saoriverse-console
bash setup.sh
bash run.sh
```

**Game opens at:** http://localhost:8501

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install streamlit pillow

# Run the game
streamlit run velinor_app.py
```

---

## Integration with Your Glyph System

### Current Integration Status
✅ **FirstPerson hooks already in place** (line 556 of velinor_app.py)
- Game engine ready for FirstPerson orchestrator connection
- NPC system prepared for emotional analysis
- Glyph system placeholders ready

### To Enable FirstPerson Integration

#### Step 1: Update velinor_app.py
Modify the game initialization section to import and connect FirstPerson:

```python
# Around line 540-560 in velinor_app.py
from src.emotional_os.deploy.core.firstperson import FirstPersonOrchestrator, AffectParser

# Then when creating orchestrator:
orchestrator = VelinorTwineOrchestrator(
    game_engine=engine,
    story_path=str(story_path),
    first_person_module=FirstPersonOrchestrator("game_npc", "velinor_session"),  # ← Add this
    npc_system=npc_system
)
```

#### Step 2: Environment Variables (Secrets)
For Streamlit Cloud deployment, add to `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml
[firstperson]
module_path = "src.emotional_os.deploy.core.firstperson"
session_name = "velinor_game"
enable_affect_analysis = true

[glyph]
database_url = "your_supabase_or_db_url"
enable_persistence = true
glyph_collection_enabled = true

[deployment]
environment = "production"  # or "development"
debug_mode = false
```

#### Step 3: Session Secrets (for Streamlit Cloud)
1. Go to your app's Settings on Streamlit Cloud
2. Click "Secrets"
3. Add the same TOML content above

### For Local Development (No Secrets Needed)
The game works perfectly without FirstPerson/Glyph integration:
- Full game playable standalone
- All story functionality works
- Stats and mechanics fully functional
- Perfect for testing before integration

---

## Running Velinor

### Local Testing
```bash
# Terminal 1: Start the app
streamlit run velinor_app.py

# App runs at http://localhost:8501
# Press Ctrl+C to stop
```

### With FirstPerson Connected
```bash
# If FirstPerson is enabled, additional debug info will show
streamlit run velinor_app.py --logger.level=debug
```

---

## Deployment Options

### Option A: Local Only (Recommended for Development)
**Pros:**
- No secrets needed
- Fast iteration
- Full offline gameplay
- Can integrate FirstPerson locally

**Setup:** Run `bash run.sh`

---

### Option B: Streamlit Cloud (Free)
**Steps:**
1. Push to GitHub (already done - `feature/velinor-remnants-of-tone` merged to main)
2. Go to share.streamlit.io
3. Create new app from GitHub
4. Select `saoriverse-console` repo
5. Set main file to `velinor_app.py`
6. Add secrets if integrating FirstPerson

**Pros:**
- Free hosting
- Easy updates (auto-sync from GitHub)
- Public URL sharing

**Cons:**
- Limited compute resources
- Slow cold starts
- Need secrets for FirstPerson

---

### Option C: Docker Deployment
**Dockerfile already compatible:**
```bash
docker build -t velinor-game .
docker run -p 8501:8501 velinor-game
```

---

## Secrets Configuration

### Do You Need Secrets?

| Scenario | Secrets Required? | What For? |
|----------|------------------|-----------|
| Local play (offline) | ❌ No | Game works standalone |
| Local with FirstPerson | ⚠️ Optional | Only if FirstPerson needs DB access |
| Streamlit Cloud (no integration) | ❌ No | Game works as-is |
| Streamlit Cloud + FirstPerson | ✅ Yes | FirstPerson module needs config |
| Production with Glyphs | ✅ Yes | Database, auth, persistence |

### Current Status
✅ **Game is fully playable WITHOUT secrets**
- All mechanics work
- Save/load works
- Graphics display
- NPC system functions
- Multiplayer ready

### If Integrating with Glyph System Later

Add to `.streamlit/secrets.toml`:
```toml
# Glyph persistence
[glyph]
supabase_url = "https://your-project.supabase.co"
supabase_key = "your-anon-key"

# FirstPerson if needed
[firstperson]
api_key = "your-api-key"
session_scope = "velinor_game"

# Optional: Analytics
[analytics]
enabled = false
```

---

## What's Already Configured

✅ **Streamlit Config** (`.streamlit/config.toml`):
- Port: 8501
- Theme: Light mode with pink accent (#ff6b9d)
- Error details: Hidden for clean UI
- Toolbar: Viewer mode (no editing)
- Max upload: 200MB

✅ **Game Configuration**:
- 15 background locations
- 7 NPC characters
- Dice mechanics (d20 system)
- 5 player stats
- Save/load system
- Multiplayer support (2-4 players)

✅ **Assets**:
- All images in `velinor/backgrounds/` and `velinor/npcs/`
- Story in `velinor/stories/sample_story.json`
- Complete UI with light theme

---

## File Locations

```
saoriverse-console/
├── velinor_app.py              ← Main game app
├── setup.sh                    ← Install script
├── run.sh                       ← Launch script
├── .streamlit/
│   └── config.toml             ← Streamlit settings
├── velinor/
│   ├── engine/
│   │   ├── orchestrator.py     ← FirstPerson hook here (line 115)
│   │   └── npc_system.py       ← NPC integration point
│   ├── backgrounds/            ← 15 images
│   ├── npcs/                   ← 7 character images
│   └── stories/
│       └── sample_story.json
└── src/
    └── emotional_os/
        └── deploy/
            └── core/
                └── firstperson/  ← Import from here for integration
```

---

## Quick Commands

```bash
# Setup
bash setup.sh

# Run game
bash run.sh

# Manual run
streamlit run velinor_app.py

# Debug mode
streamlit run velinor_app.py --logger.level=debug

# Check version
streamlit --version

# Clear cache
rm -rf ~/.streamlit

# Deactivate venv
deactivate
```

---

## Status Check

```bash
# Check if Python dependencies installed
pip list | grep -E "streamlit|pillow"

# Check game files
ls -la velinor/engine/
ls -la velinor/backgrounds/
ls -la velinor/npcs/

# Test game imports
python3 -c "from velinor.engine import VelinorEngine; print('✓ Game ready')"
```

---

## For FirstPerson/Glyph Integration

When ready to integrate your emotional resonance system:

1. **NPC dialogue generation** - hooks in `velinor/engine/npc_system.py` line 19
2. **Game state analysis** - available via `orchestrator.process_player_action()`
3. **Glyph collection** - can be stored in `player.glyphs_collected` (player stats)
4. **Emotional analysis** - FirstPerson can analyze player choices via `player_input`

### Integration Points Ready
- ✅ FirstPerson import location (line 556)
- ✅ NPC system accepts FirstPerson module
- ✅ Game engine has hooks for external analysis
- ✅ Player stats include glyph tracking
- ✅ Session management ready for persistence

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `bash setup.sh` |
| Port 8501 in use | Change in config.toml or use `streamlit run velinor_app.py --server.port 8502` |
| Images not showing | Check `velinor/backgrounds/` and `velinor/npcs/` exist |
| Game crashes on start | Clear cache: `rm -rf ~/.streamlit` |
| FirstPerson import error | Update import path in velinor_app.py |
| Secrets not loading | Ensure `.streamlit/secrets.toml` is in .gitignore |

---

## Summary

**To Start Playing Right Now:**
```bash
cd /Volumes/My\ Passport\ for\ Mac/saoriverse-console
bash setup.sh
bash run.sh
```

**Secrets Required?** Only if integrating with FirstPerson/Glyph system

**Integration Ready?** Yes! Hooks already in place - just connect your modules

**Environment?** Local (offline) works perfectly; add secrets only for cloud deployment or FirstPerson integration
