## Malrik, Elenya, and Coren — Cleaned Design Notes

This file is a concise, cleaned extract of the original character and mechanics material.

### Archivist Malrik
- Role: Archivist
- Core: empirical, rigorous, service-oriented, socially miscalibrated
- Speech: clipped proclamations, abrupt pivots, half-explanations
- Visual: desert tones, practical wrap, sand diagrams
- Key glyphs: Fractured Memory, Mirage Echo, Sand Memories, Measured Step, Boundary Stone

Gameplay/Mechanical hooks:
- Glyph triggers tied to player recognition (e.g., recognizing a semantic fracture, choosing to dismiss a mirage).

### High Seer Elenya
- Role: Mystic / High Seer
- Core: intuitive, ritualistic, presence-oriented
- Speech: metaphors, long blinks, gentle clarity
- Visual: mountain palette, wind-touched hair, layered robes
- Key glyphs: Sky Revelry, Blooming Path, Veiled Silence, Covenant Flame

Gameplay/Mechanical hooks:
- Participation and presence mechanics (join revelry, remain silent at shrine, tend covenant flame).

### Coren the Mediator
- Role: Mediator with two aspects (Collapse / Sovereignty)
- Glyphs: Preemptive Severance (cult encampment), Held Ache (market concourse)

Mechanic: Coren's aspect/glyph depends on player orientation; teaches either severance or co-witnessing.

### Observational Mini-Game (Sand Diagram Scene)
- Anchors: Elenya watching, hand on gut; Malrik drawing and unaware
- Orientations: trust, observation, narrative, empathy
- Choice menus vary by orientation; each choice applies micro-shifts to tone stats
- Tone stats: trust, observation, narrative, empathy (0.0–1.0)
- Shifts range between +0.01 and +0.04; small counterweights can be applied to keep realism

### Systems
- Attunement score (hidden) accumulates from empathy-weighted choices and controls Malrik/Elenya correlation:
  - attunement <= 0.10 -> correlation = -0.5
  - 0.10 < attunement <= 0.25 -> correlation = 0.0
  - attunement > 0.25 -> correlation = +0.5
- NPC correlation example: Ravi/Nima mirrored at 50% of player shift by design

### Files generated
- JSON: malrik_elenya_coren.json (structured data for engines)
- YAML: malrik_elenya_coren.yaml (human-friendly export)
- Python: velinor/game_mechanics/characters.py (loader and simple mechanics)
- TypeScript: velinor/game_mechanics/characters.ts (frontend counterpart)

If you want, I can now:
- Hook the Python module into a small unit test showing several player choices
- Add UI mockups for the mini-game choice menus
- Convert the YAML into an in-engine config loader
