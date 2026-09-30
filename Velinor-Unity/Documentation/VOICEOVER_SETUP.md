# Voiceover Setup Guide

## Overview

Voiceovers in Velinor dialogue are now **automatically loaded** using a logical naming convention. If a voiceover file doesn't exist, Unity simply skips it without errors.

## File Organization

All voiceover files go in:
```
Resources/Audio/Voiceover/{scene_id}/{filename}.ogg
```

Example:
```
Resources/Audio/Voiceover/nima_encounter_01/Nima_nima_encounter_01_1_T_npc.ogg
Resources/Audio/Voiceover/nima_encounter_01/Lioren_nima_encounter_01_1_T.ogg
```

## Naming Convention

### Beat/NPC Response Voiceover
```
{speaker}_{scene_id}_{beat_id}_{tone}_npc.ogg
```

- **speaker**: NPC character name (e.g., `Nima`, `Ravi`, `Lioren`)
- **scene_id**: Dialogue scene ID from JSON (e.g., `nima_encounter_01`)
- **beat_id**: Beat number, with decimals converted to underscores (e.g., `1` → `1`, `3.1` → `3_1`)
- **tone**: Tone choice (T, O, N, E) - only for choice responses
- **_npc**: Suffix indicating this is the NPC's response to a player choice

### Examples

#### NPC Main Dialogue (no tone)
```
Nima_nima_encounter_01_1.ogg
```
NPC Nima speaking during beat 1 of nima_encounter_01

#### NPC Response to Trust Tone Choice
```
Nima_nima_encounter_01_1_T_npc.ogg
```
Nima's response to the player's Trust (T) choice in beat 1

#### Player Choice Line (optional - rarely used)
```
Lioren_nima_encounter_01_1_T.ogg
```
Lioren's player choice line for the Trust option in beat 1 (no `_npc` suffix)

## Tone Codes

| Tone | Meaning |
|------|---------|
| `T` | Trust |
| `O` | Observation |
| `N` | Narrative Presence |
| `E` | Empathy |
| `C` | Custom/Unique choice |

## JSON Configuration

### Option 1: Automatic (Recommended)
Leave the `audio_clip` and `audio_clip_on_response` fields **empty or omitted**. The system will auto-generate filenames.

```json
{
  "id": 1,
  "active_speaker": "Nima",
  "prompt": "Hello there...",
  "audio_clip": ""
}
```

### Option 2: Manual (Legacy)
Specify the exact filename (without `.ogg`). This overrides auto-naming if provided.

```json
{
  "id": 1,
  "active_speaker": "Nima",
  "prompt": "Hello there...",
  "audio_clip": "nima_encounter_01_1_custom"
}
```

## Graceful Fallback

- ✅ File exists → Plays audio
- ❌ File missing → Skips silently (no warning, no error)
- ✅ Cache prevents re-loading the same file multiple times

## Beat ID Formatting

If your beat ID contains decimals (e.g., `3.1`, `2.5`), the naming system converts them to underscores:

| Beat ID | Filename |
|---------|----------|
| `1` | `...1.ogg` |
| `2.1` | `...2_1.ogg` |
| `3.5` | `...3_5.ogg` |
| `10.25` | `...10_25.ogg` |

## Workflow

1. **Add dialogue to JSON** (leave audio_clip fields empty)
2. **Test gameplay** - dialogue works without audio
3. **Record voiceovers** as needed
4. **Export to Resources/Audio/Voiceover/{scene_id}/**
5. **Use exact naming convention** - Unity finds and plays them automatically

## Example: Full Nima Encounter

Scene ID: `nima_encounter_01`

### Beat 1 NPC intro:
```
Nima_nima_encounter_01_1.ogg
```

### Beat 1 - Trust response:
```
Nima_nima_encounter_01_1_T_npc.ogg
```

### Beat 1 - Observation response:
```
Nima_nima_encounter_01_1_O_npc.ogg
```

### Beat 1 - Narrative response:
```
Nima_nima_encounter_01_1_N_npc.ogg
```

### Beat 1 - Empathy response:
```
Nima_nima_encounter_01_1_E_npc.ogg
```

## Debugging

Check the Console for:
- ✅ `[VoiceoverManager] Loaded voiceover: Audio/Voiceover/...` - File found and playing
- ℹ️ `[VoiceoverManager] Voiceover skipped (file not found): ...` - File doesn't exist yet (expected)

No warnings or errors mean the system is working correctly!

## Audio Settings

- **Format**: OGG Vorbis (compressed, Unity's preferred format)
- **Sample Rate**: 44.1 kHz (standard)
- **Channels**: Mono (dialogue) or Stereo
- **Compression**: Default Unity compression is fine
