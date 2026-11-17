# MachinesCave_01 Scene - UI Setup Guide

## Quick Fix (Automated) - UPDATED

I've updated the editor script to avoid TextMeshPro font corruption issues. Follow these steps:

### Step 1: Clean Up (Important!)
1. **First, delete any corrupted TextMeshPro elements** from your scene that may be using the "desyrel SDF" font
2. This includes any existing NotificationText or DiaryText components you created manually

### Step 2: Run the Setup Script
1. Open the **machinescave_01** scene in Unity (should be clean now)
2. Go to menu: **Tools → Setup MachinesCave UI**
3. Wait for the console message: ✓ MachinesCave UI Setup Complete!

### Step 2: Verify References (Manual)
The script creates:
- ✅ **CodexPanel** (CanvasGroup) - for Codex display
- ✅ **DiaryPanel** (CanvasGroup with DiaryController) - for Diary display  
- ✅ **NotificationPanel** (CanvasGroup) - for system notifications
- ✅ **UIController** GameObject with **DialogueUIController** component

### Step 3: Test Input Bindings
Press these keys in Play mode:
- **N** = Toggle Diary Panel
- **C** = Toggle Codex Panel
- **E** = Interact

---

## What the Script Does

### Creates Three UI Panels:

**CodexPanel**
- Full screen overlay (black semi-transparent background)
- Displays codex/glyphs
- Alpha = 0 by default (hidden)
- Responds to C key toggle

**DiaryPanel**  
- Right-side scrollable panel (500×600 pixels)
- Displays diary entries
- Includes DiaryController component
- Alpha = 0 by default (hidden)
- Responds to N key toggle

**NotificationPanel**
- Top-center notification bar (600×80 pixels)
- Shows system messages ("Diary updated. Press [N] to access.")
- Alpha = 0 by default (hidden)

### Adds DialogueUIController Component
- Listens for N, C, E keypresses
- Manages panel visibility transitions
- Handles notification display

---

## Troubleshooting

### If Panels Don't Appear:
1. Check that Canvas is set to **Screen Space - Overlay** mode
2. Verify RenderMode in Canvas inspector
3. Ensure CanvasGroup components have correct anchor/pivot settings

### If Input Doesn't Work:
1. Verify InputSystem is enabled in project
2. Check that DialogueUIController is on active GameObject
3. Ensure Unity Input System package is installed

### If Text Doesn't Show:
1. Check TextMeshPro font asset is assigned
2. Font should be a valid TMP Font (LiberationSans SDF, etc.)
3. If using custom font, make sure it has proper atlas

---

## Manual Alternative (If Script Doesn't Work)

If the automated script doesn't work, create manually:

### 1. Create CodexPanel:
- Right-click Canvas → UI → Panel
- Rename: `CodexPanel`
- Set anchors to full screen (stretch)
- Add CanvasGroup component
- Set alpha = 0

### 2. Create DiaryPanel:
- Right-click Canvas → UI → Panel
- Rename: `DiaryPanel`
- Anchor: Right-Center
- Size: 500×600
- Position: X = -300, Y = 0
- Add DiaryController component
- Add CanvasGroup component
- Set alpha = 0

### 3. Create NotificationPanel:
- Right-click Canvas → UI → Panel
- Rename: `NotificationPanel`
- Anchor: Top-Center  
- Size: 600×80
- Add child TextMeshPro - Text
- Set text: "Diary updated. Press [N] to access."
- Add CanvasGroup component to panel
- Set alpha = 0

### 4. Create UIController:
- Right-click in Hierarchy → Create Empty
- Name: `UIController`
- Add Component: DialogueUIController
- Drag panels into Inspector fields:
  - codexPanel → CodexPanel (CanvasGroup)
  - diaryPanel → DiaryPanel (CanvasGroup)
  - notificationPanel → NotificationPanel (CanvasGroup)
  - notificationText → NotificationText inside NotificationPanel

---

## Expected Console Output

```
✓ MachinesCave UI Setup Complete!
  - Created CodexPanel
  - Created DiaryPanel with DiaryController
  - Created NotificationPanel
  - Added DialogueUIController to UIController GameObject
  - Press N to toggle Diary, C to toggle Codex
```

If you see warnings about missing fonts or references, they can be safely ignored or assigned manually in the Inspector.
