# Dialogue Mode Refactor: Quick Reference Guide

## 🎯 TL;DR

**Problem**: Dialogue system had state ambiguity causing NPC responses to overwrite, delays to affect everything, and incorrect modes.

**Solution**: Four explicit `DialogueMode` enums + UI completion signals + mode-based state machine.

**Result**: Deterministic dialogue flow, no race conditions, backwards compatible.

---

## 📋 Four Dialogue Modes at a Glance

### 1️⃣ NPCToNPC (Shared Dialogue)
- **Use When**: Multiple NPCs speak in sequence (exposition)
- **JSON Type**: `"type": "npc_shared"`
- **Player Sees**: Seamless speaker transitions
- **Shows Choices**: ❌ NO
- **Shows NPC Response**: ❌ NO
- **Waits For Input**: ❌ NO (auto-advances)
- **Example**: 
  ```json
  {
    "type": "npc_shared",
    "shared_dialogue": [
      { "speaker": "Ravi", "text": "..." },
      { "speaker": "Nima", "text": "..." }
    ]
  }
  ```

### 2️⃣ NPCToPlayer (NPC Responds)
- **Use When**: NPC always responds to player choice
- **JSON Type**: `"type": "npc_turn"`
- **Player Sees**: Prompt → Choices → NPC Response → Next Beat
- **Shows Choices**: ✅ YES
- **Shows NPC Response**: ✅ **ALWAYS**
- **Waits For Input**: ✅ YES
- **Example**:
  ```json
  {
    "type": "npc_turn",
    "tone_choices": [
      {
        "text": "...",
        "npc_response": "NPC says: ..."
      }
    ]
  }
  ```

### 3️⃣ PlayerInnerThought (Monologue)
- **Use When**: Player thinks/reflects (no NPC response needed)
- **JSON Type**: `"type": "player_posture"` + NO choices
- **Player Sees**: Italicized inner thought → Auto-advance
- **Shows Choices**: ❌ NO
- **Shows NPC Response**: ❌ NO
- **Waits For Input**: ❌ NO (auto-advances)
- **Example**:
  ```json
  {
    "type": "player_posture",
    "active_speaker": "Player",
    "prompt": "<i>I wonder what they're thinking...</i>",
    "next_beat_id": 2
  }
  ```

