# Continue System Fix - Simpler, More Reliable

## What Was Wrong

The previous button-repurposing approach was too fragile:
- Tried to find "TONE_button" by name (might not match your scene)
- Tried to wire click handlers dynamically (complex and error-prone)
- If button wasn't found, system silently failed with no fallback
- Result: Response text showed for <1 second then disappeared, no continue button, player stuck

## What's Fixed Now

**Simplified architecture:**
- No button repurposing or dynamic wiring
- Text-based prompt: `[Press SPACE or CLICK to continue]`
- Simple Input polling in Update()
- Coroutine yields until player input received

**Three-part flow:**
1. Response text displays (via ShowDialogue)
2. After 0.5s render time, ShowContinuePrompt() appends the instruction text
3. Update() listens for Space or LMB → OnPlayerContinue() triggers advance

## Code Changes

### DialogueUIController.cs

**Update() method (lines 156-167):**
```csharp
// Handle continue input (Space key or left mouse click)
if (waitingForPlayerContinue)
{
    bool spacePressedThisFrame = Input.GetKeyDown(KeyCode.Space);
    bool mousePressedThisFrame = Input.GetMouseButtonDown(0);
    
    if (spacePressedThisFrame || mousePressedThisFrame)
    {
        Debug.Log("[UI] Continue input detected");
        OnPlayerContinue();
    }
}
```

**ShowContinuePrompt() method (lines 276-285):**
```csharp
public void ShowContinuePrompt()
{
    if (dialogueText != null)
    {
        dialogueText.text += "\n\n<size=70%><color=#CCCCCC>[Press SPACE or CLICK to continue]</color></size>";
        dialogueText.ForceMeshUpdate();
        Debug.Log("[UI] Continue prompt shown");
    }
}
```

**Removed:** ShowContinueButton() (the broken button-repurposing method)

### DialogueManager.cs

**HandleNpcToPlayerResponse() - added after WaitForDisplayComplete():**
```csharp
// Show continue prompt
dialogueUIController.ShowContinuePrompt();

// Wait for player to click continue
Debug.Log("[DialogueManager] Waiting for player to continue...");
yield return dialogueUIController.WaitForPlayerContinue();
```

**HandlePlayerActionChoiceFollowup() - added after WaitForDisplayComplete():**
```csharp
// Show continue prompt
dialogueUIController.ShowContinuePrompt();

// Wait for player to click continue
Debug.Log("[DialogueManager] Waiting for player to continue...");
yield return dialogueUIController.WaitForPlayerContinue();
```

## Expected Behavior Now

1. **Make a dialogue choice**
   ```
   NPC Response appears:
   ────────────────────
   "Thanks for your insight."
   
   [Press SPACE or CLICK to continue]
   ```

2. **Read at your own pace**
   - Text doesn't disappear
   - No timeout
   - Player is in control

3. **Press Space or click**
   - Prompt input is detected
   - onPlayerContinue() breaks the yield loop
   - Next beat displays immediately

## Why This Works

✅ **No button finding/wiring** - Text-based, always visible
✅ **No timing guesses** - Explicitly waits for player input  
✅ **Simple input polling** - Standard Update() pattern
✅ **Fallback-safe** - If prompt text fails to append, at least Update() still runs
✅ **Keyboard + Mouse** - Both inputs supported
✅ **Visible instruction** - Player knows how to continue

## Testing Checklist

- [ ] Build project (no compile errors)
- [ ] Start dialogue with NPC
- [ ] Make a choice that triggers NPC response
- [ ] **Verify:** Response text appears with prompt below
- [ ] **Wait 3+ seconds** (text should stay visible)
- [ ] **Press Space** - Dialogue advances to next beat
- [ ] **Repeat:** Make another choice, click mouse instead
- [ ] **Verify:** Mouse click also advances
- [ ] **Test edge cases:**
  - [ ] Multi-line responses (do they all fit?)
  - [ ] Multiple dialogue chains (does system stay stable?)
  - [ ] Player inner thoughts (should skip continue? or show it?)
  - [ ] Action choices (do they show continue prompt?)

## If Something's Still Wrong

**Response text still disappears too fast:**
- Increase MINIMUM_DISPLAY_DURATION from 0.5f to 2.0f (line 37, DialogueUIController.cs)
- This delays when ShowContinuePrompt() is called

**Continue prompt doesn't appear:**
- Check Debug log for "[UI] Continue prompt shown"
- If not there, dialogueText is null (UI hierarchy issue)
- Check that DialoguePanel → NPCDialogueText exists in scene

**Continue prompt appears but pressing Space doesn't work:**
- Check Debug log for "[UI] Continue input detected"
- If not there, Update() isn't running or waitingForPlayerContinue is false
- Check that Update() is being called (not paused, not on disabled script)

**Next beat appears but choices don't:**
- This is a separate issue (not related to continue system)
- Check DisplayPassage() method in DialogueManager
- Verify ClearButtons() isn't hiding buttons permanently

## Key Differences from Before

| Aspect | Old System | New System |
|--------|-----------|------------|
| Continue signal | Button click with dynamic wiring | Keyboard/Mouse input in Update() |
| Visibility | Button might not display | Text prompt always visible |
| Reliability | Fragile (button name-dependent) | Robust (simple polling) |
| Input types | Only button clicks | Space or LMB |
| Failure mode | Silent failure, player stuck | Degrades gracefully |

---

**Status:** Ready to build and test
**Confidence:** High (simple, robust approach)
**Next steps:** Build → Test dialogue → Report any edge case issues
