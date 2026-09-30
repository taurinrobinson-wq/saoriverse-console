# Voiceover Setup - Simplified Guide

## The Simple System

Each dialogue piece in your JSON gets an `audio_clip` field. If you specify a filename, it tries to load it. If the file doesn't exist, it just skips silently.

## Naming Convention

Use this pattern for all your audio files:

```
{speaker}_{dialogue_id}_{beat_id}[_{tone}][_npc].ogg
```

### Components

| Part | Example | Notes |
|------|---------|-------|
| speaker | `Saori` | Character name from `active_speaker` |
| dialogue_id | `desert_encounter_01` | Short name for the scene |
| beat_id | `1` or `3_1` | Beat number (decimals use underscores) |
| tone | `T`, `O`, `N`, `E` | Only for choice responses (Trust, Observation, Narrative, Empathy) |
| _npc | suffix | Only for NPC responses to player choices |

## Real Examples

### Main Beat Dialogue
```json
{
  "id": 1,
  "active_speaker": "Saori",
  "prompt": "You are on your way to the market?",
  "audio_clip": "Saori_desert_encounter_01_1.ogg"
}
```
**File needed:** `Saori_desert_encounter_01_1.ogg`

### NPC Response to Choice
```json
{
  "tone": "T",
  "label": "Trust",
  "text": "Yeah. I'm looking for work...",
  "npc_response": "I cannot offer any of that.",
  "audio_clip_on_response": "Saori_desert_encounter_01_1_T_npc.ogg"
}
```
**File needed:** `Saori_desert_encounter_01_1_T_npc.ogg`

### Second Beat
```json
{
  "id": 2,
  "active_speaker": "Saori",
  "prompt": "Some other dialogue...",
  "audio_clip": "Saori_desert_encounter_01_2.ogg"
}
```
**File needed:** `Saori_desert_encounter_01_2.ogg`

### Decimal Beat ID
```json
{
  "id": 2.1,
  "active_speaker": "Saori",
  "prompt": "...",
  "audio_clip": "Saori_desert_encounter_01_2_1.ogg"
}
```
**Note:** Beat ID `2.1` becomes `2_1` in the filename

## Tone Codes

| Code | Meaning |
|------|---------|
| T | Trust |
| O | Observation |
| N | Narrative Presence |
| E | Empathy |

Only include tone codes for NPC responses to player choices (add `_npc` suffix).

## File Organization

```
Resources/Audio/Voiceover/{scene_id}/{filename}.ogg
```

Example:
```
Resources/Audio/Voiceover/desert_encounter_01/
├── Saori_desert_encounter_01_1.ogg           (Beat 1 intro)
├── Saori_desert_encounter_01_1_T_npc.ogg     (Trust response)
├── Saori_desert_encounter_01_1_O_npc.ogg     (Observation response)
├── Saori_desert_encounter_01_1_N_npc.ogg     (Narrative response)
├── Saori_desert_encounter_01_1_E_npc.ogg     (Empathy response)
├── Saori_desert_encounter_01_2.ogg           (Beat 2 intro)
└── ...
```

## How It Works

1. **In JSON:** Specify `audio_clip` field with filename
2. **VoiceoverManager:** Tries to load the file from Resources
3. **If found:** Plays the audio
4. **If missing:** Skips silently (no errors, no warnings)

## JSON Setup

Leave the `audio_clip` field empty if you don't have audio yet:

```json
{
  "audio_clip": ""
}
```

Or just omit it. Either way, dialogue works perfectly without audio. When you have the file ready, fill it in:

```json
{
  "audio_clip": "Saori_desert_encounter_01_1.ogg"
}
```

## Workflow

1. **Write JSON with empty audio_clip fields**
   ```json
   "audio_clip": ""
   ```

2. **Test game** - everything works, just no audio yet ✓

3. **Record voiceovers** when you're ready

4. **Export as .ogg files** using the naming convention

5. **Drop in Resources/Audio/Voiceover/{scene_id}/**

6. **Update JSON** with the filename:
   ```json
   "audio_clip": "Saori_desert_encounter_01_1.ogg"
   ```

7. **Test game** - voiceover plays ✓

## Console Output

### File Found
```
[VoiceoverManager] Loaded voiceover: Audio/Voiceover/desert_encounter_01/Saori_desert_encounter_01_1
[VoiceoverManager] Playing: desert_encounter_01/Saori_desert_encounter_01_1
```

### File Missing (Expected)
When the file doesn't exist, the system just silently skips it. No warnings, no errors. Dialogue continues normally without audio.

## Complete Example

### Beat 1 in JSON
```json
{
  "id": 1,
  "type": "npc_turn",
  "active_speaker": "Saori",
  "prompt": "You are on your way to the market?",
  "audio_clip": "Saori_desert_encounter_01_1.ogg",
  "tone_choices": [
    {
      "tone": "T",
      "label": "Trust",
      "text": "Yeah. I'm looking for work, food, and a place to stay.",
      "npc_response": "I cannot offer any of that.",
      "audio_clip_on_response": "Saori_desert_encounter_01_1_T_npc.ogg"
    },
    {
      "tone": "O",
      "label": "Observation",
      "text": "Looks like you're headed somewhere too?",
      "npc_response": "I'm just passing through.",
      "audio_clip_on_response": "Saori_desert_encounter_01_1_O_npc.ogg"
    }
  ]
}
```

### Files Needed
```
Saori_desert_encounter_01_1.ogg
Saori_desert_encounter_01_1_T_npc.ogg
Saori_desert_encounter_01_1_O_npc.ogg
```

### Folder Structure
```
Resources/Audio/Voiceover/desert_encounter_01/
├── Saori_desert_encounter_01_1.ogg
├── Saori_desert_encounter_01_1_T_npc.ogg
└── Saori_desert_encounter_01_1_O_npc.ogg
```

## Tips

- **Empty audio_clip?** Leave it as `""` or omit the field. Dialogue works without audio.
- **Missing file?** No problem. System skips silently. No errors.
- **Different character?** Just change the speaker name: `Ravi_desert_encounter_01_1.ogg`
- **Different scene?** Create new folder: `Resources/Audio/Voiceover/different_scene/`
- **Decimal beat ID?** Use underscore: Beat `3.1` → filename `3_1`

## Quick Checklist

Before recording:
- [ ] Scene name from `scene_id` field
- [ ] Speaker name from `active_speaker` field
- [ ] Beat numbers
- [ ] Tone codes (T, O, N, E)
- [ ] Which pieces have NPC responses (need `_npc` suffix)

When recording:
- [ ] Record NPC voice
- [ ] Export as .ogg format (44.1 kHz standard)
- [ ] Use exact naming convention
- [ ] Place in `Resources/Audio/Voiceover/{scene_id}/`
- [ ] Fill in `audio_clip` field in JSON

That's it!
