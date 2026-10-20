# Dialogue Gatekeep System

## Overview

The **Dialogue Gatekeep** system prevents players from progressing past dialogue encounters without actually participating in them. It works by:

1. **Disabling forward colliders** by default (player can't proceed)
2. **Starting dialogue** when player approaches an NPC
3. **Setting a GameFlag** when dialogue completes
4. **Automatically enabling forward colliders** once the flag is set

This ensures players must engage with NPCs and get their story context before moving forward, while still allowing safe backtracking at any time.

## Problem It Solves

**Scenario:** InsideMarket_00 has Ravi & Nima. Without gatekeeping:
- Player enters scene
- Sees dialogue prompt from Ravi/Nima
- Ignores it and tries to go forward anyway
- Hits disabled collider... but nothing stops them from trying again
- Or worse: accidentally ends up in InsideMarket_01_01 (post-conversation scene)
- Returns via backtrack collider to InsideMarket_00_02 (which doesn't have Ravi/Nima)
- Player has now skipped the dialogue entirely and broken narrative continuity

**With Gatekeep System:**
- Player enters InsideMarket_00
- Forward colliders are disabled
- Player can't move forward no matter what
- Player must interact with Ravi/Nima to trigger dialogue
- Dialogue completes → flag sets → forward colliders enable
- Only then can player move forward to InsideMarket_01_01
- If player returns to InsideMarket_00_02, colliders stay enabled (flag persists)
- Narrative continuity maintained

## Components

### 1. DialogueGatekeep (New Script)

**Location:** `Assets/Scripts/Interactions/DialogueGatekeep.cs`

Manages all dialogue gates in a scene. Listens for `DialogueManager.OnDialogueEnded` and enables corresponding forward colliders.

**Setup:**
- Attach to scene root or a "Managers" GameObject
- Add a DialogueGate entry for each NPC dialogue in the scene
- Specify: completion flag name, NPC ID, colliders to enable

**Key Methods:**
- `HandleDialogueEnded()` - Called automatically when any dialogue ends
- `UnlockGate(string flag)` - Manually unlock a gate (for debugging)

### 2. StartDialogueOnTrigger (Enhanced)

**Location:** `Assets/Scripts/StartDialogueOnTrigger.cs`

Already existed; now has **optional** completion flag support.

**New Fields:**
- `completionFlag` - Name of flag to set when dialogue completes (e.g., "ravi_nima_dialogue_complete")
- `setCompletionFlag` - Toggle to enable flag-setting behavior

**Flow:**
1. Player collides with NPC trigger
2. StartDialogueOnTrigger loads dialogue JSON and starts conversation
3. Player completes dialogue
4. `HandleDialogueEnded()` fires
5. If `setCompletionFlag` is true, sets the flag
6. DialogueManager.OnDialogueEnded broadcasts to all listeners
7. DialogueGatekeep receives broadcast and checks if flag is set
8. If flag is set, enables forward colliders

### 3. GameFlags (Existing System)

**Location:** `Assets/Scripts/Management/GameFlags.cs` (or similar)

Persistent global state tracker. Flags survive scene transitions.

**Usage:**
```csharp
GameFlags.Set("ravi_nima_dialogue_complete", true);
bool isComplete = GameFlags.Get("ravi_nima_dialogue_complete");
```

## Setup Instructions

### Example: InsideMarket Scene

**Step 1: Create Scene Hierarchy**

```
InsideMarket_00
├── [SceneRoot]
│   └── [DialogueGatekeep] (this script, attached to SceneRoot or child)
├── Player Spawn Point
│
├── ColliderGroup_BackToEntrance
│   └── Collider_Back_To_Start (ALWAYS enabled)
│
├── DialogueGates/
│   └── Gate_Ravi_Nima/
│       ├── Collider_To_Market_01_01 (DISABLED initially)
│       ├── Collider_To_Market_01_02 (DISABLED initially - alt path)
│
├── NPCs/
│   └── Ravi
│       └── Collider_RaviDialogue
│           └── [StartDialogueOnTrigger]
│   └── Nima
│       └── Collider_NimaDialogue
│           └── [StartDialogueOnTrigger]
```

**Step 2: Configure StartDialogueOnTrigger on Ravi's Collider**

| Field | Value |
|-------|-------|
| NPC ID | Ravi |
| Starting Passage ID | beat_1 |
| Story Resource Path | Dialogue/ravi_market_01 |
| Required Flag | (leave unchecked or empty if no prerequisite) |
| Lock Player Movement | ✓ (checked) |
| **Set Completion Flag** | ✓ (checked) |
| **Completion Flag** | ravi_nima_dialogue_complete |

**Step 3: Configure StartDialogueOnTrigger on Nima's Collider**

| Field | Value |
|-------|-------|
| NPC ID | Nima |
| Starting Passage ID | beat_1 |
| Story Resource Path | Dialogue/nima_market_01 |
| Required Flag | (leave unchecked) |
| Lock Player Movement | ✓ (checked) |
| **Set Completion Flag** | ✓ (checked) |
| **Completion Flag** | ravi_nima_dialogue_complete |

*(Both NPCs set the same flag, so completing either one unlocks the gate)*

**Step 4: Configure DialogueGatekeep**

1. Select SceneRoot or parent GameObject
2. Add DialogueGatekeep component
3. In inspector, expand "Dialogue Gates" and click "+" to add a new gate
4. Configure the gate:

```
DialogueGate [0]:
  Completion Flag: ravi_nima_dialogue_complete
  NPC Id: Ravi (documentation only)
  Forward Colliders: (drag Gate_Ravi_Nima/Collider_To_Market_01_01)
                     (drag Gate_Ravi_Nima/Collider_To_Market_01_02)
  Colliders Then Disable: (leave empty, or add any blockers)
```

**Step 5: Test**

1. Enter InsideMarket_00
2. Try to walk forward → colliders are disabled, you can't move forward
3. Approach Ravi/Nima → dialogue prompt appears
4. Complete dialogue
5. Forward colliders now enabled → you can walk forward
6. Enter InsideMarket_01_01
7. Use bottom collider to go back to InsideMarket_00_02
8. Forward colliders remain enabled (flag is still set)
9. You can exit freely

## Advanced Usage

### Multiple NPCs, Single Gate

If multiple NPCs guard the same passage (e.g., Ravi AND Nima must both be talked to):

```
DialogueGate:
  Completion Flag: ravi_nima_both_complete
  
StartDialogueOnTrigger (Ravi): setCompletionFlag=false (don't set yet)
StartDialogueOnTrigger (Nima): setCompletionFlag=false (don't set yet)

// Create a separate script or event that:
// - Tracks if both NPCs have been talked to
// - Sets "ravi_nima_both_complete" only when both are done
```

*(This is a more complex pattern; document if you implement it)*

### Multiple Gates, Same Scene

If a scene has multiple gated dialogue areas:

```
DialogueGatekeep:
  Gates [0]:
    Completion Flag: ravi_dialogue_complete
    Forward Colliders: [To_Market_01]
  
  Gates [1]:
    Completion Flag: side_npc_dialogue_complete
    Forward Colliders: [To_Side_Cave]
```

Both can coexist in the same scene manager.

### Optional Dialogue (No Gate)

If an NPC dialogue is optional (player can skip):

1. Don't create a DialogueGate for it
2. Set `setCompletionFlag=false` on StartDialogueOnTrigger
3. Colliders remain enabled regardless

## Debugging

### Useful Debug Commands

Add these to a debug console or cheat system:

```csharp
// Check if a flag is set
bool isComplete = GameFlags.Get("ravi_nima_dialogue_complete");
Debug.Log($"Dialogue complete: {isComplete}");

// Manually set a flag (for testing)
GameFlags.Set("ravi_nima_dialogue_complete", true);

// Reset a flag (to replay scene)
GameFlags.Set("ravi_nima_dialogue_complete", false);
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Forward colliders won't enable | Check that `setCompletionFlag=true` on StartDialogueOnTrigger. Check that `Completion Flag` name matches exactly (case-sensitive) |
| Player locked forever | Check if dialogue even completed (watch for "[DialogueManager] Dialogue ended" in console). Check if OnDialogueEnded event is firing |
| Gate works first time, breaks on reload | Flags are persistent in GameFlags; use SceneStateController to reset them on scene load if needed |
| Wrong colliders enabling | Double-check DialogueGatekeep inspector - make sure you're assigning colliders to the right gate |

## Implementation Checklist

For each dialogue gated area:

- [ ] Create DialogueGates folder with disabled colliders
- [ ] Attach StartDialogueOnTrigger to NPC collider
  - [ ] Set `setCompletionFlag = true`
  - [ ] Set unique `Completion Flag` name
- [ ] Attach DialogueGatekeep to scene root
  - [ ] Add DialogueGate entry
  - [ ] Assign forward colliders
  - [ ] Verify completion flag name matches
- [ ] Test: approach NPC → dialogue → colliders enable
- [ ] Test: backtrack → colliders remain enabled
- [ ] Test: reload scene → colliders remain enabled (flag persists)

## Notes

- **Flags persist** across scene loads; use `SceneStateController` to reset them if scenes are meant to be "fresh" on reload
- **Backtracking is always allowed** via the back collider (never add it to a gated folder)
- **Multiple paths** (e.g., Market_01_01 and Market_01_02) can both be in the same gate - both enable at the same time
- **Order doesn't matter** - DialogueGatekeep checks all flags, so it works even if multiple dialogues complete in the same scene

## Integration with Existing Scene-State System

This system works **alongside** the existing scene-state architecture:

- **Scene-State System** (Location_StateNum naming) handles "how does the world change as you progress?"
- **Dialogue Gatekeep System** handles "how do you enforce dialogue flow within a scene?"

They don't conflict; use both together for robust narrative flow.
