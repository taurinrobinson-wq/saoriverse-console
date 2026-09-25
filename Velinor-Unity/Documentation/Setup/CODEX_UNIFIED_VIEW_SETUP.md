# Codex Unified View Setup Guide

## Overview

This guide walks through merging the Glyphs and Impressions (diary) interfaces into a single Codex device UI, using the `CodexViewController` toggle system.

## Architecture

```
CodexPanel (Codex Device)
├── Header Section
│   ├── [Glyphs Button]
│   └── [Impressions Button]
│
├── Glyphs View (Toggled)
│   ├── GlyphGrid_Pg1 (GameObject)
│   ├── GlyphGrid_Pg2 (GameObject)
│   └── Navigation (GameObject)
│       ├── PrevButton (Glyphs)
│       └── NextButton (Glyphs)
│
└── Impressions View (Toggled)
    ├── TextDisplay (GameObject)
    ├── PrevButton (Impressions)
    └── NextButton (Impressions)
```

**Key Principle:** Both views exist in the scene simultaneously. The controller just toggles visibility. No existing systems are disrupted.

---

## Step 1: Add the Toggle Controller Script

1. **Select CodexPanel** (or the parent panel containing the codex UI)
2. **Add Component** → `CodexViewController`
3. Leave it for now—we'll configure it in the next step

---

## Step 2: Create/Position the Impressions View Elements

You need these GameObjects ready (they might already exist from the diary system):

- **TextDisplay** — The text component showing diary/impression entries
- **ImpressionsNavigation** folder containing:
  - **PrevButton** — Previous entry button
  - **NextButton** — Next entry button

**Position these** so they align visually with the Codex device design where you want the impressions to appear.

---

## Step 3: Wire Up the CodexViewController

With CodexViewController still selected in the Inspector:

### Button References
- **Glyphs Button:** Drag the "Glyphs" button from the hierarchy
- **Impressions Button:** Drag the "Impressions" button from the hierarchy

### Glyphs View Elements
- **Glyph Grid_Pg1:** Drag `GlyphGrid_Pg1` GameObject
- **Glyph Grid_Pg2:** Drag `GlyphGrid_Pg2` GameObject
- **Glyphs Navigation:** Drag the Navigation GameObject (contains prev/next buttons)

### Impressions View Elements
- **Impressions Text Display:** Drag `TextDisplay` GameObject
- **Impressions Prev Button:** Drag the Impressions PrevButton
- **Impressions Next Button:** Drag the Impressions NextButton

---

## Step 4: Test the Toggle

1. **Press Play**
2. **Press N** to open the Codex
3. **Click "Glyphs"** — Should show the grid layout with navigation
4. **Click "Impressions"** — Should show the text entries with navigation
5. **Verify:** Check the console for debug messages confirming view switches

### Expected Console Output

```
[CodexViewController] Switching to view: glyphs
[CodexViewController] Glyphs view enabled

[CodexViewController] Switching to view: impressions
[CodexViewController] Impressions view enabled
```

---

## Step 5: Verify Existing Systems Still Work

After setting up the toggle:

- ✅ Glyph pagination should still work when in Glyphs view
- ✅ Diary/Impression pagination should still work when in Impressions view
- ✅ Glyph interactions should not be affected
- ✅ Diary entries should continue to append normally

If anything breaks, the issue is likely with a script dependency referencing disabled GameObjects. The `CodexViewController` only toggles `.SetActive()`, so the underlying systems should be unaffected.

---

## Future Cleanup (Phase 2)

Once this system is stable, you can later:

1. **Remove BookBackground** if not needed
2. **Remove "Press N for Diary"** UI prompts
3. **Streamline animations** to only affect the Codex device (not a separate diary book)
4. **Consolidate button logic** for opening/closing the device

For now, keep those systems in place to avoid breaking dependencies.

---

## Troubleshooting

### View doesn't toggle
- Check all GameObject references are properly assigned in the inspector
- Verify buttons are wired correctly in the OnClick events
- Check console for error messages

### Navigation buttons don't appear
- Make sure the Impressions buttons are positioned correctly on the device
- Verify they're not hidden behind other UI elements
- Check their RectTransform values

### Glyph view breaks after toggle
- This might mean a script is trying to access a disabled GameObject
- Check `GlyphGridController` or similar scripts for `OnDisable()`/`OnEnable()` hooks
- Those might need adjustment if they expect the GameObject to always be active

### Both views show at the same time
- This shouldn't happen, but if it does, check that all references are correctly assigned
- Make sure you're not manually enabling/disabling these GameObjects elsewhere

---

## Next Steps

Once this is working:

1. Refine the visual alignment of Impressions view on the device
2. Test with multiple diary entries to ensure pagination works
3. Plan Phase 2: Remove BookBackground and cleanup animations
4. Update player-facing UI to explain the Glyphs/Impressions toggle

---

*Last Updated: September 25, 2026*
