# Voiceover System Setup Guide

The voiceover system allows dialogue beats and responses to have accompanying audio narration. The system gracefully handles missing audio files, making it safe to implement the infrastructure before recording voice actors.

## Overview

- **Files**: .ogg audio clips (compressed, game-optimized format)
- **Loading**: Automatic from Resources folder using beat/tone metadata
- **Playback**: Seamless with fade-out when player makes choices
- **Status**: Non-critical (dialogue works without audio)

## Folder Structure

```
Assets/Resources/Audio/Voiceover/
  {scene_id}/
    {npc_name}_{beat_id}.ogg           # NPC speaking during beat
    {npc_name}_{beat_id}_{tone}.ogg    # NPC response to player tone choice
```

## Example File Organization

For `ravi_nima_market_discovery.json` scene:

```
Assets/Resources/Audio/Voiceover/ravi_nima_market_discovery/
  Player_1.ogg              # Beat 1: Player's inner thought
  Nima_2.ogg                # Beat 2: Nima's opening line
  Nima_2_T.ogg              # Beat 2 Trust response
  Nima_2_O.ogg              # Beat 2 Observation response
  Nima_2_N.ogg              # Beat 2 Narrative response
  Nima_2_E.ogg              # Beat 2 Empathy response
  Ravi_4.ogg                # Beat 4: Ravi's warning
  Ravi_4_response_T.ogg     # Beat 4 Trust response
  Ravi_4_response_O.ogg     # Beat 4 Observation response
  Ravi_4_response_N.ogg     # Beat 4 Narrative response
  Ravi_4_response_E.ogg     # Beat 4 Empathy response
  Player_5.ogg              # Beat 5: Player's focus shift
```

## Tone Code Reference

Player tone codes used in filenames:
- `T` = Trust
- `O` = Observation
- `N` = Narrative/NarrativePresence
- `E` = Empathy
- `C` = Challenge (if used)

## Adding Audio to JSON

### Beat-level Audio

Add `audio_clip` field to any beat to play audio when the beat displays:

```json
{
  "id": 2,
  "type": "npc_turn",
  "active_speaker": "Nima",
  "audio_clip": "Nima_2",
  "prompt": "What do you want anyway? We don't trust outsiders.",
  "tone_choices": [...]
}
```

### Response-level Audio

Add `audio_clip_on_response` to any tone choice to play audio when the NPC responds:

```json
{
  "tone": "T",
  "label": "Trust",
  "text": "I'm trying to find work. I'm new here.",
  "npc_response": "Work is scarce for people who actually belong here...",
  "audio_clip_on_response": "Nima_2_T",
  "tone_effects": [...]
}
```

## Behavior

### Playback
1. When a beat displays with `audio_clip` set, the audio plays immediately
2. When player selects a tone choice, currently playing audio fades out over 0.3 seconds
3. NPC response audio (`audio_clip_on_response`) plays after the fade completes
4. When dialogue ends, any remaining audio stops immediately

### Missing Files
- If an audio file doesn't exist, the system logs a warning but continues normally
- Text dialogue displays regardless of audio availability
- This allows you to iterate on voice recording without breaking gameplay

### Volume & Timing
- Voiceover plays at full volume (1.0) by default
- Fade-out duration: 0.3 seconds (prevents jarring cuts)
- Audio stops immediately on dialogue end (not faded)

## Implementation Details

### VoiceoverManager
- Located: `Assets/Scripts/UI/VoiceoverManager.cs`
- Responsibilities:
  - Load .ogg clips from Resources/Audio/Voiceover/{sceneId}/{clipName}
  - Cache loaded clips to avoid repeated file I/O
  - Play/stop/fade voiceover
  - Handle missing files gracefully

### DialogueManager Integration
- Captures `scene_id` from JSON (used for file paths)
- Calls `VoiceoverManager.PlayVoiceover()` when beats/responses display
- Calls `FadeOutAndStop()` when player chooses
- Calls `StopVoiceover()` when dialogue ends

### BeatData Structure
```csharp
public string audio_clip;                      // Beat-level audio (e.g., "Nima_2")
public string audio_clip_on_response;          // Response audio (e.g., "Nima_2_T")
```

## Recording Guidelines

When ready to record voice acting:

1. **Naming Convention**: Use exact filenames from JSON
   - Example: `Nima_2_T.ogg` for Beat 2 Trust response
   - No variations or nicknames

2. **Audio Specs** (recommended):
   - Format: .ogg Vorbis
   - Sample Rate: 44100 Hz or 48000 Hz
   - Bit Depth: 16-bit
   - Mono or Stereo (both work)

3. **Recording Tips**:
   - Record in quiet environment (reduces post-processing)
   - Match character tone/emotion to portrait expression
   - Keep takes consistent length (don't artificially pad)
   - Name files immediately to match JSON references

4. **Post-Processing**:
   - Normalize audio to -1dB
   - Remove silence at start/end
   - Apply light EQ if needed
   - Export as .ogg at 128kbps bitrate (good quality/compression balance)

## Testing Without Audio

To test dialogue flow before recording:

1. Dialogue works perfectly without audio files
2. Warnings in console show which files are expected
3. Add audio files one scene at a time
4. Reload scene in Unity to pick up new audio files

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Audio not playing | Check filename matches JSON exactly (case-sensitive) |
| Audio cuts off mid-word | Ensure choice is made after audio completes, or fade duration is long enough |
| Console warnings about missing files | Normal during development; add .ogg file with matching name |
| Audio plays from wrong character | Verify `active_speaker` in JSON matches folder organization |
| Volume too quiet/loud | Adjust in AudioSource in VoiceoverManager or Mixer |

## Future Enhancements

Potential improvements:
- Voiceover subtitle display synced to audio playback
- Adjustable fade-out duration per beat
- Character-specific volume levels
- Audio ducking (lower voiceover when UI sounds play)
- Localization support (multiple language folders)
