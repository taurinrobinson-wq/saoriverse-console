# NPC Disabling on Scene Transition - Setup Guide

## Overview
When the Ravi & Nima dialogue completes, they are disabled in the scene. When you return to InsideMarket_00 later, they should stay disabled.

This is accomplished with:
1. **DialogueManager** - Disables NPCs via `disable_npc` system triggers ✅ (Implemented)
2. **GameFlags** - Persists state across scene transitions ✅ (Already working)
3. **SceneStateController** - Re-applies NPC disabled state when returning to scene ⚠️ (Needs setup in Inspector)

---

## Step 1: Verify Dialogue System Changes ✅
The dialogue system now properly handles:
- `disable_npc` triggers from your JSON (finds NPC by name and disables it)
- `set_flag` triggers to persist state (sets `ravi_nima_market_discovery_complete = true`)

**What happens during dialogue:**
1. Dialogue completes
2. `disable_npc` trigger fires → Ravi & Nima GameObjects are disabled
3. `set_flag` trigger fires → `ravi_nima_market_discovery_complete = true` stored in GameFlags

---

## Step 2: Add SceneStateController to Your SceneManager

### Instructions

1. Open **InsideMarket_00.unity** scene in editor
2. In the Hierarchy, find **SceneManager** GameObject
   - It currently has: SceneTransitionManager + SceneSpawnManager components
3. Add **SceneStateController** component to SceneManager:
   - Select SceneManager
   - Inspector → Add Component → SceneStateController
4. Configure the SceneStateController Actions:
   - Expand the **Actions** list in Inspector
   - Click + button to add two new State Actions

**Action 1 - Disable Ravi:**
- Required Flag: `ravi_nima_market_discovery_complete`
- Target: `Ravi` (drag the Ravi GameObject from Hierarchy)
- Set Active: `false` (checkbox unchecked)

**Action 2 - Disable Nima:**
- Required Flag: `ravi_nima_market_discovery_complete`
- Target: `Nima` (drag the Nima GameObject from Hierarchy)
- Set Active: `false` (checkbox unchecked)

5. **Save the scene** (Ctrl+S)

### SceneManager Components Overview

After setup, your SceneManager will have:
```
SceneManager (GameObject)
├── SceneTransitionManager (existing)
├── SceneSpawnManager (existing)
└── SceneStateController (NEW - handles NPC state per scene)
```

This keeps all scene management logic centralized! ✅

---

## Step 3: Test the Setup

### Test Scenario 1: First Visit
1. Play the game
2. Enter InsideMarket_00
3. Ravi & Nima should be visible and enabled
4. Start dialogue with them
5. Complete the full dialogue
6. At the end, they should fade out (disabled)

### Test Scenario 2: Return Visit
1. Leave the scene (go to another location)
2. Come back to InsideMarket_00
3. Ravi & Nima should still be disabled (not visible)
4. **This confirms SceneStateController is working!**

### Console Output to Look For

**When dialogue completes:**
```
[DialogueManager] NPC disabled: Ravi
[DialogueManager] NPC disabled: Nima
[DialogueManager] Flag set: ravi_nima_market_discovery_complete = true
```

**When returning to scene:**
```
[SceneStateController] Applying 2 state actions...
[SceneStateController] Ravi: Disabled (flag: ravi_nima_market_discovery_complete)
[SceneStateController] Nima: Disabled (flag: ravi_nima_market_discovery_complete)
```

---

## How It Works

### Timeline of Events

```
FIRST VISIT TO InsideMarket_00:
  Scene loads
  ├─ SceneStateController.Start() runs
  ├─ Checks flag: ravi_nima_market_discovery_complete = false (not set yet)
  ├─ Does NOT disable Ravi/Nima (flag not true)
  └─ Ravi & Nima are visible ✓

  Player talks to Ravi & Nima
  ├─ Dialogue plays through all beats
  └─ At Beat 7, system triggers fire:
     ├─ disable_npc Ravi
     ├─ disable_npc Nima
     └─ set_flag ravi_nima_market_discovery_complete = true ✓

  Ravi & Nima GameObjects are now disabled ✓

RETURN TO InsideMarket_00 (after leaving scene):
  Scene loads
  ├─ SceneStateController.Start() runs
  ├─ Checks flag: ravi_nima_market_discovery_complete = true ✓
  ├─ Action 1: Disable Ravi (flag is true, so do it)
  ├─ Action 2: Disable Nima (flag is true, so do it)
  └─ Ravi & Nima stay disabled ✓
```

