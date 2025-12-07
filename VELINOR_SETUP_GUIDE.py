"""
Velinor Game - Setup & Launch Guide
====================================

Complete instructions for installing and running the Velinor game.
"""

# ============================================================================
# INSTALLATION GUIDE
# ============================================================================

INSTALLATION_STEPS = """
# Velinor Game - Installation & Setup

## Requirements

- Python 3.8+ (3.10+ recommended)
- pip (Python package manager)
- Virtual environment (recommended)

## Step 1: Install Dependencies

```bash
# Navigate to project root
cd saoriverse-console

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\\Scripts\\activate

# Install required packages
pip install streamlit pillow
```

## Step 2: Verify Installation

```bash
# Check Streamlit installation
streamlit version

# Should output something like:
# Streamlit, version X.X.X
```

## Step 3: Run the Game

```bash
# From project root directory
streamlit run velinor_app.py

# Game will open in your browser at: http://localhost:8501
```

---

## Troubleshooting

### ModuleNotFoundError: No module named 'velinor'

**Solution:** Make sure you're running streamlit from the project root directory:
```bash
cd /path/to/saoriverse-console
streamlit run velinor_app.py
```

### Image files not found

**Solution:** Verify graphics files exist:
```bash
ls velinor/backgrounds/
ls velinor/npcs/
ls velinor/velinor_title_transparent.png
```

### Port already in use (Error: Port 8501 is already in use)

**Solution:** Use a different port:
```bash
streamlit run velinor_app.py --server.port 8502
```

### Virtual environment issues

**Solution:** Reinstall with clean environment:
```bash
# Deactivate current env (if active)
deactivate

# Remove old env
rm -rf venv/

# Create fresh env and reinstall
python -m venv venv
source venv/bin/activate
pip install streamlit pillow
```

---

## Optional: FirstPerson Integration

To enable dynamic dialogue generation:

1. Ensure FirstPerson module is available at: `src/emotional_os/deploy/core/firstperson.py`

2. Modify `velinor_app.py` or `engine/orchestrator.py`:
   ```python
   # Instead of:
   first_person_module=None
   
   # Use:
   from src.emotional_os.deploy.core.firstperson import FirstPersonOrchestrator
   first_person_module=FirstPersonOrchestrator()
   ```

3. Restart the app

---

## Game Controls

### Main Screen
- **Buttons** - Click to select a choice
- **Text Input** - Type your response, click "Submit Response"
- **Stats** - Player stats shown in right sidebar
- **Save/Load** - Access from menu

### Menu Options
- **Play** - Start a new game
- **Save/Load** - Save current game or load a save
- **Settings** - Change player name, enable multiplayer
- **About** - Information about the game

---

## Creating Custom Stories

1. **Option A: Use Twine 2 Editor**
   - Download Twine 2 from https://twinery.org/
   - Create your story visually
   - Export as JSON
   - Place in `velinor/stories/` directory
   - Update `velinor_app.py` story path

2. **Option B: Programmatically**
   ```python
   from velinor.engine import StoryBuilder
   
   story = StoryBuilder("My Story")
   story.add_passage("start", "Your story text...", is_start=True)
   story.add_choice("start", "A choice", "next_passage")
   story.export_json("my_story.json")
   ```

---

## Save Game Location

Save files are stored in: `velinor/saves/`

Each save is a JSON file with:
- Current passage ID
- Player stats
- Visited passages
- Dialogue history
- Full game log

---

## Advanced Configuration

### Modify Streamlit Settings

Create/edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#7c3aed"
backgroundColor = "#0a0e27"
secondaryBackgroundColor = "#1a1f3a"
textColor = "#e0e0e0"
font = "sans serif"

[client]
showErrorDetails = true

[logger]
level = "info"
```

### Custom Port & Server

```bash
streamlit run velinor_app.py \\
  --server.port 8501 \\
  --server.address localhost \\
  --client.showErrorDetails true
```

---

## Development Mode

For faster iteration during development:

```bash
# Enable fast refresh
streamlit run velinor_app.py --logger.level=debug

# Watch for changes and auto-reload
streamlit run velinor_app.py --server.runOnSave true
```

---

## Performance Tips

1. **Preload Images** - Images cache after first load
2. **Use Session State** - Game state persists during session
3. **Optimize Story** - Fewer passages = faster load

---

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect GitHub repo
4. Select `velinor_app.py`
5. Deploy!

### Deploy to Heroku

```bash
# Create Procfile
echo "web: streamlit run velinor_app.py" > Procfile

# Create requirements.txt
pip freeze > requirements.txt

# Deploy
heroku create your-app-name
git push heroku main
```

### Deploy to AWS / Google Cloud

See Streamlit docs for cloud deployment:
https://docs.streamlit.io/knowledge-base/tutorials/deploy

---

## Next Steps

1. ✅ Install and run the game
2. Test with the sample story
3. Connect FirstPerson orchestrator for dynamic dialogue
4. Create custom stories with Twine 2
5. Deploy to cloud platform
6. Invite friends to play multiplayer!

---

For more information, see:
- `TWINE_INTEGRATION_GUIDE.md` - Story system reference
- `STATUS.md` - Project status
- `README.md` - Project overview
"""


