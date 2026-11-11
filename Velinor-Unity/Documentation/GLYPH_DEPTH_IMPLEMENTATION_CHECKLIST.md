# Glyph Depth Adjustment - Implementation Checklist

## Pre-Implementation (Verification)

### Understand the Problem ✓
- [ ] You have a glyph at z=1 (behind debris, not interactable)
- [ ] You want it at z=0 during player interaction (interactable)
- [ ] You want it to move invisibly during fade transitions
- [ ] You understand this is solved by dynamic Z updates

### Environment Check ✓
- [ ] Unity project open with Willy scene
- [ ] Scene has fade transition mechanic (DialogueTransitionFade)
- [ ] Scene has debris that gets disabled during fade
- [ ] Scene has GlyphPickup_Sorrow that needs adjusting

---

## Implementation (Do This Now)

### Step 1: Add GlyphDepthAdjuster Component (2 minutes)

- [ ] Open Hierarchy
- [ ] Find and select **GlyphPickup_Sorrow**
- [ ] In Inspector, click **Add Component**
- [ ] Search for **GlyphDepthAdjuster**
- [ ] Click to add the component
- [ ] Component appears in Inspector ✓

### Step 2: Configure Component (1 minute)

In the Inspector, you should see these fields:

**Position Configuration:**
- [ ] Background Depth: **1.0** (default - DO NOT CHANGE)
- [ ] Interaction Depth: **0.0** (default - DO NOT CHANGE)

**References:**
- [ ] Player Transform: (Leave blank - auto-finds via tag)
- [ ] Glyph Pickup: (Already set automatically)

**Timing:**
- [ ] Adjust Z During Transition: **☑ ON** (default - DO NOT CHANGE)
- [ ] Delay After Fade In: **0.3** (default - DO NOT CHANGE)

All values are already correct! No changes needed. ✓

### Step 3: Verify Player Tag (1 minute)

- [ ] Find **Player** GameObject in Hierarchy
- [ ] In Inspector, check the **Tag** dropdown
- [ ] Tag should be set to **"Player"**
- [ ] If not set, click Tag dropdown and select **"Player"**
- [ ] (Alternative: Manually assign Player Transform in GlyphDepthAdjuster)

### Step 4: Save Scene (30 seconds)

- [ ] Press **Ctrl+S** to save the scene
- [ ] Confirm scene is saved ✓

---

## Testing Phase 1: Basic Functionality (5 minutes)

### Play Mode Test
- [ ] Press **Play** button
- [ ] Watch Console for: `[GlyphDepthAdjuster] initialized at depth=1`
- [ ] Game is running ✓

### Check Initial State
- [ ] Walk near the Sorrow Glyph
- [ ] Try to interact with it (press E)
- [ ] Confirm it's **NOT interactable** (correct!)
- [ ] This is expected - it's at z=1 in the background

### Check Sphere Collider
- [ ] Stop play mode
- [ ] Select **GlyphPickup_Sorrow**
- [ ] Find **Sphere Collider** component
- [ ] Confirm it shows **Enabled: ☐** (unchecked, disabled)
- [ ] This is correct - it gets enabled during the fade

---

## Testing Phase 2: Fade Transition (10 minutes)

### Set Up Dialogue Trigger
- [ ] Play the game
- [ ] Walk to **Willy**
- [ ] Look for interaction prompt: "Press G to talk to Willy"
- [ ] Press **G** to start first dialogue

### Watch the Dialogue
- [ ] Listen/read through Willy's first dialogue
- [ ] Continue through all dialogue beats
- [ ] Watch for the **"debris clear" or "scene rearrange"** beat
- [ ] This is when the fade transition should trigger

### Observe the Fade Transition
- [ ] Console should show: `[GlyphDepthAdjuster] Transition started`
- [ ] Screen fades to black (normal)
- [ ] Hold on black screen for ~1 second
- [ ] Screen fades back in
- [ ] Look for: `[GlyphDepthAdjuster] Adjusted to interaction depth=0`
- [ ] Debris is gone ✓
- [ ] Scene is restored ✓

### Check Console Messages
After fade completes, console should show:
```
[GlyphDepthAdjusterTrigger] Found 1 GlyphDepthAdjuster components
  - GlyphPickup_Sorrow
[GlyphDepthAdjuster] GlyphPickup_Sorrow: Transition started
[GlyphDepthAdjuster] GlyphPickup_Sorrow: Adjusted to interaction depth=0
```

All three messages? ✓ Perfect! Everything is working.

---

## Testing Phase 3: Glyph Interaction (5 minutes)

### Move to Glyph
- [ ] After fade completes, walk toward **Sorrow Glyph**
- [ ] No debris should block you
- [ ] Walk right up to the glyph

