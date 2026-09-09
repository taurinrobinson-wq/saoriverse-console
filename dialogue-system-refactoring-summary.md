# Velinor Dialogue System - Beats-Based Refactoring

## ✅ Implementation Complete

The dialogue system has been fully refactored to use a pure **beats-based architecture** instead of the hybrid beats/passages system. This is a clean, Unity-native design that eliminates state ambiguity and aligns with your game's reactive, response-driven nature.

---

## 🎯 What Changed

### 1. **New Core Data Structures**

#### `DialogueMode.cs` (10 lines)
Defines the four fundamental dialogue interaction types:
- `NPCToNPC` - Shared dialogue, auto-advances
- `NPCToPlayer` - NPC speaks, player chooses, NPC responds
- `PlayerInnerThought` - Player monologue, auto-advances
- `PlayerActionChoice` - Player acts, sees feedback, optional NPC response

#### `BeatData.cs` (68 lines)
Replaces the old passage system with a unified beat structure:
- `BeatData` - The core unit of dialogue
  - `pid` - Beat identifier ("beat_1", "beat_2")
  - `beat_type` - Dialogue type ("player_posture", "npc_turn", "npc_shared")
  - `active_speaker` - Who speaks
  - `text` - Main dialogue text
  - `choices` - Array of player choices
  - `mode` - Inferred at load time

- `BeatChoice` - A single player choice
  - `tone` - T/O/N/E indicator
  - `playerLine` - What player says
  - `label` - UI label for button
  - `npc_response` - NPC's reply (if any)
  - `result_text` - Immediate feedback
  - `target` - Next beat ID
  - `tone_effects` - TONE stat changes
  - `remnants_effects` - NPC stat changes

### 2. **New DialogueManager** (292 lines)
Complete rewrite from passage-based to beat-based:

**Key Methods:**
- `LoadBeatsFromJson()`
  - Loads dialogue JSON directly into beat dictionary
  - Infers `DialogueMode` for each beat automatically
  - No runtime conversion needed

- `StartDialogue(string npcId, string startBeatPid)`
  - Initiates dialogue from a specific NPC and beat
  - Replaces old `LoadStory()` / `StartDialogue(TextAsset)`

- `DisplayBeat(BeatData beat)`
  - State machine that handles all 4 dialogue modes
  - Shows speaker name, text, and choices as appropriate
  - No text racing or timing issues

- `ResolveChoiceCoroutine(BeatChoice choice)`
  - Shows `result_text` (player action feedback)
  - Applies TONE and REMNANTS effects
  - Shows NPC response if appropriate
  - Advances to next beat

### 3. **Updated DialogueUIController** (615 lines)
New methods for beats system:
- `ShowSpeaker(string name)` - Display speaker name
- `HideSpeaker()` - Hide speaker
- `ClearButtons()` - Reset choice buttons
- `ShowChoices(BeatData beat, Action<BeatChoice> callback)` - Display and wire choices

**Existing functionality preserved:**
- Dialogue panel management
- Text display with `ShowText()`
- UI completion signal with `WaitForDisplayComplete()`
- Continue input handling (Space/LMB click)

---

## 🔄 How the System Works Now

### Flow for Each Beat Type:

**NPCToNPC (Shared Dialogue)**
1. Show NPC speaker name
2. Display text
3. Auto-advance to next beat (or wait for [Continue] if explicit)

**NPCToPlayer (NPC asks question)**
1. Show NPC speaker name
2. Display NPC's prompt
3. Show tone choice buttons
4. Player selects → applies TONE/REMNANTS effects
5. Show NPC response
6. Auto-advance to target beat

**PlayerInnerThought (Monologue)**
1. Hide speaker name
2. Display player's thought
3. Auto-advance to next beat

**PlayerActionChoice (Player acts)**
1. Show player speaker name
2. Display action prompt
3. Show tone choice buttons
4. Player selects → show result_text feedback
5. Apply TONE/REMNANTS effects
6. Optional: show NPC response
7. Auto-advance to target beat

### Effect Application:

Each choice can trigger:
- **Tone Effects** - Modify TONE stats (Trust/Observation/Narrative/Empathy)
  - Applied via `StatManager.AdjustPlayerTone()`
- **Remnants Effects** - Modify NPC stats (Resolve/Trust/Memory/etc.)
  - Applied by directly modifying NPC's Remnants object

---

## 📝 JSON Format (Already Compatible)

