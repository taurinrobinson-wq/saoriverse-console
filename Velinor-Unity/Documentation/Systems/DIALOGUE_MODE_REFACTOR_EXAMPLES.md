# Dialogue Mode Refactor: JSON Examples

This document shows how to use the new `DialogueMode` system in your JSON files.

---

## 📋 Example 1: Player Action Choice (no NPC response shown)

```json
{
  "id": 1,
  "type": "player_posture",
  "active_speaker": "Player",
  "mode": "PlayerActionChoice",
  "prompt": "They're staring at you in the marketplace. What should you do?",
  "tone_choices": [
    {
      "tone": "T",
      "label": "Trust",
      "text": "Step toward the figures",
      "result_text": "You approach with open body language. The man's expression shifts slightly.",
      "npc_response": "",
      "tone_effects": [
        { "stat": "trust", "delta": 0.02 },
        { "stat": "observation", "delta": -0.015 }
      ],
      "remnants_effects": [
        { "target": "activeNpcId", "stat": "resolve", "delta": 0.01 },
        { "target": "activeNpcId", "stat": "trust", "delta": 0.01 }
      ]
    }
  ],
  "next_beat_id": 2
}
```

**Mode Behavior**:
1. Show prompt: "They're staring at you..."
2. Show choice buttons: [Trust] [Observation] [Narrative] [Empathy]
3. Player clicks "Trust"
4. Show result_text: "You approach with open body language..."
5. **NO NPC response shown** (mode prevents this)
6. Display next beat (beat_2)

**Key Difference**: `result_text` is shown, but no automatic NPC response lookup.

---

## 📖 Example 2: NPC to Player (NPC responds to choice)

```json
{
  "id": 2,
  "type": "npc_turn",
  "active_speaker": "Nima",
  "mode": "NPCToPlayer",
  "prompt": "NIMA: \"What do you want anyway? We don't trust outsiders.\"",
  "tone_choices": [
    {
      "tone": "T",
      "label": "Trust",
      "text": "I'm trying to find work. I'm new here.",
      "npc_response": "NIMA: \"Work is scarce for people who actually belong here. Intentions don't fill empty bellies.\"",
      "result_text": "",
      "tone_effects": [
        { "stat": "trust", "delta": 0.02 }
      ],
      "remnants_effects": [
        { "target": "Nima", "stat": "resolve", "delta": 0.01 },
        { "target": "Nima", "stat": "trust", "delta": 0.01 }
      ]
    }
  ],
  "responseWindow": 1.0,
  "next_beat_id": 3
}
```

**Mode Behavior**:
1. Show prompt: "NIMA: What do you want anyway..."
2. Show choice buttons
3. Player clicks "Trust"
4. **DO show NPC response** (mode requires this): "NIMA: Work is scarce..."
5. Wait for text display complete
6. Wait additional 1.0 seconds (responseWindow)
7. Display next beat (beat_3)

**Key Fields**:
- `npc_response`: Explicit response text in the choice
- `responseWindow`: Per-beat delay (can also set per-choice with `responseWindowOverride`)

---

## 💭 Example 3: Player Inner Thought (monologue, auto-advance)

```json
{
  "id": 5,
  "type": "player_inner",
  "active_speaker": "Player",
  "mode": "PlayerInnerThought",
  "prompt": "Something about this marketplace feels different. Watched. The air itself seems to breathe.",
  "tone_choices": [],
  "next_beat_id": 6
}
```

**Mode Behavior**:
1. Show prompt in italics (no speaker name)
2. **NO choice buttons shown** (no tone_choices)
3. **NO NPC response shown** (mode prevents this)
4. Auto-advance to beat_6 after brief delay
5. Seamless flow - player barely notices the transition

**Key Difference**: No `npc_response` field needed, no choice handling.

---

## 👥 Example 4: Shared NPC Dialogue (multiple speakers)

```json
{
  "id": 6,
  "type": "npc_shared",
  "mode": "NPCToNPC",
  "shared_dialogue": [
    {
      "speaker": "Ravi",
      "text": "The codex belongs to the old families. We shouldn't speak of it with strangers."
    },
    {
      "speaker": "Nima",
      "text": "But if they've already seen the glyph, silence won't help us."
    },
    {
      "speaker": "Ravi",
      "text": "Then we take a calculated risk. We tell them what they need to know—no more."
    }
  ],
  "next_beat_id": 7
}
```

**Mode Behavior**:
1. Show Ravi's line (auto-advance, no player interaction)
2. Show Nima's line (auto-advance)
3. Show Ravi's second line (auto-advance)
4. **NO player choices** - dialogue flows seamlessly
5. **NO NPC responses** to player choices
6. Automatically advance to beat_7 after all speakers finish

**Key Points**:
- `shared_dialogue` array instead of `tone_choices`
- System displays each speaker's line sequentially
- No player input during shared dialogue
- Perfect for NPC-to-NPC exposition scenes

---

## 🔄 Example 5: Mode Inference (Legacy Format - Still Works!)

If you DON'T specify `mode`, the system infers it automatically:

