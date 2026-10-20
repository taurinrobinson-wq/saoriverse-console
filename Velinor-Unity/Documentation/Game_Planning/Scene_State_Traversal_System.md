# Velinor Scene-State Traversal System

*A lightweight, collider-driven scene progression architecture for Unity.*

## Overview

**Problem**: Players should never revisit the same emotional or narrative moment twice, even if they walk backward through scenes.

**Solution**: Use scene duplication with incremented state numbers. The player believes they are returning to the same location. In reality, they are loading a *different version* of that location with updated NPCs, glyphs, and narrative state.

**No persistent world simulation. No global flags. No complex state machines. Just clean snapshots.**

---

## 1. Naming Convention

Use this exact pattern:

```
Location_StateNum
```

### Examples:

```
Market_01      → First version (Ravi & Nima present, marketplace active)
Market_02      → Second version (Nima absent, Ravi waiting)
Market_03      → Third version (post-glyph event, Nima returns)

Desert_01      → First version (empty, harsh)
Desert_02      → Second version (Saori encounter)

TrigglyphChamber_01    → First entry (sealed, no glyphs)
TrigglyphChamber_02    → Post-glyph acquisition (glyphs visible)

Velhara_01     → First version (edge camp, Saori present)
Velhara_02     → Second version (Saori absent)
```

### Rules:

- **Never overwrite a scene. Always duplicate.**
- **State numbers only increase. Never reuse or go backward.**
- **Each state is a frozen snapshot of the world at that narrative moment.**
- **Use zero-padding** (01, 02, 03) for natural filesystem sorting.
- **Location names are brief** but clear enough to identify in file explorer.

---

## 2. Folder Structure

Organize scenes by location in `Assets/Scenes/`:

```
Assets/Scenes/
├── Market/
│   ├── Market_01.unity
│   ├── Market_02.unity
│   ├── Market_03.unity
│   └── Market_04.unity
├── Desert/
│   ├── Desert_01.unity
│   ├── Desert_02.unity
│   └── Desert_03.unity
├── TrigglyphChamber/
│   ├── TrigglyphChamber_01.unity
│   └── TrigglyphChamber_02.unity
├── Velhara/
│   ├── Velhara_01.unity
│   ├── Velhara_02.unity
│   ├── Velhara_03.unity
│   └── Velhara_04.unity
├── MysticEncampment/
│   ├── MysticEncampment_01.unity
│   └── MysticEncampment_02.unity
└── [Other Locations]/
```

**Benefits:**
- Instant visual clarity: which scene is in which state?
- Easy to expand: add new states without cluttering the list
- Natural sorting: filesystem organizes by location, then by state number
- Minimal search time: "I need Desert" → look in `/Desert/` folder

---

## 3. Collider-Based Traversal System

Each scene contains **multiple colliders** representing exits to other locations. Only **one collider per direction** is enabled at any time.

### Example: Market_01 Scene Hierarchy

```
Market_01.unity
├── [Scene Objects, NPCs, etc.]
├── ExitToDesert
│   ├── Collider_ToDesert_01 (enabled)
├── ExitToVelhara
│   ├── Collider_ToVelhara_01 (disabled)
│   ├── Collider_ToVelhara_02 (disabled)
├── ExitToMysticEncampment
│   ├── Collider_ToMysticEncampment_01 (enabled)
└── ExitToTrigglyphChamber
    ├── Collider_ToTrigglyphChamber_01 (enabled)
    └── Collider_ToTrigglyphChamber_02 (disabled)
```

**Rule**: For each possible destination, create separate collider GameObjects. Only enable the one(s) that should be active in the current state.

### Why Multiple Colliders?

Imagine the player's journey:

