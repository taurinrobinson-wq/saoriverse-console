# Developer Quick Start Guide

**Last Updated**: Phase 10 - Documentation Updates
**Project Status**: ✅ Fully Modularized & Organized

##

## 🚀 Quick Start (5 minutes)

### First Time Setup

```bash

# 1. Navigate to project
cd /workspaces/saoriverse-console

# 2. Install dependencies
pip install -r config/requirements.txt

# 3. Start the application
python core/start.py

# OR for Streamlit
```text

```text
```


### Project Structure at a Glance

```

root/
├── core/                 ← All essential Python code
├── docs/                 ← All documentation (guides, reports, archives)
├── data/                 ← All data files (glyphs, lexicons, analysis)
├── config/               ← Configuration & dependencies
├── emotional_os/         ← Modularized application core
├── tools/                ← Organized analysis/testing tools

```text

```

##

## 📂 Finding What You Need

### "I need to understand the project architecture"

→ **Start**: `docs/guides/MODULARIZATION_COMPLETE.md`
→ **Then**: `docs/INDEX.md` for navigation

### "I need to run the application"

→ **File**: `core/start.py` or `core/main_v2.py`
→ **Config**: `config/requirements.txt`

### "I need to understand the core response system"

→ **Files**:

- `core/main_response_engine.py` - Response pipeline
- `core/response_adapter.py` - Response translation
- `core/tone_adapters.py` - Tone adaptation

### "I need glyph system documentation"

→ **File**: `docs/guides/GLYPH_SYSTEM_AUDIT.md`
→ **Data**: `data/glyphs/`

### "I need analysis tools"

→ **Location**: `tools/analysis/`
→ **Examples**:

- Gate distribution analyzer
- Symbolic tagger
- Scenario reporting

### "I'm looking for logs/debugging info"

→ **Location**: `logs/`

### "I need deployment scripts"

→ **Location**: `scripts/`
→ **Files**: `deploy.sh`, `run_local.sh`

##

## 🔧 Core Python Files (core/)

All essential Python files are in `core/`:

| File | Purpose |
|------|---------|
| `start.py` | Railway deployment entry point |
| `main_v2.py` | Streamlit application entry point |
| `main_response_engine.py` | Core response pipeline orchestrator |
| `response_adapter.py` | Emotional response translation layer |
| `response_selector.py` | Response selection logic |
| `symbolic_tagger.py` | Input parsing & symbolic tagging |
| `tone_adapters.py` | Tone adaptation system |
| `enhanced_response_composer.py` | Response composition |
| `relational_memory.py` | Relational memory system |
| `glyph_generator.py` | Compatibility shim |
| `phase_modulator.py` | Compatibility shim |

### Importing from Core

```python


# Import from core/ directory
from core.main_response_engine import process_user_input from core.response_adapter import
translate_emotional_response from core.tone_adapters import generate_archetypal_response

# Or maintain backward compatibility with shims
from core.phase_modulator import detect_phase

```text
```text

```

##

## 📚 Documentation Organization (docs/)

### guides/

Design documents, project references, and analysis:

- `MODULARIZATION_COMPLETE.md` ⭐ **START HERE** - Complete architecture guide
- `PROJECT_INDEX.md` - Project overview & file mapping
- `WINTER_CLEANING_COMPLETION.md` - Root directory reorganization
- `DELIVERABLES.md` - Project deliverables summary
- `GLYPH_SYSTEM_AUDIT.md` - Glyph system design
- `MULTIMODAL_INTEGRATION_PLAN.md` - Multi-modal design
- `UI_MODULARIZATION_ANALYSIS.md` - UI component organization
- `VOICE_INTERFACE_IMPLEMENTATION.md` - Voice interface design

### reports/

Analysis reports and test results:

- JSON reports: Gate distribution, glyph validation, etc.
- Text reports: Commit summaries, legacy references, etc.

### archives/

Historical phase and sprint documentation:

- Phase 1-5 documentation
- Sprint documentation
- Session summaries

### INDEX.md

**Navigation guide for all documentation** - Start here if you're lost!

##

## 📊 Data Organization (data/)

### glyphs/

Glyph generation and validation data:

- Phase 1, 3, 4 glyph data
- Validation results
- Glyph lexicon rows
- SQL database file

### lexicons/

NLP lexicon and antonym data:

- Enhanced lexicon
- NRC lexicon
- Antonym glyphs
- Indexed antonym data

### analysis/

Analysis output directory (expand as needed)

### exports/

Export files directory (expand as needed)

##

## ⚙️ Configuration (config/)

All dependencies and configuration files:

```


config/
├── package.json              (Node dependencies)
├── package-lock.json         (Locked versions)
├── requirements.txt          (Core Python dependencies)
├── requirements-dev.txt      (Development dependencies)
├── requirements-nlp.txt      (NLP-specific dependencies)
├── requirements-voice.txt    (Voice interface dependencies)

```text
```


Install dependencies:

```bash
pip install -r config/requirements.txt
```text

```text
```


##

## 📜 Scripts (scripts/)

Deployment and setup scripts:

```bash


# Deploy to production
scripts/deploy.sh

# Run locally

```text

