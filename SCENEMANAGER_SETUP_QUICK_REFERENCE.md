# SceneManager Setup - Quick Reference

## Where to Add SceneStateController

In each scene, you have **SceneManager** GameObject:

```
InsideMarket_00 (Scene)
└── SceneManager (GameObject) ← ADD COMPONENT HERE
    ├── Transform
    ├── SceneTransitionManager
    ├── SceneSpawnManager
    └── SceneStateController (NEW) ← Click "Add Component"
```

---

## Step-by-Step for InsideMarket_00

### 1. Open Scene & Select SceneManager
- Open: **InsideMarket_00.unity**
- Hierarchy: Click on **SceneManager**

### 2. Add Component
- Inspector: Click **Add Component** button
- Search: `SceneStateController`
- Click to add

### 3. Configure Actions
You should see:
```
Script: SceneStateController
Actions: Size (2)
```

**Action [0]:**
```
Required Flag:   ravi_nima_market_discovery_complete
Target:          Ravi (drag from Hierarchy)
Set Active:      ☐ (unchecked = disabled)
```

**Action [1]:**
```
Required Flag:   ravi_nima_market_discovery_complete
Target:          Nima (drag from Hierarchy)
Set Active:      ☐ (unchecked = disabled)
```

### 4. Save
- Press **Ctrl+S** to save scene

---

## Repeat for Other Scenes

Once the pattern is established, apply the same approach to other scenes:

**DesertToMarketTrek_00:**
- If it has NPCs that should disable, add SceneStateController to SceneManager
- Add appropriate state actions

**DesertToMarketTrek_01:**
- Same pattern as above

**TitleScene:**
- Usually no state actions needed

---

## Console Output When Working

### First Visit - Dialogue Completes:
```
[DialogueManager] NPC disabled: Ravi
[DialogueManager] NPC disabled: Nima
[DialogueManager] Flag set: ravi_nima_market_discovery_complete = true
```

### Return Visit - Scene Loads:
```
[SceneStateController] Applying 2 state actions...
[SceneStateController] Ravi: Disabled (flag: ravi_nima_market_discovery_complete)
[SceneStateController] Nima: Disabled (flag: ravi_nima_market_discovery_complete)
```

---

## What Each Component Does

| Component | Location | Purpose |
|-----------|----------|---------|
| **SceneTransitionManager** | SceneManager | Handles scene fade/load transitions |
| **SceneSpawnManager** | SceneManager | Spawns NPCs, items, props at scene start |
| **SceneStateController** | SceneManager | Applies state changes based on game flags (NEW) |

All three work together to manage the complete scene state!

---

## Common Inspector Mistakes ❌

- ❌ Set Active: **CHECKED** (should be UNCHECKED to disable)
- ❌ Required Flag: `ravi_nima_discovery` (should be `ravi_nima_market_discovery_complete`)
- ❌ Target: Empty or wrong GameObject (drag Ravi/Nima from Hierarchy)
- ❌ SceneStateController on wrong GameObject (should be on SceneManager)

---

## If It's Not Working

1. **Build the project first** - Compile new code
2. **Check console for errors** - Look for red text
3. **Verify component is enabled** - SceneStateController checkbox should be checked
4. **Verify flag name exactly** - Case-sensitive!
5. **Test in Play mode** - Press Play and watch console output

---

## Reference: Full Scene Setup

When complete, every scene should have:

**SceneManager GameObject:**
- SceneTransitionManager (existing)
- SceneSpawnManager (existing)  
- SceneStateController (NEW - if scene has conditional NPC visibility)
- Transform component (standard)

This keeps all scene-level logic in one organized place! ✅
