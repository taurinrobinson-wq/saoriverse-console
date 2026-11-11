# Glyph Depth Adjustment - Quick Setup (5 Minutes)

## The Problem
- Glyph at z=1 → Can't interact (outside player's space)
- Glyph at z=0 → Clips through debris
- **Solution:** Move glyph from z=1 to z=0 during the fade transition

## The Solution
Use two new components to automatically handle Z-position during transitions.

---

## Quick Setup

### Step 1: Select Your Glyph (30 seconds)
1. In Hierarchy, find **GlyphPickup_Sorrow**
2. Click to select it

### Step 2: Add the Component (1 minute)
1. In Inspector, click **Add Component**
2. Search for **GlyphDepthAdjuster**
3. Select it to add

### Step 3: Configure (1 minute)
In the Inspector, you'll see:

```
Glyph Depth Adjuster
┌─ Background Depth: 1.0          ← KEEP THIS
├─ Interaction Depth: 0.0         ← KEEP THIS
├─ Player Transform: [Assign]     ← Leave blank (auto-finds)
├─ Glyph Pickup: [Auto]           ← Already set
├─ Adjust Z During Transition: ☑  ← KEEP ON
└─ Delay After Fade In: 0.3       ← KEEP THIS
```

**No changes needed!** All defaults are correct.

### Step 4: Test (2 minutes)
1. Click **Play**
2. Talk to Willy (first dialogue)
3. Watch the fade transition
4. After fade, walk to the glyph
5. **You should now be able to interact with it!** ✅
6. Collect the glyph
7. Second dialogue triggers ✅
8. Press **Stop**

---

## What Just Happened?

**Before Fade:**
```
Glyph at z=1.0 (background, not interactable)
```

**During Fade (screen black):**
```
Glyph moves from z=1.0 to z=0.0 (hidden by fade)
```

**After Fade:**
```
Glyph at z=0.0 (player layer, fully interactable!)
```

---

## That's It!

Your glyph depth problem is solved. The system:
- ✅ Automatically detects fade transitions
- ✅ Updates glyph Z-position invisibly
- ✅ Makes glyph interactable at the right moment
- ✅ Resets when you press Stop (no permanent changes)

---

## Optional: Manual Verification

Check the Console during play for these messages:

```
[GlyphDepthAdjuster] GlyphPickup_Sorrow initialized at depth=1
[GlyphDepthAdjuster] GlyphPickup_Sorrow: Transition started
[GlyphDepthAdjuster] GlyphPickup_Sorrow: Adjusted to interaction depth=0
```

If you see these, everything is working perfectly!

---

## If It Doesn't Work

1. **Glyph still not interactable**
   - Make sure Sphere Collider is enabled
   - Check that Willy's collider/debris clearing events work

2. **Glyph visible popping to new position**
   - Set "Delay After Fade In" to 0.5 instead of 0.3

3. **Console errors about player**
   - Ensure your player GameObject has tag "Player"
   - Or manually assign Player in the Inspector

---

## Full Documentation

For more details, see: `GLYPH_DEPTH_ADJUSTMENT_SYSTEM.md`

---

## Summary

```
Add GlyphDepthAdjuster to GlyphPickup_Sorrow
                    ↓
Keep all default settings
                    ↓
Play and test
                    ↓
Done! 🎉
```
