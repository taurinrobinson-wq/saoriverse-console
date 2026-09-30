# Voiceover Setup in Dialogue JSON - Complete Example

## Example: Nima's First Encounter

### File: `nima_encounter_01.json`

```json
{
  "scene_id": "nima_encounter_01",
  "required_flags": ["kaelen_confessed == true"],
  "beats": [
    {
      "id": 1,
      "type": "npc_turn",
      "active_speaker": "Nima",
      "display_name": "Nima",
      "portrait_expression": "concerned",
      "prompt": "Hello there. I've been waiting for you.",
      "audio_clip": "",
      "tone_choices": [
        {
          "tone": "T",
          "label": "Trust",
          "text": "Step closer to her.",
          "result_text": "You approach slowly.",
          "npc_response": "Good. I needed to talk to someone I could trust.",
          "audio_clip_on_response": "",
          "portrait_expression_on_response": "relieved",
          "tone_effects": [
            {"stat": "Trust", "delta": 0.02}
          ],
          "remnants_effects": [
            {"target": "Nima", "stat": "trust", "delta": 0.01}
          ],
          "target": 2
        },
        {
          "tone": "O",
          "label": "Observation",
          "text": "Watch from a distance.",
          "result_text": "You stay back, observing.",
          "npc_response": "I see. You're always so cautious.",
          "audio_clip_on_response": "",
          "portrait_expression_on_response": "thoughtful",
          "tone_effects": [
            {"stat": "Observation", "delta": 0.02}
          ],
          "remnants_effects": [
            {"target": "Nima", "stat": "nuance", "delta": 0.01}
          ],
          "target": 2
        },
        {
          "tone": "N",
          "label": "Narrative",
          "text": "You know what's happening.",
          "result_text": "You acknowledge the situation.",
          "npc_response": "Yes. You always do.",
          "audio_clip_on_response": "",
          "portrait_expression_on_response": "resigned",
          "tone_effects": [
            {"stat": "NarrativePresence", "delta": 0.02}
          ],
          "remnants_effects": [
            {"target": "Nima", "stat": "authority", "delta": 0.01}
          ],
          "target": 2
        },
        {
          "tone": "E",
          "label": "Empathy",
          "text": "Are you okay?",
          "result_text": "You express concern.",
          "npc_response": "That's kind of you to ask. I'm... managing.",
          "audio_clip_on_response": "",
          "portrait_expression_on_response": "vulnerable",
          "tone_effects": [
            {"stat": "Empathy", "delta": 0.02}
          ],
          "remnants_effects": [
            {"target": "Nima", "stat": "sympathy", "delta": 0.01}
          ],
          "target": 2
        }
      ]
    },
    {
      "id": 2,
      "type": "npc_turn",
      "active_speaker": "Nima",
      "display_name": "Nima",
      "portrait_expression": "serious",
      "prompt": "We need to talk about what's coming.",
      "audio_clip": "",
      "next_beat_id": 3
    }
  ]
}
```

## Expected Audio Files

Place these in: `Resources/Audio/Voiceover/nima_encounter_01/`

### Beat 1 - Main NPC Dialogue
```
Nima_nima_encounter_01_1.ogg
└─ Nima's opening line: "Hello there. I've been waiting for you."
```

### Beat 1 - Trust Response
```
Nima_nima_encounter_01_1_T_npc.ogg
└─ Nima's response: "Good. I needed to talk to someone I could trust."
```

### Beat 1 - Observation Response
```
Nima_nima_encounter_01_1_O_npc.ogg
└─ Nima's response: "I see. You're always so cautious."
```

### Beat 1 - Narrative Response
```
Nima_nima_encounter_01_1_N_npc.ogg
└─ Nima's response: "Yes. You always do."
```

### Beat 1 - Empathy Response
```
Nima_nima_encounter_01_1_E_npc.ogg
└─ Nima's response: "That's kind of you to ask. I'm... managing."
```

### Beat 2 - Main NPC Dialogue
```
Nima_nima_encounter_01_2.ogg
└─ Nima's line: "We need to talk about what's coming."
```

