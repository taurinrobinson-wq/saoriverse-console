# Voiceover Workflow - Visual Guide

## Complete System Overview

```
DIALOGUE JSON
    ↓
    ├─ scene_id: "nima_encounter_01"
    ├─ beat 1
    │   ├─ active_speaker: "Nima"
    │   ├─ prompt: "Hello there..."
    │   ├─ audio_clip: ""  ← Leave empty!
    │   └─ tone_choices
    │       └─ tone: "T"
    │           ├─ text: "Step forward"
    │           ├─ npc_response: "Good..."
    │           └─ audio_clip_on_response: ""  ← Leave empty!
    ↓
DIALOGUE MANAGER
    ↓
    ├─ DisplayBeat(beat)
    │   └─ voiceoverManager.PlayBeatVoiceover(sceneId, beat)
    │       ↓
    │       └─ Generates: "Nima_nima_encounter_01_1"
    │           ↓
    │           └─ Loads: Nima_nima_encounter_01_1.ogg
    │
    └─ ResolveChoice(beat, choice)
        └─ voiceoverManager.PlayChoiceResponseVoiceover(sceneId, beat, choice)
            ↓
            └─ Generates: "Nima_nima_encounter_01_1_T_npc"
                ↓
                └─ Loads: Nima_nima_encounter_01_1_T_npc.ogg
    ↓
VOICEOVER MANAGER
    ↓
    ├─ Auto-generates filename
    │   └─ {Speaker}_{scene_id}_{beat_id}[_{tone}_npc]
    ├─ Tries to load from Resources
    │   └─ Resources/Audio/Voiceover/{scene_id}/{filename}.ogg
    └─ If file exists → plays ✓
       If missing → skips silently ✓
    ↓
AUDIO OUTPUT
    ↓
    └─ Dialogue with voiceover!
```

## Filename Generation Logic

```
Input Data From JSON
    ├─ speaker: beat.active_speaker → "Nima"
    ├─ scene_id: root.scene_id → "nima_encounter_01"
    ├─ beat_id: beat.id → 1 (or 3.1 → 3_1)
    ├─ tone: choice.tone → "T"
    └─ is_npc: for response → true
        ↓
    BUILD FILENAME
        ├─ Start: {speaker}_{scene_id}_{beat_id}
        │   = Nima_nima_encounter_01_1
        ├─ Add tone (if applicable): _{tone}
        │   = Nima_nima_encounter_01_1_T
        ├─ Add _npc suffix (if response): _npc
        │   = Nima_nima_encounter_01_1_T_npc
        └─ Add extension: .ogg
            = Nima_nima_encounter_01_1_T_npc.ogg
        ↓
    LOAD PATH
        = Resources/Audio/Voiceover/nima_encounter_01/Nima_nima_encounter_01_1_T_npc.ogg
```

## Decision Tree for File Naming

```
NEW VOICEOVER FILE NEEDED?
    ↓
    Is it the main NPC dialogue for a beat?
    ├─ YES → {Speaker}_{scene_id}_{beat_id}.ogg
    │         Example: Nima_nima_encounter_01_1.ogg
    │
    └─ NO → Is it an NPC response to a player choice?
            ├─ YES → {Speaker}_{scene_id}_{beat_id}_{tone}_npc.ogg
            │         Example: Nima_nima_encounter_01_1_T_npc.ogg
            │
            └─ NO → Is it a player choice line?
                    ├─ YES → {Speaker}_{scene_id}_{beat_id}_{tone}.ogg
                    │         Example: Lioren_nima_encounter_01_1_T.ogg
                    │         (Note: no _npc suffix)
                    │
                    └─ UNCLEAR → Ask what scene, beat, and speaker!
```

## File Location Checklist

```
✓ Location: Resources/Audio/Voiceover/{scene_id}/
  Example: Resources/Audio/Voiceover/nima_encounter_01/

✓ Format: .ogg (OGG Vorbis)
  • 44.1 kHz sample rate
  • Mono or Stereo
  • Standard compression

✓ Naming: {Speaker}_{scene_id}_{beat_id}[_{tone}_npc].ogg
  • Exact case sensitivity (case-sensitive on some systems)
  • Underscores for decimals (3.1 → 3_1)
  • No spaces or special characters

✓ Scene ID: Must match JSON "scene_id" field
  Example: "nima_encounter_01" in JSON
           ↓
           nima_encounter_01 in filename
           ↓
           nima_encounter_01 in folder path
```

