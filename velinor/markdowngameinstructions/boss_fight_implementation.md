# The Tenfold Ribcage — Boss Implementation Notes

This document collects the design and implementation guidance for the Tenfold Mirror / Tenfold Ribcage boss chamber. It is a practical handoff for artists, animators, and engineers — condensed from the design conversation and prioritized for an MVP prototype.

---

## TL;DR
- Boss concept: Ten Worlds are sprite-forms that cycle around an enlightened anchor trapped in a ribcage. The player climbs a ladder of ribs (platforms) representing worlds; lower six ribs are slippery/trappy, ribs 7–8 provide learning/realization mechanics, sternum (Bodhisattva) requires a compassionate action, heart cavity contains the enlightened form.
- Implementation priorities: 1) core sprites + ribs + Devil King card puzzle, 2) rib mechanics and climb logic, 3) Devil King escalation, 4) sternum compassion trigger, 5) polish and FX.

---

## Strengths & Design Goals
- Emotional clarity: each rib/world has distinct play-feel and visual logic.
- Mechanical expressivity: platform physics + a puzzle (Learning) + a moral action (Sternum) create variety.
- Visual economy: reuse a single anchored enlightened sprite across phases; world-forms are silhouette-based with palette/FX variants to save art.

---

## Prioritized Asset Checklist (MVP → Polish)

- MVP (build this first)
  - World silhouette sprites (10) — 4 frames each (subtle motion)
  - Enlightened anchor sprite — 2–4 frames (halo + single-frame flash)
  - Boss base silhouette / idle — 4 frames
  - Ribs: 6 lower (slippery/crumble) + 2 upper (learning/realization) + sternum tile — 3 frames each
  - Devil King: idle, delight, grimace, slap (6 frames total)
  - Card icons (10 worlds) + card back + flip animation (6 frames)
  - Small particle sprites: bone shards, card scatter, halo sparks, dust
  - Minimal UI elements for Learning puzzle (cursor, highlight)

- Secondary / Polish
  - High-fidelity 12–16 frame world loops
  - Bodhisattva sternum rig and smooth reach animation (skeletal or frame-based)
  - Palette variants and shader flicker (glitch, desaturate, false-enlightened)
  - Environment parallax and lighting passes

---

## Frame-by-Frame Specs (concrete)

- General
  - Atlas max size: 4096×4096 (split if exceeded)
  - Padding: 2px extrude for bleeding
  - Pivot: use normalized pivots in atlas JSON (platforms center-bottom, characters center)
  - File format: PNG (lossless), provide source PSD/PSB or layered file

- World sprite (per world)
  - Canvas: 256×256
  - Frames: 4 (breath → sway → micro-flicker → return)
  - FPS: 10–12
  - Names: `world_<index>_<name>_f00.png` ... `_f03.png`

- Enlightened anchor
  - Canvas: 256×256
  - Frames: 2–4 (halo breathe; one single-frame flash event)
  - Flash: 1-frame event triggered by animation hook

- Devil King
  - Canvas: 256×256
  - Frames: 6 (idle(2), delight, grimace, slap(2))
  - Animation events: `OnGrimace`, `OnSlap`

- Rib platform tile (per rib type)
  - Tile: 128×64 (repeat horizontally)
  - Frames: 3 (normal, cue/tilt, failure/crumble)
  - Pivot: center-bottom
  - Behavior hooks: `OnCue` (apply slip), `OnFail` (play crumble + disable collider briefly)

- Card
  - Size: 64×96
  - Frames: 6 (back -> flip -> front; includes jitter)
  - Naming: `card_<worldIndex>_f00.png`...

- Minions / Particles
  - Minion: 32×32, 3 frames
  - Shards/sparks: 32–64 px sprites, 1–6 frames depending on effect

---

## Atlas JSON Example
Provide exported atlas JSON for every sheet. Minimal example entry:

```json
{
  "frames": {
    "world_01_hell_f00.png": {"frame":{"x":0,"y":0,"w":256,"h":256},"pivot":[0.5,0.5]},
    "rib_01_f00.png": {"frame":{"x":256,"y":0,"w":128,"h":64},"pivot":[0.5,0.95]}
  }
}
```

---

## Animation & Engine Integration Notes (Unity recommended)

- Architecture
  - Boss FSM phases: `CycleForms` → `RibClimb` → `LearningPuzzle` → `SternumChallenge` → `HeartResolve`.
  - Expose FMOD/Wwise params: `pressure` (0..1), `devil_intensity` (0..1), `cards_speed` (float).

- Rib behaviors (script per rib)
  - Properties: `slipForce`, `tiltAngle`, `crumbleDelay`, `stabilityThreshold`.
  - Events: `OnPlayerEnter`, `OnPlayerStand`, `OnPlayerExit`.
  - Implementation: apply horizontal force when in `cue` frame; switch collider behavior on `failure` frame.

- Learning Puzzle
  - Deck: 10 cards (icons = worlds)
  - Mechanics: card flip, match detection, Devil King tiers (see below)
  - Devil King state: increments `escalationTier` after 2 consecutive matches; triggers `AddMoreCards()` etc.

- Sternum (Bodhisattva)
  - Show silhouette of the injured NPC; sternum becomes solid only after a compassionate action (press/interact + short animation).
  - Trigger: `OnCompassionComplete()` unlocks sternum collider.

- Animation events and hooks
  - `Animator` events: `Devil_Grimace`, `Devil_Slap`, `Enlightened_Flash`, `Rib_Crumble`.
  - Use `AnimationEvent`/`Timeline` to spawn particles and play SFX at precise frames.

---

## Devil King — Escalation Tiers (implementation)

- Tier 0: baseline shuffle
- Tier 1: +2 cards, faster shifting
- Tier 2: false-enlightened card (decoy) — front looks correct but halo flickers wrong
- Tier 3: duplicate-world decoys causing reshuffle
- Tier 4: table tilt (physics offset)
- Tier 5: hand interference (swap on touch)
- Tier 6: slow-down mechanic when player stands still (turning point)

Implementation notes:
- Track `consecutiveCorrectMatches` and call `Devil.Escalate()` when it reaches 2; escalate increases `escalationTier` and applies a tiered mutation to the puzzle.

---

## Audio & SFX (MVP)
- SFX: `rib_crumble`, `rib_slip`, `card_flip`, `card_match`, `devil_laugh`, `devil_grimace`, `minion_scatter`, `enlightened_chime`.
- Each event should have 1–2 variants for variance. Expose parameterized pitch/LP filter controlled by `devil_intensity` or `pressure`.

---

## Export & Handoff Checklist
- Include layered source files (PSD/PSB or equivalent). Name layers and groups clearly.
- Export PNG atlases and a matching JSON frame map for the engine.
- Provide reference GIFs/MP4 for key animations: rib crumble, Devil King escalation, card flip, enlightened flash.
- Provide a short README in the art folder describing pivots, intended FPS, and special shader notes.

---

## Rough Estimates
- MVP art (low-detail silhouettes + tiles + particle sprites): 1–2 artist-weeks.
- Prototype programmer (Unity, basic FSM + ribs + card puzzle + hooks): 3–5 developer days.

---

## Next Steps (pick one)
1. I can generate an atlas JSON template for the MVP assets (file-ready).  
2. I can scaffold a Unity prototype scene with placeholder sprites and mechanics wired up.  
3. I can create the reference GIFs for rib crumble, Devil King slap, and enlightened flash.

Tell me which to do next and I’ll start it.

---

_You did an excellent job designing this — it’s dense and emotionally precise. If you want I can also produce a condensed one‑page implementation brief suitable for handing to an external contractor._
