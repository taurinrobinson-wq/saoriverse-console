# MachinesCave_02 Story Screen Setup Guide

*How to build the first MachinesCave_02 template and replicate it for all state variations.*

---

## Overview

`MachinesCave_02` is the **story sequence room** where the player interacts with:
1. A **Triglyph Monster projection** (visual, non-interactive)
2. A **story screen** (interactive via `Press E`)
3. The **Codex** (opens to Mind Logs page)

This guide walks you through setting up **one solid MachinesCave_02 scene** that you can duplicate for all variants (_01, _02, _03, _04).

---

## Scene Setup (Step-by-Step)

### 1. Basic Scene Structure

Create your scene with this hierarchy:

```
MachinesCave_02_01 (Scene root)
├── Background
│   └── [background image for cave chamber]
├── Projections
│   ├── TriglyphMonsterProjection
│   │   └── Image (the projection visual)
│   └── GlyphObject (for _04 only, hidden initially)
├── InteractableScreens
│   ├── StoryScreenCollider
│   │   ├── Collider2D (trigger)
│   │   ├── StoryScreenInteraction (script)
│   │   └── Image (the screen UI panel)
│   └── Canvas (for UI elements)
├── Audio
│   ├── AudioSource (for activation sound)
│   └── AudioSource (for door opening - _04 only)
└── Lighting
    └── [lights for mood]
```

---

## Step 1: Create the Triglyph Projection

**In your scene:**

1. Create an empty GameObject: `TriglyphMonsterProjection`
2. Add an **Image** component as child
3. Assign a sprite/texture showing the monster projection
4. For **_01**: Use highly distorted/glitched texture
5. For **_02**: Use slightly clearer texture
6. For **_03**: Use nearly-resolved texture
7. For **_04**: Use fully-resolved texture

**Why different versions?**
- The projection clarity progression is core to the narrative
- Copy base _02 scene, then just swap the sprite in the Image component for each variant

---

## Step 2: Create the Story Screen (Interactive)

**In your scene:**

1. Create an empty GameObject: `StoryScreenCollider`
2. Add a **Collider2D** (BoxCollider2D recommended)
   - Set as **Trigger**
   - Position it near the projection or on the "screen" area
   - Tag: `StoryScreen` (or use in script detection)
3. Add the **StoryScreenInteraction** script to this GameObject
4. Add a child **Image** component for the screen UI
   - This displays when player presses E
   - Position: center of screen (use Canvas if needed)
   - Initially **disabled** (script activates it)

---

## Step 3: Configure StoryScreenInteraction Script

**In the Inspector, for each MachinesCave_02 variant:**

### MachinesCave_02_01 (Story 1)

| Field | Value |
|-------|-------|
| **Story Screen Image** | (drag Image component) |
| **Story Screen Canvas Group** | (add CanvasGroup to Image parent) |
| **Fade In Duration** | 0.5 |
| **Activation Sound** | (optional SFX) |
| **Dialogue JSON File Name** | `story_1_sequence` |
| **Open Codex On Activation** | ✓ (checked) |
| **Codex Controller** | (Find auto, or drag) |

### MachinesCave_02_02 (Story 2)

| Field | Value |
|-------|-------|
| **Dialogue JSON File Name** | `story_2_sequence` |
| *(rest same as above)* | |

### MachinesCave_02_03 (Story 3)

| Field | Value |
|-------|-------|
| **Dialogue JSON File Name** | `story_3_sequence` |
| *(rest same as above)* | |

### MachinesCave_02_04 (Story Final + Glyph)

| Field | Value |
|-------|-------|
| **Dialogue JSON File Name** | *(empty - no dialogue, only interactions)* |
| **Open Codex On Activation** | ✗ (unchecked) |
| *(Story Screen component disabled for this variant)* | |

---

## Step 4: Special Setup for MachinesCave_02_04

**This scene has special behavior:**

### Projection Machine Interaction (First Press E)

1. Create a separate collider: `ProjectionMachineCollider`
2. Create a new script: `GlyphCollectionSequence.cs` (or similar)
3. On press E:
   - Fade out the projection image
   - Wait 1.5 seconds
   - Fade in the Glyph object

**Reference the earlier example** for full GlyphCollectionSequence implementation.

### Glyph Interaction (Second Press E)

