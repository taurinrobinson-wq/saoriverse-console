# Reorganization Quick Reference

**Use this during reorganization to track progress and run commands.**

---

## Phase 1: Analysis Commands

```bash
# Count tests
find . -name "test_*.py" -type f | wc -l

# Find voice code
find . -path "*spoken_interface*" -name "*.py" | sort

# Find response generation code
find . -type f \( -name "*response*" -o -name "*generator*" \) | grep -v __pycache__

# Check main imports
grep -l "emotional_os" *.py 2>/dev/null || echo "No imports in root"

# Create backup branch
git checkout -b refactor/reorganization-master
git tag pre-reorganization
```

---

## Phase 2: Create Directory Structure

```bash
# Core source structure
mkdir -p src/
mkdir -p tests/unit/
mkdir -p tests/integration/
mkdir -p tests/fixtures/
mkdir -p data/lexicons/
mkdir -p data/models/
mkdir -p data/fixtures/
mkdir -p scripts/data/
mkdir -p scripts/setup/
mkdir -p scripts/debug/
mkdir -p docs/archive/
mkdir -p config/

# Create __init__.py files
touch src/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch scripts/__init__.py
touch scripts/data/__init__.py
touch scripts/setup/__init__.py
touch scripts/debug/__init__.py
```

---

## Phase 3: Move Files Checklist

### Core Source Files (Create in src/)
- [ ] src/emotional_os.py (from emotional_os/)
- [ ] src/signal_parser.py (from parser/ or emotional_os/core/)
- [ ] src/response_generator.py (from main_response_engine.py)
- [ ] src/archetype_response_v2.py (from emotional_os/glyphs/)
- [ ] src/prosody_planner.py (from spoken_interface/)
- [ ] src/streaming_tts.py (from spoken_interface/)
- [ ] src/voice_interface.py (from spoken_interface/voice_ui.py)
- [ ] src/audio_pipeline.py (from spoken_interface/)
- [ ] src/multimodal_fusion.py (new or from emotional_os/core/)
- [ ] src/privacy_layer.py (from emotional_os/privacy/)
- [ ] src/learning.py (from learning/ or emotional_os/learning/)

### Test Files (Move to tests/)
```bash
# Move all test_*.py from root to tests/
mv test_*.py tests/ 2>/dev/null || true

# Organize by module
mv tests/test_emotional_os.py tests/unit/ 2>/dev/null || true
mv tests/test_signal_parser.py tests/unit/ 2>/dev/null || true
# ... etc for each test
```

### Data Files
```bash
# Consolidate data
mkdir -p data/lexicons
mkdir -p data/models

# Move lexicon data
mv *lexicon*.json data/lexicons/ 2>/dev/null || true
mv *glyph*.json data/ 2>/dev/null || true

# Move database
mv *.db data/ 2>/dev/null || true
```

### Scripts Organization
```bash
# Data processing scripts
mv scripts/download*.py scripts/data/ 2>/dev/null || true
mv scripts/migrate*.py scripts/data/ 2>/dev/null || true
mv scripts/export*.py scripts/data/ 2>/dev/null || true

# Setup scripts
mv scripts/init*.py scripts/setup/ 2>/dev/null || true
mv scripts/seed*.py scripts/setup/ 2>/dev/null || true

# Debug scripts
mv scripts/inspect*.py scripts/debug/ 2>/dev/null || true
mv scripts/debug*.py scripts/debug/ 2>/dev/null || true
mv scripts/trace*.py scripts/debug/ 2>/dev/null || true
```

---

## Phase 4: Verify Imports

Create `tools/import_checker.py`:
```bash
cat > tools/import_checker.py << 'EOF'
"""Verify all imports work."""
import sys

def check():
    errors = []
    
    try:
        from src import EmotionalOS
        print("✅ EmotionalOS imports")
    except Exception as e:
        errors.append(f"❌ EmotionalOS: {e}")
    
    try:
        from src import ArchetypeResponseGeneratorV2
        print("✅ ArchetypeResponseGeneratorV2 imports")
    except Exception as e:
        errors.append(f"❌ ArchetypeResponseGeneratorV2: {e}")
    
    try:
        from src import VoiceInterface
        print("✅ VoiceInterface imports")
    except Exception as e:
        errors.append(f"❌ VoiceInterface: {e}")
    
    try:
        from src import privacy_layer
        print("✅ privacy_layer imports")
    except Exception as e:
        errors.append(f"❌ privacy_layer: {e}")
    
    try:
        from src import learning
        print("✅ learning imports")
    except Exception as e:
        errors.append(f"❌ learning: {e}")
    
    if errors:
        for error in errors:
            print(error)
        return False
    
    print("\n✅ All imports successful!")
    return True

if __name__ == "__main__":
    sys.exit(0 if check() else 1)
EOF
```

