# Z-Depth Adjustment for Glyphs During Scene Transitions

## Problem Summary

Your Willy scene has the following setup:
- **Player** at z=0
- **Debris** at z=0.5 (so it doesn't clip through player)
- **Sorrow Glyph** at z=1 (so it doesn't clip through debris)

**The Issue:** With the glyph at z=1, it's outside the player's interaction space, making it uninteractable.

**The Solution:** Dynamically move the glyph from z=1 (background) to z=0 (interactive) when the debris fade transition completes, then back to z=1 after collection.

---

## How It Works: Visual Flow

```
BEFORE TRANSITION:
├─ Player: z=0
├─ Debris: z=0.5 (visible)
└─ Sorrow Glyph: z=1 (not interactable)

FADE OUT (Screen Goes Black):
├─ GlyphDepthAdjuster.OnTransitionStart()
└─ (Glyph position hidden while screen is black)

ON FADE IN (Screen Fades Back In):
├─ GlyphDepthAdjuster.OnTransitionComplete()
├─ Wait 0.3 seconds for fade to finish
└─ Sorrow Glyph: z=0 (NOW INTERACTABLE!)

PLAYER COLLECTS GLYPH:
├─ Glyph removed from scene
└─ Z-position resets when scene stops
```

---

## Files Created

### 1. **GlyphDepthAdjuster.cs**
Manages the Z-position of a specific glyph during transitions.

**Attach to:** The `GlyphPickup_Sorrow` GameObject

**Inspector Settings:**
- **Background Depth:** 1.0 (z position when glyph should be behind player)
- **Interaction Depth:** 0.0 (z position when player can interact)
- **Adjust Z During Transition:** ✅ ON
- **Delay After Fade In:** 0.3 seconds

### 2. **GlyphDepthAdjusterTrigger.cs**
Manages all glyphs in a scene, coordinating depth adjustments.

**Automatically finds** all `GlyphDepthAdjuster` components and updates them during transitions.

### 3. **DialogueTransitionFade.cs** (Updated)
Enhanced to notify glyph adjusters when transitions occur.

**Changes:**
- Detects `GlyphDepthAdjusterTrigger`
- Calls `OnTransitionStarted()` when fade-to-black completes
- Calls `OnTransitionCompleted()` when fade-in completes

---

## Step-by-Step Setup

### Step 1: Add GlyphDepthAdjuster to Your Glyph
1. Select **GlyphPickup_Sorrow** in the Hierarchy
2. Add Component → **GlyphDepthAdjuster**
3. In the Inspector, set:
   - **Background Depth:** 1.0
   - **Interaction Depth:** 0.0
   - **Adjust Z During Transition:** ✅ ON
   - **Delay After Fade In:** 0.3

### Step 2: Configure Player Reference
The script auto-finds the player by tag, but you can manually assign:
1. Drag the **Player** GameObject into the **Player Transform** field

### Step 3: Test the Mechanic

**Test 1: Initial State**
1. Enter Play Mode
2. Check Console: Should see `[GlyphDepthAdjuster] initialized at depth=1`
3. Glyph should NOT be interactable yet
4. Verify **Sphere Collider** is disabled on the glyph ✅

**Test 2: After First Dialogue**
1. Play the scene
2. Talk to Willy (first dialogue)
3. Fade transition occurs
4. Check Console: Should see `Adjusted to interaction depth=0`
5. **Sphere Collider** is now enabled
6. Walk up to the glyph
7. You should now be able to interact with it ✅

**Test 3: Collection & Second Dialogue**
1. Continue from Test 2
2. Press E to interact with glyph
3. Glyph collects, Codex updates
4. Second dialogue with Willy triggers ✅

---

## Advanced Configuration

### Scene-Wide Depth Adjustment

If you need to adjust multiple glyphs in one scene:

```csharp
// In any scene script
GlyphDepthAdjusterTrigger trigger = FindAnyObjectByType<GlyphDepthAdjusterTrigger>();

// Move specific glyph to interaction depth
trigger.MoveGlyphToInteraction("Sorrow");

// Move all glyphs to background
trigger.MoveAllToBackground();

// Move all to interaction
trigger.MoveAllToInteraction();
```

### Per-Glyph Customization

Each glyph can have different depth values:

**Glyph A (Standard):**
- Background Depth: 1.0
- Interaction Depth: 0.0

**Glyph B (Further Back):**
- Background Depth: 2.0
- Interaction Depth: 0.0

**Glyph C (Slightly Behind):**
- Background Depth: 0.8
- Interaction Depth: 0.0

---

## What Happens Behind the Scenes

### Timeline of Events

**T=0.0s - Dialogue "Complete" Called**
```
Player clicks past final dialogue beat
```

**T=0.0-1.2s - Fade to Black**
```
Screen gradually darkens (alpha 0 → 1)
Glyph position is invisible, so changes aren't seen
```

**T=1.2s - Screen Fully Black**
```
DialogueTransitionFade.ExecuteTransitionFade() fires
GlyphDepthAdjuster.OnTransitionStart() is called
Debris gets disabled (via existing scene events)
Sphere Collider on glyph gets enabled (via existing scene events)
```

**T=1.2-2.0s - Hold on Black Screen**
```
Scene rearrangement happens
```

**T=2.0s - Fade Back In**
```
Screen gradually brightens (alpha 1 → 0)
```

**T=3.2s - Fade Complete**
```
GlyphDepthAdjuster.OnTransitionCompleted() is called
Coroutine waits 0.3 seconds for fade animation to settle
```

**T=3.5s - Glyph Z Updated**
```
Glyph Z position updates from 1.0 → 0.0
Player can now interact with glyph
```

### Key Insight: Why It Works

The glyph's Z position change happens:
1. **While screen is fading** (visually masked by the fade)
2. **After the fade completes** (player sees it in final position)
3. **Before player can interact** (no jarring pop-in visible)

This creates a seamless visual experience while solving the interaction problem.

---

## Debugging

### Check These If It's Not Working

1. **Glyph not moving to interaction depth after transition**
   - ✅ Console should show: `Adjusted to interaction depth=0`
   - ❌ If not showing, check that `Adjust Z During Transition` is ON

2. **Glyph was visible popping to new position**
   - This means the fade didn't hide it properly
   - Increase `Delay After Fade In` to 0.5 seconds

3. **Still not interactable after transition**
   - Check that Sphere Collider is enabled on the glyph
   - Verify `Interaction Depth` (0.0) matches player depth

4. **Console shows errors finding player**
   - Ensure player GameObject is tagged "Player"
   - Or manually assign Player Transform in Inspector

### Console Messages to Expect

**On Start:**
```
[GlyphDepthAdjuster] GlyphPickup_Sorrow initialized at depth=1
```

**During Fade Transition:**
```
[GlyphDepthAdjusterTrigger] Found 1 GlyphDepthAdjuster components
  - GlyphPickup_Sorrow
[GlyphDepthAdjuster] GlyphPickup_Sorrow: Transition started
[GlyphDepthAdjuster] GlyphPickup_Sorrow: Adjusted to interaction depth=0
```

---

## How This Integrates with Existing Systems

### Existing Debris Clearing
Your scene probably has something like:
```csharp
// In scene initialization or dialogue event
debrisObject.SetActive(false);
glyphPickup.GetComponent<Collider>().enabled = true;
```

**This system doesn't replace that.** Instead, it:
1. Waits for your existing code to disable debris
2. Then updates the glyph's Z position
3. The timing is perfect because it happens during the fade

### Integration with DialogueTransitionFade
The fade already calls `ExecuteTransitionFade()` with callbacks. We just:
1. Detect when the fade starts and completes
2. Call the appropriate `GlyphDepthAdjuster` methods
3. Everything else works as before

---

## Temporary Changes in Play Mode

As you mentioned, **play mode changes reset when you press Stop**. This system works because:

1. **Initial Scene Load:** Glyph is at z=1 (set in the Scene file)
2. **During Play:** Z updates to 0.0 dynamically
3. **Press Stop:** Everything reverts to original z=1
4. **Next Play:** Repeats

This is actually ideal because it means:
- ✅ Scene always starts in a known state
- ✅ Transition animations work perfectly
- ✅ No permanent changes needed to the Scene
- ✅ Easy to iterate on values

---

## Example Scene Structure

Your Willy scene should now have:

```
Scene: willy_glyph_collection
├─ Player (z=0)
│   └─ Tag: "Player"
├─ Willy NPC
│   ├─ NPCDialogueDriver
│   ├─ dialogueJson: willy_glyph_01_json
│   └─ secondaryDialogueJson: willy_glyph_collection_json
├─ Debris (z=0.5) ← Gets disabled during fade
├─ GlyphPickup_Sorrow (z=1, becomes z=0)
│   ├─ Sphere Collider (initially disabled)
│   ├─ GlyphPickup component
│   └─ GlyphDepthAdjuster
│       ├─ Background Depth: 1.0
│       └─ Interaction Depth: 0.0
└─ UI_Canvas
    └─ DialogueTransitionFade
```

---

## Testing Checklist

- [ ] GlyphDepthAdjuster script added to GlyphPickup_Sorrow
- [ ] Inspector configured (Background=1.0, Interaction=0.0)
- [ ] Player assigned in the adjuster (or auto-found via tag)
- [ ] Play mode test: Glyph starts at z=1 (not interactable)
- [ ] After first Willy dialogue: Glyph moves to z=0 (interactable)
- [ ] Player can walk up and interact with glyph
- [ ] Glyph disappears, added to Codex
- [ ] Second dialogue with Willy triggers
- [ ] Console shows expected messages
- [ ] Stop play: Scene resets to original state

---

## Performance Notes

- **Negligible cost:** Z-position change is a single `transform.position.z =` operation
- **No per-frame checks:** Only runs during specific transition events
- **Memory efficient:** One small script per glyph
- **Works with existing systems:** No conflicts with dialogue, colliders, or scene management

---

## Advanced: Multiple Glyphs in One Scene

If you have multiple glyphs that need depth adjustment:

```csharp
// Glyph 1: Sorrow (requires interaction depth adjustment)
GlyphPickup_Sorrow.AddComponent<GlyphDepthAdjuster>()
  .Background Depth = 1.0
  .Interaction Depth = 0.0

// Glyph 2: Joy (always at interaction depth)
GlyphPickup_Joy.AddComponent<GlyphDepthAdjuster>()
  .Background Depth = 0.0  ← Same as interaction
  .Interaction Depth = 0.0  ← Stays in one layer
  .Adjust Z During Transition = false  ← Disable adjustment

// Glyph 3: Fury (different background depth)
GlyphPickup_Fury.AddComponent<GlyphDepthAdjuster>()
  .Background Depth = 1.5  ← Further back
  .Interaction Depth = 0.0
```

Each glyph can have independent behavior!

---

## Summary

✅ **Your z-depth problem is solved with a clean, elegant system**

- Glyphs stay in the background (z=1) when not needed
- Automatically move to player depth (z=0) when interactive
- Transition happens invisibly during the fade
- Player experience is seamless
- No scene code changes needed
- Fully automatic and debuggable

Now you can have proper layering (no clipping through debris) while maintaining full interactivity!