1. Create another collider: `GlyphCollider`
2. Attach script that:
   - Collects the glyph (remove from world)
   - Triggers ghost sequence
   - Plays door opening sound
   - Enables exit collider

---

## Step 5: Image Assets

**You need to create/source:**

1. **Projection images** (4 variants):
   - `projection_state_1_distorted.png` (highly glitched)
   - `projection_state_2_lessdistorted.png`
   - `projection_state_3_clear.png`
   - `projection_state_4_resolved.png`

2. **Story screen panel image** (same for all):
   - `story_screen_panel.png` (UI background for when E is pressed)

3. **Optional**:
   - `glyph_contained_loss.png` (bobbing glyph for _04)
   - `young_velinor_ghost.png` (ghost sprite for _04)

**Storage:**
- Place in `Assets/Resources/Images/MachinesCave/`
- Or reference from your existing sprite asset folders

---

## Step 6: Duplicate for All Variants

### Once MachinesCave_02_01 is solid:

1. Save the scene
2. Right-click → **Duplicate** → rename to `MachinesCave_02_02`
3. Open new scene, update:
   - Projection Image sprite → `projection_state_2_lessdistorted.png`
   - StoryScreenInteraction script → `story_2_sequence`
4. Save and repeat for _03, _04

### For MachinesCave_02_04 (Final):

1. Duplicate from _03
2. Update projection sprite → fully resolved
3. **Disable** StoryScreenInteraction script
4. Add `GlyphCollectionSequence` script
5. Add glyph object (initially hidden)
6. Add ghost animator/animator controller
7. Add audio source for door opening

---

## Codex Integration

**The key is opening Codex to Mind Logs page:**

```csharp
// In StoryScreenInteraction.cs
private void OpenCodexToMindLogs()
{
    if (codexController == null)
    {
        codexController = FindObjectOfType<CodexController>();
    }
    
    if (codexController)
    {
        codexController.OpenCodex();
        codexController.NavigateToPage("MindLogs");
    }
}
```

**You may need to adjust** `NavigateToPage()` method name based on your actual Codex implementation.

---

## Mind Log Timing

**Each story screen should have a corresponding Mind Log:**

- Story 1 completes → Mind Log: *"How did I get back here?"*
- Story 2 completes → Mind Log: *"The projection is clearer..."*
- Story 3 completes → Mind Log: *"All three resolved..."*

**Trigger timing:**
- Should fire when player returns to hub room (MachinesCave_01_02, 01_03, 01_04)
- Not when entering projection room

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Script can't find CodexController | Use `FindObjectOfType<CodexController>()` or assign in Inspector |
| Codex doesn't open | Check `codexController.OpenCodex()` is public method |
| Screen image doesn't fade | Add CanvasGroup component to image parent |
| No "Press E" prompt | Implement notification system (hook into UIManager) |
| Glyph not disappearing on collect | Add `.SetActive(false)` to glyph GameObject |

---

## Checklist: First MachinesCave_02_01 Scene

- [ ] Background image placed
- [ ] Projection image (distorted) added
- [ ] Story screen collider created (trigger)
- [ ] Story screen image added
- [ ] CanvasGroup added to image
- [ ] StoryScreenInteraction script attached
- [ ] Dialogue JSON filename set (`story_1_sequence`)
- [ ] AudioSource added for activation sound
- [ ] Codex controller referenced
- [ ] Audio source for background/SFX
- [ ] Scene saved to correct folder (`Assets/Scenes/MachinesCave/MachinesCave_02/`)
- [ ] Scene added to Build Settings (if needed)

---

## Checklist: Duplication to Variants

For each of _02, _03, _04:

- [ ] Scene duplicated and renamed
- [ ] Projection sprite updated
- [ ] Dialogue JSON filename updated
- [ ] Scene saved to correct subfolder
- [ ] *(For _04 only)* Glyph object added
- [ ] *(For _04 only)* GlyphCollectionSequence script added
- [ ] *(For _04 only)* Ghost animator added
- [ ] *(For _04 only)* Door opening audio source added
- [ ] Scene tested for errors

---

## Next: Hub Rooms (MachinesCave_01)

Once all projection rooms are solid, duplicate and configure the hub rooms with:
- Mind Log triggers (on scene load)
- Collider management (which exit is active)
- Player spawn positions

See **Scene_State_Traversal_System.md** for full hub room setup.
