# Directory Structure

This document explains the reorganized directory structure of the Saoriverse Console.

## Root Level (Essential Files)

- **`main_v2.py`** - Main Streamlit application entry point
- **`start.py`** - Startup script for Railway/production deployment
- **`test.js`** - JavaScript test file
- **`package.json` / `requirements.txt`** - Dependency manifests
- **`README.md` / `SETUP.md` / `LOCAL_SETUP_GUIDE.md`** - Primary documentation

## Key Directories

### Core Application

- **`emotional_os/`** - Main application package
  - `deploy/` - Deployment modules (UI, auth, conversation manager)
  - `glyphs/` - Glyph generation and learning systems
  - `learning/` - Hybrid learning engine
  - `llm/` - Language model integration
  - `parser/` - Signal and text parsing
  - `supabase/` - Supabase integration
  - `safety/` - Content safety and filtering
  - `ritual_ui/` - Ritual interface components

### Data & Configuration

- **`data/`** - Data files and databases
  - CSV/JSON lexicons
  - SQLite databases
  - Todo and configuration data

- **`config/`** - Configuration files
  - `config.py` - Main configuration
  - `config_template.py` - Configuration template
  - Diagnostic scripts

### Development & Utilities

- **`scripts/`** - Shell and Python scripts
  - `utilities/` - Utility scripts (analysis, consolidation, etc.)
  - `migrate_supabase.py` - Database migration helper
  - Shell scripts for setup and learning

- **`demos/`** - Demo and test scripts
  - End-to-end tests
  - Demo processors and consolidation scripts

- **`dev_tools/`** - Development tools

### Infrastructure & Database

- **`sql/`** - SQL schema and migrations
  - `conversations_table.sql`
  - `conversations_rls_policies.sql` (Row Level Security)
  - Other schema files

- **`supabase/`** - Supabase configuration
  - `config.toml` - Supabase configuration
  - `functions/` - Edge functions
  - `tests/` - Database tests

### Core Modules (Root Level)

- **`parser/`** - Signal parsing module
  - `signal_parser.py` - Main parser
  - `learned_lexicon.json`
  - `signal_lexicon.json`

- **`learning/`** - Learning system module
  - `lexicon_learner.py`
  - `pattern_history.json`

- **`em_trace/`** - Emotional trace engine
  - `trace_engine.py`

### Documentation & Reference

- **`docs/reference/`** - Reference documentation
  - Architecture guides
  - Implementation references
  - Phase deliverables
  - Privacy and security documentation

### UI & Static Assets

- **`src/ui/`** - UI components (legacy)
  - `emotional_os_ui.py (ARCHIVED)` (ARCHIVED)
  - `main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)` (ARCHIVED)
  - `emotional_tag_matcher.py`

- **`static/`** - Static web assets
  - HTML files (404.html, index.html)
  - Graphics

- **`graphics/`** - Graphics and visual assets

### Archive & Other

- **`archive/`** - Old/archived code and versions
- **`conversations/`** - Persistent conversation storage
- **`tests/`** - Test files and test configuration
- **`tools/`** - Compatibility shims and tools
- **`fresh-saoriverse-console/`** - Fresh copy backup
- **`.devcontainer/`** - Development container configuration

## Import Patterns

### Within emotional_os package:

```python
from emotional_os.deploy.modules.auth import SaoynxAuthentication
from emotional_os.glyphs.signal_parser import parse_input
from emotional_os.learning.hybrid_learner_v2 import get_hybrid_learner
```




### Root-level modules:

```python
from parser.signal_parser import parse_input
from learning.lexicon_learner import LexiconLearner
from em_trace.trace_engine import save_trace_json
```




### Scripts and utilities:

```python

# Scripts should add repo root to path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from emotional_os import ...
```




## Running the Application

```bash

# Direct Streamlit
streamlit run main_v2.py

# Via startup script (production)
python3 start.py
```




## Environment Setup

See `LOCAL_SETUP_GUIDE.md` for complete setup instructions.

Key files:
- `.streamlit/secrets.toml` - Streamlit secrets (Supabase credentials)
- `.env.example` - Environment variable template
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