1. **Market_01** → player talks to Ravi (he warns: "Don't tell Nima yet")
2. Player exits to Desert, triggers event
3. Player returns to Market → loads **Market_02** (Ravi's warning had effect; Nima is now unavailable)
4. Player later triggers a different event
5. Player returns to Market → loads **Market_03** (Nima returns; new dialogue available)

Each return loads a *different scene*, but the player feels they're in the same location.

---

## 4. Collider Configuration

### Naming Convention for Colliders

```
Collider_To[Location]_[StateNum]
```

### Examples:

```
Collider_ToMarket_01
Collider_ToDesert_02
Collider_ToTrigglyphChamber_01
Collider_ToVelhara_03
```

### Minimal Script (Attach to Each Collider)

```csharp
using UnityEngine;
using UnityEngine.SceneManagement;

public class ScenePortal : MonoBehaviour
{
    [SerializeField] private string sceneToLoad;

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            SceneManager.LoadScene(sceneToLoad);
        }
    }
}
```

**Inspector Setup:**
1. Add the `ScenePortal` script to the collider GameObject
2. Set `sceneToLoad` to the target scene name (e.g., "Desert_02")
3. Disable colliders that should not be active in this state
4. Enable colliders that should be active

---

## 5. Controlling Collider State

Use this pattern to enable/disable colliders when narrative events occur:

```csharp
using UnityEngine;

public class SceneStateController : MonoBehaviour
{
    [SerializeField] private GameObject[] colliders;

    /// <summary>
    /// Enable only the collider at the specified index.
    /// Disable all others.
    /// </summary>
    public void ActivateCollider(int index)
    {
        for (int i = 0; i < colliders.Length; i++)
        {
            colliders[i].SetActive(i == index);
        }
    }

    /// <summary>
    /// Enable/disable a specific collider by name.
    /// </summary>
    public void SetColliderActive(string colliderName, bool active)
    {
        foreach (var collider in colliders)
        {
            if (collider.name == colliderName)
            {
                collider.SetActive(active);
                return;
            }
        }
        Debug.LogWarning($"Collider '{colliderName}' not found in scene.");
    }
}
```

**Usage Example:**

When Ravi finishes his dialogue warning, call:
```csharp
sceneStateController.ActivateCollider(1);  // Enable second collider (exit to Market_02)
```

---

## 6. Scene State Progression: Example Flow

### Story Beats:

1. **Player enters Market_01**
   - Ravi is present, warns: "Don't tell Nima yet"
   - Collider_ToMarket_01 is enabled
   - Exit leads to Desert_01

2. **Player goes to Desert, triggers event**
   - Returns to Market

3. **Market_02 loads** (same location, different state)
   - Nima is absent (Ravi's warning had effect)
   - Ravi has new dialogue
   - Collider_ToMarket_02 is enabled
   - Exit now leads to Desert_02 (post-event version)

4. **Player acquires Glyph of Marked Boundaries**
   - Scene controller switches colliders

5. **Player returns to Market**

6. **Market_03 loads** (newest state)
   - Nima has returned
   - Both Ravi and Nima have post-glyph dialogue
   - Collider_ToMarket_03 is enabled

**The player never sees:**
- Repeated dialogue
- NPCs who should be gone reappearing
- Reset emotional beats
- Broken narrative continuity

**The world feels alive because it never rolls backward.**

---

## 7. Workflow: Creating New Scene States

### Step 1: Build the Initial Version
Create `Market_01.unity` with:
- NPCs (Ravi, Nima)
- Environmental objects
- Colliders (all disabled initially)
- Collider_ToDesert_01 (enabled)
- Collider_ToVelhara_01 (enabled)

### Step 2: Duplicate for Next State
1. In Unity, right-click `Market_01.unity` → Duplicate
2. Rename to `Market_02.unity`
3. Open the new scene

### Step 3: Make Changes
- Remove or hide NPCs (e.g., delete Nima's GameObject)
- Update dialogue if collider uses dialogue JSON
- Update colliders:
  - Disable old exit colliders
  - Enable new ones (e.g., Collider_ToDesert_02)

### Step 4: Repeat
For each major narrative beat, duplicate again and make changes.

**Time investment**: ~5 minutes per new state (mostly duplication + minor changes)

---

## 8. Location Map & Scene State Chart

Fill in this chart to visualize your scene progression. Update it as you plan new states.

| Location | State | Ravi | Nima | Saori | Kaelen | Glyph | Notes |
|----------|-------|------|------|-------|--------|-------|-------|
| Market | 01 | ✓ | ✓ | - | - | - | Initial marketplace encounter |
| Market | 02 | ✓ | - | - | - | - | After Ravi's warning; Nima absent |
| Market | 03 | ✓ | ✓ | - | - | ✓ | Post-glyph; Nima returns |
| Desert | 01 | - | - | - | - | - | First exploration |
| Desert | 02 | - | - | ✓ | - | - | Saori encounter |
| TrigglyphChamber | 01 | - | - | - | - | - | Sealed, first entry |
| TrigglyphChamber | 02 | - | - | - | - | ✓ | Glyphs visible; story puzzle active |
| Velhara | 01 | - | - | ✓ | - | - | Saori at edge camp |
| Velhara | 02 | - | - | - | - | - | Post-Saori event |

---

## 9. Tips & Best Practices

### Don't:
- ❌ Use global flags to track scene state (the scene name *is* your state)
- ❌ Toggle NPCs on/off at runtime (create new scene states instead)
- ❌ Reuse state numbers (01, 02, 01 again breaks continuity)
- ❌ Make state numbers sparse (Market_01, Market_47 creates confusion)

### Do:
- ✅ Create one scene per narrative beat
- ✅ Name colliders clearly so you know where they lead
- ✅ Keep the scene folder structure clean (one folder per location)
- ✅ Duplicate rather than edit (preserves old states for reference)
- ✅ Comment in dialogue JSON which scene state it belongs to

### Performance Consideration:
If you have many states, you might accumulate 50+ scene files. This is fine:
- Scene files are small (mostly references)
- Unity's build system only includes active scenes
- Duplication doesn't affect runtime performance

---

## 10. Integration with Dialogue System

Your existing dialogue JSON files (like `ravi_encounter_01.json`) can reference which scene state they belong to:

```json
{
  "scene_id": "ravi_encounter_01",
  "scene_state": "Market_02",
  "required_flags": ["ravi_nima_dialogue_01_true"],
  "beats": [
    {
      "id": 1,
      "active_speaker": "Ravi",
      "prompt": "Don't tell Nima what you saw. Not yet."
    }
  ]
}
```

This way, the dialogue loader can verify: "Am I in the right scene state for this dialogue?"

---

## 11. Troubleshooting

### Q: Player loads wrong scene version
**A**: Check which colliders are enabled in the previous scene. Only one per direction should be active.

### Q: NPC dialogue repeats across states
**A**: Create a new dialogue JSON for each state's version of the conversation. Update collider references.

### Q: State numbers getting out of sync
**A**: Use a naming convention strictly. Never manually reorder. Always increment.

### Q: Too many scene files
**A**: This is expected. Organize into location folders. Use `.gitignore` if needed.

---

## 12. Summary: The Entire System in 5 Points

1. **Naming**: `Location_StateNum` (Market_01, Market_02, etc.)
2. **Folders**: One folder per location containing all its state versions
3. **Colliders**: Multiple exit paths per scene; enable only the correct one per state
4. **Script**: Minimal `ScenePortal.cs` handles traversal
5. **Control**: Use `SceneStateController.ActivateCollider()` when narrative beats occur

**Result**: Seamless illusion of a living world without persistence, flags, or complexity.

---

## Next Steps

1. Create the folder structure in `Assets/Scenes/`
2. Audit your current scenes and identify which locations need multiple states
3. Create a chart (like the one in Section 8) showing your planned progression
4. Start duplicating and incrementing state numbers
5. Add colliders and update scene references

Let me know if you need help mapping out the specific scene states for your current game flow!
