# SaoriVerse Console: Comprehensive Reorganization Master Plan

**Date**: December 3, 2025
**Goal**: Create a clean, modular structure that enables efficient testing, clear imports, and seamless Streamlit deployment
**Effort**: ~6-8 hours of reorganization
**Expected Outcome**: Zero import errors, all tests passing, single clear Streamlit entry point
##

## CURRENT STATE ANALYSIS

### Problems Identified

1. **Root Directory Cluttered**
   - 15+ test files in root (test_*.py)
   - 5+ demo/entry point files (main_v2.py, main_v2_simple.py, start.py)
   - 100+ documentation files (PHASE_13_*, PRIVACY_*, LEXICON_*, etc.)
   - 50+ scripts in scripts/ directory
   - Result: Import confusion, cleanup breaks dependencies

2. **Duplicate/Competing Module Structures**
   - `emotional_os/` (deep, nested)
   - `parser/` (3 files)
   - `src/` (2 files)
   - `local_inference/` (orphaned)
   - Result: Unclear which is canonical

3. **Tests Scattered**
   - Root directory: test_*.py
   - `tests/` directory: integration/, fixtures/, conftest.py
   - `tests/` directory: 60+ test files
   - Result: Unclear test discovery, pytest confused

4. **No Clear Entry Point**
   - main_v2.py (wrapper redirecting to core/main_v2.py)
   - main_v2_simple.py (emergency bypass)
   - start.py (unused?)
   - Result: Streamlit can't find right entry point

5. **Voice Systems Undocumented in Code**
   - `spoken_interface/` directory exists (complete!)
   - Never integrated into entry points
   - Tests exist but scattered
   - Result: Voice features exist but unreachable
##

## TARGET STATE

### Directory Structure (Clean & Logical)

```text
```

saoriverse-console/
│
├── app.py                          ← SINGLE Streamlit entry point (30 lines)
├── requirements.txt                ← All dependencies
├── pyproject.toml                  ← Package config
├── pytest.ini                      ← Test discovery
├── .env.example                    ← Environment template
│
├── src/                            ← Core application logic (FLAT, no nesting)
│   ├── __init__.py
│   ├── emotional_os.py             ← Main emotional OS logic
│   ├── signal_parser.py            ← Parse text to signals
│   ├── response_generator.py       ← Generate responses
│   ├── archetype_response_v2.py    ← Response type alternation
│   ├── prosody_planner.py          ← Emotion → voice mapping
│   ├── streaming_tts.py            ← Streaming TTS pipeline
│   ├── voice_interface.py          ← Voice I/O orchestration
│   ├── audio_pipeline.py           ← STT pipeline
│   ├── multimodal_fusion.py        ← Multimodal analysis
│   ├── privacy_layer.py            ← Privacy/encryption
│   └── learning.py                 ← Learning systems
│
├── data/                           ← All data files
│   ├── glyphs.json                 ← Glyph definitions
│   ├── lexicons/                   ← Lexicon files
│   │   ├── nrc_lexicon.json
│   │   ├── custom_lexicon.json
│   │   └── antonym_glyphs.json
│   ├── models/                     ← ML models
│   └── fixtures/                   ← Test data
│
├── tests/                          ← All tests (UNIFIED)
│   ├── conftest.py                 ← Pytest config
│   ├── test_*.py                   ← Root level tests moved here
│   ├── unit/                       ← Unit tests by module
│   │   ├── test_emotional_os.py
│   │   ├── test_signal_parser.py
│   │   ├── test_response_generator.py
│   │   ├── test_prosody_planner.py
│   │   ├── test_streaming_tts.py
│   │   ├── test_voice_interface.py
│   │   ├── test_privacy_layer.py
│   │   └── test_learning.py
│   ├── integration/                ← E2E tests
│   │   ├── test_full_e2e.py
│   │   ├── test_voice_to_response.py
│   │   └── test_multimodal.py
│   └── fixtures/                   ← Test helpers & data
│       ├── conftest.py
│       └── sample_data.py
│
├── scripts/                        ← Utility/admin scripts (ORGANIZED)
│   ├── README.md                   ← Script guide
│   ├── data/                       ← Data processing scripts
│   │   ├── download_nrc_lexicon.py
│   │   ├── migrate_glyphs.py
│   │   └── export_glyphs.py
│   ├── setup/                      ← One-time setup scripts
│   │   ├── init_db.py
│   │   └── seed_data.py
│   └── debug/                      ← Debugging/inspection scripts
│       ├── inspect_glyphs.py
│       └── trace_imports.py
│
├── docs/                           ← Documentation (ORGANIZED)
│   ├── README.md                   ← Start here
│   ├── REORGANIZATION_MASTER_PLAN.md ← This file
│   ├── ARCHITECTURE.md             ← System architecture
│   ├── TESTING_GUIDE.md            ← How to run tests
│   ├── API_REFERENCE.md            ← Module reference
│   ├── DEPLOYMENT.md               ← Deployment guide
│   ├── guides/                     ← Implementation guides
│   │   ├── VOICE_INTERFACE_GUIDE.md
│   │   ├── PRIVACY_LAYER_GUIDE.md
│   │   ├── LEARNING_SYSTEM_GUIDE.md
│   │   └── MULTIMODAL_GUIDE.md
│   └── archive/                    ← Old reference docs
│       ├── PHASE_13_*.md
│       ├── PRIVACY_LAYER_*.md
│       └── LEXICON_*.md
│
├── config/                         ← Configuration files
│   ├── settings.py                 ← App settings
│   └── logging.conf                ← Logging config
│
├── tools/                          ← Development tools
│   ├── test_runner.py              ← Test suite runner
│   ├── coverage_report.py           ← Coverage analysis
│   └── import_checker.py            ← Verify imports work
│
├── .streamlit/
│   └── config.toml                 ← Streamlit config
│
└── .github/                        ← CI/CD
    └── workflows/
        └── tests.yml               ← Test workflow