### 4️⃣ PlayerActionChoice (Player Acts)
- **Use When**: Player chooses action with optional NPC response
- **JSON Type**: `"type": "player_posture"` + HAS choices
- **Player Sees**: Prompt → Choices → Result Text → (Optional NPC Response) → Next Beat
- **Shows Choices**: ✅ YES
- **Shows NPC Response**: ⚠️ OPTIONAL (controlled by next beat's mode)
- **Waits For Input**: ✅ YES
- **Example**:
  ```json
  {
    "type": "player_posture",
    "tone_choices": [
      {
        "text": "Approach them",
        "result_text": "You move closer..."
      }
    ]
  }
  ```

---

## 🔧 How to Specify Mode

### Option A: Explicit (Recommended)
```json
{
  "id": 1,
  "type": "npc_turn",
  "mode": "NPCToPlayer",  // ← Explicit
  "prompt": "...",
  "tone_choices": [...]
}
```

### Option B: Implicit (Auto-Inferred)
```json
{
  "id": 1,
  "type": "npc_turn",
  // mode is auto-inferred to NPCToPlayer
  "prompt": "...",
  "tone_choices": [...]
}
```

**Inference Rules**:
- `type == "npc_shared"` → NPCToNPC
- `type == "player_posture"` + NO choices + `active_speaker == "Player"` → PlayerInnerThought
- `type == "npc_turn"` + HAS choices → NPCToPlayer
- `type == "player_posture"` + HAS choices → PlayerActionChoice

---

## 💬 Key Fields

### Per-Beat
| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `type` | string | - | "player_posture", "npc_turn", "npc_shared" |
| `mode` | enum | inferred | Explicit DialogueMode (optional) |
| `responseWindow` | float | 0.0 | Seconds to wait after NPC response before showing next beat |
| `active_speaker` | string | - | "Player", "Nima", "Ravi", etc. |
| `shared_dialogue` | array | - | For mode NPCToNPC: array of {speaker, text} |

### Per-Choice
| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `tone` | string | - | "T", "O", "N", "E" |
| `text` | string | - | Button label (player choice text) |
| `result_text` | string | "" | Action description shown after choice |
| `npc_response` | string | "" | NPC's direct response (for NPCToPlayer mode) |
| `responseWindowOverride` | float | -1 | Per-choice delay override (-1 = use beat default) |

---

## 🚀 Common Usage Patterns

### Pattern 1: Simple NPC Dialogue
```json
{
  "id": 1,
  "type": "npc_turn",
  "active_speaker": "Nima",
  "prompt": "What do you want?",
  "tone_choices": [
    {
      "tone": "T",
      "text": "I need help",
      "npc_response": "Help is expensive here."
    }
  ],
  "next_beat_id": 2
}
```

### Pattern 2: Player Action with Consequence
```json
{
  "id": 1,
  "type": "player_posture",
  "prompt": "Do you pick the lock?",
  "tone_choices": [
    {
      "tone": "O",
      "text": "Attempt it",
      "result_text": "Your hands shake slightly as you work the lock..."
    }
  ],
  "next_beat_id": 2
}
```

### Pattern 3: NPC to NPC Exposition
```json
{
  "id": 1,
  "type": "npc_shared",
  "shared_dialogue": [
    { "speaker": "Ravi", "text": "They're getting closer." },
    { "speaker": "Nima", "text": "Then we move the artifact." }
  ],
  "next_beat_id": 2
}
```

### Pattern 4: Player Reflection
```json
{
  "id": 1,
  "type": "player_posture",
  "active_speaker": "Player",
  "prompt": "This doesn't feel right. Something is very wrong here.",
  "next_beat_id": 2
}
```

---

## ⚡ Troubleshooting

### ❓ NPC response not showing
**Check**: Is mode `NPCToPlayer`?  
**Fix**: `"type": "npc_turn"` with `"mode": "NPCToPlayer"` or let it infer  
```json
{ "type": "npc_turn", "tone_choices": [...] }
// ↓ infers to NPCToPlayer
```

### ❓ Choices showing on inner thought
**Check**: Is beat using PlayerInnerThought?  
**Fix**: Remove `tone_choices` and set `active_speaker: "Player"`  
```json
{
  "type": "player_posture",
  "active_speaker": "Player",
  "prompt": "Inner thought...",
  "tone_choices": []  // ← Keep empty or remove
}
```

### ❓ NPC response showing too fast
**Check**: Is `responseWindow` set?  
**Fix**: Add delay to beat:  
```json
{
  "id": 1,
  "type": "npc_turn",
  "responseWindow": 2.0,  // ← Add this
  "tone_choices": [...]
}
```

### ❓ Rapid dialogue feels slow
**Check**: Are `responseWindow` delays too long?  
**Fix**: Reduce per-beat delays:  
```json
{
  "responseWindow": 0.5  // ← Reduced from 2.0
}
```

---

## 📊 Mode Decision Tree

```
START
  ↓
Is this NPC-to-NPC exposition (multiple speakers)?
  YES → Use NPCToNPC (shared_dialogue array)
  NO → Continue
  ↓
Is this player monologue with NO choices?
  YES → Use PlayerInnerThought
  NO → Continue
  ↓
Is this NPC turn with player choice and NPC response?
  YES → Use NPCToPlayer
  NO → Continue
  ↓
Is this player action choice?
  YES → Use PlayerActionChoice
  NO → Default to NPCToNPC
```

---

## 🔄 UI Flow Sequences

### NPCToPlayer Flow
```
1. ShowDialogue(NPC, "What do you want?")
2. ShowChoices([T][O][N][E])
3. Player clicks
4. ShowDialogue(NPC, "Your choice: ...")
5. WaitForDisplayComplete()
6. ShowDialogue(Next, "...")
```

### PlayerActionChoice Flow
```
1. ShowDialogue("", "What do you do?")
2. ShowChoices([T][O][N][E])
3. Player clicks
4. ShowDialogue("", "You do this...")
5. WaitForDisplayComplete()
6. ShowDialogue(Next, "...")  [No NPC response unless next beat requires it]
```

### PlayerInnerThought Flow
```
1. ShowDialogue("", "<i>I wonder...</i>")
2. WaitForDisplayComplete()
3. AutoAdvance to next beat
4. ShowDialogue(Next, "...")
```

### NPCToNPC Flow
```
1. ShowDialogue(Ravi, "Text 1")
2. AutoAdvance
3. ShowDialogue(Nima, "Text 2")
4. AutoAdvance
5. ShowDialogue(Next, "...")
```

---

## 📝 Implementation Checklist

When creating a new dialogue scene:

- [ ] Define beats with clear `type` values
- [ ] For each beat, ask: "What mode is this?"
- [ ] Add explicit `"mode"` OR rely on inference
- [ ] If NPCToPlayer: ensure `npc_response` filled
- [ ] If PlayerActionChoice: fill `result_text`
- [ ] If PlayerInnerThought: remove `tone_choices`
- [ ] If NPCToNPC: use `shared_dialogue` array
- [ ] Set `responseWindow` if needed (default 0)
- [ ] Test with JSON validator
- [ ] Load in game and verify dialogue flow

---

## 🧪 Quick Test

To verify mode inference works:

```json
{
  "id": 1,
  "type": "player_posture",
  "active_speaker": "Player",
  "prompt": "Inner thought (no choices)",
  "next_beat_id": 2
}
// ↓ Infers to: PlayerInnerThought
```

```json
{
  "id": 1,
  "type": "player_posture",
  "active_speaker": "Player",
  "prompt": "What do you do?",
  "tone_choices": [...]
  "next_beat_id": 2
}
// ↓ Infers to: PlayerActionChoice
```

```json
{
  "id": 1,
  "type": "npc_turn",
  "active_speaker": "Nima",
  "prompt": "Question?",
  "tone_choices": [...]
  "next_beat_id": 2
}
// ↓ Infers to: NPCToPlayer
```

---

## 🎓 Quick Learning

- **State Ambiguity**: System had to guess mode from data
- **Explicit is Better**: Declare mode once, no guessing
- **UI Completion**: Use actual signal instead of blind wait
- **Backwards Compatible**: Old JSON still works (inference)

---

## 📚 Further Reading

- `DIALOGUE_SYSTEM_STATE_ANALYSIS.md` - Deep dive into the problem
- `DIALOGUE_MODE_REFACTOR_COMPLETE.md` - Implementation details
- `DIALOGUE_MODE_REFACTOR_EXAMPLES.md` - Full JSON examples

---

**Last Updated**: September 9, 2026  
**Status**: ✅ Complete & Ready for Use
