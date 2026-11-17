# Mind Log Real Data Integration Guide

## Overview
The Mind Log system now supports two modes:
1. **Test Mode** - Manually populate the grid with MemoryFragments (backward compatible)
2. **Real Data Mode** - Automatically load memories from MindLogManager

## Architecture

### Core Components

#### MindLogEntry (Data Model)
- **LogID**: Unique identifier
- **Icon**: Sprite for grid display
- **SummaryText**: 2-3 word synopsis (single-click display)
- **FullText**: Full memory text (expanded view)
- **CombineTags**: Metadata for combination logic
- **CombinationResultID**: Optional result when combined

#### MindLogManager (Singleton)
Central authority for all memory data.

**Key Methods:**
- `AddLog(MindLogEntry)` - Add/update a log
- `GetLog(string id)` - Retrieve a log
- `GetAllLogs()` - Get all logs
- `CanCombine(idA, idB)` - Check if two logs can combine
- `CombineLogs(idA, idB)` - Combine logs (returns result)
- `RemoveLog(id)` - Remove a log
- `ClearAllLogs()` - Clear all logs

#### MemoryGridController (UI Controller)
Updated to support both test and real data modes.

**Key Methods:**
- `PopulateFromManager()` - Load from MindLogManager (real data)
- `PopulateGrid(List<MemoryFragment>)` - Load from list (test mode)

#### MindLogInitializer (Data Bridge)
Converts existing MemoryFragment assets into MindLogEntry objects.

**Key Methods:**
- `InitializeFromFragments()` - Load all assigned fragments into manager
- `AddFragment(MemoryFragment)` - Add a single fragment at runtime
- `RemoveFragment(string id)` - Remove a fragment

## How to Use

### Step 1: Create MemoryFragment Assets
Create memory data using the existing "Codex/Memory Fragment" scriptable object:
- fragmentID: "memory_saori_desert_encounter"
- displayName: "Saori's Tale"
- icon: [Your sprite]
- shortSynopsis: "A fateful meeting"
- expandedText: "[Full story text]"
- tags: ["saori", "desert", "meeting"]
- combinesWith: (optional combined results)

### Step 2: Set Up the Manager
1. In your scene, create an empty GameObject called "MindLogManager"
2. Add the `MindLogManager` component
3. This is now your singleton - it auto-persists across scenes

### Step 3: Initialize with Data
Option A - Auto-initialize at startup:
1. Create another GameObject "MindLogInitializer"
2. Add `MindLogInitializer` component
3. Drag your MemoryFragment assets into the "Memory Fragments" list
4. Enable "Auto Initialize On Start"

Option B - Manual initialization:
```csharp
// In your gameplay code, when a memory is triggered:
var fragment = Resources.Load<MemoryFragment>("path/to/fragment");
var initializer = FindObjectOfType<MindLogInitializer>();
initializer.AddFragment(fragment);
```

### Step 4: Show the Mind Log Grid
When the player opens the Mind Log:
```csharp
var gridController = FindObjectOfType<MemoryGridController>();
gridController.PopulateFromManager(); // Loads all memories from MindLogManager
```

## Example: Adding a Memory at Runtime

```csharp
// After a dialogue encounter, create a memory
public void OnSaoriEncounterComplete()
{
    var memoryFragment = Resources.Load<MemoryFragment>("Memories/saori_desert");
    
    var initializer = FindObjectOfType<MindLogInitializer>();
    initializer.AddFragment(memoryFragment);
    
    // Grid will show new memory next time it's opened
    Debug.Log("New memory added: Saori's Story");
}
```

## Combination Logic

### Simple Example: Combine Two Memories
```csharp
var manager = MindLogManager.Instance;

// Check if two memories can combine
if (manager.CanCombine("memory_saori_desert", "memory_ravi_encounter"))
{
    // Combine them - returns the result log
    var combined = manager.CombineLogs("memory_saori_desert", "memory_ravi_encounter");
    Debug.Log($"Created combined memory: {combined.LogID}");
}
```

### Tag-Based Combination
Logs combine if they share at least one tag. Currently:
- Entry A: tags ["saori", "desert"]
- Entry B: tags ["desert", "journey"]
- Result: **Can combine** (both have "desert")

### Future Expansion
The combination logic is contained in `MindLogManager.CanCombine()`. You can enhance it with:
- Narrative arc matching
- Emotional tone similarity
- Scene origin grouping
- Character relationship tags
- Timeline proximity

## Testing Workflow

### With Test Data (Old Way)
```csharp
var testFragments = new List<MemoryFragment> { fragment1, fragment2, fragment3 };
gridController.PopulateGrid(testFragments);
```

### With Real Data (New Way)
```csharp
// Initialize manager once
var initializer = FindObjectOfType<MindLogInitializer>();
initializer.InitializeFromFragments();

// Then just show the grid
gridController.PopulateFromManager();
```

## Data Flow

```
MemoryFragment Assets
        ↓
MindLogInitializer
        ↓
MindLogManager (Dictionary<string, MindLogEntry>)
        ↓
MemoryGridController.PopulateFromManager()
        ↓
UI Grid Display
```

## Troubleshooting

**"MindLogManager instance not found!"**
- Ensure a GameObject with MindLogManager component exists in the scene
- Check that it's initialized before trying to access Instance

**"Memory doesn't appear in grid"**
- Check that MindLogInitializer ran (watch console logs)
- Verify MemoryFragment.IsValid() returns true
- Ensure PopulateFromManager() is called after initialization

**Combination returns null**
- Tags don't match between entries
- CombinationResultID not set on either entry
- Result log doesn't exist in manager

## Next Steps

1. ✅ Create core data structures (MindLogEntry, MindLogManager)
2. ✅ Create data bridge (MindLogInitializer)
3. ✅ Update UI to read from manager
4. ⏭️ Create real memory assets for your story
5. ⏭️ Hook memories into dialogue events
6. ⏭️ Implement combination results
7. ⏭️ Add combination UI feedback (green/red button states)
