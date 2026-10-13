# Velinor Persistent State Implementation Guide

## Overview
You now have a **complete persistent state system** that keeps your game world coherent across scene transitions. Here's what was added and how to use it.

---

## ✅ Changes Made

### 1. **GlyphPickup.cs** - Glyph Persistence
**File**: `Assets/Scripts/Core/GlyphPickup.cs`

**Changes**:
- Added `glyphCollectionFlag` string (auto-generated from glyph name)
- On `Start()`: Check if glyph was already collected via `GameFlags`
- On `CollectGlyph()`: Set flag to mark glyph as permanently collected

**Result**: ✅ Glyphs don't respawn when you return to a scene

**Example**:
```csharp
// When player collects "Sorrow" glyph:
// Flag set: "glyph_collected_sorrow" = true

// Player returns to scene later:
// Script checks flag on Start() → glyph is disabled
```

---

### 2. **DialogueManager.cs** - System Triggers Expansion
**File**: `Assets/Scripts/Core/DialogueManager.cs`

**New Trigger Types**:

#### `set_flag`
Sets a persistent flag globally.
```json
{
  "type": "system_triggers",
  "data": [
    {
      "type": "set_flag",
      "data": ["willy_dialogue_complete", "true"]
    }
  ]
}
```

#### `diary_append`
Creates a new MindLogEntry and adds to MindLogManager.
```json
{
  "type": "system_triggers",
  "data": [
    {
      "type": "diary_append",
      "data": [
        "Met a scrapper named Willy in the Concourse Ruins.",
        "Willy Encounter"
      ]
    }
  ]
}
```
- `data[0]`: Entry content/summary
- `data[1]`: Entry title (optional, defaults to "Encounter Log")

#### `movement_speed`
Changes player walk speed at runtime.
```json
{
  "type": "system_triggers",
  "data": [
    {
      "type": "movement_speed",
      "data": ["0.5"]
    }
  ]
}
```
- `data[0]`: New speed value (float as string)
- Example: "0.5" = 50% of normal speed
- Example: "2.0" = 2x normal speed

---

### 3. **PlayerController2D5.cs** - Movement Speed Control
**File**: `Assets/Scripts/PlayerController2D5.cs`

**New Method**:
```csharp
public void SetMoveSpeed(float newSpeed)
```

Called by DialogueManager when `movement_speed` trigger executes.

---

### 4. **SceneStateController.cs** - Per-Scene State Management
**File**: `Assets/Scripts/Management/SceneStateController.cs` (NEW FILE)

Attaches to each scene root and applies state changes based on GameFlags.

---

## 🚀 How to Use This System

### Step 1: Add SceneStateController to Each Scene

1. **Open each scene** you want to use persistent state in
2. **Select the scene root** (top-level empty GameObject)
3. **Add Component → SceneStateController**
4. In Inspector, set up your state actions

### Step 2: Configure State Actions

For each state change you want to persist:

1. **Increment "Actions" list size**
2. **Set "Required Flag"** - the GameFlags key that must be true
3. **Set "Target"** - the GameObject to hide/show
4. **Set "Set Active"** - whether to enable (✓) or disable (✗)

### Step 3: Example Setup for InsideMarket_01

**Scenario**: After Willy dialogue, Willy should be hidden and the glyph should be uncollectible.

**State Actions**:
| Required Flag | Target | Set Active | Purpose |
|---|---|---|---|
| `willy_dialogue_complete` | Willy (NPC) | ✗ (unchecked) | Hide Willy after dialogue |
| `sorrow_glyph_collected` | GlyphPickup | ✗ (unchecked) | Disable glyph collider after collection |

**Result**:
- When scene loads with `willy_dialogue_complete=true` → Willy hidden automatically
- When scene loads with `sorrow_glyph_collected=true` → Glyph disabled automatically

---

## 📋 Dialogue JSON Pattern

Here's the pattern for your dialogue payment sequences:

```json
{
  "id": 5,
  "type": "npc_turn",
  "active_speaker": "Willy",
  "prompt": "Everything down here has a price...",
  "system_triggers": [
    {
      "type": "set_flag",
      "data": ["willy_dialogue_complete", "true"]
    },
    {
      "type": "movement_speed",
      "data": ["0.5"]
    },
    {
      "type": "diary_append",
      "data": [
        "Met a scrapper named Willy in the Concourse Ruins. He was an odd character...laughing at suffering, coughing constantly...but helpful and not malicious.",
        "Willy Encounter"
      ]
    },
    {
      "type": "close_dialogue"
    }
  ]
}
```

---

## 🔄 Data Flow Example: Willy Encounter

