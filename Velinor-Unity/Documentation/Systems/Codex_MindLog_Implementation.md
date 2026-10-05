# Codex / Mind Log System — Step-by-Step Implementation Guide

## Overview
This document provides step-by-step instructions for implementing the enhanced Codex/Mind Log system with memory fragments, grid UI, expanded views, and combination mechanics.

All steps use existing Unity workflow and C# best practices.

---

## STEP 1 — Create ScriptableObjects for Memory Fragments

### Create File: `MemoryFragment.cs`

**Location:** `Velinor-Unity/Assets/Scripts/Core/Data/`

**Responsibilities:**
- Store individual memory data
- Support both raw memories and combined deductions
- Provide metadata for combination logic

**Key Fields:**
```
- string fragmentID          (Unique identifier)
- Sprite icon               (Grid display icon, 256x256)
- string shortSynopsis      (2-3 word summary)
- string expandedText       (Full memory description)
- List<string> tags         (Tags for combination logic)
- bool isDeduction          (True if this is a combined fragment)
- List<string> combinesWith (IDs of valid combine partners)
- string linkedScene        (Scene that triggered this memory)
```

**Usage in Inspector:**
- Create menu: `[CreateAssetMenu(menuName = "Codex/Memory Fragment")]`
- Location: `Assets/Resources/Data/MemoryFragments/`
- Naming: `memory_[scene]_[topic].asset`

**Example Assets to Create:**
```
memory_ravi_daughter.asset
memory_nima_loss.asset
memory_kaelen_pocket.asset
memory_elenya_paradox.asset
```

### Create File: `MemoryCombination.cs` (Data Structure)

**Location:** `Velinor-Unity/Assets/Scripts/Core/Data/`

**Purpose:** Define valid combinations

**Fields:**
```
- string firstFragmentID
- string secondFragmentID
- string resultFragmentID
- string combinationLogic (narrative explanation)
- Sprite resultIcon
- string resultSynopsis
- string resultExpandedText
```

**Storage:** Create a `ScriptableObject` list called `ValidCombinations.asset`

---

## STEP 2 — Build the Grid UI

### Create File: `MemoryGridUI.cs`

**Location:** `Velinor-Unity/Assets/Scripts/UI/Codex/`

**Responsibilities:**
- Populate 3x3 grid with MemoryFragment icons
- Handle single-click selection
- Handle double-click expansion
- Track selected fragments in a `List<MemoryFragment>`
- Update synopsis display

**Key Methods:**
```csharp
public void PopulateGrid(List<MemoryFragment> fragments)
    // Fill 9 grid cells with icons

public void OnGridCellClicked(MemoryFragment fragment)
    // Handle single-click: select/deselect
    // Update synopsis
    // Check if Combine button should activate

public void OnGridCellDoubleClicked(MemoryFragment fragment)
    // Open expanded view (secondary screen)

public List<MemoryFragment> GetSelectedFragments()
    // Return currently selected fragments

public void ClearSelection()
    // Deselect all fragments

public void HighlightSelectedFragments()
    // Visual feedback: border, color, scale
```

**UI Structure:**
- Parent: Canvas (existing Codex panel)
- 3x3 Grid Layout Group
- 9 Button children (grid cells)
- Each button has:
  - Image component (icon)
  - Button component (click handler)
  - Tooltip (optional)

**Grid Cell Prefab:**
```
GridCell/
├── Image (icon)
├── Button (click handler)
└── HighlightOverlay (visual feedback)
```

**Integration with CodexController:**
- CodexController instantiates MemoryGridUI
- CodexController calls `PopulateGrid()` when mode switches to Mind Log
- CodexController calls `GetSelectedFragments()` when checking combine eligibility

---

## STEP 3 — Build the Expanded Memory View

### Create File: `MemoryExpandedUI.cs`

**Location:** `Velinor-Unity/Assets/Scripts/UI/Codex/`

**Responsibilities:**
- Display expandedText in a readable format
- Display icon prominently
- Display "Back" button to return to grid
- Hide grid while expanded
- Manage smooth transitions

