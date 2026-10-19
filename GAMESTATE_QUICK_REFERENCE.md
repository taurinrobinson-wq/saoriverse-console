# GameState System - Quick Reference Card

## One-Liner: What Is This?

**A singleton that tracks NPC visibility across all scenes using a Dictionary, plus components that apply that state when scenes load.**

---

## Files & Where They Go

```
Assets/Scripts/GameState/
├─ GameState.cs .............. Singleton, tracks all state
├─ NPCState.cs ............... Attach to each NPC
└─ SceneStateApplier.cs ....... Attach to each scene root
```

---

## 60-Second Setup

```
1. Create "GameState" GameObject in first scene
   └─ Add GameState component (auto-persists)

2. Add NPCState to each NPC
   └─ Set npcID = GameObject name

3. Add SceneStateApplier to each scene root
   └─ That's it

4. Use in your code:
   GameState.Instance.SetNPCVisibility("Ravi", false);
```

---

## API Cheat Sheet

### NPC Visibility
```csharp
GameState.Instance.SetNPCVisibility("Ravi", false);  // Hide
GameState.Instance.SetNPCVisibility("Ravi", true);   // Show
bool visible = GameState.Instance.GetNPCVisibility("Ravi");
```

### Dialogue Flags
```csharp
GameState.Instance.SetDialogueFlag("ravi_met", true);
bool met = GameState.Instance.GetDialogueFlag("ravi_met");
```

### Glyph Flags
```csharp
GameState.Instance.SetGlyphFlag("glyph_sorrow", true);
bool has = GameState.Instance.GetGlyphFlag("glyph_sorrow");
```

### Quest States
```csharp
GameState.Instance.SetQuestState("quest_1", "completed");
string state = GameState.Instance.GetQuestState("quest_1");
```

### Debug
```csharp
GameState.Instance.DebugPrintState();  // Print ALL state
GameState.Instance.ResetAllState();    // Clear everything
```

---

## How It Works (The Flow)

### When You Hide an NPC
```
You call: GameState.SetNPCVisibility("Ravi", false)
    ↓
GameState updates Dictionary: npcVisibility["Ravi"] = false
    ↓
NPCState component notices (optional, for immediate feedback)
    ↓
SetActive(false) runs immediately (visual feedback)
```

### When Scene Loads
```
Scene loads
    ↓
SceneStateApplier.Start() runs
    ↓
Finds all NPCState components
    ↓
For each NPC:
  - Calls NPCState.ApplyState()
  - Checks GameState.GetNPCVisibility(npcID)
  - SetActive(true/false) based on state
```

---

## Real Code Example

### In DialogueManager.cs
```csharp
// When dialogue completes and disable_npc trigger fires:
if (trigger.type == "disable_npc")
{
    string npcName = trigger.key ?? trigger.data[0];
    GameState.Instance.SetNPCVisibility(npcName, false);
    GameObject.Find(npcName).SetActive(false);
}
```

### In Any Collider/Trigger
```csharp
private void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("Player"))
    {
        GameState.Instance.SetNPCVisibility("Kaelen", true);
    }
}
```

### Checking State
```csharp
if (GameState.Instance.GetNPCVisibility("Ravi"))
{
    // Ravi is supposed to be visible
}
```

---

## Console Commands (For Testing)

```csharp
// Hide Ravi
GameState.Instance.SetNPCVisibility("Ravi", false)

// Show Kaelen
GameState.Instance.SetNPCVisibility("Kaelen", true)

// See all state
GameState.Instance.DebugPrintState()

// Reset everything
GameState.Instance.ResetAllState()

// Check if flag exists
GameState.Instance.GetDialogueFlag("some_flag")
```

---

## Component Checklist

**Every NPC needs:**
- [ ] Existing NPC components (dialogue, etc.)
- [ ] NPCState component
  - [ ] npcID set to exact GameObject name
  - [ ] debugMode: false (unless testing)