### Initial State
```
GameFlags: {}
Scene: InsideMarket_01
- Willy visible ✓
- GlyphPickup active ✓
```

### Player Collects Glyph
```
GlyphPickup.OnTriggerEnter()
  ↓
CollectGlyph()
  ↓
GameFlags.Set("glyph_collected_sorrow", true) ← NEW
GameFlags.Set("glyph_collected_sorrow", true)
```

### Willy Payment Dialogue
```
DialogueManager.ProcessBeatSystemTriggers()
  ↓
set_flag: "willy_dialogue_complete" = true
movement_speed: 0.5
diary_append: "Willy Encounter"
close_dialogue
  ↓
GameFlags.Set("willy_dialogue_complete", true) ← NEW
PlayerController2D5.SetMoveSpeed(0.5) ← NEW
MindLogManager.AddLog(entry) ← NEW
```

### Player Moves to Next Scene
```
SceneTransitionManager loads InsideMarket_00
  ↓
SceneStateController.Start()
  ↓
Check GameFlags:
  - "willy_dialogue_complete" = true
    → Hide Willy NPC
  - Any other flags...
```

### Player Returns to InsideMarket_01
```
Scene loads
  ↓
GlyphPickup.Start()
  ↓
Check GameFlags:
  - "glyph_collected_sorrow" = true
    → Disable collider, hide visuals
```

---

## ✨ Key Benefits

| Before | After |
|--------|-------|
| ❌ Glyphs respawn on scene reload | ✅ Glyphs stay collected |
| ❌ Dialogue effects reset on scene transition | ✅ Speed slowdown persists |
| ❌ NPC visibility resets | ✅ NPCs stay hidden/shown based on flags |
| ❌ Diary entries lost on scene load | ✅ MindLog entries persist in manager |
| ❌ Manual per-scene setup needed | ✅ Reusable SceneStateController template |

---

## 🧪 Testing the System

### Test 1: Glyph Persistence
1. Play game
2. Collect Sorrow glyph
3. Open Developer Console
4. Type: `GameFlags.Get("glyph_collected_sorrow")`
5. Should return: `true`
6. Return to scene
7. Glyph should be gone

### Test 2: Speed Effect
1. Play game
2. Talk to Willy, trigger payment dialogue
3. Look at player movement speed
4. Should be 50% normal (0.5)
5. Return to next scene and back
6. Should still be 0.5 (if flag still true)

### Test 3: MindLog Entry
1. Collect glyph + talk to Willy
2. Open Codex → MindLog
3. "Willy Encounter" should appear in grid
4. Single-click shows summary
5. Return to scene and back
6. MindLog entry still there (if MindLogManager is DontDestroyOnLoad)

---

## ⚙️ Configuration Checklist

For each scene with persistent elements:

- [ ] Scene has SceneStateController on root
- [ ] Each NPC has StateAction configured
- [ ] Each glyph has StateAction configured  
- [ ] Dialogue JSON has system_triggers set correctly
- [ ] Flags used in system_triggers match StateAction required_flag names
- [ ] Movement speed values are floats (0.5, 1.0, 2.0, etc.)
- [ ] MindLog entries have titles and icons

---

## 🐛 Debugging

### Glyph not staying collected?
1. Check GlyphPickup.Start() logs
2. Verify flag name matches: `glyph_collected_{glyphName.ToLower()}`
3. Ensure GlyphPickup.CollectGlyph() is being called

### Speed not changing?
1. Check DialogueManager trigger processing logs
2. Verify PlayerController2D5 is on player
3. Check if `SetMoveSpeed()` was called

### StateAction not applying?
1. Check SceneStateController.Start() logs
2. Verify flag is actually set to true: `GameFlags.Get("flag_name")`
3. Confirm target GameObject exists in scene

### MindLog entry not appearing?
1. Verify MindLogManager is DontDestroyOnLoad
2. Check diary_append trigger format
3. Ensure content string has text

---

## 📚 Files Modified

- `Assets/Scripts/Core/GlyphPickup.cs` - Added glyph flag persistence
- `Assets/Scripts/Core/DialogueManager.cs` - Expanded system triggers
- `Assets/Scripts/PlayerController2D5.cs` - Added SetMoveSpeed() method
- `Assets/Scripts/Management/SceneStateController.cs` - NEW file

## ✅ System Status

- [x] Glyph persistence via GameFlags
- [x] Dialogue system triggers (set_flag, movement_speed, diary_append)
- [x] Player speed control
- [x] Per-scene state controller
- [x] MindLog integration
- [ ] Test across all three glyphs
- [ ] Test multi-scene transitions
- [ ] Validate MindLog entries display correctly
