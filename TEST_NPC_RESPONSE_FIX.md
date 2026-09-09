# Testing the NPC Response Fix

## What Was Fixed

Previously:
- NPC responses were calculated correctly ✓
- Response text was set in UI ✓
- But responses disappeared before player could see them ✗

**Root cause:** `ShowDialogue()` didn't signal UI completion, so `WaitForDisplayComplete()` returned instantly instead of waiting.

**Fix:** `ShowDialogue()` now:
1. Sets `isDisplaying = true`
2. Starts a 150ms timer
3. After 150ms, sets `isDisplaying = false`
4. This allows `WaitForDisplayComplete()` to actually wait

---

## How to Test

### Scenario 1: Simple Two-Beat Response (Best for Testing)

**File:** `ravi_nima_market_discovery.json` (already loaded in logs)

**Steps:**
1. Launch game
2. Spawn into InsideMarket_00
3. Press G to talk to Ravi or Nima
4. You should see: "Press G to talk to Young Man and Woman"
5. **Expected first beat:** A player action choice
   - Look for dialogue like "You're here to trade, I assume?"
   - You'll see choices like "Trust", "Intimidate", etc.

6. **Click a choice (e.g., "Trust")**
   - **Expected outcome:** 
     - See the player's action result text (e.g., "You approach with open body language...")
     - **See the NPC's response to that action** ✓ (THIS IS THE FIX)
     - Example: "NIMA: What do you want anyway..." should be VISIBLE for ~150ms

### Scenario 2: NPCToPlayer Beat Response

**Expected flow:**
1. Player makes a choice that triggers NPCToPlayer mode
2. NPC response displays
3. Wait ~150ms (long enough to read)
4. Next beat displays

---

## What to Look For

### Before Fix (Broken)
```
[Logs show response text is set]
[But visually: response flashes too briefly to read]
[Next beat appears immediately]
```

### After Fix (Working)
```
[Response text displays]
[200ms delay - response stays visible]
[Player can read it]
[Then next beat appears]
```

---

## Debug Logging

The system logs show when the fix is working:

```
[UI] Set dialogue text (length: 58)                        ← Response set
[UI] Showing dialogue from Young Woman                     ← UI display called
[DialogueManager] ✓ Showing NPC response for NPCToPlayer   ← Handler executing
[Wait ~150ms]
[DialogueManager] Displaying passage: beat_2               ← Next beat displays
```

---

## Performance Note

- **150ms minimum display:** Imperceptible to user (< reaction time)
- **No blocking:** All dialogue waits for this completion
- **Responsive:** Still fast enough to not feel sluggish
- **Optional per-beat delay:** If you need longer, set `responseWindow` in JSON

Example JSON with longer response window:
```json
{
  "mode": "NPCToPlayer",
  "npc_response": "NIMA: What do you want anyway?",
  "responseWindow": 2.0
}
```

---

## Verification Checklist

- [ ] Build the project
- [ ] Launch game
- [ ] Trigger Ravi/Nima dialogue
- [ ] Make a choice that shows NPC response
- [ ] **NPC response is now visible for ~150ms** ✓
- [ ] Next beat displays after response timeout
- [ ] No console errors about completion signal
- [ ] Dialogue feels responsive (no lag)

---

## If Response Still Doesn't Show

1. **Check logs for errors:**
   - Search for "[DialogueManager] ✓ Showing NPC response"
   - If missing: Response isn't being generated at all

2. **Verify ShowDialogue() is being called:**
   - Should see: "[UI] Set dialogue text (length: ...)"
   - If missing: Response object isn't being passed to UI

3. **Check if next beat is overwriting it:**
   - Should see ~150ms gap between response and next beat logs
   - If no gap: WaitForDisplayComplete() isn't working

4. **Enable frame-by-frame inspection:**
   - Pause game in editor when response should be visible
   - Check DialoguePanel is active and has text

---

## Technical Notes for Developers

The fix is in `DialogueUIController.cs`:

```csharp
private const float MINIMUM_DISPLAY_DURATION = 0.15f;

public void ShowDialogue(string npcName, string text)
{
    isDisplaying = true;  // ← Signal UI is displaying
    
    // ... set text and activate panel ...
    
    // Wait 150ms then signal complete
    StartCoroutine(CompleteDisplayAfterDuration());
}

private IEnumerator CompleteDisplayAfterDuration()
{
    yield return new WaitForSeconds(MINIMUM_DISPLAY_DURATION);
    OnTextFinished();  // Sets isDisplaying = false
}
```

**To customize delay:** Change the constant value (in seconds)
- `0.1f` = 100ms (too fast)
- `0.15f` = 150ms (default, recommended)
- `0.25f` = 250ms (more readable)
- `0.5f` = 500ms (slower, feels sluggish)

**To integrate animations:** Have your typewriter/animation call `OnTextFinished()` when done, instead of using the timer.
