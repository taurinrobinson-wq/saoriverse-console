# Saoriverse Dialogue System: Current State & Implementation Guide

## 🎯 Executive Summary
Your dialogue system uses a **beat-based JSON format** that gets converted to passages at runtime. The state ambiguity issue stems from four fundamentally different dialogue modes being handled as one unified flow in the `ResolveChoice()` and `DisplayPassage()` methods.

---

## 📋 Current System Architecture

### Beat JSON Structure
```json
{
  "scene_id": "market_discovery_01",
  "required_flags": ["met_saori == true"],
  "beats": [
    {
      "id": 1,
      "type": "player_posture",
      "active_speaker": "Player",
      "prompt": "They're staring at me. What should I do.",
      "tone_choices": [
        {
          "tone": "T",
          "text": "Step toward the figures",
          "result_text": "You approach with open body language...",
          "npc_response": "",
          "tone_effects": [...],
          "remnants_effects": [...]
        }
      ],
      "next_beat_id": 2
    },
    {
      "id": 2,
      "type": "npc_turn",
      "active_speaker": "Nima",
      "prompt": "NIMA: \"What do you want anyway? We don't trust outsiders.\"",
      "tone_choices": [...],
      "next_beat_id": 3
    }
  ]
}
```

### Beat Types Currently Used
1. **`player_posture`** - Player makes a choice + sees immediate feedback
   - Has: `prompt`, `tone_choices` with `result_text`
   - Flow: Show prompt → Player chooses → Show result_text → Show next beat
   - NPC Response: Sometimes empty, sometimes filled

2. **`player_inner`** (normalized to `player_posture`)
   - Has: Monologue text, NO player choices
   - Flow: Show text → Auto-advance (with delay)
   - NPC Response: Should NOT appear

3. **`npc_turn`** - NPC speaks (usually in response to player)
   - Has: `prompt` (NPC line), `tone_choices` with `npc_response`
   - Flow: Show NPC line → Player chooses → Show NPC's response to that choice
   - NPC Response: Always filled from `npc_response` field

4. **`npc_shared`** - Multiple NPCs speak in sequence
   - Has: `shared_dialogue` array with speaker/text pairs
   - Flow: Show speaker1 → Auto-advance → Show speaker2 → etc → Next beat
   - NPC Response: Should NOT appear, seamless flow

---

## 🔴 The Core Problem: State Ambiguity

Your system currently tries to guess the mode based on:
- Whether `tone_choices` exist
- The `active_speaker` value
- Whether `npc_response` is filled

**This causes:**

### Symptom 1: NPC Response Overwrite
```
Timeline:
1. Player chooses → ResolveChoice() fires
2. ResolveChoice() checks if hasNpcResponse
3. Shows NPC response text ✓
4. Waits 2 seconds (WaitForSeconds)
5. DisplayPassage(choice.target) fires
6. Next beat's text OVERWRITES NPC response ✗
```
**Root Cause**: Unity doesn't block the `WaitForSeconds` coroutine from starting the next turn. The display pipeline doesn't know the UI isn't done rendering.

### Symptom 2: Delay Hack Breaks Choices
```
The 2-second delay in ResolveChoice() line 1051:
    yield return new WaitForSeconds(2.0f);

This makes NPC responses visible, but:
- If next beat has choices, they don't appear for 2+ seconds
- Player sits confused, staring at NPC response
- Choices appear late: player thinks the beat froze
```

### Symptom 3: Inner Thoughts Show NPC Responses
```
player_inner beat:
  - active_speaker: "Player"
  - Should show: <i>Inner thought text</i>, no NPC response
  - Actually shows: Inner thought + NPC response (wrong speaker)
```

### Symptom 4: PlayerActionChoice Mode Missing
```
Some beats need:
  - Show prompt
  - Player chooses
  - Show result_text (action description)
  - DON'T show NPC response
  - Auto-advance to next beat
  
Currently: Falls through to NPCToPlayer flow, tries to show NPC response
```

### Symptom 5: Shared Dialogue Gets Interrupted
```
npc_shared beats should:
  - Flow seamlessly: Speaker1 → Speaker2 → Speaker3
  - No pauses, no player choices until all speakers done
  
Currently: Gets passed through DisplayPassage() which shows choices
```

