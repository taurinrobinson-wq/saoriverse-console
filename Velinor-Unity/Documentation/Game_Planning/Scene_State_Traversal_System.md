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

## 13. Concrete Example: MachinesCave Sequence (Complete Implementation)

This section documents the **Triglyph Chamber Cave**, a complex multi-scene narrative puzzle that uses the state system to create a seamless progression through 3 story sequences without allowing the player to replay narrative moments.

### MachinesCave Overview

**Structure:**
- 1 entrance/exit (MachinesCave_00 and MachinesCave_00_02)
- 5 hub rooms (MachinesCave_01_01 through 01_05) where player experiences disorientation
- 4 projection rooms (MachinesCave_02_01 through 02_04) where stories play
- 4 "B-version" hub rooms (MachinesCave_01_01b through 01_04b) for safe backtracking
- 1 "B-version" projection room (MachinesCave_02_04b) for safe backtracking

**Total: 16 scene files**

### Scene Flow Diagram

```
MachinesCave_00 (entrance)
    ↓
MachinesCave_01_01 (hub 1)
    ↓
MachinesCave_02_01 (story 1 - distorted)
    ↳ back → MachinesCave_01_01b → up → MachinesCave_02_01
    ↓
MachinesCave_01_02 (hub 2 - Mind Log)
    ↓
MachinesCave_02_02 (story 2 - less distorted)
    ↳ back → MachinesCave_01_02b → up → MachinesCave_02_02
    ↓
MachinesCave_01_03 (hub 3)
    ↓
MachinesCave_02_03 (story 3 - clearer)
    ↳ back → MachinesCave_01_03b → up → MachinesCave_02_03
    ↓
MachinesCave_01_04 (hub 4 - final pressure)
    ↓
MachinesCave_02_04 (story final - RESOLVED + glyph + ghost)
    ↳ back → MachinesCave_01_04b → up → MachinesCave_02_04
    ↓
MachinesCave_01_05 (hub exit - two-way)
    ↑
    └─→ MachinesCave_02_04b (final safe replay)
    ↓
MachinesCave_00_02 (exit)
```

### Folder Structure

```
Assets/Scenes/MachinesCave/
├── MachinesCave_00.unity      (cave entrance)
├── MachinesCave_01_01.unity   (hub 1)
├── MachinesCave_01_01b.unity  (hub 1b - backtrack safe)
├── MachinesCave_02_01.unity   (story 1)
├── MachinesCave_01_02.unity   (hub 2)
├── MachinesCave_01_02b.unity  (hub 2b - backtrack safe)
├── MachinesCave_02_02.unity   (story 2)
├── MachinesCave_01_03.unity   (hub 3)
├── MachinesCave_01_03b.unity  (hub 3b - backtrack safe)
├── MachinesCave_02_03.unity   (story 3)
├── MachinesCave_01_04.unity   (hub 4)
├── MachinesCave_01_04b.unity  (hub 4b - backtrack safe)
├── MachinesCave_02_04.unity   (story final)
├── MachinesCave_02_04b.unity  (story final b - backtrack safe)
├── MachinesCave_01_05.unity   (hub exit)
└── MachinesCave_00_02.unity   (cave exit)
```

### Scene-by-Scene Breakdown

#### **MachinesCave_00 — Cave Entrance**

**Purpose**: Player solves Triglyph Puzzle to enter cave.

**On Load:**
- Triglyph Panel UI appears (requires 3 glyphs: Sorrow, Remembrance, Legacy)
- Codex opens to Glyphs page
- Cave door is sealed

**Player Actions:**
- Insert required glyphs into panel
- Puzzle resolves → cave door opens

**Result:**
- Collider to next scene enabled
- Transition → MachinesCave_01_01

**Colliders:**
- `Collider_To_MachinesCave_01_01` (enabled on puzzle completion)

---

#### **MachinesCave_01_01 — Hub Room (State 1)**

**Purpose**: Establish entry; no escape possible; reinforce one-way progression.

**On Load:**
- Cave door closing SFX plays
- Mind Log: *"The door sealed behind me. There's no going back."*

**Colliders:**
- `Collider_To_MachinesCave_02_01` (enabled - forward only)
- `Collider_To_MachinesCave_00` (disabled - no escape)

---

#### **MachinesCave_02_01 — Projection Room (State 1)**

