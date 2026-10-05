# Mind Log Setup — Simplified Duplication Approach

## Overview
Instead of creating UI from scratch, **duplicate the existing GlyphsBackground** to use as the Mind Log Primary view. This reuses the tested 3×3 grid structure.

**Final Hierarchy:**
```
Codex_Panel (your existing container)
├── GlyphsBackground (existing - UNCHANGED)
│   └── [Glyph 3x3 grid]
├── MindLogPrimaryContainer (NEW - duplicate of GlyphsBackground)
│   └── [Memory 3x3 grid - reconfigured buttons]
└── MindLogBackground (existing - UNCHANGED)
    └── [Expanded text view]
```

---

## Step 1: Duplicate GlyphsBackground

1. **In your Scene Hierarchy** (Desert_Saori_Meeting):
   - Right-click `GlyphsBackground`
   - Select **Duplicate**
   - Rename to `MindLogPrimaryContainer`
   - Keep it as a child of `Codex_Panel`

2. **Verify Structure**:
   - `GlyphsBackground` should still have all its original grid cells
   - `MindLogPrimaryContainer` should have identical grid structure

---

## Step 2: Reconfigure Button Click Handlers

Your existing GlyphsBackground buttons call a method to swap glyph pages. The MindLogPrimaryContainer buttons need different behavior.

### For Each of the 9 Buttons in MindLogPrimaryContainer:

1. **Select the button** (e.g., `GridCell_0`)

2. **Remove Old Handlers**:
   - In the Button component, click the **minus (-)** button on any existing onClick listeners
   - Remove the glyph pagination calls

3. **Add New Click Handler**:
   - Click the **plus (+)** button to add a new listener
   - Drag the button's parent panel into the Object field
   - In the Function dropdown: `MemoryGridUI` → `RegisterGridCellClick(MemoryFragment)`
   - This will be wired dynamically at runtime

   **OR** if you prefer static setup:
   - Drag `CodexViewController` into the Object field
   - Select `CodexViewController` → `SwitchView(string)`
   - Type: `"mind_log_secondary"`

   **Recommendation**: Use option 1 (RegisterGridCellClick) because it integrates with the proper selection system.

---

## Step 3: Add MemoryGridUI Component

1. **Select MindLogPrimaryContainer**

2. **Add Component** → `MemoryGridUI`

3. **In the Inspector**, populate these fields:
   - **Grid Cells**: Drag all 9 button children into this list
   - **Synopsis Text**: Drag a TextMeshPro text object (create one if needed)
   - **Expanded View**: Drag the MemoryExpandedUI instance
   - **Codex View Controller**: Drag the CodexViewController
   - **Default Cell Tint**: White (1, 1, 1, 1)
   - **Selected Cell Tint**: Gold (1, 0.88, 0.45, 1)
   - **Double Click Threshold**: 0.25

---

## Step 4: Update CodexViewController

Your CodexViewController already has the field structure. Just assign:

1. **Select CodexViewController in the Scene**

2. **In the Inspector**, assign:
   - **Mind Log Primary Container**: Drag `MindLogPrimaryContainer`
   - **Memory Grid UI**: Drag the MemoryGridUI component you just added
   - **Mind Log Secondary Container**: Drag `MindLogBackground`
   - **Memory Expanded UI**: Drag the MemoryExpandedUI component in MindLogBackground
   - **Mind Log Back Button**: Drag the Back button in MindLogBackground

The rest should already be configured from your existing Glyphs setup.

---

## Step 5: Create Visual Separation (Optional but Recommended)

Since both GlyphsBackground and MindLogPrimaryContainer now use the same background image, you might want to distinguish them visually:

### Option A: Use Separate Backgrounds
- GlyphsBackground: `Glyph_Codex3.png` (current)
- MindLogPrimaryContainer: Also use `Glyph_Codex3.png` (same, for consistency)

### Option B: Tint Difference
- MindLogPrimaryContainer: Add a Canvas Group → Set Alpha to 0.95 or adjust color slightly
- This shows subtle visual difference without changing the background image

**Recommendation**: Use Option A (same background) — it's cleaner and the user knows they're in Mind Log from the button state.