### Interact with Glyph
- [ ] Stand on the glyph
- [ ] Look for interaction prompt: "Press E to collect Glyph"
- [ ] **This prompt should appear now** (it wouldn't have before fade!)
- [ ] This confirms the glyph is now at z=0 (interactable) ✓

### Collect the Glyph
- [ ] Press **E** to interact
- [ ] Glyph should disappear
- [ ] Console should show collection messages
- [ ] Codex should update (check Codex if available)

### Watch for Secondary Dialogue
- [ ] After collection, **secondary dialogue with Willy** should trigger
- [ ] Listen/read through this dialogue
- [ ] Confirm it plays correctly

---

## Testing Phase 4: Reset & Replay (3 minutes)

### Stop Play Mode
- [ ] Press **Stop** button
- [ ] Scene resets to original state
- [ ] Glyph reappears at z=1

### Replay Verification
- [ ] Press **Play** again
- [ ] Confirm initial glyph is at z=1 (not interactable)
- [ ] Repeat fade transition
- [ ] Confirm glyph moves to z=0 (interactable)
- [ ] This consistent behavior confirms everything works ✓

---

## Post-Implementation Checks

### Console Output Verification
- [ ] [ ] All expected debug messages appear
- [ ] [ ] No error messages during transitions
- [ ] [ ] No warnings about missing components

### Scene Integrity
- [ ] [ ] Scene file shows glyph still at z=1 (check in file)
- [ ] [ ] No permanent changes to saved scene
- [ ] [ ] Can replay transitions infinitely

### Gameplay Experience
- [ ] [ ] Fade transition is smooth (no pop-in)
- [ ] [ ] Glyph appears at correct depth after fade
- [ ] [ ] No visual artifacts during transition
- [ ] [ ] Player interaction works perfectly

### Edge Cases
- [ ] [ ] Multiple playthroughs work consistently
- [ ] [ ] Rapid play/stop cycles work fine
- [ ] [ ] No memory leaks or performance issues

---

## Troubleshooting Checklist

### Issue: Glyph Not Interactable After Fade

**Check:**
- [ ] Sphere Collider on glyph is enabled after fade
- [ ] Sphere Collider is enabled in the scene setup
- [ ] Check that existing debris-clearing code works
- [ ] Verify "Adjust Z During Transition" is ON
- [ ] Check console for error messages

**Fix:**
- [ ] Increase "Delay After Fade In" to 0.5 seconds
- [ ] Verify GlyphDepthAdjuster component is added
- [ ] Confirm interaction depth is 0.0

### Issue: Glyph Visible Pop-In

**Check:**
- [ ] Fade timing is correct
- [ ] Delay after fade-in is too short

**Fix:**
- [ ] Increase "Delay After Fade In" from 0.3 to 0.5 seconds
- [ ] This ensures fade animation fully completes before Z update

### Issue: Console Error "Player not found"

**Check:**
- [ ] Player GameObject exists in scene
- [ ] Player has "Player" tag assigned

**Fix:**
- [ ] Select Player GameObject
- [ ] Set Tag dropdown to "Player"
- [ ] OR manually assign in GlyphDepthAdjuster's Player Transform field

### Issue: GlyphDepthAdjuster Not Found

**Check:**
- [ ] Component was added to correct GameObject
- [ ] Component is visible in Inspector

**Fix:**
- [ ] Re-add component to GlyphPickup_Sorrow
- [ ] Verify GlyphPickup.cs exists on same GameObject

---

## Performance Verification

- [ ] [ ] No frame rate drops during transitions
- [ ] [ ] Memory usage is stable
- [ ] [ ] No coroutines accumulating
- [ ] [ ] All coroutines clean up properly

---

## Final Verification Checklist

### Component Setup ✓
- [ ] GlyphDepthAdjuster added to GlyphPickup_Sorrow
- [ ] All Inspector fields are configured (or default)
- [ ] Player Transform auto-found (or manually assigned)

### Fade System ✓
- [ ] DialogueTransitionFade works as before
- [ ] GlyphDepthAdjusterTrigger auto-created
- [ ] Fade doesn't interfere with other systems

### Gameplay ✓
- [ ] Initial state: Glyph at z=1 (not interactable)
- [ ] After fade: Glyph at z=0 (interactable)
- [ ] Collection: Works normally
- [ ] Secondary dialogue: Triggers correctly

### Consistency ✓
- [ ] Multiple playthroughs work identically
- [ ] Reset behavior is consistent
- [ ] No permanent scene changes

---

## Documentation

- [ ] [ ] Read GLYPH_DEPTH_QUICK_SETUP.md (verify setup)
- [ ] [ ] Reviewed GLYPH_DEPTH_ADJUSTMENT_SYSTEM.md (understanding)
- [ ] [ ] Understand console debug messages (troubleshooting)

---

## Success Criteria

**✅ Implementation Complete When:**

1. GlyphDepthAdjuster component is on GlyphPickup_Sorrow
2. Console shows all expected debug messages
3. Glyph is not interactable before fade
4. Glyph IS interactable after fade
5. Collection and secondary dialogue work
6. No visual pop-in or artifacts
7. Scene resets properly on Stop

---

## Next Steps

After successful implementation:

1. **If Perfect:** Move on to other scenes
2. **If Needs Tuning:** Adjust timing values slightly
3. **If Multiple Glyphs:** Repeat for other glyphs
4. **If Extending:** See advanced section in GLYPH_DEPTH_ADJUSTMENT_SYSTEM.md

---

## Sign-Off

- [ ] Implementation started: _____________ (date)
- [ ] Testing completed: _________________ (date)
- [ ] Fully working: ____________________ (date)
- [ ] Deployed: _________________________ (date)

---

**Questions?** Check GLYPH_DEPTH_ADJUSTMENT_SYSTEM.md for detailed documentation.

**Ready to implement?** Follow the numbered steps above in order.

Good luck! 🎉
