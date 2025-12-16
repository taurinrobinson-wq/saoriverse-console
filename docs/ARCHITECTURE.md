# SaoriVerse Console - Architecture Guide

**Date**: December 3, 2025
**Status**: Post-Reorganization (Phase 9)
##

## Overview

SaoriVerse Console is a modular emotional AI system built with clean separation of concerns. The reorganization (Phases 1-8) established a flat, discoverable structure that enables rapid development and testing.
##

## Directory Structure

```
saoriverse-console/
├── app.py                    # Single Streamlit entry point
├── requirements.txt          # Python dependencies
├── pytest.ini               # Test discovery config
├── README.md                # Project overview
├── CONTRIBUTING.md          # Contribution guidelines
│
├── src/                     # Core application logic (25 modules)
│   ├── __init__.py
│   ├── response_generator.py         # Main response orchestration
│   ├── signal_parser.py              # Text → emotional signals
│   ├── symbolic_tagger.py            # Input classification
│   ├── enhanced_response_composer.py # Multi-glyph response generation
│   ├── response_adapter.py           # Emotional response translation
│   ├── response_selector.py          # Response selection logic
│   ├── tone_adapters.py             # Tone adaptation system
│   ├── relational_memory.py         # Memory and persistence
│   ├── phase_modulator.py           # Phase detection
│   │
│   ├── voice_interface.py           # Voice I/O orchestration
│   ├── streaming_tts.py             # TTS pipeline
│   ├── audio_pipeline.py            # STT pipeline
│   ├── prosody_planner.py           # Prosody planning
│   │
│   ├── lexicon_learner.py           # Lexicon learning
│   ├── local_learner.py             # Local learning system
│   │
│   ├── encryption_manager.py        # Privacy/encryption
│   ├── data_encoding.py             # Data encoding
│   │
│   └── (plus 5 more utility modules)
│
├── tests/                   # All test suites (unified)
│   ├── conftest.py         # Pytest configuration
│   ├── unit/               # Unit tests (26 files)
│   │   ├── test_*.py
│   │   └── ...
│   ├── integration/        # Integration tests (11 files)
│   │   ├── test_*.py
│   │   └── ...
│   └── fixtures/           # Shared test data
│
├── data/                   # All data files
│   ├── glyphs/            # Glyph definitions
│   ├── lexicons/          # Lexicon data
│   ├── models/            # ML models
│   └── fixtures/          # Test fixtures
│
├── scripts/               # Organized utility scripts
│   ├── data/             # Data processing scripts
│   ├── debug/            # Debugging scripts
│   └── setup/            # Setup scripts
│
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # This file
│   ├── TESTING_GUIDE.md # Testing documentation
│   ├── API_REFERENCE.md # API documentation
│   ├── README.md         # Quick start
│   └── archive/          # Old reference docs
│
├── config/              # Configuration files
├── tools/               # Development tools
│   └── import_checker.py # Import verification
│
└── archive/             # Old code and documentation
    ├── old_structure/   # Original directories
    └── old_modules/     # Original scripts
```


##

## Core Module Interactions

### Text-to-Response Pipeline

```
user_input (text)
    ↓
symbolic_tagger.py          Tag input (symbolic tags)
    ↓
signal_parser.py            Extract emotional signals
    ↓
response_generator.py       Main orchestrator
    ├─→ phase_modulator.py          Detect phase
    ├─→ tone_adapters.py            Generate tone-adapted response
    ├─→ response_selector.py        Select response type
    ├─→ response_adapter.py         Adapt to user-facing language
    └─→ enhanced_response_composer.py  Compose multi-glyph response
    ↓
relational_memory.py        Store memory capsule
    ↓
response (text) → Streamlit UI
```



### Voice Pipeline

```
audio_input (mp3/wav)
    ↓
audio_pipeline.py           STT (speech-to-text)
    ↓
[same as text-to-response pipeline above]
    ↓
response (text)
    ↓
prosody_planner.py          Glyph → prosody mapping
    ↓
streaming_tts.py            Text-to-speech
    ↓
audio_output (mp3/wav)
```



### Learning Pipeline

```
user_input + response + feedback
    ↓
lexicon_learner.py          Extract patterns
    ↓
local_learner.py            Store learned patterns
    ↓
relational_memory.py        Persist patterns
```


