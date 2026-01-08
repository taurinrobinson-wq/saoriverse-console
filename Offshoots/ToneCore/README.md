# ToneCore demo

This folder contains a small Streamlit demo that generates MIDI from the normalized chord pivot and
renders audio using FluidSynth.

Quick start (local devcontainer / machine):

1. Install system deps (Linux):

```bash
```text

```text
```


2. Install Python deps:

```bash

```text

```

3. Run the app:

```bash


# Example: run on port 8502 to avoid conflicts with other apps
streamlit run Offshoots/ToneCore/streamlit_app.py --server.port 8502

```

Open <http://localhost:8502> (forward the port if running in a remote container).

Notes:

- The app will try to use a local `Offshoots/ToneCore/sf2/FluidR3_GM.sf2` soundfont if present,
  fall back to common system locations, and otherwise attempt to download a small fallback
  soundfont into `Offshoots/ToneCore/sf2/` at first run.
- For reproducible high-quality rendering in CI, install a soundfont via the system package
  (e.g. `fluid-soundfont-gm` on Debian) or enable Git LFS and add your preferred SF2.
ToneCore offshoot folder, contains pivot data and Tonecore scripts.

Files:

- `chord_pivot_normalized.json`, normalized canonical pivot (chord objects)
- `emotion_map.json`, emotion → function map
- `scripts/`, Tonecore scripts (midi generator, normalizer, demo)
