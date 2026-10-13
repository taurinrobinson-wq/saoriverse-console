# Prompt Source Quick Guide

## One-Minute Overview

**Prompt Source** makes dialogue feel natural by having NPCs reference what the player just said. Instead of writing the same response twice, it pulls from the previous beat's choice.

## When to Use

Use `prompt_source` when:
- A beat follows immediately after a choice-based beat
- The NPC should respond to the player's selected tone
- You want to avoid duplicating text

Don't use if:
- The beat is standalone (no prior choices)
- The NPC ignores the player's input
- The beat is the final beat

## How to Add It

### Step 1: Identify the Flow
```
Beat 1 (NPC with choices) → Beat 2 (should reference Beat 1)
```

### Step 2: Add to Beat 2
In the beat that follows choices, add this field:

```json
{
  "id": 2,
  "type": "npc_turn",
  "active_speaker": "NPC_NAME",
  "prompt": "",
  "prompt_source": {
    "type": "previous_choice_response",
    "beat_id": 1,
    "choice_field": "npc_response"
  },
  "shared_beat": "The continuation of the dialogue..."
}
```

### Step 3: Fill In
- `beat_id`: The ID of the beat with the choices (usually the beat before this one)
- `choice_field`: Always use `"npc_response"` for choice responses
- Leave `prompt` empty (it will be replaced by the resolved response)
- Use `shared_beat` for any additional dialogue

### Step 4: Verify
Run the dialogue sequence and check that the player's chosen tone's response flows into this beat's shared_beat.

## Example

### Beat 1: Ravi's Question (with choices)
```json
{
  "id": 1,
  "type": "npc_turn",
  "active_speaker": "Ravi",
  "prompt": "What brings you here?",
  "tone_choices": [
    {
      "tone": "T",
      "text": "I'm looking for work.",
      "npc_response": "Work? There isn't much of that these days."
    },
    {
      "tone": "E",
      "text": "I want to help people.",
      "npc_response": "That's... unusual. Most people only help themselves."
    }
  ]
}
```

### Beat 2: Ravi Continues (with prompt_source)
```json
{
  "id": 2,
  "type": "npc_turn",
  "active_speaker": "Ravi",
  "prompt": "",
  "prompt_source": {
    "type": "previous_choice_response",
    "beat_id": 1,
    "choice_field": "npc_response"
  },
  "shared_beat": "Still, if you're serious, I might know someone who needs help."
}
```

### What the Player Sees

**If they chose T (Trust):**
```
Ravi: What brings you here?
Player: I'm looking for work.
Ravi: Work? There isn't much of that these days. Still, if you're serious, I might know someone who needs help.
```

**If they chose E (Empathy):**
```
Ravi: What brings you here?
Player: I want to help people.
Ravi: That's... unusual. Most people only help themselves. Still, if you're serious, I might know someone who needs help.
```

## Pro Tips

1. **Always leave `prompt` empty** when using `prompt_source` (it will be overwritten)
2. **Use `shared_beat` for continuation** after the response
3. **Test all tones** to make sure the responses flow naturally
4. **Don't use `prompt_source` for inner monologue beats** unless you know what you're doing
5. **Keep tone responses concise** so they don't overwhelm the screen

## Common Mistakes

❌ **Wrong:** Filling in both `prompt` and `prompt_source`
```json
{
  "prompt": "This text gets ignored",
  "prompt_source": { ... }  // This takes priority
}
```

✓ **Right:** Leave `prompt` empty
```json
{
  "prompt": "",
  "prompt_source": { ... }
}
```

---

❌ **Wrong:** Referencing a beat without choices
```json
{
  "prompt_source": {
    "beat_id": 3,  // Beat 3 has no tone_choices!
    "choice_field": "npc_response"
  }
}
```

✓ **Right:** Reference the beat with the actual choices
```json
{
  "prompt_source": {
    "beat_id": 1,  // Beat 1 has tone_choices
    "choice_field": "npc_response"
  }
}
```

---

❌ **Wrong:** Using incorrect `choice_field`
```json
{
  "choice_field": "player_response"  // Not a real field
}
```

✓ **Right:** Use `npc_response`
```json
{
  "choice_field": "npc_response"  // This is what stores the NPC's reply
}
```

## Testing Your Prompt Source

1. Save your dialogue file
2. Run the game in Unity
3. Trigger the dialogue
4. Select each different tone on Beat 1
5. Verify Beat 2 shows the correct response for each tone
6. Check that text flows naturally with `shared_beat`

## Troubleshooting

**Problem:** Prompt source text doesn't appear
- ✓ Check that `beat_id` matches an actual beat ID
- ✓ Verify the beat with that ID has `tone_choices`
- ✓ Ensure `choice_field` is `"npc_response"`

**Problem:** Text appears twice or looks wrong
- ✓ Check that `prompt` field is empty (not filled in)
- ✓ Look at the console for warning messages
- ✓ Verify the flow in the Dialogue Writer tool

**Problem:** Fallback text appears instead
- ✓ Check beat_id in prompt_source
- ✓ Verify the referenced beat exists
- ✓ Look for console errors

## Reference Files

See these files for working examples:
- `ravi_encounter_01.json` - Beats 2 & 6 use prompt_source
- `willy_concourse_ruins.json` - Beats 2 & 4 use prompt_source
- `nima_encounter_01.json` - Beats 2, 3, 5, 6, 7 use prompt_source
