# Adding Audio Fields to Dialogue JSON Files

## What We Just Did

Added `audio_clip` and `audio_clip_on_response` fields to the dialogue JSON files so you can specify which voiceover files to play.

## Template for Beat

Add this field to each beat:

```json
{
  "id": 1,
  "active_speaker": "Saori",
  "prompt": "You are on your way to the market?",
  "audio_clip": "Saori_saori_desert_encounter_01_1",
  ...
}
```

**Key:** `"audio_clip": "Saori_saori_desert_encounter_01_1"`

## Template for Tone Choices

Add this field to each tone choice response:

```json
{
  "tone": "T",
  "label": "Trust",
  "text": "Yeah. I'm looking for work...",
  "npc_response": "I cannot offer any of that.",
  "audio_clip_on_response": "Saori_saori_desert_encounter_01_1_T_npc",
  ...
}
```

**Key:** `"audio_clip_on_response": "Saori_saori_desert_encounter_01_1_T_npc"`

## Naming Convention

The audio filename should follow this pattern:

```
{speaker}_{scene_id}_{beat_id}[_{tone}][_npc].ogg
```

But in JSON, you can omit the `.ogg` extension - it's added automatically.

### Examples

**NPC Main Dialogue (Beat 1):**
```
JSON: "Saori_saori_desert_encounter_01_1"
File: Saori_saori_desert_encounter_01_1.ogg
```

**NPC Response to Trust Tone:**
```
JSON: "Saori_saori_desert_encounter_01_1_T_npc"
File: Saori_saori_desert_encounter_01_1_T_npc.ogg
```

**NPC Response to Observation Tone:**
```
JSON: "Saori_saori_desert_encounter_01_1_O_npc"
File: Saori_saori_desert_encounter_01_1_O_npc.ogg
```

**NPC Response to Narrative Tone:**
```
JSON: "Saori_saori_desert_encounter_01_1_N_npc"
File: Saori_saori_desert_encounter_01_1_N_npc.ogg
```

**NPC Response to Empathy Tone:**
```
JSON: "Saori_saori_desert_encounter_01_1_E_npc"
File: Saori_saori_desert_encounter_01_1_E_npc.ogg
```

## How to Update All Dialogue Files

For each dialogue JSON file:

1. **Add to each beat:**
   ```json
   "audio_clip": "{speaker}_{scene_id}_{beat_id}",
   ```

2. **Add to each tone choice:**
   ```json
   "audio_clip_on_response": "{speaker}_{scene_id}_{beat_id}_{tone}_npc",
   ```

3. **Tone code mapping:**
   - T = Trust
   - O = Observation
   - N = Narrative Presence
   - E = Empathy

## File Organization

Once you record voiceovers, place them here:

```
Resources/Audio/Voiceover/{scene_id}/{filename}.ogg
```

Example:
```
Resources/Audio/Voiceover/saori_desert_encounter_01/
├── Saori_saori_desert_encounter_01_1.ogg
├── Saori_saori_desert_encounter_01_1_T_npc.ogg
├── Saori_saori_desert_encounter_01_1_O_npc.ogg
├── Saori_saori_desert_encounter_01_1_N_npc.ogg
├── Saori_saori_desert_encounter_01_1_E_npc.ogg
├── Saori_saori_desert_encounter_01_2.ogg
└── ...
```

## How It Works

1. VoiceoverManager reads the `audio_clip` or `audio_clip_on_response` field from JSON
2. Tries to load the file from Resources
3. If found → plays it
4. If missing → skips silently (no errors)

## Empty Fields (Start Here)

You can leave the fields empty initially:

```json
"audio_clip": "",
"audio_clip_on_response": ""
```

Dialogue will work perfectly without any audio. When you record voiceovers, just fill in the filenames.

## Complete Example

Here's what a complete beat with all audio fields looks like:

```json
{
  "id": 1,
  "type": "npc_turn",
  "active_speaker": "Saori",
  "portrait_expression": "mysterious",
  "prompt": "You are on your way to the market?",
  "audio_clip": "Saori_saori_desert_encounter_01_1",
  "tone_choices": [
    {
      "tone": "T",
      "label": "Trust",
      "text": "Yeah. I'm looking for work, food, and a place to stay.",
      "npc_response": "I cannot offer any of that.",
      "audio_clip_on_response": "Saori_saori_desert_encounter_01_1_T_npc",
      "portrait_expression_on_response": "sad"
    },
    {
      "tone": "O",
      "label": "Observation",
      "text": "Looks you're headed somewhere too?",
      "npc_response": "I'm just passing through.",
      "audio_clip_on_response": "Saori_saori_desert_encounter_01_1_O_npc",
      "portrait_expression_on_response": "neutral"
    },
    {
      "tone": "N",
      "label": "NarrativePresence",
      "text": "Anything is better than being stuck out here.",
      "npc_response": "Hm... In theory...",
      "audio_clip_on_response": "Saori_saori_desert_encounter_01_1_N_npc",
      "portrait_expression_on_response": "mysterious"
    },
    {
      "tone": "E",
      "label": "Empathy",
      "text": "I just wanna be useful... and maybe get a meal.",
      "npc_response": "A practical instinct. Good.",
      "audio_clip_on_response": "Saori_saori_desert_encounter_01_1_E_npc",
      "portrait_expression_on_response": "guarded_hopefulness"
    }
  ]
}
```

## Next Steps

1. **Apply this pattern to all dialogue JSON files**
2. **Leave fields empty if you don't have audio yet** (dialogue still works!)
3. **When ready to record:** Use the naming convention for your voiceover files
4. **Place voiceovers** in `Resources/Audio/Voiceover/{scene_id}/`
5. **Fill in the JSON fields** with the audio filenames
6. **Voiceovers play automatically!**