---

## Troubleshooting

### Ravi & Nima Still Visible After Dialogue
**Problem:** They don't disappear when dialogue ends
**Solution:**
1. Check console for: `[DialogueManager] NPC disabled: Ravi/Nima`
2. If not present, verify your dialogue JSON has the `disable_npc` triggers
3. Verify Ravi and Nima GameObjects are named exactly `Ravi` and `Nima`
4. Verify GameObjects are actually being disabled (not just invisible)

### They Reappear When Returning to Scene
**Problem:** NPCs come back after leaving scene
**Solution:**
1. Check **SceneManager** has **SceneStateController** component added
2. In SceneStateController Inspector, verify Actions list has 2 entries
3. Verify both Actions have:
   - Required Flag: `ravi_nima_market_discovery_complete`
   - Set Active: **FALSE** (checkbox unchecked)
   - Target: Points to actual Ravi/Nima GameObjects
4. Check console when returning: `[SceneStateController] Disabled (flag:...)`
5. If not showing up, double-check SceneStateController is on SceneManager (not separate GameObject)

### Flag Not Being Set
**Problem:** Flag `ravi_nima_market_discovery_complete` is not true
**Solution:**
1. Check dialogue completes all 7 beats
2. Verify Beat 7 has system_triggers with `set_flag`
3. Check console: `[DialogueManager] Flag set: ravi_nima_market_discovery_complete = true`
4. Verify flag is being checked: press Play, go to console, type flag value check

### GameObject Names Not Matching
**Problem:** Console says "Could not find NPC to disable: Ravi"
**Solution:**
1. Check exact spelling of Ravi/Nima GameObjects in scene
2. Case-sensitive! Must be exactly "Ravi" and "Nima"
3. If named differently (e.g., "Ravi_NPC"), update dialogue JSON or rename GameObjects in scene
4. Verify they're at scene root or check GameObject.Find() scope

### SceneStateController Not Running
**Problem:** State actions never execute
**Solution:**
1. Check SceneStateController component is on **SceneManager** GameObject
2. Verify SceneManager has a checkmark (component enabled)
3. Check that SceneStateController script is assigned (not missing)
4. Look for console errors when scene loads
5. Verify Start() method is being called: add debug log if needed

---

## Architecture: Scene Management

Your scenes use a clean **SceneManager** pattern:

```
Every Scene Root:
└── SceneManager (Single GameObject)
    ├── SceneTransitionManager - Handles fade/load transitions
    ├── SceneSpawnManager - Spawns NPCs/items at scene start
    └── SceneStateController - Applies conditional state (NEW)
```

This centralizes all scene-level logic in one place!

### SceneStateController Role
- Runs at scene start
- Checks all GameFlags
- Applies state actions (disable/enable objects)
- Ensures consistent state on revisits

---

### DialogueManager.cs
- Added `disable_npc` trigger handler
- Updated `set_flag` to support both key/value and data array formats
- Finds NPC by name and calls `GameObject.SetActive(false)`

### BeatData.cs
- Updated `SystemTrigger` class to support `key` and `value` fields
- Supports both JSON formats:
  - Array format: `data: ["Ravi"]`
  - Key-value format: `key: "Ravi"`

---

## Implementation Complete ✅

The system is now fully implemented:
1. ✅ DialogueManager handles disable_npc triggers
2. ✅ GameFlags persists state across scenes
3. ⚠️ SceneStateController setup needed (via Inspector)

**Next Step:** Follow the setup instructions above to configure SceneStateController in your InsideMarket_00 scene!
