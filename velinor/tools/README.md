# velinor/tools/ — Velinor Game Tools & Builders

This directory contains **Velinor-specific Python utilities and scripts**, including builders for assets, glyphs, story content, and integration tools.

These are organized by function:

## 3D Asset Builders (Blender)
Procedural and importable Blender scene builders for Velinorian structures:
- **blender_import_velinorian.py** — Import MGAIA JSON structures into Blender with Velinorian materials
- **blender_build_voxels.py** — Build voxel-based 3D structures from JSON blocks
- **blender_render.py** — Headless Blender renderer for OBJ/JSON models
- **blender_render_from_json.py** — Direct JSON-to-render pipeline (no OBJ needed)

## Building Generators (Procedural & Physics)
Generate intact or collapsed buildings with visual effects:
- **brick_building_gen.py** — Procedural brick building generator
- **brick_collapse_gen.py** — Physics-based inward collapse simulation
- **procedural_building.py** — Lightweight procedural building system
- **create_building_mask.py** — Generate inpainting masks for buildings
- **generate_collapse_overlay.py** — Create rubble & dust overlay effects
- **apply_collapse.py** — Apply collapse effect to background images

## Image Processing & Composition
Asset processing and visual composition:
- **asset_pipeline.py** — Batch NPC asset processor (standardize size, apply painterly filters, generate thumbnails)

## NPC & Character Tools
Manage and generate NPC assets:
- **list_missing_npcs.py** — Find missing NPC images by comparing Glyph_Organizer.json to existing files
- **run_automatic1111_batch.py** — Batch generate NPC portraits via Automatic1111 WebUI API

## Glyph Processing & Integration
Work with the glyph cipher system:
- **ritual_capsule_processor.py** — Sacred glyph processing module (ingests, validates, structures emotional glyphs)
- **list_archived.py** — Query archived glyphs from database

## Story & Content Builders
Generate story scaffolds and narrative content:
- **build_sample_story.py** — Build sample Velinor story JSON structures using StoryBuilder

## Lexicon & Signal Processing
Expand and process emotional/psychological vocabularies:
- **expand_lexicon_with_synonyms.py** — Expand lexicon keywords using spaCy + Datamuse synonyms
- **filter_multi_word_candidates.py** — Filter multi-word candidates from OpenStax psychology phrases
- **build_combined_trigger_lexicon.py** — Merge expanded lexicon with glyph-associated keywords

## Video Post-Processing
- **grade_video.sh** — Apply Velinor aesthetic (muted colors, vignette, grain) to video files
- **velinor_palette.cube** — 3D color grading LUT for Velinor aesthetic

## Markup & Documentation
- **fix_all_markdown.py** — Batch markdown fixer (run all linting fixes sequentially)

## Entry Points
- **entrypoint.sh** — Linux entrypoint for Velinor services
- **entrypoint.firstperson.sh** — Linux entrypoint for FirstPerson service

---

## Import Patterns

Most tools import from the Velinor package hierarchy:
```python
from velinor.glyph_cipher_engine import get_engine
from velinor.npc_profiles import NPC
from velinor.velinor_api import load_seeds
```

Some tools work with external services:
- **run_automatic1111_batch.py** requires Automatic1111 WebUI running locally
- **expand_lexicon_with_synonyms.py** requires spaCy + Datamuse API access
- **grade_video.sh** requires ffmpeg on PATH

---

## Running Tools

Most tools can be run from the repo root:
```bash
# Generate missing NPC list
python velinor/tools/list_missing_npcs.py

# Batch render buildings
python velinor/tools/brick_collapse_gen.py output.png --collapse 0.8 --seed 42

# Expand lexicon
python velinor/tools/expand_lexicon_with_synonyms.py

# Grade video
./velinor/tools/grade_video.sh input.mp4 output.mp4
```

See individual files for usage patterns and command-line options.

---

## Asset Output Locations

Tools typically save to:
- **velinor/data/** — Raw game data (glyphs, lexicons, NPC profiles)
- **velinor/** — Generated seeds, registry files, configurations
- **output/** — Batch generation results (images, renders)
- **archive/** — Old versions and backups

---

## Development Guidelines

When adding a new Velinor tool:
1. Add it to this directory
2. Document its purpose in this README
3. Include usage examples in docstrings
4. If it generates outputs, specify the output directory
5. If it imports from velinor/, verify the import paths work