```json
{
  "id": 7,
  "type": "player_posture",
  "active_speaker": "Player",
  "prompt": "Do you tell them about your discovery?",
  "tone_choices": [
    {
      "tone": "T",
      "text": "Yes, tell them everything",
      "result_text": "You lay out the details of what you've found."
    },
    {
      "tone": "O",
      "text": "Hold back some details",
      "result_text": "You share only what seems relevant."
    }
  ],
  "next_beat_id": 8
}
```

**Inference**:
- `type == "player_posture"` ✓
- `active_speaker == "Player"` ✓
- `has tone_choices` ✓
- **→ Inferred as `PlayerActionChoice`**

No need to add `"mode": "PlayerActionChoice"` - it's automatic!

---

## 🎯 Decision Tree: Which Mode to Use?

```
Is this multiple NPCs speaking in sequence (exposition)?
  → YES: Use NPCToNPC (mode: "npc_shared", shared_dialogue array)
  → NO: Continue...

Is this a player inner thought with no choices?
  → YES: Use PlayerInnerThought (type: "player_posture", active_speaker: "Player", no choices)
  → NO: Continue...

Is this an NPC responding to player choices?
  → YES: Use NPCToPlayer (type: "npc_turn", always has NPC response)
  → NO: Continue...

Is this a player action with optional NPC response?
  → YES: Use PlayerActionChoice (type: "player_posture" with choices)
  → NO: Default to NPCToNPC
```

---

## 📊 Mode Comparison Table

| Mode | active_speaker | type | Has Choices? | Shows NPC Response? | Auto-Advances? |
|------|---|---|---|---|---|
| **NPCToNPC** | "Shared" | "npc_shared" | No | No | Yes (seamless) |
| **NPCToPlayer** | NPC name | "npc_turn" | Yes | **Always** | No (waits for choice) |
| **PlayerInnerThought** | "Player" | "player_posture" | No | No | Yes (after brief delay) |
| **PlayerActionChoice** | "Player" | "player_posture" | Yes | Optional | No (waits for choice) |

---

## 🔧 Response Window Examples

### No delay (default)
```json
{
  "id": 2,
  "type": "npc_turn",
  "responseWindow": 0.0,
  "...": "..."
}
```
→ After NPC response shown, immediately displays next beat

### Quick delay (half second)
```json
{
  "id": 2,
  "type": "npc_turn",
  "responseWindow": 0.5,
  "...": "..."
}
```
→ Player has time to read response before next beat appears

### Longer delay (dramatic pause)
```json
{
  "id": 2,
  "type": "npc_turn",
  "responseWindow": 3.0,
  "...": "..."
}
```
→ Gives weight to a critical NPC response

### Per-choice override
```json
{
  "id": 2,
  "type": "npc_turn",
  "responseWindow": 1.0,
  "tone_choices": [
    {
      "tone": "T",
      "text": "...",
      "responseWindowOverride": 2.0  // This choice gets 2.0s instead of 1.0s
    }
  ]
}
```
→ One choice can have a custom delay without affecting others

---

## ⚠️ Common Mistakes to Avoid

### ❌ Mistake 1: NPC Response in PlayerActionChoice
```json
{
  "type": "player_posture",
  "mode": "PlayerActionChoice",
  "tone_choices": [
    {
      "npc_response": "The NPC says something"  // DON'T do this
    }
  ]
}
```
**Why?** PlayerActionChoice shows result_text, not npc_response. If you want NPC to respond, that's the NEXT beat.

✅ **Correct**:
```json
{
  "id": 1,
  "type": "player_posture",
  "mode": "PlayerActionChoice",
  "tone_choices": [
    {
      "result_text": "You do something...",
      "npc_response": ""  // Leave empty for this mode
    }
  ],
  "next_beat_id": 2  // NPC response happens in beat_2
}
```

### ❌ Mistake 2: Shared Dialogue with tone_choices
```json
{
  "type": "npc_shared",
  "mode": "NPCToNPC",
  "shared_dialogue": [...],
  "tone_choices": [...]  // Don't mix these!
}
```

✅ **Correct**:
```json
{
  "type": "npc_shared",
  "mode": "NPCToNPC",
  "shared_dialogue": [...]  // Use this OR tone_choices, not both
}
```

### ❌ Mistake 3: Inner Thought with NPC Response
```json
{
  "type": "player_posture",
  "active_speaker": "Player",
  "mode": "PlayerInnerThought",
  "prompt": "I wonder what they're thinking...",
  "npc_response": "The NPC says..."  // Don't do this
}
```

✅ **Correct**:
```json
{
  "type": "player_posture",
  "active_speaker": "Player",
  "mode": "PlayerInnerThought",
  "prompt": "I wonder what they're thinking..."
  // No npc_response for this mode
}
```

---

## 🧪 Testing Each Mode

### Test NPCToPlayer
```json
{
  "id": 1,
  "type": "npc_turn",
  "active_speaker": "Nima",
  "mode": "NPCToPlayer",
  "prompt": "What's your business here?",
  "tone_choices": [
    {
      "tone": "T",
      "text": "I'm looking for work",
      "npc_response": "Well, you've come to the right place. But work isn't free."
    }
  ],
  "next_beat_id": 2
}
```
**Expected**: Choice text shown → Player clicks → NPC response shown → Next beat