## Folder Structure

```
Resources/Audio/Voiceover/nima_encounter_01/
├── Nima_nima_encounter_01_1.ogg
├── Nima_nima_encounter_01_1_T_npc.ogg
├── Nima_nima_encounter_01_1_O_npc.ogg
├── Nima_nima_encounter_01_1_N_npc.ogg
├── Nima_nima_encounter_01_1_E_npc.ogg
├── Nima_nima_encounter_01_2.ogg
└── [more files as needed...]
```

## How to Use

### Step 1: Keep JSON Fields Empty
In your JSON, leave the audio fields empty (as shown above):
```json
"audio_clip": "",
"audio_clip_on_response": ""
```

### Step 2: Create Audio Files
Record voiceovers and export as `.ogg` files with the correct names

### Step 3: Place in Resources Folder
Drop the files into `Resources/Audio/Voiceover/nima_encounter_01/`

### Step 4: Test
Run the dialogue in-game. Console will show:
```
[VoiceoverManager] Loaded voiceover: Audio/Voiceover/nima_encounter_01/Nima_nima_encounter_01_1
[VoiceoverManager] Playing: nima_encounter_01/Nima_nima_encounter_01_1
```

## Optional: Manual Filenames

If you need custom names instead of auto-generation, fill the fields:

```json
{
  "audio_clip": "nima_greeting_custom",
  "audio_clip_on_response": "nima_trust_response"
}
```

This will load:
- `Nima_nima_encounter_01_1.ogg` → `nima_greeting_custom.ogg`
- `Nima_nima_encounter_01_1_T_npc.ogg` → `nima_trust_response.ogg`

## Best Practices

1. **Use Empty Fields** - Let the auto-naming do the work
   ```json
   "audio_clip": ""  ✅ GOOD - auto-load
   ```

2. **Don't Mix** - Either use all auto-naming or all manual
   ```json
   "audio_clip": ""
   "audio_clip_on_response": ""  ✅ Consistent
   ```

3. **Omit if Empty** - Can also just leave the field out entirely
   ```json
   {
     "prompt": "...",
   }
   ```

4. **Recording Tips**
   - Record NPC as a single character
   - Keep tone responses under 5-10 seconds each
   - Use consistent mic/settings for all voiceovers in a scene
   - Export as Mono .ogg at 44.1 kHz

## Decimal Beat IDs

If your beat uses decimal notation (e.g., `3.1`):

```json
{
  "id": 3.1,
  "active_speaker": "Nima",
  "prompt": "...",
  "audio_clip": ""
}
```

The system automatically converts to: `Nima_scene_id_3_1.ogg` (no dot)

## Troubleshooting

### "Voiceover skipped" message
```
[VoiceoverManager] Voiceover skipped (file not found): nima_encounter_01/Nima_nima_encounter_01_1
```

✅ This is normal! File just doesn't exist yet. Record it when ready.

### No audio playing
1. Check file exists in correct folder
2. Check filename matches exactly (case-sensitive on some systems)
3. Check scene_id matches JSON: `"scene_id": "nima_encounter_01"`
4. Look for "Loaded voiceover" message in console

### File not found after recording
- Verify file extension is `.ogg` (not `.wav`, `.mp3`, etc.)
- Check folder path: `Resources/Audio/Voiceover/{scene_id}/`
- Verify filename spacing and underscores
- Check for extra spaces or hidden characters

## Complete Working Example

**Minimal JSON:**
```json
{
  "scene_id": "nima_encounter_01",
  "beats": [
    {
      "id": 1,
      "active_speaker": "Nima",
      "prompt": "Hello.",
      "audio_clip": "",
      "tone_choices": [
        {
          "tone": "T",
          "text": "Say hello back",
          "npc_response": "Good to see you.",
          "audio_clip_on_response": ""
        }
      ]
    }
  ]
}
```

**Files needed:**
1. `Nima_nima_encounter_01_1.ogg`
2. `Nima_nima_encounter_01_1_T_npc.ogg`

**Result:** Full voiced dialogue with no manual filename management!