Run it:
```bash
python tools/import_checker.py
```

---

## Phase 5: Create Entry Point

Create `app.py`:
```bash
cat > app.py << 'EOF'
"""
SaoriVerse Console - FirstPerson
Streamlit entry point.

Run: streamlit run app.py
"""

import streamlit as st
from src import EmotionalOS, ArchetypeResponseGeneratorV2

st.set_page_config(
    page_title="FirstPerson",
    page_icon="🧠",
    layout="wide",
)

def init_session():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.emotional_os = EmotionalOS()
        st.session_state.response_gen = ArchetypeResponseGeneratorV2()
        st.session_state.conversation = []

def main():
    init_session()
    st.title("🧠 FirstPerson")
    st.markdown("A private space for emotional processing and growth")
    
    user_input = st.text_input("What's on your mind?")
    if user_input:
        signal = st.session_state.emotional_os.parse_input(user_input)
        response = st.session_state.response_gen.generate(user_input)
        st.write("**Response:**")
        st.write(response)

if __name__ == "__main__":
    main()
EOF
```

---

## Phase 6: Test Everything

```bash
# Test imports
python tools/import_checker.py

# Test with pytest
pytest tests/unit/ -v --tb=short

# Test with integration
pytest tests/integration/ -v --tb=short

# Test Streamlit launch
streamlit run app.py
# Then: Ctrl+C to stop
```

---

## Phase 7: Cleanup

```bash
# Archive old structure
mkdir -p archive/old_structure/
mv emotional_os/ archive/old_structure/ 2>/dev/null || true
mv parser/ archive/old_structure/ 2>/dev/null || true
mv local_inference/ archive/old_structure/ 2>/dev/null || true

# Remove old entry points
rm -f main_v2.py main_v2_simple.py start.py

# Archive old docs (keep README, CONTRIBUTING, docs/)
mkdir -p docs/archive/
for file in *.md; do
    if [[ "$file" != "README.md" && "$file" != "CONTRIBUTING.md" ]]; then
        mv "$file" docs/archive/" 2>/dev/null || true
    fi
done
```

---

## Phase 8: Commit

```bash
# Stage everything
git add -A

# Check what's being committed
git status

# Commit with detailed message
git commit -m "refactor: Complete codebase reorganization

- Move core logic to src/ with flat structure
- Consolidate tests under tests/unit/ and tests/integration/
- Create single app.py entry point for Streamlit
- Organize scripts by purpose (data/, setup/, debug/)
- Archive old structure and documentation
- All tests passing, all modules importable
- Ready for efficient development and deployment"

# Push to GitHub
git push origin refactor/reorganization-master
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
- Solution: Make sure you're running from the project root
- Run: `pwd` to verify location
- Fix: `cd /path/to/saoriverse-console` then retry

### "ImportError: cannot import name 'X' from 'src'"
- Solution: X doesn't exist in src/ yet or import path is wrong
- Fix: Check `src/__init__.py` has `from src.module import X`
- Verify: `python tools/import_checker.py` to diagnose

### "pytest: no tests found"
- Solution: Tests aren't in right location or pytest.ini is wrong
- Fix: Ensure `tests/conftest.py` exists
- Verify: `ls tests/test_*.py` shows test files
- Run: `pytest tests/ -v` (not `pytest` alone)

### "streamlit run app.py" hangs
- Solution: Import error or circular dependency
- Fix: Run `python tools/import_checker.py` first
- Debug: Run `python -c "from src import *"` to see errors

---

## One-Command Workflow After Reorganization

After everything is organized:

```bash
# Run all tests
pytest tests/ -v --cov=src

# Launch app for testing
streamlit run app.py

# Create new test
touch tests/unit/test_new_feature.py
# ... write test ...
pytest tests/unit/test_new_feature.py -v

# Commit changes
git add -A
git commit -m "feat: Add new feature"
git push origin feature/name
```

No more juggling between different directories or hunting for imports!

---

## File Count Before & After

**Before (Messy)**
- Root: 100+ files (test_*.py, main_*.py, *.md, *.py)
- Difficult to find anything

**After (Clean)**
- Root: ~20 files (app.py, requirements.txt, .gitignore, etc.)
- All code in src/
- All tests in tests/
- All scripts in scripts/
- All docs in docs/

---

## Quick Links During Work

- Master plan: docs/REORGANIZATION_MASTER_PLAN.md
- Current phase: Check the "Phase X" section above
- Import test: `python tools/import_checker.py`
- Run tests: `pytest tests/`
- Launch app: `streamlit run app.py`
- Commit work: Git commands in Phase 8

---

**Ready to start? Begin with Phase 1 commands and work through sequentially.**
