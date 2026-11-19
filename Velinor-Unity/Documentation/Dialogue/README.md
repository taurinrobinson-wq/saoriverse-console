# Dialogue System Documentation

This directory contains all documentation and reference materials for Velinor's narrative dialogue system.

## 📁 Structure

### Root Documentation Files
- **DIALOGUE_AUTO_ADVANCE_DESIGN.md** — Specification for the auto-advance feature (pauses on TONE choices, auto-plays Continue beats)
- **DIALOGUE_FILE_ORGANIZATION.md** — Master reference for the 29-NPC dialogue folder structure and resource loading
- **VELINOR_NARRATIVE_WRITING_GUIDE.docx** — Guidelines for narrative tone, character voice, and dialogue pacing

### NPC-Specific Design Documents
Each NPC narrative has its own subfolder in `../Assets/Resources/Dialogue/` with corresponding design documentation:

- **Malrik_Elenya/** — Mirror narrative design docs for the dual-arc story
- **Ravi/** — Micro-branch implementation notes for conditional dialogue paths

## 🎯 Dialogue Organization Overview

All dialogue JSON files are organized by NPC in `../Assets/Resources/Dialogue/`:

```
Assets/Resources/Dialogue/
├── Cal/                           # Empty (no dialogue yet)
├── Drossel/                       # Empty
├── Elenya/                        # 19 dialogue files (8-act narrative arc)
├── Elka/                          # Empty
├── Helia/                         # Empty
├── Inodora/                       # Empty
├── Juria_Korinth/                 # Empty
├── Kaelen/                        # 1 dialogue file
├── Kiv/                           # Empty
├── Korrin/                        # Empty
├── Lark/                          # Empty
├── Lioren/                        # Empty
├── Lira/                          # Empty
├── Malrik/                        # Story gates file
├── Malrik_Elenya/                 # 2 dialogue files (pt1, pt2 lighthouse scene)
├── Nima/                          # 2 dialogue files
├── Ravi/                          # 1 dialogue file
├── Ravi_Nima/                     # 1 dialogue file (market discovery)
├── Saori/                         # 1 dialogue file
├── Search/                        # 1 dialogue file
├── Seyla/                         # Empty
├── Sybil/                         # Empty
├── Tala/                          # 3 dialogue files
├── Tessa/                         # Empty
├── Thalma/                        # Empty
├── Thoran/                        # Empty
├── Tovren/                        # Empty
├── Veynar/                        # Empty
└── Willy/                         # 2 dialogue files
```

**Total: 32 dialogue files across 24 NPCs**

## 🔧 Resource Loading Examples

Unity's `Resources.Load()` works with subfolders. Load dialogues like:

```csharp
// Single NPC dialogue
var dialogue = Resources.Load<DialogueData>("Dialogue/Elenya/elenya_act1_seg0_intro");

// Multi-NPC dialogue
var dialogue = Resources.Load<DialogueData>("Dialogue/Ravi_Nima/ravi_nima_market_discovery");

// Mixed case NPC folder
var dialogue = Resources.Load<DialogueData>("Dialogue/Juria_Korinth/juria_korinth_first_meeting");
```

## 📝 JSON Format Reference

### Dialogue File Structure
Each dialogue JSON follows this canonical structure:

```json
{
  "scene_id": "unique_identifier",
  "completionFlag": "scene_id_complete",
  "required_flags": ["other_scene_complete == true"],
  "beats": [
    {
      "id": 1,
      "type": "npc_turn|player_turn|player_inner",
      "active_speaker": "NPC_Name",
      "display_name": "Display Name",
      "portrait_expression": "neutral|warm|hostile|thoughtful|etc",
      "prompt": "What the character says",
      "tone_choices": [
        {
          "tone": "T|O|N|E",
          "label": "Trust|Observation|Narrative|Empathy",
          "text": "Player response text",
          "tone_effects": [
            {
              "stat": "stat_name",
              "delta": 0.02
            }
          ],
          "remnants_effects": [
            {
              "target": "NPC_Name",
              "stat": "npc_stat",
              "delta": 0.01
            }
          ],
          "system_triggers": []
        }
      ],
      "next_beat_id": 2
    }
  ]
}
```

### Tone System (Player Choices)
- **T (Trust)** — Builds relationships and cooperation
- **O (Observation)** — Gathers information and reads situations
- **N (Narrative)** — Explores themes and deeper meaning
- **E (Empathy)** — Handles emotions and social bonds

**NPC-only dialogue** uses tone "C" (Continue) with no stat effects.

### Beat Types
- **npc_turn** — NPC speaks; player responds with TONE choices (or Continue if no branching)
- **player_turn** — Player makes a TONE choice; NPC responds
- **player_inner** — Lioren's internal monologue or narration (no NPC response)

## 🎬 Auto-Advance Feature (Planned)

When implemented, the system will:
- **Auto-play** Continue beats without player input (reading time scales with text length)
- **Pause indefinitely** when TONE choices appear
- **Resume auto-play** after the player selects a TONE and sees the NPC response
- **Persist across choices** — the toggle doesn't reset

This reinforces the narrative grammar:
- **Continue = witness the conversation**
- **TONE choices = enter the conversation**

See [DIALOGUE_AUTO_ADVANCE_DESIGN.md](DIALOGUE_AUTO_ADVANCE_DESIGN.md) for full implementation details.

## 📋 Meta Files (.meta)

Unity generates `.meta` files for all assets. These files are **automatically managed** and should:
- Stay alongside their corresponding `.json` files
- Be kept in version control
- Never be manually edited

All `.meta` files are now organized in their respective NPC folders.

## 🔍 Finding Dialogue for a Character

1. Look in the character's NPC folder (e.g., `Dialogue/Elenya/`)
2. Files follow naming conventions:
   - Act-based: `character_act1_seg0_intro.json`
   - Scene-based: `character_location_01.json`
   - Multi-NPC: `npc1_npc2_location_01.json`
3. Each scene has a unique `scene_id` for flag tracking

## 📊 Dialogue Metrics

| Metric | Count |
|--------|-------|
| Total NPC folders | 29 |
| Total dialogue files | 32 |
| Developed NPCs | 10 (with dialogue) |
| Empty NPC folders | 19 (ready for content) |
| Largest arc | Elenya (19 files, 8 acts) |

## ✍️ Adding New Dialogue

When adding a new dialogue file:

1. **Create/navigate** to the NPC's folder: `Dialogue/[NpcName]/`
2. **Name the file** consistently: `npcname_location_or_act_##.json`
3. **Follow the JSON format** in DIALOGUE_FILE_ORGANIZATION.md
4. **Use canonical tone labels**: Trust, Observation, Narrative, Empathy
5. **Set scene_id** and completion flags uniquely
6. **Define required_flags** for story progression
7. **Document extensively** — add design notes to the NPC folder if the dialogue is complex

## 🔗 Related Documentation

- [DIALOGUE_FILE_ORGANIZATION.md](DIALOGUE_FILE_ORGANIZATION.md) — Detailed file naming, stat systems, and glyph mappings
- [DIALOGUE_AUTO_ADVANCE_DESIGN.md](DIALOGUE_AUTO_ADVANCE_DESIGN.md) — Auto-advance feature specification
- [Malrik_Elenya/MALRIK_ELENYA_MIRROR_NARRATIVE.md](Malrik_Elenya/MALRIK_ELENYA_MIRROR_NARRATIVE.md) — Dual-arc design philosophy
- [Ravi/RAVI_ENCOUNTER_MICRO_BRANCHES.md](Ravi/RAVI_ENCOUNTER_MICRO_BRANCHES.md) — Conditional dialogue path implementation
- [VELINOR_NARRATIVE_WRITING_GUIDE.docx](VELINOR_NARRATIVE_WRITING_GUIDE.docx) — Narrative tone and character voice guidelines

---

**Last Updated:** 2026-11-18  
**Organization Version:** 2.0 (NPC folders + meta files + documentation subfolders)
