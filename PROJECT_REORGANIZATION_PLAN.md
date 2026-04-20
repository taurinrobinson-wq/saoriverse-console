# Project Reorganization Plan

## Problem Identified
The project root contains 65 Python files, most of which should be organized into subdirectories.
This causes: 1. **Import confusion**: Streamlit struggles with module resolution when files are
scattered 2. **Navigation difficulty**: Hard to understand which files are active vs. deprecated 3.
**Maintenance burden**: No clear separation between game code, backend services, tests, and
utilities

## Current State
- **65 Python files** in root directory
- **4 major subsystems**: Velinor game, FirstPerson backend, test suite, utilities
- **No clear organization** for what's active, deprecated, or in-progress

## Proposed Organization

### 1. Move ALL Tests (27 files) → `tests/`
```
tests/
├── test_phase*.py (game phases)
├── test_api_import.py
├── test_backend_health.py
├── test_end_to_end.py
├── test_litone_integration.py
├── test_memory_*.py
├── test_glyph_*.py
├── test_remnants_import.py
├── test_tier1_manual.py
├── COMPREHENSIVE_VALIDATION_USER_DRIVEN.py
├── FINAL_VALIDATION.py
├── FIRSTPERSON_INTEGRATION_TEST.py
├── SEMANTIC_PARSING_WALKTHROUGH.py
├── conftest.py (pytest config)
└── ... etc
```

### 2. Move Backend Services (9 files) → `backend/`
```
backend/
├── firstperson_api.py
├── firstperson_backend.py
├── firstperson_backend_flask.py
├── firstperson_backend_minimal.py
├── firstperson_backend_simple.py
├── firstperson_backend_v2.py
├── backend_keeper.py
├── run_backend.py
└── velinor_api.py
```

### 3. Move Utility Tools (13+ files) → `tools/`
```
tools/
├── glyph_generator.py
├── glyph_tools/
│   ├── init_glyph_db.py
│   ├── evolving_glyph_integrator.py
│   └── check_glyph_templates.py
├── diagnostics/
│   ├── check_spacy_local.py
│   ├── check-docker-requirements.py
│   ├── diagnose_backend.py
│   ├── validate_installation.py
│   ├── validate_full_pipeline.py
│   └── profile_feeling_system.py
├── fix_all_markdown.py
├── inspect_json.py
└── ... (other utilities)
```

### 4. Keep Essential Launch Files in Root
```
/root
├── run_streamlit_game.py (✓ NEW - Streamlit launcher)
├── app.py (primary app entry point?)
├── startup.py (startup sequence)
├── conftest.py (pytest configuration)
├── README.md
├── requirements.txt
├── docker-compose.yml
└── ... (existing documentation)
```

### 5. Consider New Directories
```
/root
├── docs/ (move VELINOR_SETUP_GUIDE.py, other docs)
├── legacy/ (deprecated files like old velinor_app.py variants)
└── experiments/ (research code like train_emotion_model.py)
```

## Files Requiring Review/Decision

| File | Current Status | Recommendation |
|------|---|---|
| `build_sample_story.py` | ? | Move to `velinor/tools/` or `tools/` |
| `main_response_engine.py` | Active? | Keep or move to `backend/` |
| `train_emotion_model.py` | Experimental? | Move to `legacy/` or `experiments/` |
| `debug_remnants.py` | Debugging? | Move to `tools/diagnostics/` |
| `app.py` | Entry point? | Keep in root with clear purpose documentation |
| `startup.py` | Entry point? | Keep in root with clear purpose documentation |

## Migration Steps

1. Create new directories: `backend/`, `tests/`, `tools/` 2. Move files in batches (5-10 at a time)
3. Update import statements in moved files 4. Update any references in documentation 5. Update
`.gitignore` if needed 6. Test each subsystem after moving:
   - Run tests from `tests/`
   - Run backend from `backend/`
   - Run game from root with `run_streamlit_game.py`

## Expected Benefits

✅ **Cleaner root directory** (from 65 files → ~10-15 files) ✅ **Clear module organization** (easier
to find what you need) ✅ **Better import clarity** (modules import from logical locations) ✅
**Improved maintainability** (easy to see what's active vs. deprecated) ✅ **Streamlit
compatibility** (clearer path resolution) ✅ **Professional project structure** (follows Python
conventions)

## Timeline
- Once approved, can be executed in one comprehensive operation
- ~30-45 minutes for full reorganization
- ~15 minutes for testing after reorganization
- All work tracked via git commits

---

**Recommendation**: Execute this reorganization BEFORE continuing with game testing, as it will prevent future import headaches and make the codebase more maintainable.