**Every Scene needs:**
- [ ] SceneManager or root GameObject
- [ ] SceneStateApplier component
  - [ ] debugMode: false (unless testing)

**Every Project needs:**
- [ ] One GameState GameObject (any always-loaded scene)
- [ ] GameState component added to it

---

## Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| NPCs disappear on scene reload | Add NPCState to NPC, set npcID correctly |
| State doesn't persist between scenes | GameState must exist and use DontDestroyOnLoad |
| Changes don't apply immediately | Call SetActive() after GameState.SetNPCVisibility() |
| Found 0 NPCs warning | Add NPCState components to all NPCs in scene |
| GameState.Instance is null | Create GameState GameObject in first scene |

---

## Why This Beats Per-Scene Config

**Old Way (SceneStateController):**
- Every scene: Manually add StateAction in Inspector
- Every trigger: Configure in scene's SceneStateController
- Every new NPC: Update all affected scenes
- Result: Confusing, error-prone, hard to maintain

**New Way (GameState):**
- Every scene: Add one generic SceneStateApplier component
- Every trigger: Call `GameState.SetNPCVisibility()`
- Every new NPC: Add NPCState component, done
- Result: Simple, centralized, maintainable

---

## Scaling Example

**With 5 NPCs and 10 Scenes:**

Old way: 50 individual StateAction configurations  
New way: 10 SceneStateApplier components + 5 NPCState components = 15 total

**With 20 NPCs and 30 Scenes:**

Old way: 600+ individual StateAction configurations  
New way: 30 SceneStateApplier components + 20 NPCState components = 50 total

This system **gets better the bigger your game gets.**

---

## Dictionary Structure

```csharp
public Dictionary<string, bool> npcVisibility = 
{
    "Ravi" => false,      // Hidden
    "Nima" => false,      // Hidden
    "Kaelen" => true,     // Visible
    "Willy" => true,      // Visible
    ...
};

public Dictionary<string, bool> dialogueFlags = 
{
    "ravi_nima_market_discovery" => true,
    "kaelen_sorrow_quest" => false,
    ...
};

public Dictionary<string, bool> glyphFlags = 
{
    "glyph_sorrow" => true,
    "glyph_silence" => false,
    ...
};

public Dictionary<string, string> questStates = 
{
    "market_investigation" => "completed",
    "sorrow_collection" => "in_progress",
    ...
};
```

---

## Performance Notes

- **Memory:** 100 flags = ~5KB
- **Speed:** SetNPCVisibility() = instant (O(1) Dictionary lookup)
- **Overhead:** Negligible, not worth optimizing
- **Bottleneck:** Not GameState, it's SetActive() on GameObjects
- **Scaling:** Works fine with 1000+ flags/NPCs

---

## When to Use GameState

✅ Tracking NPC visibility  
✅ Dialogue completion flags  
✅ Glyph collection  
✅ Quest progress  
✅ Any boolean or string state  
✅ Cross-scene communication  

❌ Don't use for: Frame-by-frame gameplay logic  
❌ Don't use for: Physics/colliders  
❌ Don't use for: UI state (use UI system instead)  

---

## Integration Timeline

**15 min:** Setup (add components)  
**30 min:** Test (verify state persists)  
**1 hour:** Update DialogueManager  
**2 hours:** Update all triggers to use GameState  
**1 hour:** Verify everything works  

**Total: ~5 hours to full integration**

Or do it gradually (add GameState, keep old system, migrate over weeks).

---

## Next Steps

1. Read `GAMESTATE_QUICK_START.md` (setup)
2. Read `GAMESTATE_CODE_EXAMPLES.md` (how to use)
3. Follow checklist in `GAMESTATE_IMPLEMENTATION_GUIDE.md`
4. Test with console commands
5. Update DialogueManager
6. Migrate other systems one at a time

---

## Key Insight

**The old system stored state per-scene and you had to manually configure each scene.**

**This system stores state globally and each scene automatically applies it.**

Same information, better architecture. ✓