---

## Step 6: Verify the View Switching Logic

In **CodexViewController.cs**, the button listeners should handle:

```
glyphsButton.onClick → SwitchView("glyphs")        // Shows GlyphsBackground
impressionsButton.onClick → SwitchView("mind_log_primary")  // Shows MindLogPrimaryContainer
```

**Check your OnEnable method** in CodexViewController:
```csharp
if (impressionsButton != null)
    impressionsButton.onClick.AddListener(() => SwitchView("mind_log_primary"));
```

This should already be in place from the previous update.

---

## Step 7: Test Navigation

### Test Sequence:
1. **Click Glyphs button** → Should show GlyphsBackground with glyph grid
2. **Click Mind Log button** → Should show MindLogPrimaryContainer with memory grid
3. **Single-click a memory** → Icon highlights, synopsis shows
4. **Double-click a memory** → Should switch to MindLogBackground (expanded view)
5. **Click Back button** → Should return to MindLogPrimaryContainer

### If something doesn't work:
- **Memory grid shows nothing?** → Populate with test MemoryFragments
- **Double-click doesn't expand?** → Verify MemoryExpandedUI reference in MemoryGridUI
- **Back button doesn't work?** → Check mindLogBackButton is assigned in CodexViewController

---

## Step 8: Populate with Memory Fragments

Once the UI is wired:

1. **Create test MemoryFragment assets**:
   - Right-click in Assets → Create → ScriptableObject → MemoryFragment
   - Fill in: fragmentID, displayName, icon, shortSynopsis, expandedText

2. **Create a Manager Script** or populate manually:
   ```csharp
   List<MemoryFragment> testMemories = new List<MemoryFragment>();
   // Load your memory assets
   memoryGridUI.PopulateGrid(testMemories);
   ```

3. **Or wire in the Inspector**:
   - Add a public field to hold the memory list
   - Assign memory assets in the Inspector
   - Call PopulateGrid() in Start()

---

## Simplified Hierarchy Reference

```
Codex_Panel (RectTransform container)
│
├─ GlyphsBackground (Image component)
│  ├─ Viewport
│  └─ [9 Glyph buttons]
│  
├─ MindLogPrimaryContainer (Image component) [DUPLICATE of above]
│  ├─ Viewport
│  └─ [9 Memory buttons]
│  └─ [MemoryGridUI script attached here]
│
└─ MindLogBackground (Image component)
   ├─ Icon
   ├─ TitleText
   ├─ ExpandedText (with ScrollRect)
   ├─ BackButton
   └─ [MemoryExpandedUI script attached here]
```

---

## Workflow Summary

| Action | Result |
|--------|--------|
| Click **Glyphs** button | Show GlyphsBackground |
| Click **Mind Log** button | Show MindLogPrimaryContainer |
| Single-click memory | Highlight + show synopsis |
| Double-click memory | Fade to MindLogBackground |
| Click **Back** button | Fade back to MindLogPrimaryContainer |

---

## Files That Reference This Setup

- **CodexViewController.cs** — Manages view switching
  - Check OnEnable for button assignments
  - Verify field assignments in Inspector

- **MemoryGridUI.cs** — Grid management
  - Attached to MindLogPrimaryContainer
  - Handles single/double-click logic

- **MemoryExpandedUI.cs** — Expanded display
  - Attached to MindLogBackground
  - Handles fade transitions and Back button

---

## Quick Troubleshooting

| Problem | Check |
|---------|-------|
| Memory grid shows glyph icons | Update button icon references after duplication |
| Double-click doesn't swap to expanded | Verify MemoryExpandedUI reference in MemoryGridUI |
| Back button doesn't return | Verify mindLogBackButton is assigned in CodexViewController |
| Views overlap on screen | Ensure CodexViewController properly disables inactive containers |
| Buttons not clickable | Check CanvasGroup.blocksRaycasts on active view |

---

## Expected Time

- **Duplication & Setup**: 15-20 minutes
- **Script Assignment**: 10-15 minutes
- **Testing**: 5-10 minutes
- **Total**: ~30-45 minutes

Much faster than building from scratch!
