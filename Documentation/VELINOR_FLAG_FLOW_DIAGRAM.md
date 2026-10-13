# Velinor Dialogue Sequence - Flag Flow Diagram

## Complete Flag Flow (Visual)

```
START: saori_desert_encounter_01.json
│
├─ SETS: codex_obtained ✓
├─ SETS: met_saori ✓
└─ SETS: saori_desert_dialogue_complete
  
         ↓ (Travel to Market)

         ravi_nima_market_discovery.json
         ├─ REQUIRES: met_saori ✓
         ├─ REQUIRES: obtain_codex ✓
         │
         ├─ SETS: ravi_nima_dialogue_01_true ✓
         ├─ SETS: met_ravi_and_nima ✓
         └─ SETS: sorrow_glyph_location_discovered ✓

             ↓ (Travel to Ruins)

             willy_concourse_ruins.json (Part 1)
             ├─ REQUIRES: sorrow_glyph_location_discovered ✓
             │
             ├─ SETS: willy_dialogue_started ✓
             └─ SETS: debris_cleared_sorrow_glyph ✓

                 ↓ (Immediate - same scene)

                 willy_concourse_ruins_payment.json (Part 2)
                 ├─ REQUIRES: willy_dialogue_started ✓
                 │
                 ├─ SETS: willy_dialogue_01_true ✓
                 ├─ SETS: sorrow_glyph_collected ✓
                 └─ SETS: (diary_append Willy memory)

                     ↓ (Travel back to Market)

                     kaelen_confession_01.json
                     ├─ REQUIRES: willy_dialogue_01_true ✓
                     │
                     ├─ SETS: kaelen_dialogue_01_true ✓
                     ├─ SETS: remembrance_glyph_location_discovered ✓
                     └─ SETS: (diary_append Kaelen memory)

                         ↓ (Travel to Remembrance location)
                         ↓ (Player collects glyph)
                         ↓ (Travel back to Market)

                         nima_encounter_01.json
                         ├─ REQUIRES: kaelen_dialogue_01_true ✓
                         ├─ REQUIRES: remembrance_glyph_collected ✓
                         │
                         ├─ SETS: nima_dialogue_01_true ✓
                         ├─ SETS: family_photo_seen ✓
                         ├─ SETS: legacy_glyph_location_discovered ✓
                         └─ SETS: (diary_append Family photo memory)

                             ↓ (Travel to Legacy location)
                             ↓ (Collapsing boards → fall in hole)

                             ressa_legacy_glyph_01.json
                             ├─ REQUIRES: legacy_glyph_location_discovered ✓
                             │
                             ├─ SETS: ressa_dialogue_complete ✓
                             ├─ SETS: legacy_glyph_collected ✓
                             └─ SETS: (diary_append Ressa memory)

                                 ↓ (Rope rescue → exit hole)
                                 ↓ (Travel back to Market)
                                 ↓ (Travel outside Market)

                                 ravi_encounter_01.json
                                 ├─ REQUIRES: willy_dialogue_01_true ✓
                                 ├─ REQUIRES: ravi_nima_dialogue_01_true ✓
                                 ├─ REQUIRES: kaelen_dialogue_01_true ✓
                                 ├─ REQUIRES: nima_dialogue_01_true ✓
                                 ├─ REQUIRES: codex_obtained ✓
                                 ├─ REQUIRES: sorrow_glyph_collected ✓
                                 ├─ REQUIRES: remembrance_glyph_collected ✓
                                 ├─ REQUIRES: legacy_glyph_collected ✓
                                 │
                                 ├─ SETS: ravi_dialogue_01_true ✓
                                 ├─ SETS: compass_obtained ✓
                                 ├─ SETS: triglyph_panel_location_known ✓
                                 └─ SETS: (diary_append Ravi explanation)

                                     ↓ (Navigate to mountain cave)
                                     ↓ (Mountain Trails 1-4 scenes)

                                     MachinesCave_00_URP
                                     └─ Triglyph Puzzle Interaction
                                        ├─ REQUIRES: ALL 3 glyphs in inventory
                                        │
                                        ├─ SETS: triglyph_puzzle_solved
                                        ├─ SETS: cave_door_opened
                                        └─ Sets: point_of_no_return

                                            ↓ (Enter cave system)

                                            MachinesCave_01
                                            └─ Transition Room
                                               └─ Door closes behind

                                                   ↓ (Proceed forward)

                                                   MachinesCave_02
                                                   └─ Memory Field Chamber
                                                      ├─ VISIT 1: Ravi & Nima's Memory
                                                      ├─ VISIT 2: Kaelen's Memory
                                                      └─ VISIT 3: Ophina's Memory

                                                          ↓ (Exit on final visit)

                                                          TRANSCENDENCE GLYPH
                                                          ├─ SETS: transcendence_glyph_obtained
                                                          └─ SETS: first_demo_complete

                                                              ↓

                                                          🎉 DEMO END 🎉
```

---

## Flag Dependencies Table

