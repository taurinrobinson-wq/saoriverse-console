# Global State & NPC Appearance System

## Overview

This system manages persistent game state across scenes, allowing NPCs to appear/disappear based on dialogue completion and other global flags.

## Architecture

### 1. **GlobalStateManager** (Persistent Singleton)
- Lives across all scene changes (`DontDestroyOnLoad`)
- Manages the lifecycle of all persistent singletons
- Auto-creates on first scene load via `DialogueManager.Awake()`

```csharp
GlobalStateManager.GetOrCreate();
GlobalStateManager.Instance.DebugPrintFlags();
GlobalStateManager.Instance.ResetAllState();
```

### 2. **GameFlags** (Static Dictionary)
- Global key-value store for boolean flags
- Persists across scenes via GlobalStateManager
- Set from dialogue system triggers

```csharp
GameFlags.Set("ravi_nima_market_discovery_complete", true);
if (GameFlags.Get("ravi_nima_market_discovery_complete")) { ... }
GameFlags.HasFlag("some_flag");
```

### 3. **SceneStateController** (Per-Scene)
- Attaches to scene root
- Reads GameFlags on scene load
- Shows/hides NPCs based on flag values
- Applied in `Start()` automatically

## Workflow: Ravi & Nima Example

### Step 1: Set Flags in Dialogue JSON
After player completes Ravi/Nima encounter, set a flag:

```json
{
  "id": 7,
  "mode": "player_posture",
  "prompt": "...",
  "tone_choices": [...],
  "next_beat_id": 0,
  "system_triggers": [
    {
      "type": "set_flag",
      "key": "ravi_nima_market_discovery_complete",
      "value": true,
      "note": "Marks completion of first market encounter"
    }
  ]
}
```

### Step 2: Create NPC GameObjects with Tags
In the scene (e.g., InsideMarket_00):
- Create GameObject: "Ravi"
  - Add tag: "ravi" (and/or "npc", "market", "encounter")
  - Add Collider, NPC scripts, etc.
- Create GameObject: "Nima"
  - Add tag: "nima"
  - Add Collider, NPC scripts, etc.

### Step 3: Configure SceneStateController
Add SceneStateController to scene root:

1. In Inspector, create State Actions:
   - **Action 1:**
     - Required Flag: `ravi_nima_market_discovery_complete`
     - Target: Ravi GameObject
     - Set Active: FALSE (hide after dialogue)
   - **Action 2:**
     - Required Flag: `ravi_nima_market_discovery_complete`
     - Target: Nima GameObject
     - Set Active: FALSE (hide after dialogue)

2. When player re-enters InsideMarket_00:
   - SceneStateController reads GameFlags at Start()
   - Finds flag is TRUE
   - Disables Ravi and Nima GameObjects
   - NPCs are hidden from view

## NPC Tag System (Future Enhancement)

The tag system allows more complex behaviors:

```csharp
// Example: Show NPC only if player has talked to them
if (GameFlags.Get("talked_to_ravi"))
{
    ShowNPCsByTag("ravi");
}

// Example: Hide all market NPCs after discovery
if (GameFlags.Get("ravi_nima_market_discovery_complete"))
{
    HideNPCsByTag("market");
}
```

Could be implemented as additional system trigger types:
- `"type": "show_npc_by_tag"` - Show all NPCs with specific tag
- `"type": "hide_npc_by_tag"` - Hide all NPCs with specific tag
- `"type": "enable_interaction_by_tag"` - Enable colliders/interaction for tagged NPCs

## Debugging

Check what flags are currently set:

```csharp
// In Console or Debug menu:
GlobalStateManager.Instance.DebugPrintFlags();

// Output:
// [GlobalStateManager] Active flags:
//   ravi_nima_market_discovery_complete = True
//   saori_desert_encounter_complete = True
//   willy_dialogue_started = True
// Total flags: 3
```

## Best Practices

1. **Flag Naming Convention:**
   - Use snake_case: `ravi_nima_market_discovery_complete`
   - Include event + action: `[npc]_[scene]_[event]_[state]`
   - Examples:
     - `ravi_nima_market_discovery_complete`
     - `saori_desert_encounter_complete`
     - `willy_first_dialogue_started`

2. **When to Set Flags:**
   - At end of dialogue beats (see system_triggers in JSON)
   - On glyph collection (see GlyphPickup.cs)
   - On scene entry for important state changes

3. **Scene State Actions:**
   - One action per NPC/object you want to control
   - Use requiredFlag to gate the action
   - Can disable individual Colliders or entire GameObjects

4. **Testing:**
   - Use `GlobalStateManager.Instance.DebugPrintFlags()` in Console
   - Use `ResetAllState()` between test runs
   - SceneStateController logs all actions applied

## File References

- [GlobalStateManager.cs](../Scripts/Management/GlobalStateManager.cs)
- [GameFlags.cs](../Scripts/Core/GameFlags.cs)
- [SceneStateController.cs](../Scripts/Management/SceneStateController.cs)
- [DialogueManager.cs](../Scripts/Core/DialogueManager.cs) - Initializes GlobalStateManager