---

## 🏗️ Current Display & Resolution Pipeline

### DisplayPassage() Flow (Line ~740)
```csharp
DisplayPassage(pid)
  1. Get StoryPassage
  2. Check if "Shared" dialogue (line 750)
  3. Process system_triggers (line 752-763)
  4. Show NPC/Player text in UI (line 765-790)
  5. ClearButtons() (line 800)
  6. DisplayChoicesForPassage(pid) (line 801)
```

### DisplayChoicesForPassage() Flow (Line ~836)
```csharp
DisplayChoicesForPassage(pid)
  1. Check if hasPlayerChoices (line 842)
  2. If NO choices:
     - If Shared speaker: AutoAdvanceDialogue(skipDisplay: true) (line 853)
     - Else: AutoAdvanceDialogue() (line 859)
  3. If YES choices:
     - Show TONE buttons (T/O/N/E) (line 868-915)
     - Map each choice to a button
     - Attach OnChoiceMade() listener
```

### ResolveChoice() Flow (Line ~953)
```csharp
ResolveChoice(choice)
  1. ClearButtons()
  2. Execute PlayerActionHandler if result_text exists (line 958-961)
  3. Apply tone effects & remnants (line 964-977)
  4. Process data hooks & system triggers (line 980-981)
  5. Build responseText from choice.shared_beat (line 983-988)
  6. Check if choice.target exists (line 991-1072)
  7. IF target exists:
     - Load nextPassage (line 1000)
     - Determine hasNpcResponse (line 1003-1024)
     - IF hasNpcResponse: Show it (line 1029-1048) 
     - WAIT 2 seconds (line 1051) ← DELAY HACK
     - Check if nextPassage is npc_turn: DisplayChoicesForPassage()
     - Else: DisplayPassage()
  8. Else: EndDialogue()
```

---

## 🧩 TONE/REMNANTS Integration

### TONE System
- **Player Side** (`tone_effects`): Adjusts player's emotional stats (trust, observation, narrative, empathy)
- **NPC Side** (`npc_resonance`): Adjusts NPC's perception of player
- **Applied In**: ResolveChoice() line 966-974

```json
"tone_effects": [
  { "stat": "trust", "delta": 0.02 },
  { "stat": "observation", "delta": -0.015 },
  { "stat": "narrative", "delta": -0.01 },
  { "stat": "empathy", "delta": 0.005 }
]
```

### REMNANTS System
- **Target Specificity**: Can target `"activeNpcId"` or specific NPC name like `"Nima"`, `"Ravi"`
- **Applied In**: ResolveChoice() line 977 calls ApplyRemnantsEffects()
- **Multi-NPC Support**: Allows same choice to affect multiple NPCs differently

```json
"remnants_effects": [
  {
    "target": "Nima",
    "stat": "resolve",
    "delta": 0.01
  },
  {
    "target": "activeNpcId",  // Resolves to current NPC
    "stat": "trust",
    "delta": -0.01
  }
]
```

### System Triggers
- **Processed Before Display** (line 754-763)
- **Types**: Name reveals, item gives, flags, etc.
- **Multi-NPC**: Supports targeting specific NPCs by name

---

## 🎭 Four Dialogue Modes (To Be Formalized)

### Mode 1: NPC→NPC (Shared Dialogue)
**When**: `type == "npc_shared"` with `shared_dialogue` array
**What player sees**: Multiple NPCs speaking in sequence
**Player action**: None (auto-advance only)
**NPC response**: None, seamless flow
**UI State**:
- Hide choice buttons
- Show speaker name + text
- Auto-advance without delay