##

## Key Modules Explained

### response_generator.py (Main Orchestrator)
- **Purpose**: Coordinates the entire response pipeline
- **Main Function**: `process_user_input(user_input, context=None) → str`
- **Flow**: Tags → Parses → Adapts → Composes → Stores
- **Uses**: All other response modules

### signal_parser.py
- **Purpose**: Convert text to emotional signals
- **Key Concepts**: Voltage, tone, attunement, certainty, valence
- **Output**: Structured signal dict for downstream modules

### enhanced_response_composer.py
- **Purpose**: Blend multiple glyphs into coherent responses
- **Algorithm**: Gate activation + tone blending + voltage weighting
- **Output**: Natural, multi-faceted response text

### voice_interface.py
- **Purpose**: High-level API for voice integration
- **Features**: STT orchestration, TTS orchestration, error handling
- **Used By**: Streamlit app for voice features

### relational_memory.py
- **Purpose**: Persist interaction memories for learning
- **Storage**: Local JSONL files (append-only)
- **Access**: Query by session, user, or time range
##

## Import Patterns

### In app.py (Streamlit entry point):

```python
from src import (
    process_user_input,
    DynamicResponseComposer,
    VoiceInterface,
)
```



### In internal modules:

```python
from src.signal_parser import parse_input
from src.relational_memory import store_capsule
```



### Key Constraint:
- **No circular imports** - src/ modules never import from app.py
- **Unidirectional imports** - Lower-level modules don't depend on higher-level UI
##

## Testing Architecture

### Unit Tests (tests/unit/)
- Test individual modules in isolation
- Mock external dependencies
- Fast execution (< 100ms per test)
- Run with: `pytest tests/unit/`

### Integration Tests (tests/integration/)
- Test module interactions
- Use real or fixture data
- Slower execution (can take seconds)
- Run with: `pytest tests/integration/`

### Test Discovery
- Pytest configuration in `pytest.ini`
- Shared fixtures in `tests/conftest.py`
- Auto-discovery of `test_*.py` files
##

## Deployment

### Single Streamlit Entry Point:

```bash
streamlit run app.py
```



### Environment Setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```



### CI/CD:
- GitHub Actions in `.github/workflows/`
- Runs tests on push to refactor/* branches
- Validates imports, runs test suite
##

## Module Dependencies (by layer)

### Layer 1: Input Processing
- `symbolic_tagger.py` (no dependencies on other modules)
- `signal_parser.py` (no dependencies on other modules)

### Layer 2: Response Generation
- `response_generator.py` (orchestrator)
- `response_selector.py` (uses signal_parser)
- `response_adapter.py` (uses signal_parser)
- `tone_adapters.py` (uses signal_parser)
- `enhanced_response_composer.py` (uses signal_parser)

### Layer 3: Persistence
- `relational_memory.py` (no core dependencies)
- `phase_modulator.py` (no core dependencies)

### Layer 4: Voice (Optional)
- `voice_interface.py` (orchestrator)
- `streaming_tts.py` (standalone)
- `audio_pipeline.py` (standalone)
- `prosody_planner.py` (uses signal_parser)

### Layer 5: Learning (Optional)
- `lexicon_learner.py` (standalone)
- `local_learner.py` (standalone)
##

## Future Improvements

1. **Type Hints**: Add comprehensive type annotations (Python 3.8+)
2. **API Documentation**: Generate API docs with Sphinx
3. **Performance Profiling**: Add timing metrics to critical paths
4. **Error Handling**: Standardize error handling across modules
5. **Configuration**: Move hardcoded values to config files
6. **Logging**: Structured logging with context propagation
##

## Quick Reference: Finding Things

| Looking for... | File | Location |
|---|---|---|
| Main entry point | app.py | root/ |
| Response generation | response_generator.py | src/ |
| Signal parsing | signal_parser.py | src/ |
| Voice interface | voice_interface.py | src/ |
| Memory/persistence | relational_memory.py | src/ |
| Tests | test_*.py | tests/unit/ or tests/integration/ |
| Test fixtures | conftest.py | tests/ |
| Data files | *.json, *.sql | data/ |
##

**For detailed testing information, see**: `docs/TESTING_GUIDE.md`
**For API reference, see**: `docs/API_REFERENCE.md`