## Tone Mapping Quick Reference

```
DIALOGUE JSON              FILENAME
─────────────────────      ────────────────────
tone: "T"            →     ..._{T}_npc.ogg
tone: "O"            →     ..._{O}_npc.ogg
tone: "N"            →     ..._{N}_npc.ogg
tone: "E"            →     ..._{E}_npc.ogg
(no tone/main beat)  →     ...(no tone suffix).ogg
```

## Beat ID Handling

```
JSON Beat ID          Filename Beat ID
─────────────────     ─────────────────
1                →    1
2                →    2
2.1              →    2_1
3.5              →    3_5
10.25            →    10_25
1.1.1            →    1_1_1

Pattern: Replace all dots (.) with underscores (_)
```

## Real-World Example

### Dialogue JSON
```json
{
  "scene_id": "ravi_market_01",
  "beats": [
    {
      "id": 5,
      "active_speaker": "Ravi",
      "prompt": "You look familiar...",
      "audio_clip": "",
      "tone_choices": [
        {
          "tone": "T",
          "text": "I'm trustworthy",
          "npc_response": "I'll believe you",
          "audio_clip_on_response": ""
        }
      ]
    }
  ]
}
```

### Generated Filenames
1. **Main NPC dialogue:**
   ```
   Ravi_ravi_market_01_5.ogg
   └─ Ravi's line: "You look familiar..."
   ```

2. **Response to Trust choice:**
   ```
   Ravi_ravi_market_01_5_T_npc.ogg
   └─ Ravi's line: "I'll believe you"
   ```

### Required File Structure
```
Resources/Audio/Voiceover/ravi_market_01/
├── Ravi_ravi_market_01_5.ogg
└── Ravi_ravi_market_01_5_T_npc.ogg
```

### Unity Console Output
```
[VoiceoverManager] Loaded voiceover: Audio/Voiceover/ravi_market_01/Ravi_ravi_market_01_5
[VoiceoverManager] Playing: ravi_market_01/Ravi_ravi_market_01_5

[VoiceoverManager] Loaded voiceover: Audio/Voiceover/ravi_market_01/Ravi_ravi_market_01_5_T_npc
[VoiceoverManager] Playing: ravi_market_01/Ravi_ravi_market_01_5_T_npc
```

## Troubleshooting Decision Tree

```
Voiceover not playing?
    ↓
    Does console show "Voiceover skipped"?
    ├─ YES (expected)
    │   ├─ File not recorded yet? → Wait to record
    │   ├─ File in wrong location? → Move to Resources/Audio/Voiceover/{scene_id}/
    │   └─ Filename wrong? → Check naming against convention
    │
    └─ NO (no console message about voiceover)
        ├─ audio_clip field not empty? → Empty it so auto-load works
        └─ DialogueManager not calling PlayBeatVoiceover? → Check code update

Still not working?
    ↓
    ├─ Is file .ogg format? (not .wav, .mp3, etc.)
    ├─ Does folder exist? (Resources/Audio/Voiceover/{scene_id}/)
    ├─ Is scene_id correct? (matches JSON exactly)
    ├─ Is speaker name correct? (matches active_speaker field)
    ├─ Is beat ID correct? (3.1 becomes 3_1 in filename)
    └─ Is tone code correct? (T, O, N, E, or omitted for main beat)
```

## Success Indicators

✓ **Console shows "Loaded voiceover"**
  → File found and playing correctly

✓ **Console shows "Voiceover skipped"**
  → File not found yet (expected, record when ready)

✓ **No console messages about voiceover at all**
  → Either file loaded silently or audio_clip field has explicit value

✓ **Dialogue proceeds without audio**
  → Normal! System works without voiceovers

✗ **Warnings or errors about missing files**
  → Should NOT happen with this system (graceful degradation)