### Mode 2: NPC→Player (Interactive Dialogue)
**When**: `type == "npc_turn"` with `tone_choices`
**What player sees**: NPC prompt → Player chooses → NPC responds to choice
**Player action**: Must choose from 4 tones
**NPC response**: Required, shown after choice (from `npc_response` field)
**UI State**:
- Show NPC name + prompt
- Show choice buttons (T/O/N/E)
- Wait for player click
- Show NPC response (on choice's speaker)
- Wait for render complete
- Show next beat

### Mode 3: Player Inner Thought (Monologue)
**When**: `active_speaker == "Player"` AND `type == "player_posture"` with NO choices
**What player sees**: Italicized inner thought text
**Player action**: Auto-advance
**NPC response**: None, should be hidden
**UI State**:
- Hide NPC name
- Show italicized text
- Hide choice buttons
- Auto-advance after brief delay

### Mode 4: Player Action Choice (Choice Outcome)
**When**: `type == "player_posture"` with `tone_choices` (player can act)
**What player sees**: Situation → Choose action → See action outcome → NPC responds
**Player action**: Must choose, gets `result_text` feedback
**NPC response**: May be empty or may be filled (dependent on JSON)
**UI State**:
- Show prompt (situation)
- Show choice buttons
- Wait for player click
- Show result_text (player action feedback)
- Show NPC response IF exists
- Show next beat

---

## 🔌 UI Display Pipeline Sequence

### Current Architecture (Problematic)
```
ResolveChoice()
  ├─ Apply effects immediately
  ├─ Start coroutine ResolveChoice() (async)
  │  ├─ Wait 2 seconds
  │  └─ Call DisplayPassage() (no sync point)
  └─ Return immediately (fire-and-forget)
  
↓ PROBLEM: Next beat can fire before UI finishes rendering current text
```

### What's Needed
```
ResolveChoice()
  ├─ Apply effects immediately
  ├─ Show NPC response text (if any)
  ├─ AWAIT ui.WaitForDisplayComplete()  ← Explicit signal
  └─ Call DisplayPassage(nextBeat)  ← Only when UI ready
```

---

## 📂 Key Code Locations

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| Beat Structure | DialogueManager.cs | 554-614 | `BeatData`, `BeatToneChoice`, etc. |
| Beat Conversion | DialogueManager.cs | 400-552 | `ConvertBeatsToPassages()` |
| Display Pipeline | DialogueManager.cs | 740-802 | `DisplayPassage()` |
| Choice Display | DialogueManager.cs | 836-926 | `DisplayChoicesForPassage()` |
| Choice Resolution | DialogueManager.cs | 953-1079 | `ResolveChoice()` (THE PROBLEM AREA) |
| Remnants Apply | DialogueManager.cs | 1087-1120 | `ApplyRemnantsEffects()` |
| UI Controller | DialogueUIController.cs | 1-100+ | Receives display calls |
| NPC Trigger | NPCDialogueDriver.cs | 1-200+ | Initiates dialogue |

---

## ✅ What Works Currently

1. ✓ JSON parsing (both passages and beats formats)
2. ✓ Conversion of beats to passages
3. ✓ TONE system (player emotional tracking)
4. ✓ REMNANTS system (NPC stat changes)
5. ✓ Multi-NPC scene support (conversationId filtering)
6. ✓ System triggers (name reveals, item gives)
7. ✓ Choice button mapping (T/O/N/E)
8. ✓ Text display in DialogueUIController
9. ✓ Auto-advance for beats with no choices

---

## ❌ What Needs Fixing

1. ✗ State ambiguity: System guesses which mode it's in
2. ✗ Race condition: Next beat fires before NPC response finishes rendering
3. ✗ Delay hack: 2-second WaitForSeconds affects all modes indiscriminately
4. ✗ Mode mixing: PlayerInnerThought mode shows NPC responses
5. ✗ No UI completion signal: DisplayPassage() has no way to know when UI is ready
6. ✗ Coroutine timing: Fire-and-forget ResolveChoice() doesn't synchronize with UI

---

## 🧠 Questions for Implementation

When implementing the mode-based state machine fix:

### 1. **Beat Data Structure Addition**
```csharp
public enum DialogueMode {
    NPCToNPC,           // Shared dialogue, no player choices
    NPCToPlayer,        // NPC response required after choice
    PlayerInnerThought, // Monologue, no NPC response
    PlayerActionChoice  // Action choice, optional NPC response
}
```

Should `DialogueMode` be:
- A) Added to JSON beats (requires JSON migration)?
- B) Inferred from beat data at load time (converted beats)?
- C) Both (explicit in JSON, fallback inference for legacy beats)?

