# Running the App with Python 3.12

## Problem

When clicking "Voice Mode", you see:
```
Voice recording unavailable - missing: faster-whisper, sounddevice
Install with: pip install faster-whisper sounddevice
```

**Root Cause:** The app is running with Python 3.13 (or another version), not Python 3.12 where the packages are installed.

---

## Solution: Use Python 3.12

All packages are installed in Python 3.12. You just need to start Streamlit with Python 3.12 specifically.

### Option 1: Command Line (Recommended)

```powershell
py -3.12 -m streamlit run app.py
```

Then open http://localhost:8501

### Option 2: Batch File

Double-click `run_app.bat` in the project directory.

### Option 3: PowerShell Script

```powershell
.\run_app.ps1
```

### Option 4: VS Code Task (Recommended if using VS Code)

1. Press `Ctrl+Shift+B` in VS Code
2. Select "Streamlit: Run with Python 3.12"
3. Streamlit will start with the correct Python version

---

## How to Verify You're Using Python 3.12

When the app starts, check the sidebar:

- ✅ **Shows "✓ Python 3.12.x"** - Correct! Voice mode will work
- ⚠️ **Shows "⚠️ Python 3.13.x"** or other - Wrong! Use the command above

---

## Quick Reference

| Task | Command |
|------|---------|
| Run app (Python 3.12) | `py -3.12 -m streamlit run app.py` |
| Run on different port | `py -3.12 -m streamlit run app.py --server.port 8502` |
| Check Python version | `py -3.12 --version` |
| List installed packages | `py -3.12 -m pip list` |
| Run tests | `py -3.12 -m pytest` |
| Install new package | `py -3.12 -m pip install package-name` |

---

## Why This Matters

The development machine has multiple Python versions:

- **Python 3.12** ← All audio packages installed here ✓
- **Python 3.13** ← Where Streamlit might default to ✗

When you run `streamlit run app.py`, it uses the default Python, which is often 3.13. But the audio packages (faster-whisper, sounddevice) are only installed in 3.12.

By using `py -3.12 -m streamlit run app.py`, you explicitly tell it to use Python 3.12.

---

## Permanent Fix (Optional)

To make Python 3.12 the default:

```powershell
# Check current default
py --version

# Set Python 3.12 as default (if needed)
# This requires manual registry edit or environment variable setup
```

For now, just use the `py -3.12` prefix to ensure you're using the correct version.

---

## Testing Voice Mode

Once running with Python 3.12:

1. Check sidebar - should show "✓ Python 3.12.x"
2. Enable "Voice Mode" toggle in sidebar
3. Click the microphone button
4. Speak your message
5. It will transcribe using faster-whisper
6. Response will be synthesized using pyttsx3

If you still see the missing packages error, the app is not using Python 3.12. Kill it and restart with the correct command.

---

## Files Created

New helper files in project root:

- `run_app.bat` - Windows batch launcher
- `run_app.ps1` - PowerShell launcher
- `.vscode/tasks.json` - VS Code task configuration

Use any of these to run the app with Python 3.12 guaranteed.