**Key Methods:**
```csharp
public void DisplayMemory(MemoryFragment fragment)
    // Show icon
    // Show expandedText
    // Show "Back" button

public void OnBackButtonClicked()
    // Return to grid view
    // Restore grid selection state

public void SetActive(bool active)
    // Toggle expanded panel visibility
```

**UI Structure:**
- Parent: Canvas overlay (on top of grid)
- Panel (background/container)
  - IconDisplay (large sprite)
  - TextDisplay (scrollable, multi-line)
  - BackButton (button)
  - CloseButton (X button, optional)

**Styling:**
- Icon: center-top, 256x256 or larger
- Text: scrollable, readable font
- Back button: left-aligned, distinctive color
- Semi-transparent background (to see grid behind)

**Transition:**
- Fade in expanded panel
- Fade out grid (or dim it)
- Smooth position/scale animation (optional)

---

## STEP 4 — Build the Combination System

### Create File: `MemoryCombineSystem.cs`

**Location:** `Velinor-Unity/Assets/Scripts/Core/Codex/`

**Responsibilities:**
- Accept List<MemoryFragment> selectedFragments
- Check if fragments can combine (using ValidCombinations list)
- If valid → generate new MemoryFragment (deduction)
- Add new fragment to Codex list
- Trigger animation
- Trigger notification
- Update grid

**Key Methods:**
```csharp
public bool CanCombine(List<MemoryFragment> fragments)
    // Check if valid combination exists
    // Return true/false

public MemoryCombination GetCombination(List<MemoryFragment> fragments)
    // Find matching combination in ValidCombinations list
    // Return combination data (or null if none)

public MemoryFragment CreateDeduction(MemoryCombination combination)
    // Instantiate new MemoryFragment
    // Set icon, synopsis, expandedText from combination
    // Mark as isDeduction = true
    // Return new fragment

public void CombineFragments(List<MemoryFragment> fragments)
    // Get combination
    // Create deduction fragment
    // Add to Codex
    // Trigger animation
    // Trigger notification
    // Refresh grid
    // Clear selection
```

**Combination Logic:**
- Query `ValidCombinations.asset` for valid pairs
- Support multiple valid combinations for same pair (optional)
- Fallback: grey out button if no valid combination

**Example Combination:**
```
Input: [memory_ravi_daughter, memory_nima_loss]
Output: deduction_shared_grief
Action: Create new MemoryFragment with grief-related content
```

---

## STEP 5 — Add Combine Button Logic

### Update File: `CodexController.cs`

**Add/Modify:**

```csharp
// Field
private Button combineButton;
private MemoryCombineSystem combineSystem;

// In CodexController.OnMemoryGridSelectionChanged()
public void OnMemoryGridSelectionChanged(List<MemoryFragment> selected)
{
    if (selected.Count < 2)
    {
        combineButton.gameObject.SetActive(false);
        return;
    }
    
    combineButton.gameObject.SetActive(true);
    
    bool canCombine = combineSystem.CanCombine(selected);
    
    combineButton.interactable = canCombine;
    // Change color: green if canCombine, grey if not
    Image buttonImage = combineButton.GetComponent<Image>();
    buttonImage.color = canCombine ? Color.green : Color.gray;
}

// In CodexController
public void OnCombineButtonClicked()
{
    List<MemoryFragment> selected = memoryGridUI.GetSelectedFragments();
    
    combineSystem.CombineFragments(selected);
    // This triggers animation, notification, and grid refresh
}
```

**Combine Button UI:**
- Located: Bottom-center of Codex panel
- Default state: Inactive (not visible)
- Appears when 2+ fragments selected
- Color: Green (valid) or Grey (invalid)
- Text: "Combine"
- On click: CombineFragments() → animation → notification

---

## STEP 6 — Add Combination Animation

### Create File: `MemoryCombineAnimation.cs`

**Location:** `Velinor-Unity/Assets/Scripts/UI/Animation/`

