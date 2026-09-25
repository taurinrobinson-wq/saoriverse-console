# How to Use the New DialogueManager

## Quick Start

### 1. Setup in Scene
```csharp
// In your scene, create a GameObject with:
// - DialogueManager component
// - DialogueUIController component

// Assign your dialogue JSON in Inspector
public TextAsset dialogueJson;
```

### 2. Start Dialogue from an NPC

```csharp
// Called when player interacts with NPC or dialogue should start
public void OnTalkToNima()
{
    string npcId = "Nima";
    string startBeatId = "beat_1";
    
    // Load JSON and start at first beat
    DialogueManager.Instance.LoadDialogue(dialogueJsonAsset);
    DialogueManager.Instance.StartDialogue(npcId, startBeatId);
}
```

## Understanding the Four Dialogue Modes

### Mode 1: NPCToNPC (Shared Dialogue)
When NPCs talk to each other while player watches.

**Example beat in JSON:**
```json
{
  "pid": "beat_3",
  "beat_type": "npc_shared",
  "active_speaker": "Shared",
  "text": "NIMA: \"You shouldn't trust him.\" RAVI: \"But we have no choice.\"",
  "choices": []  // or optional [{"playerLine": "Continue", "target": "beat_4"}]
}
```

**What happens:**
- NPC name displays (or custom label)
- Text shows
- Auto-advances to next beat (or waits for [Continue])
- No player input needed

---

### Mode 2: NPCToPlayer (NPC Asks)
NPC speaks, player chooses from tone options, NPC responds.

**Example beat:**
```json
{
  "pid": "beat_2",
  "beat_type": "npc_turn",
  "active_speaker": "Nima",
  "text": "What brings you here, stranger?",
  "choices": [
    {
      "tone": "T",
      "label": "Trust",
      "playerLine": "I'm here to help",
      "npc_response": "NIMA: That's what they all say...",
      "result_text": "You speak earnestly.",
      "target": "beat_3",
      "tone_effects": [{"stat": "trust", "delta": 0.02}],
      "remnants_effects": [{"target": "activeNpcId", "stat": "trust", "delta": 0.01}]
    }
    // ... more T/O/N/E choices
  ]
}
```

**What happens:**
1. Show speaker: "Nima"
2. Show text: "What brings you here, stranger?"
3. Show choice buttons (T/O/N/E)
4. Player clicks Trust
5. Show result_text: "You speak earnestly."
6. Apply TONE effect: Trust +0.02
7. Apply REMNANTS effect: Nima Trust +0.01
8. Show NPC response: "That's what they all say..."
9. Auto-advance to beat_3

---

### Mode 3: PlayerInnerThought (Monologue)
Player's internal reflection, no choices, no NPC involved.

**Example beat:**
```json
{
  "pid": "beat_5",
  "beat_type": "player_posture",
  "active_speaker": "Player",
  "text": "I have to be careful. This place is dangerous.",
  "choices": []
}
```

**What happens:**
- Hide speaker name
- Show text (italicized or styled differently in UI)
- Auto-advance
- No choices, no effects

---

### Mode 4: PlayerActionChoice (Player Acts)
Player chooses an action, sees immediate feedback, optional NPC response.

**Example beat:**
```json
{
  "pid": "beat_1",
  "beat_type": "player_posture",
  "active_speaker": "Player",
  "text": "They're staring at me. What should I do?",
  "choices": [
    {
      "tone": "T",
      "label": "Trust",
      "playerLine": "Step toward them",
      "result_text": "You approach with open body language.",
      "npc_response": "",  // Optional NPC comment
      "target": "beat_2",
      "tone_effects": [{"stat": "trust", "delta": 0.02}],
      "remnants_effects": [{"target": "activeNpcId", "stat": "resolve", "delta": 0.01}]
    }
    // ... more choices
  ]
}
```

**What happens:**
1. Show: "They're staring at me. What should I do?"
2. Show choice buttons (T/O/N/E)
3. Player clicks Trust
4. Show result_text: "You approach with open body language."
5. Apply TONE + REMNANTS effects
6. Optional: Show NPC response if non-empty
7. Auto-advance to beat_2

---

## Mapping Your Game to Beat Types

### Use NPCToNPC when:
- Multiple NPCs are talking and player is just watching
- You want to show world dynamics
- No player input needed

### Use NPCToPlayer when:
- NPC is asking player a question
- You want NPC to react to player's choice
- Player picks from T/O/N/E tone options

### Use PlayerInnerThought when:
- Player is reflecting or thinking
- No NPC is present
- No choices available
- You want to show narrative context

### Use PlayerActionChoice when:
- Player is deciding what to do
- The action has consequences (TONE/REMNANTS changes)
- Optional NPC comment follows
- Player picks from T/O/N/E options

---

## Integrating with Your Game Systems

### TONE System
```csharp
// In StatManager
public void AdjustPlayerTone(ToneType tone, float amount, string activeNpcId)
{
    // Called automatically for each choice's tone_effects
    // Trust, Observation, NarrativePresence, Empathy
    // Amount is added to player's tone for this NPC
}
```

### REMNANTS System (NPC Stats)
```csharp
// In StatManager
public Remnants GetNpcRemnants(string npcId)
{
    // Get an NPC's stat object
    // Modify via remnants.Set(RemnantType, value)
}
```