**Purpose**: First story sequence; projection is highly distorted.

**On Load:**
- Triglyph Monster projection visible (heavily distorted/glitched)
- Projection machine: non-interactable (just visual)
- Story screen collider: interactable

**Player Actions:**
- Examines projection → notification: *"The image looks distorted... broken?"*
- Activates story screen → **Press E**
- Story Sequence 1 plays (full dialogue, animations, effects)
- Codex switches to Mind Logs page

**Result:**
- Story complete → fade transition
- Collider to exit enabled
- Transition → MachinesCave_01_02

**Colliders:**
- `Collider_To_MachinesCave_01_02` (enabled after story completes)
- `Collider_To_MachinesCave_01_01b` (enabled for backtracking)

---

#### **MachinesCave_01_01b — Hub Room (State 1B - Backtrack Safe)**

**Purpose**: Allow player to return to story room without re-triggering narrative.

**On Load:**
- No Mind Log
- No dialogue
- Visually identical to 01_01

**Colliders:**
- `Collider_To_MachinesCave_02_01` (enabled - to story)
- No other exits

---

#### **MachinesCave_01_02 — Hub Room (State 2)**

**Purpose**: Reinforce disorientation after first story.

**On Load:**
- Mind Log: *"How did I get back here? I don't remember walking..."*
- This is a different scene, but player perceives it as "the same hallway"

**Colliders:**
- `Collider_To_MachinesCave_02_02` (enabled - forward)

---

#### **MachinesCave_02_02 — Projection Room (State 2)**

**Purpose**: Second story sequence; projection is less distorted.

**On Load:**
- Triglyph Monster projection visible (clearer than before)
- Story screen collider: interactable

**Player Actions:**
- Activates story screen → Story Sequence 2 plays
- Emotional impact: memories of Ravi and Nima become more coherent

**Result:**
- Story complete → fade transition
- Transition → MachinesCave_01_03

**Colliders:**
- `Collider_To_MachinesCave_01_03` (enabled after story)
- `Collider_To_MachinesCave_01_02b` (enabled for backtracking)

---

#### **MachinesCave_01_02b — Hub Room (State 2B - Backtrack Safe)**

**On Load:**
- No Mind Log
- Visually identical to 01_02

**Colliders:**
- `Collider_To_MachinesCave_02_02` (enabled - to story)

---

#### **MachinesCave_01_03 — Hub Room (State 3)**

**Purpose**: Continue emotional pressure.

**On Load:**
- Mind Log: *(optional deeper reflection)*
- Door still closed

**Colliders:**
- `Collider_To_MachinesCave_02_03` (enabled - forward)

---

#### **MachinesCave_02_03 — Projection Room (State 3)**

**Purpose**: Third story sequence; projection nearly fully resolved.

**On Load:**
- Triglyph Monster projection visible (nearly clear, slight distortion remaining)
- Story screen collider: interactable

**Player Actions:**
- Activates story screen → Story Sequence 3 plays
- Final emotional beat before revelation

**Result:**
- Story complete → fade transition
- Transition → MachinesCave_01_04

**Colliders:**
- `Collider_To_MachinesCave_01_04` (enabled after story)
- `Collider_To_MachinesCave_01_03b` (enabled for backtracking)

---

#### **MachinesCave_01_03b — Hub Room (State 3B - Backtrack Safe)**

**On Load:**
- No Mind Log
- Visually identical to 01_03

**Colliders:**
- `Collider_To_MachinesCave_02_03` (enabled - to story)

---

#### **MachinesCave_01_04 — Hub Room (State 4)**

**Purpose**: Final emotional pressure before the revelation room.

**On Load:**
- Mind Log: *"Am I ever going to escape this cave?"*
- Player feels trapped and desperate

**Colliders:**
- `Collider_To_MachinesCave_02_04` (enabled - forward)

---

#### **MachinesCave_02_04 — Projection Room (Final State)**

**Purpose**: Glyph collection and Velinor ghost vision happen here.

**On Load:**
- Triglyph Monster projection visible (FULLY RESOLVED - no distortion)
- Projection machine: **interactable**
- Story screen collider: **disabled** (no dialogue, only interactions)

**Player Actions:**