**Responsibilities:**
- Animate logs sliding together
- Animate new icon appearing
- Play visual effects (sparkle, glow, etc.)

**Key Methods:**
```csharp
public IEnumerator AnimateCombination(List<MemoryFragment> oldFragments, 
                                      MemoryFragment newFragment)
{
    // 1. Highlight old fragments
    // 2. Slide them toward center
    // 3. Fade them out
    // 4. Fade new icon in at center
    // 5. Play success effect (sparkle, glow, etc.)
    // 6. Return to normal grid state
}
```

**Animation Timeline:**
1. (0.0s) Old icons highlight + scale up slightly
2. (0.3s) Old icons slide toward center
3. (0.6s) Old icons fade out
4. (0.7s) New icon fades in at center
5. (0.9s) Success effect (optional)
6. (1.2s) Animation complete

**Visual Effects:**
- Use `DOTween` for smooth tweens (if available)
- Fallback: Unity `Coroutine` with `Vector3.Lerp()`
- Effects: Fade, Scale, Position

---

## STEP 7 — Add Memory Unlock Triggers

### Create File: `MemoryUnlockTrigger.cs`

**Location:** `Velinor-Unity/Assets/Scripts/Events/`

**Responsibilities:**
- Listen for unlock events
- Add MemoryFragment to Codex
- Trigger notification

**Trigger Points:**
1. **Dialogue Choice**: Add memory at end of specific dialogue beat
2. **Location Visit**: Add memory when player enters a zone
3. **Codex Pulse**: Add memory when glyph resonance reaches threshold
4. **NPC Interaction**: Add memory on successful interaction

**Example: Dialogue Trigger**
```csharp
// In dialogue system (after beat completes)
if (beatID == "kaelen_confession_01" && toneChoice == "E")
{
    memoryUnlockTrigger.UnlockMemory("memory_kaelen_pocket");
}
```

**Example: Location Trigger**
```csharp
// In scene collider
void OnTriggerEnter(Collider other)
{
    if (other.tag == "Player")
    {
        memoryUnlockTrigger.UnlockMemory("memory_cave_refuge");
    }
}
```

### Create File: `CodexNotificationUI.cs`

**Location:** `Velinor-Unity/Assets/Scripts/UI/`

**Responsibilities:**
- Display notification when memory unlocked
- Display notification when combination successful
- Queue multiple notifications

**Messages:**
```
Memory Acquired: [Fragment Name]
Mind Logs Successfully Combined
Double click new icon to read combined log
```

---

## STEP 8 — Integrate Modes (Glyph ↔ Mind Log)

### Update File: `CodexController.cs`

**Add/Modify:**

```csharp
public enum CodexMode { Glyphs, MindLog }
private CodexMode currentMode = CodexMode.Glyphs;

public void SwitchMode(CodexMode newMode)
{
    currentMode = newMode;
    
    if (newMode == CodexMode.MindLog)
    {
        glyphGridUI.gameObject.SetActive(false);
        memoryGridUI.gameObject.SetActive(true);
        memoryGridUI.PopulateGrid(codexMemories);
    }
    else
    {
        memoryGridUI.gameObject.SetActive(false);
        glyphGridUI.gameObject.SetActive(true);
        glyphGridUI.PopulateGrid(codexGlyphs);
    }
    
    combineButton.gameObject.SetActive(currentMode == CodexMode.MindLog);
}
```

**Top Bar Integration:**
```csharp
public void UpdateTopBar()
{
    if (currentMode == CodexMode.Glyphs)
    {
        topBarText.text = selectedGlyph?.glyphName ?? "Glyphs";
    }
    else
    {
        topBarText.text = selectedMemory?.shortSynopsis ?? "Mind Log";
    }
}
```

---

## STEP 9 — Test Checklist