**Example: Directly modifying NPC stats**
```csharp
var remnants = StatManager.Instance.GetNpcRemnants("Nima");
if (remnants != null)
{
    remnants.Set(RemnantType.Trust, remnants.trust + 0.01);
}
```

---

## Checking Dialogue Status

```csharp
// Is dialogue currently playing?
if (DialogueManager.Instance.IsDialogueActive)
{
    Debug.Log("Dialogue in progress");
}

// When dialogue ends, handle cleanup:
// - Player regains control
// - Update NPC state (appearance, dialogue options, etc.)
// - Trigger any dialogue-complete events
```

---

## Common Patterns

### Sequential Dialogue
Each beat targets the next one:
```
beat_1 → beat_2 → beat_3 → beat_4 → DIALOGUE_END
```

### Branching Based on Player Choice
Different choices lead to different beats:
```
beat_1
  ├─ Trust (T) → beat_2
  ├─ Observation (O) → beat_3
  ├─ Narrative (N) → beat_4
  └─ Empathy (E) → beat_5
```

### Loops (Circular Dialogue)
A beat can target back to an earlier beat:
```
beat_1 → beat_2 → beat_3
  ↑_________________|
(player can keep asking same question)
```

### Silent Actions (Empty result_text)
Some choices might have no visible feedback:
```json
{
  "result_text": "",
  "npc_response": "",
  "target": "beat_next"
}
```

---

## Debug Tips

### Enable Detailed Logging
DialogueManager logs everything:
```
[DialogueManager] Loaded beat: beat_1 (mode: PlayerActionChoice)
[DialogueManager] Displaying beat: beat_1 (mode: PlayerActionChoice)
[DialogueManager] Applied tone effect: trust +0.02
[DialogueManager] Applied remnants effect: Nima.resolve +0.01
```

### Check Mode Inference
If dialogue isn't displaying correctly, check mode:
- `beat_type` value must be exactly "player_posture", "npc_turn", or "npc_shared"
- `active_speaker` matters for inference
- `choices.Length` determines if auto-advance or choice buttons show

### Verify Effects Applied
```csharp
// Log player tone after choice:
Debug.Log($"Player Trust: {StatManager.Instance.GetPlayerTone(ToneType.Trust)}");

// Log NPC remnants:
var remnants = StatManager.Instance.GetNpcRemnants("Nima");
Debug.Log($"Nima Trust: {remnants.trust}");
```

---

## Troubleshooting

### "No beat with pid 'beat_X'"
- Check JSON has that beat
- Verify `target` values in choices match actual beat IDs
- Look for typos (beat_1 vs Beat_1)

### Choice buttons not appearing
- Verify `beat.choices` array is non-empty
- Check mode was inferred correctly (should show "PlayerActionChoice" or "NPCToPlayer")
- Ensure DialogueUIController can find choice buttons in scene

### NPC response not showing
- Check `npc_response` field is non-empty
- Verify beat_type is "npc_turn" or mode is "NPCToPlayer" / "PlayerActionChoice"
- Check dialogue mode should show NPC responses (not PlayerInnerThought)

### Text disappears too fast
- `ShowText()` calls `OnTextFinished()` immediately (no typewriter)
- Dialogue auto-advances based on `WaitForDisplayComplete()`
- To add delay, extend `ShowText()` with animation before calling `OnTextFinished()`

---

## Example: Nima Market Discovery

```json
{
  "name": "market_discovery_01",
  "startnode": "beat_1",
  "passages": [
    {
      "pid": "beat_1",
      "conversationId": "market_discovery_01",
      "beat_type": "player_posture",
      "active_speaker": "Player",
      "text": "They're staring at me. What should I do?",
      "choices": [
        {
          "tone": "T",
          "playerLine": "Step toward the figures",
          "label": "Trust",
          "result_text": "You approach with open body language. The man's expression shifts slightly.",
          "target": "beat_2",
          "tone_effects": [
            {"stat": "trust", "delta": 0.02}
          ],
          "remnants_effects": [
            {"target": "activeNpcId", "stat": "resolve", "delta": 0.01}
          ]
        }
      ]
    },
    {
      "pid": "beat_2",
      "conversationId": "market_discovery_01",
      "beat_type": "npc_turn",
      "active_speaker": "Nima",
      "text": "Work is scarce for people who actually belong here.",
      "choices": [
        {
          "tone": "O",
          "label": "Observation",
          "playerLine": "You're from here originally?",
          "npc_response": "NIMA: I am. And I didn't leave.",
          "result_text": "The bitterness in her voice is unmistakable.",
          "target": "beat_3",
          "tone_effects": [
            {"stat": "observation", "delta": 0.02}
          ],
          "remnants_effects": [
            {"target": "activeNpcId", "stat": "memory", "delta": 0.01}
          ]
        }
      ]
    }
  ]
}
```

## When to Use StartDialogue vs LoadDialogue

- `LoadDialogue(TextAsset jsonFile)` - Load a new dialogue file (call once per conversation)
- `StartDialogue(string npcId, string startBeatId)` - Begin at a specific beat (can call multiple times with different beats)

Example:
```csharp
// First time
DialogueManager.Instance.LoadDialogue(nimaDialogueJson);
DialogueManager.Instance.StartDialogue("Nima", "beat_1");

// Later, different conversation
DialogueManager.Instance.LoadDialogue(raviDialogueJson);
DialogueManager.Instance.StartDialogue("Ravi", "beat_1");
```
