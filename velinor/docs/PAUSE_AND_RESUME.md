**PAUSE_AND_RESUME — Saoriverse / Velinor console**

Purpose
- A concise snapshot so you (or anyone you hand this to) can pause now and resume later without losing context.

Quick status
- Title/demo UI: `velinor_title_transparent.png` + `tools/run_title_demo.py` (Streamlit) — runnable demo.
- 3D pipeline: `tools/mgaia_converter.py`, `velinor/assets/structures/*.json`, OBJ/GLB outputs in `velinor/` and Blender helper scripts in `tools/`.
- Procedural 2D building overlays: `tools/procedural_building.py` and generated images in `velinor/overlays/`.
- NPC art and glyphs: many PNGs in repo root and `velinor/` subfolders; some still need background clean-up.

Key files / how to reproduce the title demo
- Demo runner: `tools/run_title_demo.py`
- Title image: `velinor_title_transparent.png`
- Requirements (for demo): `requirements_streamlit.txt`

To run the title demo locally
1. Install dependencies:

```powershell
pip install -r requirements_streamlit.txt
```

2. Run the demo:

```powershell
streamlit run tools/run_title_demo.py
```

If you need a portable package, create a `deliverable/` folder and copy `velinor_title_transparent.png`, `city_market.png`, `Mariel_nobg.png`, `tools/run_title_demo.py`, and `requirements_streamlit.txt` into it.

Blender renders and headless scripts
- Scripts added to `tools/`:
  - `blender_build_voxels.py` — Blender script to create cubes per block (interactive)
  - `blender_render.py` — headless OBJ import + render helper
  - `blender_render_from_json.py` — headless builder-from-JSON + render (recommended if OBJ import fails)

Where structure data lives
- `velinor/assets/structures/*.json` (18 structures exported from MGAIA)
- OBJ/MTL: `velinor/*_velinorian.obj` + `.mtl` (per-structure)

Short-term next steps (pick one)
- Package and share the title demo (`deliverable/`): quick win for sharing.
- Batch-clean NPC PNGs (automated background removal): will standardize characters for layering.
- Batch-process glyphs to canonical sizes and export sprite sheets.
- Finish Blender renders for a handful of structures to produce images for marketing.

Longer-term (after short-term)
- Integrate 3D assets into a lightweight engine or into the web client.
- Implement core game loop: scenes, NPCs, basic dialogue.
- Flesh out story arcs and place sample NPCs into scenes.

If you step away
- Commit your working branch and push.
- Add a short note to the PR or an issue describing what you wanted to do next (e.g., "clean NPC PNGs and make standardized 512x512 assets").

If you want me to continue
- Tell me which short-term next step to start and I will begin work and report progress.

Contact points (repo locations)
- Title/demo runner: `tools/run_title_demo.py`
- Build/export scripts: `tools/mgaia_converter.py`, `tools/blender_*` scripts
- 2D procedural: `tools/procedural_building.py`
- Structures: `velinor/assets/structures/` (JSON)

— End of snapshot