### Functionality Tests
- ✅ Memory icons display in 3x3 grid
- ✅ Single-click selects fragment + updates synopsis
- ✅ Double-click opens expanded view
- ✅ Back button returns to grid
- ✅ Multiple selections highlight correctly
- ✅ Combine button appears when 2+ selected
- ✅ Combine button green when valid, grey when invalid
- ✅ Clicking combine triggers animation + notification
- ✅ New combined fragment appears in grid
- ✅ Double-click combined fragment shows deduction text
- ✅ Mode switching (Glyphs ↔ Mind Log) works
- ✅ Top bar updates text based on selection

### UX Tests
- ✅ Grid is responsive and readable
- ✅ Icons are clear and distinct
- ✅ Selection feedback is obvious
- ✅ Animation is smooth and polished
- ✅ Notification is readable and timed well
- ✅ Transitions (grid ↔ expanded) are smooth
- ✅ Combine button state is intuitive

### Edge Cases
- ✅ Selecting then deselecting works
- ✅ Selecting 1, then deselecting, then selecting 2 works
- ✅ Invalid combinations don't allow combine
- ✅ Same fragment cannot combine with itself
- ✅ Order of selection doesn't matter (A+B = B+A)

---

## STEP 10 — Performance Optimization

### Memory Management
- Cache MemoryFragment sprites in memory
- Don't instantiate new Sprite objects per grid cell
- Use object pooling for grid cells if >9 fragments

### UI Optimization
- Use Canvas.SetActive() to disable unused panels
- Lazy-load expanded view content
- Batch grid updates (don't refresh every frame)

### Animation Performance
- Use `DOTween` or lightweight tweens
- Limit simultaneous animations
- Avoid expensive effects (blur, post-processing) during animation

---

## File Structure Summary

```
Velinor-Unity/
├── Assets/
│   ├── Scripts/
│   │   ├── Core/
│   │   │   ├── Codex/
│   │   │   │   ├── CodexController.cs (modified)
│   │   │   │   └── MemoryCombineSystem.cs
│   │   │   └── Data/
│   │   │       ├── MemoryFragment.cs
│   │   │       └── MemoryCombination.cs
│   │   ├── UI/
│   │   │   └── Codex/
│   │   │       ├── MemoryGridUI.cs
│   │   │       ├── MemoryExpandedUI.cs
│   │   │       └── MemoryCombineAnimation.cs
│   │   └── Events/
│   │       └── MemoryUnlockTrigger.cs
│   └── Resources/
│       └── Data/
│           └── MemoryFragments/
│               ├── memory_*.asset
│               └── ValidCombinations.asset
└── Documentation/
    └── Systems/
        └── Codex_MindLog_System.md
```

---

## Next Steps After Implementation

1. **Create Memory Assets**: Instantiate MemoryFragment assets for each scene
2. **Define Combinations**: Create `ValidCombinations.asset` with all valid pairs
3. **Integrate Unlock Triggers**: Add `MemoryUnlockTrigger` calls to dialogue/scenes
4. **Polish Animation**: Adjust timing, effects, and visual feedback
5. **Test with Real Dialogue**: Unlock memories during actual gameplay
6. **Iterate on Combinations**: Refine which memories should combine based on narrative

---

## Common Pitfalls to Avoid

❌ Storing icons as separate instances instead of references  
✅ Use Sprite references in MemoryFragment, not image files

❌ Hard-coding valid combinations in code  
✅ Use ScriptableObject `ValidCombinations` list for easy editing

❌ Forgetting to clear selection after combining  
✅ Call `ClearSelection()` at end of `CombineFragments()`

❌ Animation plays before grid updates  
✅ Update grid AFTER animation completes

❌ Combine button state not updating on every selection change  
✅ Call `OnMemoryGridSelectionChanged()` after every click

---

## Questions & Iteration

- **How long should animation play?** → ~1.0-1.2 seconds (adjust based on feel)
- **Should combined fragments be removable?** → Recommend: no (they persist)
- **Can same fragment combine with multiple others?** → Yes, define all in `ValidCombinations`
- **Should combining consume original fragments?** → Recommend: no (all persist in Codex)