### 2. **UI Completion Signal**
The fix needs `await ui.WaitForDisplayComplete()`. Should this:
- A) Emit a callback when text animation finishes?
- B) Use a fixed wait based on text length?
- C) Poll the DialogueUIController for render state?
- D) Use TMPro.TextAnimator completion events?

### 3. **NPC Response Handling**
Current code checks 3 places for NPC response:
- Line 1003: `choice.npc_response` (from JSON)
- Line 1006: `nextPassage.npc_responses` (tone-dependent)
- Line 1022: `nextPassage.text` (beat prompt, fallback)

For mode-based fix, should:
- A) Only use Mode enum to determine IF to show response?
- B) Consolidate response lookup into one place?
- C) Add explicit `npcResponse` field to Mode definition?

### 4. **Delay Customization**
Current code has hard-coded 2-second wait (line 1051).
Should mode-based fix support:
- A) Per-beat `responseWindow` as suggested?
- B) Per-choice delay override?
- C) Completely remove delay (rely on UI completion signal)?
- D) All three (hierarchy)?

### 5. **Multi-NPC Scene Complexity**
In `ravi_nima_market_discovery.json`, choices can target specific NPCs:
```json
"remnants_effects": [
  { "target": "Ravi", "stat": "...", "delta": ... },
  { "target": "Nima", "stat": "...", "delta": ... }
]
```

Should mode-based fix:
- A) Support multi-NPC responses (show both Ravi AND Nima)?
- B) Only support single active NPC at a time?
- C) Add new Mode like `MultiNPCResponse`?

---

## 📊 Example Flow: Current vs. Fixed

### Current (Problematic)
```
Beat 1: player_posture (Choice)
├─ Show: "They're staring at me. What should I do?"
├─ Show: [Trust] [Observation] [Narrative] [Empathy] buttons
├─ Player clicks "Trust"
├─ ResolveChoice():
│  ├─ Apply tone effects
│  ├─ Execute result_text: "You approach..."
│  ├─ Show NPC response? (guesses based on data)
│  ├─ Wait 2 seconds (delays everything)
│  └─ DisplayPassage(beat_2)
│     ├─ Beat 2 text tries to show immediately
│     └─ OVERWRITES NPC response ✗

Result: NPC response gets lost, player confused
```

### Fixed (Proposed)
```
Beat 1: player_posture [Mode.PlayerActionChoice]
├─ Show: "They're staring at me. What should I do?"
├─ Show: [Trust] [Observation] [Narrative] [Empathy] buttons
├─ Player clicks "Trust"
├─ ResolveChoice():
│  ├─ Apply tone effects
│  ├─ Execute result_text: "You approach..."
│  ├─ Switch(mode):
│  │  └─ PlayerActionChoice:
│  │     ├─ NO NPC response (mode determines this)
│  │     ├─ AWAIT ui.WaitForDisplayComplete()
│  │     └─ DisplayPassage(beat_2)
│  └─ Continue...

Beat 2: npc_turn [Mode.NPCToPlayer]
├─ Show: "NIMA: What do you want anyway?"
├─ Show: [Trust] [Observation] [Narrative] [Empathy] buttons
├─ Player clicks "Observation"
├─ ResolveChoice():
│  ├─ Apply tone effects
│  ├─ Switch(mode):
│  │  └─ NPCToPlayer:
│  │     ├─ Show NPC response: "Work is scarce for people..."
│  │     ├─ AWAIT ui.WaitForDisplayComplete()
│  │     └─ DisplayPassage(beat_3)
│  └─ Continue...

Result: Correct sequencing, no overwrites, choices appear when ready ✓
```

---

## 🎬 Ready for Refactor

This document provides:
1. ✓ Current system architecture
2. ✓ Beat types and JSON structure
3. ✓ Four dialogue modes (implicit, need to be formalized)
4. ✓ State ambiguity problems with specific examples
5. ✓ TONE/REMNANTS integration points
6. ✓ Code locations for each component
7. ✓ Key implementation questions

Share this with the other copilot, and they'll have enough context to:
- Add the `DialogueMode` enum
- Modify beat conversion to infer/set mode
- Refactor ResolveChoice() to use explicit mode switching
- Implement UI completion signal
- Test with existing JSON files

