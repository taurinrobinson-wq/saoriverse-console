# Audio Fields Template for Dialogue JSON

Use this template when adding audio fields to other dialogue JSON files.

## Complete Example with All Audio Fields

```json
{
  "scene_id": "willy_glyph_01",
  "beats": [
    {
      "id": 1,
      "type": "npc_turn",
      "active_speaker": "Willy",
      "prompt": "Careful. That pile shifts. Saw a man lose a leg under one just like it.",
      "audio_clip": "Willy_willy_glyph_01_1",
      "tone_choices": [
        {
          "tone": "T",
          "label": "Trust",
          "text": "I'm not from around here.",
          "audio_clip_on_choice": "Lioren_willy_glyph_01_1_T",
          "result_text": "",
          "npc_response": "Hah. Then you're lucky ya still got all yah limbs.",
          "audio_clip_on_response": "Willy_willy_glyph_01_1_T_npc"
        },
        {
          "tone": "O",
          "label": "Observation",
          "text": "How long have you been out here?",
          "audio_clip_on_choice": "Lioren_willy_glyph_01_1_O",
          "result_text": "",
          "npc_response": "Long enough to know better.",
          "audio_clip_on_response": "Willy_willy_glyph_01_1_O_npc"
        },
        {
          "tone": "N",
          "label": "NarrativePresence",
          "text": "This place doesn't look safe.",
          "audio_clip_on_choice": "Lioren_willy_glyph_01_1_N",
          "result_text": "",
          "npc_response": "Safe is for other places.",
          "audio_clip_on_response": "Willy_willy_glyph_01_1_N_npc"
        },
        {
          "tone": "E",
          "label": "Empathy",
          "text": "That sounds like it hurt.",
          "audio_clip_on_choice": "Lioren_willy_glyph_01_1_E",
          "result_text": "",
          "npc_response": "It did. Ah-hahaha.",
          "audio_clip_on_response": "Willy_willy_glyph_01_1_E_npc"
        }
      ]
    }
  ]
}
```

## Field Descriptions

### Beat Level
- **`audio_clip`** ← NPC's main dialogue for this beat
  - Format: `{speaker}_{scene_id}_{beat_id}`
  - Example: `Willy_willy_glyph_01_1`
  - File: `Assets/Resources/Audio/Voiceover/willy_glyph_01/Willy_willy_glyph_01_1.wav`

### Choice Level (Per Tone)

- **`audio_clip_on_choice`** ← Player's voiced choice line
  - Format: `{speaker}_{scene_id}_{beat_id}_{tone}`
  - Example: `Lioren_willy_glyph_01_1_T`
  - File: `Assets/Resources/Audio/Voiceover/willy_glyph_01/Lioren_willy_glyph_01_1_T.wav`
  - Note: No `_npc` suffix for player lines

- **`audio_clip_on_response`** ← NPC's response to this specific tone
  - Format: `{speaker}_{scene_id}_{beat_id}_{tone}_npc`
  - Example: `Willy_willy_glyph_01_1_T_npc`
  - File: `Assets/Resources/Audio/Voiceover/willy_glyph_01/Willy_willy_glyph_01_1_T_npc.wav`
  - Note: Includes `_npc` suffix for NPC lines

## Tone Mapping

| Code | Label | Audio Suffix |
|------|-------|--------------|
| T | Trust | `_T` |
| O | Observation | `_O` |
| N | NarrativePresence | `_N` |
| E | Empathy | `_E` |

## File Naming Convention

### For NPC Beat Intro
```
{NPC_NAME}_{SCENE_ID}_{BEAT_ID}.wav
```
Example: `Saori_saori_desert_encounter_01_1.wav`

### For Player Choice
```
Lioren_{SCENE_ID}_{BEAT_ID}_{TONE}.wav
```
(Player character is typically "Lioren", adjust if different)
Examples:
- `Lioren_saori_desert_encounter_01_1_T.wav`
- `Lioren_saori_desert_encounter_01_1_O.wav`
- `Lioren_saori_desert_encounter_01_1_N.wav`
- `Lioren_saori_desert_encounter_01_1_E.wav`

