# Voiceover System - Quick Start (2 Minutes)

## What You Need to Know

Your dialogue system now **auto-loads voiceovers** using a smart naming convention. Files that don't exist are simply skipped—no errors.

## The Pattern

```
{NPC_Name}_{scene_id}_{beat_id}[_{tone}_npc].ogg
```

**Real examples:**
- `Nima_nima_encounter_01_1.ogg` — Nima speaks in beat 1
- `Nima_nima_encounter_01_1_T_npc.ogg` — Nima responds to Trust choice
- `Ravi_ravi_market_01_2_O_npc.ogg` — Ravi responds to Observation choice

## Setup in 3 Steps

### 1. Keep JSON Simple
```json
{
  "scene_id": "nima_encounter_01",
  "beats": [
    {
      "id": 1,
      "active_speaker": "Nima",
      "prompt": "Hello there...",
      "audio_clip": "",  ← Leave empty
      "tone_choices": [
        {
          "tone": "T",
          "npc_response": "Good to meet you",
          "audio_clip_on_response": ""  ← Leave empty
        }
      ]
    }
  ]
}
```

### 2. Create Folder
```
Resources/Audio/Voiceover/nima_encounter_01/
```

### 3. Record and Export
- Export voiceovers as `.ogg` files
- Use exact names from the pattern
- Drop them in the folder
- Done! They'll play automatically

## Tone Codes

| Code | Meaning |
|------|---------|
| T | Trust |
| O | Observation |
| N | Narrative Presence |
| E | Empathy |

## Examples for Beat 1

| File | When it plays |
|------|---------------|
| `Nima_nima_encounter_01_1.ogg` | Beat 1 NPC intro |
| `Nima_nima_encounter_01_1_T_npc.ogg` | Player picks Trust |
| `Nima_nima_encounter_01_1_O_npc.ogg` | Player picks Observation |
| `Nima_nima_encounter_01_1_N_npc.ogg` | Player picks Narrative |
| `Nima_nima_encounter_01_1_E_npc.ogg` | Player picks Empathy |

## Decimal Beat IDs

If beat ID is `3.1`, use `3_1` in filename:
```
Nima_scene_id_3_1.ogg
Nima_scene_id_3_1_T_npc.ogg
```

## What You'll See

✅ File exists and plays:
```
[VoiceoverManager] Loaded voiceover: Audio/Voiceover/nima_encounter_01/Nima_nima_encounter_01_1
[VoiceoverManager] Playing: nima_encounter_01/Nima_nima_encounter_01_1
```

✅ File doesn't exist yet (totally fine):
```
[VoiceoverManager] Voiceover skipped (file not found): nima_encounter_01/Nima_nima_encounter_01_1
```

## That's It!

- No code changes needed
- Dialogue works without audio
- Add voiceovers whenever you want
- System finds and plays them automatically
- Missing files cause no problems

**Start recording whenever you're ready. The system is already looking for your files.**