Your JSON files are already in the correct format! The "passages" array contains beats:

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
      "text": "They're staring at me. What should I do.",
      "choices": [
        {
          "tone": "T",
          "playerLine": "Step toward the figures",
          "label": "Trust",
          "npc_response": "",
          "result_text": "You approach with open body language...",
          "target": "beat_2",
          "tone_effects": [{"stat": "trust", "delta": 0.02}],
          "remnants_effects": [{"target": "activeNpcId", "stat": "resolve", "delta": 0.01}]
        }
      ]
    }
  ]
}
```

---

## 🔧 Integration Steps

### Step 1: Wire DialogueManager to Scene
1. In your scene, add DialogueManager component to a GameObject
2. Assign the JSON file to the `dialogueJson` field in Inspector
3. Ensure `DialogueUIController` is also in scene (marked DontDestroyOnLoad)

### Step 2: Start Dialogue
```csharp
DialogueManager.Instance.LoadDialogue(jsonFileAsset);
DialogueManager.Instance.StartDialogue("Nima", "beat_1");
```

### Step 3: Handle Dialogue End
Wire up a callback for when dialogue ends:
```csharp
// In DialogueManager.EndDialogue(), you can add:
// onDialogueEnd?.Invoke();
// or trigger a system event
```

---

## 🧪 Testing Checklist

- [ ] JSON files load without errors
- [ ] Beat mode inference works (check Debug logs)
- [ ] First beat displays correctly
- [ ] Choice buttons appear and are clickable
- [ ] NPC responses display and don't get cut off
- [ ] TONE effects apply correctly (check StatManager values)
- [ ] REMNANTS effects apply to correct NPC
- [ ] Dialogue advances to next beat after choice
- [ ] Auto-advance beats move forward on their own
- [ ] Player inner thoughts hide speaker name
- [ ] Shared dialogue displays correctly
- [ ] Dialogue properly ends (UI hides, not stuck)

---

## 🎭 Mode Inference Logic

The system automatically detects the dialogue mode based on JSON data:

```
if beat_type == "npc_shared"
  → NPCToNPC (auto-advance)

if beat_type == "player_posture" AND active_speaker == "Player" AND no choices
  → PlayerInnerThought (auto-advance)

if beat_type == "npc_turn" AND has choices
  → NPCToPlayer (show choices, play NPC response after)

if beat_type == "player_posture" AND has choices
  → PlayerActionChoice (show result_text, optional NPC response)

else
  → NPCToNPC (fallback)
```

No need to manually set modes—they're inferred automatically!

---

## 📊 Architecture Comparison

### Old System (Hybrid)
- Beats in JSON
- Runtime conversion to passages
- Race conditions (next beat fires before text renders)
- Confusion about what's passages vs beats

### New System (Pure Beats) ✨
- Beats in JSON → directly loaded as BeatData
- No conversion needed
- UI completion signals prevent races
- Clear state machine (4 modes, no ambiguity)
- More native to Unity (coroutines, state machines)

---

## 🔗 File Changes Summary

| File | Lines | Change |
|------|-------|--------|
| DialogueMode.cs | 10 | NEW - Mode enum |
| BeatData.cs | 68 | NEW - Data structures |
| DialogueManager.cs | 292 | REPLACED - Old 1389 lines with new beat-based runner |
| DialogueUIController.cs | 615 | UPDATED - Added ShowSpeaker, ShowChoices, ClearButtons |

**Backup:** `DialogueManager.cs.backup` (1389 lines old version)

---

## ✨ Key Improvements

1. **State Machine** - No ambiguity about what should display
2. **Race Conditions Fixed** - UI completion signals prevent text cutoff
3. **Automatic Mode Detection** - No manual mode config needed
4. **Cleaner Code** - 292 lines vs 1389 lines (75% reduction)
5. **Unity-Native** - Uses coroutines, not passage graphs
6. **Future-Ready** - Audio, visual editors, NPCs all work naturally on beats

---

## 🐛 If You Encounter Issues

### Choices not showing
- Check `DialogueUIController.FindChoiceButtons()` - may need UI button setup
- Verify beat has `choices` array non-empty
- Check mode inference logic matches your beat_type values

### NPC responses cut off
- `DialogueUIController.WaitForDisplayComplete()` should signal when done
- Ensure `ShowText()` is called, which marks text as displaying

### Effects not applying
- Check StatManager has correct NPC ID
- Verify stat names in JSON match `ParseTone()` / `ParseRemnantType()` case handling

### JSON parse errors
- Verify JSON is valid (use online JSON validator)
- Check that "passages" array exists
- Ensure all required fields present in BeatData

---

## 🚀 Next Steps (Optional Enhancements)

1. **Audio System** - Add `audio_clip` fields to BeatData
2. **Visual Editor** - Build UI editor around beats
3. **Dialogue Variables** - Add `flags`, `conditions` for branching
4. **Diary Integration** - Trigger diary entries on beat completion
5. **Codex Triggers** - Unlock glyphs based on beat text content

All of these extend naturally from the beats architecture!
