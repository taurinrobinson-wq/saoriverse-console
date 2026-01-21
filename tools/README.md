# tools/ — General Utilities

This directory contains **general-purpose utility scripts** that are **NOT Velinor-specific**.

These utilities support the broader project and can be used across multiple subsystems.

## Contents

### Diagnostic & Health Checks
- **railway_diagnostics.py** — Check Railway deployment environment, imports, and configuration
- **self_diagnostic.py** — System self-diagnostic utility
- **import_checker.py** — Verify core imports work correctly

### Deployment & Startup
- **start.py** — Railway startup script for FirstPerson Streamlit app

### Image Processing (Generic)
- **color_match.py** — Color-match images using Reinhard color transfer (useful for any image processing task)
- **overlay_compare.py** — Create side-by-side and blended image comparisons

### Testing Utilities
- **e2e_chat_test.py** — End-to-end chat API test utility
- **transcribe_test.py** — Test transcription functionality

### System Updates
- **update_system.py** — System updater utility

---

## Velinor-Specific Tools

**These tools have been moved to [velinor/tools/](../velinor/tools/):**
- Blender scene builders (blender_import_velinorian.py, blender_render.py, etc.)
- Building generators (brick_building_gen.py, procedural_building.py, etc.)
- Glyph processors (ritual_capsule_processor.py, etc.)
- Story builders (build_sample_story.py)
- NPC tools (list_missing_npcs.py, asset_pipeline.py)
- Lexicon expanders (expand_lexicon_with_synonyms.py, filter_multi_word_candidates.py)
- And 20+ other Velinor-specific utilities

See [velinor/tools/README.md](../velinor/tools/README.md) for the complete list.

---

## Guidelines

✅ **Keep in tools/ if:**
- It's a general utility usable by multiple projects/systems
- It doesn't import from velinor/ or game-specific modules
- It's a diagnostic, test, or deployment helper

❌ **Move to velinor/tools/ if:**
- It's specific to the Velinor game
- It processes glyphs, NPCs, buildings, or story content
- It imports from velinor/ or game-specific modules

---

## Adding New Tools

When adding a new utility:
1. Ask: "Is this Velinor-specific?"
2. If YES → create in [velinor/tools/](../velinor/tools/) and add to its README
3. If NO → create here in tools/ and update this README
