# Velinor Architecture Inventory

## ✅ What You Already Have

### 1. **GameFlags** (Static Persistent State)
- **Location**: `Assets/Scripts/Core/GameFlags.cs`
- **Purpose**: Dictionary-based flag system (string key → bool value)
- **Persistence**: Static, survives scene loads automatically
- **Usage**: `GameFlags.Set("willy_dialogue_complete", true)`
- **Status**: ✅ Ready to use

### 2. **UIPersistenceManager** (UI Canvas Persistence)
- **Location**: `Assets/Scripts/UI/UIPersistenceManager.cs`
- **Purpose**: Ensures UI_Canvas doesn't get destroyed on scene loads
- **Mechanism**: DontDestroyOnLoad singleton pattern
- **Status**: ✅ Working

### 3. **SceneTransitionManager** (Scene Loading + Fade)
- **Location**: `Assets/Scripts/SceneTransitionManager.cs`
- **Purpose**: Async scene loading with fade in/out
- **Mechanism**: Uses `SceneManager.LoadSceneAsync` + coroutines
- **Persistence**: DontDestroyOnLoad singleton
- **Status**: ✅ Working

### 4. **SceneSpawnManager** (Player Spawn Positioning)
- **Location**: `Assets/Scripts/SceneSpawnManager.cs`
- **Purpose**: Moves player to correct spawn point on scene load
- **Uses**: `SpawnPoint` components with SpawnID matching
- **Cross-Scene Ref**: `SceneSpawnManager.nextSpawnID` (string static)
- **Status**: ✅ Working

### 5. **GlyphPickup** (Glyph Collection)
- **Location**: `Assets/Scripts/Core/GlyphPickup.cs`
- **Current Issue**: 
  - Adds glyph to `CodexController` (local scene object, resets on load)
  - Sets `hasBeenCollected` locally (not persisted)
  - No global tracking → glyphs respawn on scene reload
- **Status**: ❌ Not persistent

### 6. **CodexController** (Codex/Glyph Storage)
- **Purpose**: Stores collected glyphs in scene
- **Issue**: Scene-local, resets on load
- **Status**: ❌ Needs global backing

### 7. **DialogueManager** (Dialogue Playback)
- **Location**: `Assets/Scripts/Core/DialogueManager.cs`
- **Features**: 
  - Reads JSON dialogue files
  - Supports `system_triggers` (not yet fully implemented)
  - Calls `ProcessBeatSystemTriggers()` but limited handling
- **Issue**: Doesn't process `diary_append`, `set_flag`, movement speed changes
- **Status**: ⚠️ Partially ready

## ❌ What You're Missing

### 1. **Global Glyph Tracker**
- Need: Persistent HashSet/List of collected glyph IDs
- Should integrate with: `GameFlags` or a new `GameState` class

### 2. **System Trigger Handler** (in DialogueManager)
- Need: Full implementation of `system_triggers` types:
  - `set_flag` → call `GameFlags.Set()`
  - `diary_append` → call `DiaryManager.Append()`
  - `movement_speed` → apply to player controller
  - `spawn_npc` / `despawn_npc` → scene state changes

### 3. **Scene State Controller** (Per-Scene)
- Need: Simple script on each scene root that:
  - Checks `GameFlags` at Start
  - Shows/hides NPCs based on flags
  - Enables/disables glyph colliders
  - Removes debris if flag set

### 4. **One-Time Trigger System** (for Glyph Encounters)
- Need: Wrapper around colliders that fires only once
- Current Issue: Glyph collision can fire multiple times
- Solution: Check flag before triggering dialogue

### 5. **Narrative Sequence System** (Optional but powerful)
- Need: State machine for multi-part sequences
- Example: Willy encounter phases (intro → payment → NPC shift)
- Could be implemented in `DialogueManager` or separate

## 🎯 Dependencies & Data Flow

```
Scene Loads
    ↓
[SceneSpawnManager] → Places player at nextSpawnID
    ↓
[SceneStateController] → Checks GameFlags, hides/shows objects
    ↓
Player Interacts with Glyph
    ↓
[GlyphPickup] → Triggers collision
    ↓
[DialogueManager] → Plays payment dialogue
    ↓
[system_triggers] → Applies effects (speed, flags, diary)
    ↓
[GameFlags] → Persists state
    ↓
Player Moves to Next Scene
    ↓
[SceneSpawnManager] → Uses nextSpawnID
    ↓
[SceneStateController] → Reads updated GameFlags, repositions NPCs
    ↓
✅ New scene reflects all changes from previous scene
```

## 🚀 Implementation Priority

### Phase 1: Make Glyphs Persistent (TODAY)
1. Add glyph collection tracking to `GameFlags`
2. Modify `GlyphPickup.CollectGlyph()` to set flag
3. Add `SceneStateController` to disable glyph colliders if collected

### Phase 2: Make Dialogue Effects Persistent (TODAY)
1. Implement full `system_triggers` in `DialogueManager`
2. Add movement speed handler
3. Add flag setter

### Phase 3: Multi-Scene State (THIS WEEK)
1. Create reusable `SceneStateController` template
2. Apply to each scene
3. Test NPC visibility persistence

### Phase 4: Narrative Sequences (LATER)
1. Add sequence state machine
2. Enable cinematic multi-part encounters