```


##

## PHASE 1: ANALYSIS & PREPARATION (30 min)

### 1.1 Audit Current State

```bash


# Count tests
find . -name "test_*.py" -type f | wc -l

# Output: Test count by location

# Check imports
grep -r "from emotional_os" --include="*.py" | head -20

# Output: What's importing what

# Check entry points
grep -l "if __name__ == '__main__'" *.py

```text
```




### 1.2 Create Backup

```bash

# Create branch for reorganization
git checkout -b refactor/reorganization-master

# Tag current state
```text
```text
```



### 1.3 Document Dependencies
Create a dependency map showing:
- What imports what
- Where each module actually lives
- Which modules are used by Streamlit
- Which modules are voice-specific
- Which modules are privacy-specific
##

## PHASE 2: CREATE TARGET STRUCTURE (1-2 hours)

### 2.1 Create New Source Structure

```bash


# Create src/ with flat structure
mkdir -p src/
touch src/__init__.py

# Create core modules (move/consolidate existing code)
touch src/emotional_os.py          # Consolidate glyph + signal logic
touch src/signal_parser.py         # Parse inputs to signals
touch src/response_generator.py    # Generate responses
touch src/archetype_response_v2.py # Response alternation
touch src/prosody_planner.py       # TTS prosody planning
touch src/streaming_tts.py         # Streaming TTS integration
touch src/voice_interface.py       # Voice orchestration
touch src/audio_pipeline.py        # STT pipeline
touch src/multimodal_fusion.py     # Multimodal analysis
touch src/privacy_layer.py         # Privacy/encryption

```text
```




### 2.2 Create Test Structure

```bash

# Create tests/ with organization
mkdir -p tests/unit/
mkdir -p tests/integration/
mkdir -p tests/fixtures/

# Create test discovery
touch tests/__init__.py
touch tests/conftest.py             # Pytest configuration
```text
```text
```



### 2.3 Organize Data

```bash


# Consolidate data files
mkdir -p data/lexicons/
mkdir -p data/models/
mkdir -p data/fixtures/

# Move all glyph/lexicon data to data/
mv glyphs.db data/

```text
```




### 2.4 Organize Documentation

```bash

# Archive old docs
mkdir -p docs/archive/
mv docs/PHASE_13_*.md docs/archive/
mv docs/PRIVACY_LAYER_*.md docs/archive/
mv docs/LEXICON_*.md docs/archive/

# Create new guide structure
touch docs/ARCHITECTURE.md
touch docs/TESTING_GUIDE.md
```text
```text
```


##

## PHASE 3: CONSOLIDATE SOURCE CODE (2-3 hours)

### 3.1 Identify Code Locations

**Goal**: Find where each piece of core logic actually lives

