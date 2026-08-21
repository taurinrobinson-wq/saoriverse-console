# Triglyph Puzzle Workflow - Complete Setup

This guides you through the entire puzzle system: collecting glyphs, selecting for puzzle, placing on panel, and triggering the door sequence.

---

## Part 1: Glyph Collection (Already Working ✅)

When player collects a glyph:
```
GlyphData → CodexController.AddGlyph() → GlyphUI instantiated → Slot_0, Slot_1, etc.
```

This is automatic via `GlyphTestingController` or actual game pickup event.

---

## Part 2: Glyph Selection for Puzzle (NEW)

### Step 1: Add TriglyphPuzzleController to Scene

1. Select **CodexPanel** (or create empty object under it)
2. **Add Component** → `TriglyphPuzzleController`
3. In Inspector, assign these references:

   - **Codex Controller**: Drag from scene (or find automatically)
   - **Codex Panel**: Drag the CodexPanel
   - **Triglyph Panel**: Drag the TriglyphPanel or TriglyphPanelUI
   - **Mountain Overlay Sealed**: Drag MountainOverlay_Sealed
   - **Mountain Overlay Unsealed**: Drag MountainOverlay_Unsealed
   - **Door Sprite**: Drag the DoorSprite
   - **Puzzle Prompt Text**: Drag a TextMeshPro text object (or create one)
   - **Door Open Position**: X=550.6, Y=472 (will animate from current position to this)
   - **Door Open Speed**: 1.5 (adjust for faster/slower animation)

### Step 2: Add/Wire Triglyph Slots

The TriglyphPanel needs 3 interactive slots:

1. Find or create 3 slot GameObjects under TriglyphPanel
2. Name them: `TriglyphSlot_0`, `TriglyphSlot_1`, `TriglyphSlot_2`
3. Each needs:
   - **RectTransform** (for positioning)
   - **Image** component (visual representation)
   - **Button** component (interactivity)
   - **TriglyphSlot** script component

4. Select **TriglyphPuzzleController** in hierarchy
5. In Inspector, expand **Triglyph Slots** array (size 3)
6. Drag each slot's **TriglyphSlot component** into Elements 0, 1, 2

### Step 3: Hook GlyphUI Clicks into Puzzle Selection

**Problem:** Currently GlyphUI only notifies CodexController when clicked. We need it to also notify TriglyphPuzzleController.

**Solution:** Modify how glyph selection works.

In CodexController.OnGlyphSelected(), add:
```csharp
// Notify puzzle controller for selection tracking
TriglyphPuzzleController puzzleController = FindAnyObjectByType<TriglyphPuzzleController>();
if (puzzleController != null)
{
    puzzleController.OnGlyphClickedForPuzzle(glyph);
}
```

---

## Part 3: Testing the Workflow

1. **Play Scene**
2. **Collect glyphs** (via GlyphTestingPanel toggles or game pickup)
   - 3 glyphs appear in Codex slots
3. **Click on 3 glyphs in Codex**
   - They highlight/show selection state
   - Prompt appears: "Select glyphs: 0/3" → "Select glyphs: 3/3" → "Press E to add selected glyphs to panel"
4. **Press E**
   - Glyphs copied to TriglyphPanel slots
   - CodexPanel hides
   - TriglyphPanel hides (after brief delay)
   - MountainOverlay_Sealed hides
   - MountainOverlay_Unsealed appears
   - DoorSprite animates upward
5. **Player can now transition to next scene**

---

## Part 4: Scene Transition (When Puzzle Completes)

After door opens, wire your scene transition:

```csharp
if (puzzleController.IsPuzzleCompleted())
{
    SceneManager.LoadScene("MachinesCave_01");
}
```

Or add a trigger collider that checks this condition.

---

## What Each Script Does

| Script | Purpose | Where |
|--------|---------|-------|
| **TriglyphPuzzleController** | Manages puzzle workflow | CodexPanel (1 instance) |
| **GlyphUI** | Individual glyph in Codex (already made) | Instantiated per glyph |
| **TriglyphSlot** | Individual puzzle slot | Each TriglyphSlot_0,1,2 |
| **GlyphGridPagination** | Toggle between Page1/Page2 | Pagination manager |

---

## Checklist

- [ ] TriglyphPuzzleController added to scene
- [ ] Scene references assigned (panels, overlays, door, etc.)
- [ ] Triglyph slots have TriglyphSlot components
- [ ] Triglyph slots assigned to TriglyphPuzzleController array
- [ ] Puzzle prompt text created/assigned
- [ ] CodexController modified to notify puzzle controller
- [ ] Test: Collect glyphs
- [ ] Test: Select 3 glyphs (should see selection state change)
- [ ] Test: Prompt appears when all 3 selected
- [ ] Test: Press E → Door sequence triggers
- [ ] Test: Can transition to next scene after puzzle

---

## Puzzle Completion Sequence (What Happens)

1. Player clicks 3 glyphs to select them
2. Prompt shows "Press E to add selected glyphs to panel"
3. Player presses E
4. Glyphs copied to TriglyphPanel slots (glyphs stay in Codex too)
5. Both panels disabled
6. MountainOverlay_Sealed disabled
7. MountainOverlay_Unsealed enabled
8. DoorSprite animates from current position to doorOpenPosition
9. `IsPuzzleCompleted()` returns true
10. Scene transition available