### Test PlayerActionChoice
```json
{
  "id": 1,
  "type": "player_posture",
  "active_speaker": "Player",
  "mode": "PlayerActionChoice",
  "prompt": "They're watching you. What do you do?",
  "tone_choices": [
    {
      "tone": "T",
      "text": "Step toward them",
      "result_text": "You move closer. They don't back away."
    }
  ],
  "next_beat_id": 2
}
```
**Expected**: Prompt shown → Choice → Result text shown → Next beat (NO NPC response between result and next beat)

### Test PlayerInnerThought
```json
{
  "id": 1,
  "type": "player_posture",
  "active_speaker": "Player",
  "mode": "PlayerInnerThought",
  "prompt": "Something's wrong. I can feel it.",
  "next_beat_id": 2
}
```
**Expected**: Inner thought shown in italics → Auto-advance → Next beat (no choices, no NPC response)

### Test NPCToNPC
```json
{
  "id": 1,
  "type": "npc_shared",
  "mode": "NPCToNPC",
  "shared_dialogue": [
    { "speaker": "Nima", "text": "Should we tell them?" },
    { "speaker": "Ravi", "text": "I don't think we have a choice." }
  ],
  "next_beat_id": 2
}
```
**Expected**: Dialogue flows seamlessly → Player never sees choice buttons → Next beat

---

## 📝 Migration Guide: Old JSON → New Format

### Old Format (Still Works!)
```json
{
  "id": 2,
  "type": "npc_turn",
  "active_speaker": "Nima",
  "prompt": "What do you want?",
  "tone_choices": [...]
}
```
→ System automatically infers `mode: NPCToPlayer`

### New Format (Explicit)
```json
{
  "id": 2,
  "type": "npc_turn",
  "active_speaker": "Nima",
  "mode": "NPCToPlayer",
  "prompt": "What do you want?",
  "tone_choices": [...]
}
```
→ More explicit, easier to validate and debug

**No migration needed!** Your existing JSON files will work unchanged.

---

## 🎬 Full Scene Example: Marketplace Discovery

Here's a complete scene showing all four modes in action:

```json
{
  "scene_id": "market_discovery_complete",
  "beats": [
    {
      "id": 1,
      "type": "player_posture",
      "active_speaker": "Player",
      "mode": "PlayerActionChoice",
      "prompt": "Two figures in the marketplace are staring at you. What's your move?",
      "tone_choices": [
        {
          "tone": "T",
          "text": "Approach them",
          "result_text": "You walk toward them with confidence. They don't flinch."
        }
      ],
      "next_beat_id": 2
    },
    {
      "id": 2,
      "type": "npc_turn",
      "active_speaker": "Ravi",
      "mode": "NPCToPlayer",
      "prompt": "RAVI: \"Brave or foolish. Time will tell.\"",
      "tone_choices": [
        {
          "tone": "O",
          "text": "Who are you?",
          "npc_response": "RAVI: \"Names have power here. First, prove you're worth knowing.\""
        }
      ],
      "responseWindow": 1.5,
      "next_beat_id": 3
    },
    {
      "id": 3,
      "type": "npc_shared",
      "mode": "NPCToNPC",
      "shared_dialogue": [
        {
          "speaker": "Nima",
          "text": "The codex. They might know about it."
        },
        {
          "speaker": "Ravi",
          "text": "Too early. We test them first."
        }
      ],
      "next_beat_id": 4
    },
    {
      "id": 4,
      "type": "player_inner",
      "active_speaker": "Player",
      "mode": "PlayerInnerThought",
      "prompt": "They're communicating without words. This is something I don't understand.",
      "next_beat_id": 5
    },
    {
      "id": 5,
      "type": "npc_turn",
      "active_speaker": "Ravi",
      "mode": "NPCToPlayer",
      "prompt": "RAVI: \"Tell us what you're looking for.\"",
      "tone_choices": [
        {
          "tone": "T",
          "text": "I'm seeking knowledge",
          "npc_response": "RAVI: \"Everyone seeks something. What makes you worth the risk?\""
        }
      ],
      "next_beat_id": 6
    }
  ]
}
```

**Flow**:
1. Beat 1: Player decides action (PlayerActionChoice)
2. Beat 2: Ravi responds to choice (NPCToPlayer)
3. Beat 3: Nima & Ravi confer (NPCToNPC - seamless)
4. Beat 4: Player's inner thought (PlayerInnerThought - italicized, auto-advance)
5. Beat 5: Ravi's question (NPCToPlayer - waits for response)

---

## ✅ Summary

The new mode system makes dialogue flow **predictable, maintainable, and extendable**:

- ✅ **Explicit**: Each beat clearly states its purpose (mode)
- ✅ **Flexible**: Mix and match modes within a single scene
- ✅ **Backwards Compatible**: Old JSON still works (auto-inferred modes)
- ✅ **Debuggable**: Clear error messages when mode/content mismatch
- ✅ **Performant**: No more guessing or blind waits

Use these examples as templates for your own dialogue scenes!