```bash


# Find all emotional_os related files
find . -type f -name "*.py" -exec grep -l "emotional_os" {} \; | grep -v __pycache__ | sort

# Find all response generation code
find . -type f -name "*response*" -o -name "*generator*" | grep -v __pycache__

# Find all voice code

```text
```




### 3.2 Consolidate into src/

For each major component:

**emotional_os.py**
- Source: Merge from `emotional_os/core/`, `emotional_os/glyphs/`
- Keep: Glyph definitions, Gate system, emotional state representation
- Remove: Test code, debug code, old iterations
- Size target: < 500 lines (core logic only)

**signal_parser.py**
- Source: `emotional_os/core/signal_parser.py` (if exists) or `parser/signal_parser.py`
- Keep: Text → Signal conversion
- Add: Error handling, edge cases
- Size target: < 300 lines

**response_generator.py**
- Source: `main_response_engine.py`, `emotional_os/deploy/response_*.py`
- Keep: Core response generation logic (not templates, not UI)
- Remove: Streamlit code, UI logic
- Size target: < 400 lines

**archetype_response_v2.py**
- Source: ArchetypeResponseGeneratorV2 class and helpers
- Keep: Response type alternation, principle-based generation
- Remove: Streamlit integration
- Size target: < 300 lines

**prosody_planner.py**
- Source: `spoken_interface/prosody_planner.py`
- Keep: Glyph → Prosody mapping, guardrails
- Size target: < 400 lines

**streaming_tts.py**
- Source: `spoken_interface/streaming_tts.py`
- Keep: Full TTS pipeline with streaming
- Size target: < 600 lines

**voice_interface.py** (NEW - orchestration)
- Source: `spoken_interface/voice_ui.py` + new code
- Keep: High-level voice API for Streamlit
- Include: STT orchestration, TTS orchestration, error handling
- Size target: < 300 lines

**audio_pipeline.py**
- Source: `spoken_interface/audio_pipeline.py`
- Keep: STT pipeline, audio processing
- Size target: < 400 lines

**privacy_layer.py**
- Source: `emotional_os/privacy/`, `emotional_os/core/privacy*`
- Keep: Glyph encryption, privacy protocols, sanctuary mode
- Size target: < 300 lines

**learning.py**
- Source: `emotional_os/learning/`, learning module code
- Keep: Pattern learning, effectiveness tracking, reward model
- Size target: < 300 lines

**multimodal_fusion.py**
- Source: `emotional_os/core/multimodal*` if exists, new code
- Keep: Text+voice+facial congruence analysis
- Size target: < 250 lines

### 3.3 Create Clean Imports

**src/__init__.py**

```python
"""
SaoriVerse Console - Emotional OS Core

Exports all public APIs for use by UI layers (Streamlit, etc.)
"""

from src.emotional_os import EmotionalOS, GlyphSignals
from src.signal_parser import parse_input, extract_themes
from src.response_generator import generate_response
from src.archetype_response_v2 import ArchetypeResponseGeneratorV2
from src.voice_interface import VoiceInterface
from src.privacy_layer import encrypt_signals, decrypt_signals
from src.learning import LearningSystem

