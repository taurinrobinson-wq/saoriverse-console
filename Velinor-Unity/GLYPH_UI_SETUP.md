# Glyph UI System - Scene Setup Instructions

## Phase 1: Create GlyphData ScriptableObjects

In Unity Editor, create three GlyphData objects in `Assets/Resources/Glyphs/`:

### 1. GlyphOfSorrow
- **Create Method**: Right-click → Create → Velinor → Glyph Data
- **File name**: `GlyphOfSorrow`
- **Properties**:
  - Glyph Name: "Sorrow"
  - Icon: (Select a sprite - recommend using a sad/dark emotion icon)
  - Description: "The glyph of loss and mourning"

### 2. GlyphOfRemembrance
- **File name**: `GlyphOfRemembrance`
- **Properties**:
  - Glyph Name: "Remembrance"
  - Icon: (Select a memory/light icon)
  - Description: "The glyph of cherished memories"

### 3. GlyphOfLegacy
- **File name**: `GlyphOfLegacy`
- **Properties**:
  - Glyph Name: "Legacy"
  - Icon: (Select a legacy/forward-looking icon)
  - Description: "The glyph of lasting impact"

---

## Phase 2: Create GlyphUI Prefab

### Create the prefab structure:
1. Create a new empty GameObject named **"GlyphUI"**
2. Add child: **Image** (for glyph icon)
   - Component: Image
   - Set Layout Element to preferred size
3. Add child: **Text** (for glyph name)
   - Component: TextMeshProUGUI
   - Text content: "Glyph Name"
4. Add child: **GlowHighlight** (visual indicator when selected)
   - Component: Image
   - Color: Yellow or bright glow color
   - Set to inactive by default

### Root GameObject setup:
- **Component**: Button
- **Component**: GlyphUI script
- **Component**: Image (for background)
- **Layout**: Set up LayoutElement for 150×150px or similar

### GlyphUI Script Inspector setup:
- Icon Image: Assign the Image child
- Name Text: Assign the Text child
- Glow Highlight: Assign the GlowHighlight GameObject
- Button: Assign root Button component

### Save as Prefab:
- Drag into `Assets/Resources/Prefabs/GlyphUI.prefab`

---

## Phase 3: Create Testing Panel

In MachinesCave_00 scene:

### Create hierarchy:
```
GlyphTestingPanel (new GameObject)
  ├── Title (TextMeshProUGUI)
  ├── SorrowToggle (Toggle)
  ├── RemembranceToggle (Toggle)
  └── LegacyToggle (Toggle)
```

### Add GlyphTestingController script to root
- Assign the three toggles
- Assign the three GlyphData assets
- Assign the CodexController reference

---

## Phase 4: Setup CodexController References

### In CodexController Inspector:
- **Glyph UI Prefab**: Assign `Assets/Resources/Prefabs/GlyphUI.prefab`
- **Slots Page 1**: Find 9 GlyphSlot components from codex grid
- **Slots Page 2**: Find 9 more GlyphSlot components (if paginated)

### Setup GlyphSlot components:
- Find all slots in CodexPanel/GlyphGrid
- Add GlyphSlot script to each
- Setup Image and Button components on each slot

---

## Phase 5: Setup TriglyphSlot

In the TriglyphPanel (from InteractionUICanvas):

### Create three slot GameObjects:
```
TriglyphPanel
  ├── TriglyphSlot_0 (Image + Button + TriglyphSlot script)
  ├── TriglyphSlot_1 (Image + Button + TriglyphSlot script)
  └── TriglyphSlot_2 (Image + Button + TriglyphSlot script)
```

### For each TriglyphSlot:
- **Component**: Image (for glyph display)
- **Component**: Button
- **Component**: TriglyphSlot script
- **Inspector Setup**:
  - Assign Slot Image
  - Assign Button
  - Set Slot Index (0, 1, or 2)

---

## Phase 6: Testing Workflow

1. **Enter playmode**
2. **Open codex** (press C)
3. **Enable testing toggles** (turn on Sorrow, Remembrance, Legacy)
4. **Glyphs appear** in codex grid slots
5. **Click glyphs** to select them (should glow)
6. **Glyph name updates** at top
7. **Navigate to triglyph panel** (near position 4, -2, 0)
8. **Press E** to open triglyph panel + codex
9. **Click glyph in codex** to select it
10. **Click slot in triglyph panel** to place glyph
11. **All three slots filled** = puzzle ready to verify

---

## Troubleshooting

### Glyphs not appearing:
- Check GlyphUI prefab is assigned in CodexController
- Verify GlyphSlot components exist on codex grid
- Check console for errors in GlyphTestingController

### Selection not working:
- Ensure GlyphUI script has Button reference
- Check that OnGlyphSelected is being called (check logs)

### Triglyph placement not working:
- Verify TriglyphSlot components are created
- Check GlyphPlacementManager exists and has OnTriglyphSlotClicked method
- Review console logs for errors

