# Voiceover Naming Convention - Quick Reference

## File Structure

```
Resources/
├── Audio/
│   └── Voiceover/
│       ├── nima_encounter_01/          ← scene_id (from JSON)
│       │   ├── Nima_nima_encounter_01_1.ogg           [Beat 1, main NPC line]
│       │   ├── Nima_nima_encounter_01_1_T_npc.ogg     [Beat 1, Trust response]
│       │   ├── Nima_nima_encounter_01_1_O_npc.ogg     [Beat 1, Observation response]
│       │   ├── Nima_nima_encounter_01_1_N_npc.ogg     [Beat 1, Narrative response]
│       │   ├── Nima_nima_encounter_01_1_E_npc.ogg     [Beat 1, Empathy response]
│       │   ├── Nima_nima_encounter_01_2.ogg           [Beat 2, main NPC line]
│       │   ├── Nima_nima_encounter_01_2_T_npc.ogg     [Beat 2, Trust response]
│       │   └── ...
│       ├── ravi_encounter_01/
│       │   ├── Ravi_ravi_encounter_01_1.ogg
│       │   ├── Ravi_ravi_encounter_01_1_T_npc.ogg
│       │   └── ...
│       └── kaelen_confession_01/
│           └── ...
└── Dialogue/
    └── [.json dialogue files]
```

## Naming Pattern

### Main Beat Voiceover (NPC dialogue)
```
{Speaker}_{scene_id}_{beat_id}.ogg
```

```
Nima_nima_encounter_01_1.ogg
 ├─ Speaker: Nima
 ├─ Scene: nima_encounter_01
 └─ Beat: 1
```

### Response to Tone Choice
```
{Speaker}_{scene_id}_{beat_id}_{tone}_npc.ogg
```

```
Nima_nima_encounter_01_1_T_npc.ogg
 ├─ Speaker: Nima
 ├─ Scene: nima_encounter_01
 ├─ Beat: 1
 ├─ Tone: T (Trust)
 └─ Type: npc response
```

## Tone Legend

```
T → Trust
O → Observation
N → Narrative Presence
E → Empathy
C → Custom (rare)
```

## Beat ID Conversion

Decimal beats use underscores:

```
Beat JSON ID  →  Filename
    1         →  1
    2.1       →  2_1
    3.5       →  3_5
    10.25     →  10_25
```

## JSON Configuration

### Beat Definition
```json
{
  "id": 1,                           ← Beat ID
  "active_speaker": "Nima",          ← Speaker (for voiceover)
  "prompt": "Hello there...",
  "audio_clip": "",                  ← Leave empty (auto-load)
  "tone_choices": [
    {
      "tone": "T",
      "text": "Step forward",
      "npc_response": "You're brave...",
      "audio_clip_on_response": ""   ← Leave empty (auto-load)
    }
  ]
}
```

→ Automatically loads:
  - `Nima_scene_id_1.ogg` (beat intro)
  - `Nima_scene_id_1_T_npc.ogg` (Trust response)

## Common Scenarios

### 1. Nima's first meeting - Beat 1, NPC intro
**What Unity looks for:**
```
Nima_nima_encounter_01_1.ogg
```

**If missing:** Dialogue plays without audio ✓

### 2. Player chooses Trust tone
**What Unity looks for:**
```
Nima_nima_encounter_01_1_T_npc.ogg
```

**If missing:** Nima's text appears silently ✓

### 3. Beat with decimal ID (3.1)
**What Unity looks for:**
```
Nima_scene_01_3_1_T_npc.ogg
```

Note: `3.1` becomes `3_1` in filename

### 4. Override with manual filename
**In JSON:**
```json
{
  "audio_clip": "custom_nima_greeting"
}
```

**Loads:** `custom_nima_greeting.ogg` instead of auto-generated name

## Checklist for Adding Voiceovers

- [ ] Create `Resources/Audio/Voiceover/{scene_id}/` folder
- [ ] Export audio files as `.ogg`
- [ ] Use exact naming: `{Speaker}_{scene_id}_{beat_id}[_{tone}_npc].ogg`
- [ ] Place files in the folder
- [ ] Test in-game
- [ ] If audio doesn't play, check:
  - [ ] File exists in correct folder
  - [ ] Filename matches naming convention exactly
  - [ ] File is .ogg format
  - [ ] Console shows "Loaded voiceover" message