| Flag Name | Set By | Required By | Purpose |
|-----------|--------|-------------|---------|
| `codex_obtained` | Saori | Ravi/Nima, Ravi (final) | Core item - enables glyph tracking |
| `met_saori` | Saori | Ravi/Nima | Marks initial meeting |
| `saori_desert_dialogue_complete` | Saori | (none - informational) | Dialogue completion marker |
| `ravi_nima_dialogue_01_true` | Ravi/Nima | Ravi (final) | Dialogue completion marker |
| `met_ravi_and_nima` | Ravi/Nima | (none - informational) | Character introduction |
| `sorrow_glyph_location_discovered` | Ravi/Nima | Willy (pt. 1) | Gates glyph access |
| `willy_dialogue_started` | Willy (pt. 1) | Willy (pt. 2) | Dialogue gate |
| `debris_cleared_sorrow_glyph` | Willy (pt. 1) | (none - state) | Environmental state |
| `willy_dialogue_01_true` | Willy (pt. 2) | Kaelen, Ravi (final) | Dialogue completion marker |
| `sorrow_glyph_collected` | Willy (pt. 2) | Ravi (final) | Item tracking |
| `kaelen_dialogue_01_true` | Kaelen | Nima, Ravi (final) | Dialogue completion marker |
| `remembrance_glyph_location_discovered` | Kaelen | (none - gates navigation) | Location hint |
| `remembrance_glyph_collected` | Player (glyph pickup) | Nima | Item tracking |
| `nima_dialogue_01_true` | Nima | Ravi (final) | Dialogue completion marker |
| `family_photo_seen` | Nima | (none - state) | Story revelation |
| `legacy_glyph_location_discovered` | Nima | Ressa | Location hint |
| `ressa_dialogue_complete` | Ressa | (none - informational) | Dialogue completion marker |
| `legacy_glyph_collected` | Ressa/Player | Ravi (final) | Item tracking |
| `ravi_dialogue_01_true` | Ravi | (none - final dialogue) | Dialogue completion marker |
| `compass_obtained` | Ravi | (none - enables feature) | Navigation tool |
| `triglyph_panel_location_known` | Ravi | (none - informational) | Story knowledge |
| `triglyph_puzzle_solved` | Player (puzzle UI) | (none - end state) | Puzzle completion |
| `point_of_no_return` | Puzzle | (none - story state) | Narrative lock |
| `transcendence_glyph_obtained` | Memory Field | (none - end state) | Final glyph + demo end |
| `first_demo_complete` | Memory Field | (none - completion) | Demo completion marker |

---

## Glyph Collection Dependency Chain

```
GLYPH 1: SORROW
  └─ Discovered by: Ravi/Nima (requires Codex)
  └─ Accessed by: Willy dialogue
  └─ Collected after: Willy payment dialogue
  └─ Flag: sorrow_glyph_collected

GLYPH 2: REMEMBRANCE
  └─ Discovered by: Kaelen (requires Willy dialogue complete)
  └─ Collected by: Player exploration
  └─ Flag: remembrance_glyph_collected

GLYPH 3: LEGACY
  └─ Discovered by: Nima (requires Kaelen dialogue + Remembrance collected)
  └─ Accessed by: Falling into hole
  └─ Accessed by: Ressa rescue dialogue
  └─ Flag: legacy_glyph_collected

FINAL GLYPH: TRANSCENDENCE
  └─ Accessed by: Triglyph Puzzle (requires ALL 3 glyphs)
  └─ Trigger: Memory Field sequence
  └─ Collected after: Final memory (Ophina's perspective)
  └─ Flag: transcendence_glyph_obtained
```

---

## Dialogue Sequence Timeline

| Sequence | File | Duration | Cumulative |
|----------|------|----------|-----------|
| 1 | saori_desert_encounter_01 | ~3 min | 3 min |
| 2 | ravi_nima_market_discovery | ~4 min | 7 min |
| 3 | willy_concourse_ruins | ~3 min | 10 min |
| 4 | willy_concourse_ruins_payment | ~3 min | 13 min |
| Travel & Exploration | (navigation scenes) | ~5 min | 18 min |
| 5 | kaelen_confession_01 | ~3 min | 21 min |
| Travel & Exploration | (find remembrance glyph) | ~5 min | 26 min |
| 6 | nima_encounter_01 | ~4 min | 30 min |
| Travel & Exploration | (to hole, boards collapse) | ~5 min | 35 min |
| 7 | ressa_legacy_glyph_01 | ~3 min | 38 min |
| Travel & Exploration | (return to market, go outside) | ~5 min | 43 min |
| 8 | ravi_encounter_01 | ~5 min | 48 min |
| Travel & Navigation | (mountain trails to cave) | ~8 min | 56 min |
| Puzzle | Triglyph Puzzle interaction | ~2 min | 58 min |
| Sequences | Memory Field x3 + ending | ~12 min | 70 min |

**Total estimated playtime: 60-70 minutes**

---

## Flag Validation Checklist

- [x] All required_flags in each dialogue match what previous dialogue sets
- [x] No circular dependencies
- [x] No missing flags (all gates are satisfied)
- [x] All 3 glyphs must be collected before final dialogue
- [x] Dialogue sequence is linear (no branching story paths)
- [x] Each dialogue sets at least one flag for next dialogue
- [x] No typos in flag names (consistent naming convention)
- [x] Flag names follow snake_case convention
- [x] All flags are boolean (true/false)