### For NPC Response
```
{NPC_NAME}_{SCENE_ID}_{BEAT_ID}_{TONE}_npc.wav
```
Examples:
- `Saori_saori_desert_encounter_01_1_T_npc.wav`
- `Saori_saori_desert_encounter_01_1_O_npc.wav`
- `Saori_saori_desert_encounter_01_1_N_npc.wav`
- `Saori_saori_desert_encounter_01_1_E_npc.wav`

## Quick Checklist for Adding Audio Fields

When updating an existing dialogue JSON:

- [ ] Add `audio_clip` to each beat (NPC's main dialogue)
- [ ] Add `audio_clip_on_choice` to each tone choice (player's line)
- [ ] Add `audio_clip_on_response` to each tone choice (NPC's response)
- [ ] Follow naming convention exactly
- [ ] Match `scene_id` from JSON in filenames
- [ ] Use tone codes: T, O, N, E
- [ ] Add `_npc` suffix only to NPC response lines

## Minimal Example (Single Beat, Single Tone)

```json
{
  "scene_id": "example_scene_01",
  "beats": [
    {
      "id": 1,
      "active_speaker": "NPC_Name",
      "prompt": "Opening dialogue...",
      "audio_clip": "NPC_Name_example_scene_01_1",
      "tone_choices": [
        {
          "tone": "T",
          "label": "Trust",
          "text": "Player's response...",
          "audio_clip_on_choice": "Lioren_example_scene_01_1_T",
          "npc_response": "NPC's reply...",
          "audio_clip_on_response": "NPC_Name_example_scene_01_1_T_npc"
        }
      ]
    }
  ]
}
```

## Generating Placeholder Files

For any dialogue JSON with audio fields, generate placeholders:

```bash
# Activate Python virtual environment (if needed)
cd c:\saoriverse-console

# Run the placeholder generator
python create_audio_placeholders.py
```

This will:
1. Read the JSON files
2. Extract all `audio_clip` references
3. Generate silent WAV files in the appropriate folders
4. Show which files were created vs. already exist

## Folder Structure Per Scene

Each scene gets its own folder:

```
Assets/Resources/Audio/Voiceover/
├── scene_id_01/
│   ├── Speaker_scene_id_01_1.wav
│   ├── Lioren_scene_id_01_1_T.wav
│   ├── Speaker_scene_id_01_1_T_npc.wav
│   ├── Lioren_scene_id_01_1_O.wav
│   ├── Speaker_scene_id_01_1_O_npc.wav
│   └── ... (continue for N and E tones)
├── scene_id_02/
│   └── ... (same structure)
└── scene_id_03/
    └── ... (same structure)
```

## Automation: Adding Fields to Existing JSON

Manual process:
1. Open JSON in text editor
2. Add `"audio_clip": ""` to each beat
3. Add `"audio_clip_on_choice": ""` to each tone_choice
4. Add `"audio_clip_on_response": ""` to each tone_choice
5. Fill in filenames following naming convention
6. Save and test

## Pre-Loading in Unity

Once JSON is updated and files are in place:

1. Assign JSON to NPCDialogueDriver in Inspector
2. OnValidate() runs automatically
3. Check console for: `"Pre-loaded X audio clips"`
4. Clips are now cached and ready for O(1) lookup

## Performance Notes

- Pre-loading happens once when JSON assigned
- Lookup during dialogue: O(1) dictionary, <1ms
- No file I/O during gameplay
- Safe to have many large audio files (Unity caches)

## Optional: Empty Fields

Audio fields can be left empty or omitted entirely:
```json
"audio_clip": "",
"audio_clip_on_choice": "",
"audio_clip_on_response": ""
```

Dialogue will work perfectly fine without audio. Fields can be filled in incrementally as voiceovers are recorded.

---

**Use this template when updating other dialogue JSON files with audio support.**