# ============================================================================
# QUICK START SCRIPTS
# ============================================================================

SETUP_SCRIPT_MACOS_LINUX = """#!/bin/bash
# Velinor Game - Quick Setup (macOS/Linux)

set -e

echo "🎮 Velinor Game Setup"
echo "===================="
echo ""

# Check Python
echo "✓ Checking Python..."
python3 --version

# Create virtual environment
echo "✓ Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip
pip install streamlit pillow

# Verify installation
echo "✓ Verifying installation..."
streamlit version

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the game:"
echo "  1. source venv/bin/activate"
echo "  2. streamlit run velinor_app.py"
echo ""
"""

SETUP_SCRIPT_WINDOWS = """@echo off
REM Velinor Game - Quick Setup (Windows)

echo 🎮 Velinor Game Setup
echo ====================
echo.

REM Check Python
echo ✓ Checking Python...
python --version

REM Create virtual environment
echo ✓ Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\\Scripts\\activate.bat

REM Install dependencies
echo ✓ Installing dependencies...
pip install --upgrade pip
pip install streamlit pillow

REM Verify installation
echo ✓ Verifying installation...
streamlit version

echo.
echo ✅ Setup complete!
echo.
echo To run the game:
echo   1. venv\\Scripts\\activate.bat
echo   2. streamlit run velinor_app.py
echo.
"""

RUN_SCRIPT_MACOS_LINUX = """#!/bin/bash
# Velinor Game - Run Script (macOS/Linux)

source venv/bin/activate
streamlit run velinor_app.py
"""

RUN_SCRIPT_WINDOWS = """@echo off
call venv\\Scripts\\activate.bat
streamlit run velinor_app.py
"""


# ============================================================================
# EXPORT SCRIPTS
# ============================================================================

if __name__ == "__main__":
    import os
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    
    # Create setup scripts
    setup_macos = project_root / "setup.sh"
    setup_windows = project_root / "setup.bat"
    run_macos = project_root / "run.sh"
    run_windows = project_root / "run.bat"
    
    # Write setup scripts
    setup_macos.write_text(SETUP_SCRIPT_MACOS_LINUX)
    setup_windows.write_text(SETUP_SCRIPT_WINDOWS)
    run_macos.write_text(RUN_SCRIPT_MACOS_LINUX)
    run_windows.write_text(RUN_SCRIPT_WINDOWS)
    
    # Make scripts executable (Unix)
    if hasattr(os, 'chmod'):
        os.chmod(setup_macos, 0o755)
        os.chmod(run_macos, 0o755)
    
    print("✅ Setup scripts created!")
    print(f"   - {setup_macos}")
    print(f"   - {setup_windows}")
    print(f"   - {run_macos}")
    print(f"   - {run_windows}")
    print("")
    print("To get started:")
    print("  macOS/Linux:  bash setup.sh")
    print("  Windows:      setup.bat")
