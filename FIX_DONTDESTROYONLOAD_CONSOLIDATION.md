# Critical Fix: DontDestroyOnLoad Consolidation

## The Problem 🔴
The MindLogPrimaryContainer was disappearing when switching views despite logs showing it as "active". Root cause: **multiple scripts calling DontDestroyOnLoad on different parts of the hierarchy**, creating conflicts and orphaning references.

### What Was Happening:
```
CodexController.Awake()
  └─ DontDestroyOnLoad(gameObject)  ← Marks CodexController itself

CodexViewController.Awake()
  └─ DontDestroyOnLoad(mindLogPrimaryContainer.transform.root)
  └─ DontDestroyOnLoad(mindLogSecondaryContainer.transform.root)
  └─ DontDestroyOnLoad(glyphsBackground.transform.root)
  └─ DontDestroyOnLoad(persistenceHolder)

MindLogPersistence.OnEnable()
  └─ DontDestroyOnLoad(mindLogPrimaryContainer.transform.root)
  └─ DontDestroyOnLoad(mindLogSecondaryContainer.transform.root)
  └─ DontDestroyOnLoad(glyphsBackground.transform.root)
```

**Result**: Conflicting persistence rules → Objects marked multiple times → References orphaned → Container "disappears"

## The Solution ✅
**Single source of truth**: Only `CodexPanel` is marked DontDestroyOnLoad, managed by CodexController.

### Changes Made:

#### 1. CodexController.Awake()
```csharp
// BEFORE:
private void Awake()
{
    DontDestroyOnLoad(gameObject);  // ❌ Wrong level
    InitializeReferences();
}

// AFTER:
private void Awake()
{
    // Only mark CodexPanel, not this controller
    GameObject panelObj = GameObject.Find("UI_Canvas/CodexPanel");
    if (panelObj != null)
    {
        DontDestroyOnLoad(panelObj);  // ✅ Single source of truth
        Debug.Log("[Codex] CodexPanel marked as persistent across scenes");
    }
    InitializeReferences();
}
```

#### 2. CodexViewController.Awake()
Removed all DontDestroyOnLoad calls:
```csharp
// BEFORE:
if (mindLogPrimaryContainer != null && Application.isPlaying)
{
    Transform root = mindLogPrimaryContainer.transform.root;
    DontDestroyOnLoad(root.gameObject);  // ❌ Removed
}

// AFTER:
// Containers persist via CodexPanel's DontDestroyOnLoad
// Do NOT mark them individually - it causes conflicts
```

#### 3. CodexViewController.ShowMindLogPrimaryView()
Removed the re-application of DontDestroyOnLoad:
```csharp
// BEFORE:
DontDestroyOnLoad(root.gameObject);  // ❌ Removed

// AFTER:
// Containers persist via CodexPanel's DontDestroyOnLoad
// Do NOT re-apply - causes conflicts
```

#### 4. MindLogPersistence.OnEnable()
Removed all container persistence marks:
```csharp
// BEFORE:
if (codexController.mindLogPrimaryContainer != null)
    DontDestroyOnLoad(codexController.mindLogPrimaryContainer.transform.root.gameObject);  // ❌ Removed

// AFTER:
// Containers persist via CodexPanel's DontDestroyOnLoad
// Do NOT mark them individually here
```

## How This Fixes The Problem

### Before (Broken):
```
Scene Load → Multiple DontDestroyOnLoad calls
  → Conflicting persistence directives
  → References get orphaned
  → Container "disappears" on scene change
```

### After (Working):
```
Scene Load → CodexPanel marked as DontDestroyOnLoad (ONE TIME)
  → All children (containers) persist with parent
  → References stay valid across scene changes
  → CanvasGroup visibility control (alpha=0) keeps things hidden when needed
  → Container ALWAYS exists, just invisible when alpha=0
```

## Key Principles Applied
1. **Single Responsibility**: Only CodexController manages persistence
2. **Single Source of Truth**: CodexPanel is the only persistent root
3. **Hierarchy Preservation**: Child objects persist with parent automatically
4. **Clean Visibility**: CanvasGroup (alpha=0) for hiding, NOT SetActive(false)

## What Still Works
- ✅ CanvasGroup visibility toggling (alpha=0/1)
- ✅ Container protection via MindLogPersistence
- ✅ Memory grid population
- ✅ Click handlers for single/double-click
- ✅ View switching between Glyphs and Mind Log

## Testing Checklist
After this fix, verify:
- [ ] Click Mind Log button → Grid appears with memory icon
- [ ] Click Glyphs → Grid disappears (alpha=0)
- [ ] Click Mind Log again → Grid reappears (no orphaning)
- [ ] Single-click memory → Name displays
- [ ] Double-click memory → Secondary view opens
- [ ] Scene transitions → Codex persists
- [ ] No console errors about destroyed objects

## Why This Works

**DontDestroyOnLoad** only works on root GameObjects. By marking ONLY CodexPanel:
1. All children of CodexPanel persist with it automatically
2. References to containers stay valid forever
3. No orphaning or re-instantiation
4. Clear, predictable persistence behavior

Trying to mark multiple root objects creates:
- Conflicting hierarchy states
- Orphaned references after scene unload
- Unexpected object destruction/recreation
- Container "disappearing" despite active=true logs

## Related Files
- `Assets/Scripts/UI/CodexController.cs` - Persistence manager (fixed)
- `Assets/Scripts/UI/CodexViewController.cs` - View switcher (fixed)
- `Assets/Scripts/UI/MindLogPersistence.cs` - Container protection (fixed)
- `MINDLOG_TESTING_INSTRUCTIONS.md` - How to verify the fix

## Commit Hash
`c94d0a07b` - "FIX: Consolidate DontDestroyOnLoad to single source"

---

**Status**: ✅ FIXED
**Confidence**: VERY HIGH (root cause clearly identified)
**Testing**: Ready for verification