```

##

## 🔍 Logs (logs/)

Application logs for debugging:

- `debug_chat.log` - Chat debugging
- `fastapi.log` - API server logs
- `glyph_generation.log` - Glyph generation logs
- `streamlit.log` - Streamlit app logs
- `streamlit_tonecore.log` - ToneCore interface logs

##

## 🏛️ Modularized Application (emotional_os/)

The core application is modularized into:

### emotional_os/utils/

Utility modules:

- SVG loading
- CSS injection
- Styling utilities

### emotional_os/session/

Session management:

- Session initialization
- State management
- User preferences

### emotional_os/ui/

UI components:

- Header rendering
- Sidebar navigation
- Chat display
- Refactored consolidated UI

### emotional_os/response/

Response processing:

- Response handler
- Glyph handler

### emotional_os/features/

Optional features:

- Document processing
- Learning tracker
- Journal center
- Theme manager

### emotional_os/glyphs/

Glyph system:

- Generator
- Validator
- Lexicon management

### emotional_os/parser/

Input parsing:

- NLP parsing
- Intent detection

### emotional_os/learning/

Learning system:

- Local learner
- Memory management

##

## 🗜️ Organized Tools (tools/)

### tools/analysis/

Analysis and reporting:

- Gate distribution analyzer
- Scenario reporting
- Symbolic tagging
- Glyph evolution analysis

### tools/document_processing/

Document utilities:

- DOCX reader
- DOCX viewer
- Web DOCX viewer

### tools/glyph_testing/

Glyph testing:

- Conversation test harness
- Effectiveness validator

##

## 📝 Common Tasks

### Running the Application

```bash


# Using start.py (Railway)
python core/start.py

# Using Streamlit directly

```text
```text

```

### Adding a New Feature

1. Determine which module it belongs to
2. Add code to appropriate `emotional_os/` subdirectory
3. Update imports in `core/main_v2.py` if needed
4. Add tests to `tests/` directory

### Adding Analysis Tools

1. Create new file in `tools/analysis/`
2. Import in your analysis script
3. Document in appropriate guide

### Debugging

1. Check logs in `logs/` directory
2. Look for errors in `logs/debug_chat.log`
3. Check `logs/streamlit.log` for UI issues

### Managing Data

1. Add glyph data to `data/glyphs/`
2. Add lexicon data to `data/lexicons/`
3. Add analysis outputs to `data/analysis/`

##

## 🔗 Import Paths Reference

### Core Modules (New Locations)

```python



# Response System
from core.main_response_engine import process_user_input from core.response_adapter import
translate_emotional_response from core.response_selector import select_first_turn_response from
core.tone_adapters import generate_archetypal_response from core.symbolic_tagger import tag_input
from core.relational_memory import RelationalMemoryCapsule

# Application Entry Points
from core.start import main as start_railway from core.main_v2 import run_app

# Compatibility Shims (Legacy)
from core.phase_modulator import detect_phase

```text
```


### Emotional OS Modules

```python

# Utils
from emotional_os.utils.svg_loader import load_svg
from emotional_os.utils.css_injector import inject_css
from emotional_os.utils.styling_utils import apply_theme

# Session Management
from emotional_os.session.session_manager import SessionManager

# UI Components
from emotional_os.ui.header_ui import render_header
from emotional_os.ui.sidebar_ui import render_sidebar
from emotional_os.ui.chat_display import render_chat

# Response Processing
from emotional_os.response.response_handler import handle_response
from emotional_os.response.glyph_handler import handle_glyph

# Features
from emotional_os.features.document_processor import process_document
from emotional_os.features.learning_tracker import track_learning
from emotional_os.features.journal_center import manage_journal
from emotional_os.features.theme_manager import manage_theme

# Glyphs
```text

```text
```


### Tools

```python


# Analysis
from tools.analysis.gate_distribution_analyzer import GateDistributionAnalyzer
from tools.analysis.evolving_glyph_integrator import EvolvingGlyphIntegrator

# Document Processing
from tools.document_processing.docx_reader import read_docx
from tools.document_processing.docx_viewer import view_docx

# Glyph Testing

```text

```

##

## 📋 Checklist for New Developers

- [ ] Read `README.md` for project overview
- [ ] Read `docs/guides/MODULARIZATION_COMPLETE.md` for architecture
- [ ] Review `docs/INDEX.md` for documentation navigation
- [ ] Install dependencies: `pip install -r config/requirements.txt`
- [ ] Run application: `python core/start.py` or `streamlit run core/main_v2.py`
- [ ] Explore `core/` for main code
- [ ] Explore `emotional_os/` for modular components
- [ ] Check `logs/` when debugging

##

## 🆘 Getting Help

1. **Architecture questions** → `docs/guides/MODULARIZATION_COMPLETE.md`
2. **Finding files** → `docs/INDEX.md`
3. **Project history** → `docs/archives/`
4. **Code examples** → Look in `tests/` for usage examples
5. **Debugging** → Check `logs/` directory

##

## ✅ Project Status

```

✅ Modularization:    Complete (7 phases) ✅ Organization:      Complete (95% clutter reduction) ✅
Documentation:     Complete (comprehensive guides) ✅ Verification:      Complete (all imports
working) ✅ Ready for:         Development & Deployment

```

##

**For more information**: See `docs/INDEX.md` ⭐