__all__ = [
    "EmotionalOS",
    "GlyphSignals",
    "parse_input",
    "extract_themes",
    "generate_response",
    "ArchetypeResponseGeneratorV2",
    "VoiceInterface",
    "encrypt_signals",
    "decrypt_signals",
    "LearningSystem",
```text
```text
```


##

## PHASE 4: CONSOLIDATE TESTS (1-2 hours)

### 4.1 Move Root Tests

```bash


# Move all test_*.py from root to tests/

```text
```




### 4.2 Organize by Module

Create `tests/unit/` matching `src/`:

```
tests/unit/
├── test_emotional_os.py        # Tests for emotional_os.py
├── test_signal_parser.py       # Tests for signal_parser.py
├── test_response_generator.py  # Tests for response_generator.py
├── test_archetype_response_v2.py
├── test_prosody_planner.py
├── test_streaming_tts.py
├── test_voice_interface.py
├── test_audio_pipeline.py
├── test_privacy_layer.py
├── test_learning.py
```text
```text
```



### 4.3 Create conftest.py

```python


# tests/conftest.py
import pytest
import sys
from pathlib import Path

# Add src to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Shared fixtures
@pytest.fixture
def sample_glyph():
    return {
        "glyph_name": "Euphoric Yearning",
        "gate": "Gate 5",
        "description": "Hopeful desire with presence"
    }

@pytest.fixture
def sample_signal():
    return {
        "voltage": 0.6,
        "tone": "Yearning",
        "attunement": 0.7,
        "certainty": 0.5,
        "valence": 0.3

```sql
```




### 4.4 Update pytest.ini

```ini
[pytest]

# tests/pytest.ini
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```text
```text
```


##

## PHASE 5: CREATE STREAMLIT ENTRY POINT (30 min)

### 5.1 Create Single app.py

**app.py** (at root)

```python

"""
SaoriVerse Console - FirstPerson
Streamlit entry point for emotional AI system with voice interface.

Run: streamlit run app.py
"""

import streamlit as st
from src import (
    EmotionalOS,
    ArchetypeResponseGeneratorV2,
    VoiceInterface,
)

# Page configuration
st.set_page_config(
    page_title="FirstPerson",
    page_icon="🧠",
    layout="wide",
)

def init_session():
    """Initialize session state."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.emotional_os = EmotionalOS()
        st.session_state.response_gen = ArchetypeResponseGeneratorV2()
        st.session_state.voice = VoiceInterface()
        st.session_state.conversation = []

def main():
    """Main Streamlit app."""
    init_session()

    st.title("🧠 FirstPerson")
    st.markdown("A private space for emotional processing and growth")

    # Text input
    with st.sidebar:
        st.header("💬 Text Chat")
        user_input = st.text_input("What's on your mind?")

        if user_input:
            # Parse emotional signal
            signal = st.session_state.emotional_os.parse_input(user_input)

            # Generate response
            response = st.session_state.response_gen.generate(user_input)

            # Display
            st.write("**Response:**")
            st.write(response)

    # Voice interface (optional)
    if st.sidebar.checkbox("🎤 Enable Voice"):
        st.info("Voice interface available")
        # Voice UI would go here

if __name__ == "__main__":

```text
```




### 5.2 Delete Competing Entry Points

```bash

# Remove old entry points (after backup)
rm main_v2.py
rm main_v2_simple.py
```text
```text
```


##

## PHASE 6: ORGANIZE SCRIPTS (30 min)

### 6.1 Create scripts/ README

```markdown


# Scripts Directory

Organization:
- `data/` - Data processing and migration scripts
- `setup/` - One-time setup scripts
- `debug/` - Debugging and inspection scripts

Usage:
cd scripts/
python -m data.download_nrc_lexicon
python -m setup.init_db

```text
```




### 6.2 Reorganize scripts/

```bash

# Create subdirectories
mkdir -p scripts/data/
mkdir -p scripts/setup/
mkdir -p scripts/debug/

# Create __init__.py files
touch scripts/__init__.py
touch scripts/data/__init__.py
touch scripts/setup/__init__.py
touch scripts/debug/__init__.py

# Move scripts to appropriate locations
mv scripts/download_nrc_lexicon.py scripts/data/
mv scripts/init_test_db.py scripts/setup/
mv scripts/inspect_glyphs.py scripts/debug/

```text
```text
```


##

## PHASE 7: VERIFY & TEST (1-2 hours)

### 7.1 Test Imports

Create `tools/import_checker.py`:

```python

"""Verify all imports work correctly."""
import sys
from pathlib import Path

def test_imports():
    """Test that all core imports work."""
    try:
        from src import EmotionalOS, ArchetypeResponseGeneratorV2
        from src import VoiceInterface, privacy_layer
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()

```text
```




Run it:

```bash
```text
```text
```



### 7.2 Run Unit Tests

```bash


# Run specific test module
pytest tests/unit/test_emotional_os.py -v

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage

```text
```




### 7.3 Run Integration Tests

```bash

# E2E test
pytest tests/integration/test_full_e2e.py -v

# All integration tests
```text
```text
```



### 7.4 Launch Streamlit

```bash


# Should work with single entry point
streamlit run app.py

# Verify in browser

```text
```



##

## PHASE 8: CLEANUP & COMMIT (30 min)

### 8.1 Archive Old Files

```bash

# Create archive directory
mkdir -p archive/old_structure/

# Move old directories
mv emotional_os archive/old_structure/
mv parser archive/old_structure/
mv local_inference archive/old_structure/

# Move old documentation
mv *.md archive/old_docs/ 2>/dev/null || true

```sql
```sql
```



### 8.2 Update Root Files

**requirements.txt** - Clean list of all dependencies:

```

streamlit>=1.28.0
faster-whisper>=0.10.0
librosa>=0.10.0
TTS>=0.21.0
pydantic>=2.0
python-dotenv>=1.0

```text
```




**.gitignore** - Ensure it ignores build artifacts:

```
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
.streamlit/
.env
*.log
build/
dist/
```text
```text
```



### 8.3 Verify No Broken Imports

```bash

```text
```




### 8.4 Commit Reorganization

```bash
git add -A
git commit -m "refactor: Complete codebase reorganization

- Move core logic to src/ with flat structure (no deep nesting)
- Consolidate all tests under tests/ with unit/ and integration/ organization
- Create single app.py entry point for Streamlit
- Organize scripts/ by purpose (data/, setup/, debug/)
- Archive old structure and documentation
- Update imports and dependencies
- All tests passing, all modules importable
- Ready for efficient development and deployment"

```text
```text
```


##

## PHASE 9: DOCUMENTATION UPDATE (30 min)

### 9.1 Create ARCHITECTURE.md

Document:
- How modules relate to each other
- Data flow through the system
- Import dependencies
- When to use each module

### 9.2 Create TESTING_GUIDE.md

Document:
- How to run tests
- How to write new tests
- Test organization
- Coverage targets

### 9.3 Create API_REFERENCE.md

Document:
- Public APIs for each module
- Function signatures
- Error handling

### 9.4 Update README.md

Add:
- Quick start (one command to run: `streamlit run app.py`)
- Project structure overview
- Link to docs/
##

## FINAL CHECKLIST

### Structure ✓
- [ ] `src/` contains all core logic (flat, no nesting)
- [ ] `tests/` contains all tests (unit/ and integration/)
- [ ] `data/` contains all data files
- [ ] `docs/` contains current documentation
- [ ] `scripts/` organized by purpose
- [ ] `app.py` is single Streamlit entry point

### Imports ✓
- [ ] `from src import ...` works everywhere
- [ ] No circular dependencies
- [ ] All tests import successfully
- [ ] Streamlit imports work

### Tests ✓
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Test discovery works: `pytest tests/`
- [ ] Coverage report available: `pytest --cov=src`

### Streamlit ✓
- [ ] `streamlit run app.py` launches without errors
- [ ] Can import all core modules
- [ ] Voice interface available if enabled
- [ ] No warnings about missing modules

### Documentation ✓
- [ ] ARCHITECTURE.md written
- [ ] TESTING_GUIDE.md written
- [ ] API_REFERENCE.md written
- [ ] README.md updated
- [ ] Old docs archived but accessible
##

## ROLLBACK PLAN

If something breaks during reorganization:

```bash


# Revert to backup
git checkout pre-reorganization

# Or reset current branch
git reset --hard origin/main
git branch -D refactor/reorganization-master

```


##

## ESTIMATED TIMELINE

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Analysis & Preparation | 30 min | Planning |
| 2 | Create Target Structure | 1-2 hrs | Pending |
| 3 | Consolidate Source Code | 2-3 hrs | Pending |
| 4 | Consolidate Tests | 1-2 hrs | Pending |
| 5 | Create Entry Point | 30 min | Pending |
| 6 | Organize Scripts | 30 min | Pending |
| 7 | Verify & Test | 1-2 hrs | Pending |
| 8 | Cleanup & Commit | 30 min | Pending |
| 9 | Documentation | 30 min | Pending |
| **Total** | | **6-8 hrs** | |
##

## SUCCESS METRICS

After reorganization, you should be able to:

1. ✅ Run `streamlit run app.py` with zero errors
2. ✅ Run `pytest tests/` with all tests passing
3. ✅ Run `python tools/import_checker.py` with success
4. ✅ Import any module with `from src import X`
5. ✅ Add new tests to tests/unit/ or tests/integration/
6. ✅ Find any piece of code in 30 seconds
7. ✅ Onboard new developer in < 10 minutes
8. ✅ Deploy to cloud with single command
9. ✅ No "cleanup" runs needed anymore
10. ✅ Root directory has < 20 files (app.py, requirements.txt, docs/, src/, tests/, etc.)
##

## NEXT STEPS

1. **Review this plan** - Make sure structure matches your vision
2. **Create backup** - `git checkout -b refactor/reorganization-master`
3. **Follow phases 1-9 in order** - Don't skip steps
4. **Test at each phase** - Verify imports and tests work
5. **Commit frequently** - Don't lose work if something breaks
6. **Update CI/CD** - Ensure GitHub Actions uses new structure
##

## QUESTIONS TO ANSWER BEFORE STARTING

1. **Voice integration**: Should voice be optional or core? (Currently: optional)
2. **Data location**: Keep glyphs.json in root or move to data/? (Currently: recommending data/)
3. **Config files**: Should settings live in config/ or at root? (Currently: recommending config/)
4. **Documentation**: Keep 100+ old docs or archive them? (Currently: recommending archive/)
5. **Dependencies**: Do all packages in requirements.txt still needed? (Action: Audit)

**Answer these and you're ready to start.**
