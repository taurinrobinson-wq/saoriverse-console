# Velinor — Remnants Overview

This document summarizes the current state of the Velinor "Remnants" assets, prototypes, and implementation notes in the repo. It is intended as a single reference so you can see what exists, how to run it, and what the next steps are.

## Where things live
- Music prototypes and tools: [velinor/music_prototypes](velinor/music_prototypes)
  - `generate_motifs.py` — creates `velinor_motif.mid` and `saori_motif.mid`.
  - `render_midi_with_sf2.py` — renders MIDI → WAV using local FluidR3_GM.sf2 (or fallback synth).
  - `music_states.json` — pressure/emergence state mapping (5 states).
  - Generated files: `velinor_motif.mid`, `saori_motif.mid`, `velinor_motif.wav`, `saori_motif.wav`, plus SF2-backed `*_sf2.wav` files.

- SoundFont: `velinor/data/FluidR3_GM.sf2` (validated RIFF/sfbk) and copied to `Offshoots/ToneCore/sf2/FluidR3_GM.sf2`. Tracked via Git LFS.

- Boss design and sprite implementation notes: [velinor/markdowngameinstructions/boss_fight_implementation.md](velinor/markdowngameinstructions/boss_fight_implementation.md)
- Original music concept discussion: [velinor/markdowngameinstructions/music_concepts.md](velinor/markdowngameinstructions/music_concepts.md)

## What I added and why
- Music prototype tooling — quick way to iterate motif ideas as MIDI and produce WAVs for auditioning.
- Fallback synth for environments without FluidSynth so you always get listenable WAVs.
- `music_states.json` to map game variables to discrete audio states (useful for runtime param mapping).
- Boss implementation doc to hand off to artists/animators and to serve as a checklist for engineering.

## How to run the main tools locally
1. Create / activate Python venv in workspace (the project already has a `.venv` in this workspace).

```powershell
D:/saoriverse-console/.venv/Scripts/Activate.ps1
pip install -r velinor/music_prototypes/requirements.txt
python velinor/music_prototypes/generate_motifs.py
python velinor/music_prototypes/render_midi_with_sf2.py velinor_motif.mid velinor/music_prototypes/velinor_motif_sf2.wav
```

Notes:
- `render_midi_with_sf2.py` will prefer FluidSynth if available and a valid SoundFont is present. If not, it falls back to a simple numpy synth to produce preview WAVs.
- Valid SF2 is available at `velinor/data/FluidR3_GM.sf2` and at `Offshoots/ToneCore/sf2/FluidR3_GM.sf2` (the latter tracked in LFS).

## Git / LFS status
- The large SF2 was migrated into Git LFS and uploaded. If collaborators clone the repo, run `git lfs install` and `git lfs pull` to fetch the SF2 objects.

## Key files created
- [velinor/music_prototypes/generate_motifs.py](velinor/music_prototypes/generate_motifs.py)
- [velinor/music_prototypes/render_midi_with_sf2.py](velinor/music_prototypes/render_midi_with_sf2.py)
- [velinor/music_prototypes/music_states.json](velinor/music_prototypes/music_states.json)
- [velinor/markdowngameinstructions/boss_fight_implementation.md](velinor/markdowngameinstructions/boss_fight_implementation.md)
- Rendered WAVs: [velinor/music_prototypes/velinor_motif_sf2.wav](velinor/music_prototypes/velinor_motif_sf2.wav), [velinor/music_prototypes/saori_motif_sf2.wav](velinor/music_prototypes/saori_motif_sf2.wav)

## Next recommended steps (short term)
1. Generate per-state WAV layers (5 layers) for each motif to import into FMOD/Wwise as crossfaded stacks.
2. Produce a small artist brief + PSD templates from `boss_fight_implementation.md` (I can generate atlas JSON template next).
3. Scaffold a Unity prototype scene (placeholder art) implementing rib behaviors and the Learning puzzle.

## Quick morale note
You built a dense, emotionally precise design — it’s normal to feel exhausted after iterating this much alone. You’ve done the hardest part: the concept and structure. The rest is implementable and I can keep taking the heavy lifting from here.

---

If you'd like, I will now (pick one):
- generate the atlas JSON template for the MVP assets, or
- scaffold the Unity prototype scene with placeholder sprites.

Tell me which and I’ll start it.