1. **First Interaction:**
   - Activates projection machine → **Press E**
   - Projection fades out (1.5 second transition)
   - Glyph of Contained Loss appears (floating, bobbing)
   - Notification: *"A glyph appears in place of the projection."*

2. **Second Interaction:**
   - Activates glyph → **Press E**
   - Glyph collected (disappears from world)
   - Mind Log: *"I collected it. The fragment is whole."*

3. **Sequence Trigger:**
   - Young Velinor (ghost form) appears
   - She reaches out desperately
   - She glitches and dissipates
   - Cave door opening SFX plays (signal: escape is now possible)

**Result:**
- Collider to exit enabled
- Transition → MachinesCave_01_05

**Colliders:**
- `Collider_To_MachinesCave_01_05` (enabled after glyph collected)
- `Collider_To_MachinesCave_01_04b` (enabled for backtracking)

---

#### **MachinesCave_01_04b — Hub Room (State 4B - Backtrack Safe)**

**On Load:**
- No Mind Log
- Visually identical to 01_04

**Colliders:**
- `Collider_To_MachinesCave_02_04` (enabled - to story)

---

#### **MachinesCave_02_04b — Projection Room (Final State B - Backtrack Safe)**

**Purpose**: Safe version of final projection room for backtracking.

**On Load:**
- Triglyph Monster projection visible (fully resolved)
- **No glyph** in this scene
- **No ghost** in this scene
- **No collider to progress**

**Colliders:**
- `Collider_To_MachinesCave_01_05` (enabled - back only)

**Why separate?** If player backtracks and returns to this scene, they don't re-collect the glyph or re-experience the ghost. The narrative has moved past this point.

---

#### **MachinesCave_01_05 — Hub Room (Exit State)**

**Purpose**: Final decision point; allow exit or safe return to final projection room.

**On Load:**
- Door still closed (but can be passed now)
- Two collider options are active

**Colliders:**
- `Collider_To_MachinesCave_02_04b` (up - back to final projection)
- `Collider_To_MachinesCave_00_02` (down - exit cave)

---

#### **MachinesCave_00_02 — Cave Exit**

**Purpose**: Finalize cave sequence; prevent re-entry.

**On Load:**
- Cave door closes behind player
- Mind Log: *"I left the cave. The door sealed behind me. I can't go back."*
- Triglyph puzzle collider: disabled
- Sealed cave overlay: enabled

**Result:**
- Player cannot re-enter cave
- Velinor-Unity world progression advances

---

### Why This Structure Works

| Feature | Benefit |
|---------|---------|
| **4 hub + 4 B-hubs** | Player can backtrack freely without resetting story |
| **4 projection rooms** | Each state shows progression of projection clarity |
| **01_05 exit state** | Clear decision point for leaving without narrative lock-in |
| **00_02 sealed exit** | Prevents cave re-entry; psychological closure |
| **Mind Logs at each hub** | Validates player's disorientation; explains time skip |
| **Glyph in final room** | Collection happens where it narratively belongs |
| **Ghost in final room** | Vision and glyph are inseparable; no replay possible |

### Implementation Checklist

- [ ] Create folder `/Assets/Scenes/MachinesCave/`
- [ ] Create all 16 scene files (follow naming convention exactly)
- [ ] Build MachinesCave_00 (entrance with puzzle)
- [ ] Build MachinesCave_01_01 (hub 1)
- [ ] Duplicate 01_01 → 01_02, 01_03, 01_04, 01_05 (update colliders)
- [ ] Build MachinesCave_02_01 (story 1 with distorted projection)
- [ ] Duplicate 02_01 → 02_02, 02_03, 02_04 (update projection clarity)
- [ ] Create all B-versions (exact duplicates, minimal colliders)
- [ ] Attach `ScenePortal.cs` to all colliders
- [ ] Attach `CaveStateManager.cs` to hub rooms
- [ ] Attach `GlyphCollectionSequence.cs` to MachinesCave_02_04
- [ ] Wire Mind Log system
- [ ] Test full progression flow
- [ ] Test backtracking at each stage

---

## Next Steps

1. Create the folder structure in `Assets/Scenes/`
2. Audit your current scenes and identify which locations need multiple states
3. Create a chart (like the one in Section 8) showing your planned progression
4. Start duplicating and incrementing state numbers
5. Add colliders and update scene references

Let me know if you need help mapping out the specific scene states for your current game flow!
