# Player Continue System - NPC Response Fix

## Problem Solved

**Previous issues:**
- Fixed-delay approach (150ms, 2.5s) didn't work for all text
- Some responses too short, some too long
- Player couldn't control dialogue pacing
- Text would disappear before player finished reading

**Solution:** Implement a **player-click-to-continue** system (standard dialogue game pattern)

---

## How It Works Now

### Flow for NPC Responses

```
1. Player makes a choice
2. NPC response text displays
3. After text renders (500ms minimum):
   └─ "Continue" button appears (using first choice button)
4. Player clicks "Continue"
5. Next beat displays
```

### Key Components

**DialogueUIController.cs:**
- `waitingForPlayerContinue` - flag: waiting for player input?
- `WaitForPlayerContinue()` - coroutine that yields until player clicks
- `OnPlayerContinue()` - called when continue button clicked
- `ShowContinueButton()` - repurposes first choice button as continue
- `CompleteDisplayAfterDuration()` - shows continue button after text renders

**DialogueManager.cs:**
- `HandleNpcToPlayerResponse()` - now waits for player continue
- `HandlePlayerActionChoiceFollowup()` - now waits for player continue
- `OnContinueButtonClicked()` - handler for continue button clicks

---

## Technical Flow

### When NPC Response Shows

```csharp
// In HandleNpcToPlayerResponse:
dialogueUIController.ShowDialogue(displayName, npcResponse);
yield return dialogueUIController.WaitForDisplayComplete();  // Wait for text to render
yield return dialogueUIController.WaitForPlayerContinue();   // Wait for player click
DisplayPassage(nextPassageId);  // Show next beat
```

### When Player Clicks Continue

```
Player clicks "Continue" button
  ↓
OnContinueButtonClicked() called
  ↓
dialogueUIController.OnPlayerContinue() called
  ↓
waitingForPlayerContinue = false
  ↓
WaitForPlayerContinue() loop exits
  ↓
Next beat displays
```

---

## What Changed

### DialogueUIController.cs

**New fields:**
```csharp
private bool waitingForPlayerContinue = false;
private System.Action onPlayerContinue;
private const float MINIMUM_DISPLAY_DURATION = 0.5f;  // Minimum before button appears
```

**New methods:**
- `ShowContinueButton()` - Shows continue button using first choice button
- `WaitForPlayerContinue()` - Coroutine that yields until player clicks
- `OnPlayerContinue()` - Signals that player clicked continue

**Modified methods:**
- `CompleteDisplayAfterDuration()` - Now shows button instead of completing
- `HideButton()` - Helper to hide unused choice buttons

### DialogueManager.cs

**New method:**
- `OnContinueButtonClicked()` - Handler called when continue button clicked

**Modified handlers:**
- `HandleNpcToPlayerResponse()` - Now waits for player continue
- `HandlePlayerActionChoiceFollowup()` - Now waits for player continue

---

## Why This Works

✅ **Player controls pacing** - Short responses = quick click, long responses = time to read
✅ **No guessing delay** - System waits for explicit player input
✅ **Standard pattern** - Works like most dialogue games (Hades, Fire Emblem, etc.)
✅ **Responsive** - Player feels in control
✅ **Visual feedback** - Continue button clearly shows dialogue is waiting

---

## Testing

1. **Start dialogue** with Ravi/Nima
2. **Make a choice**
3. **NPC response appears** with "Continue" button
4. **Read at your own pace**
5. **Click Continue**
6. **Next beat displays**

Expected behavior:
- Response text stays visible until player clicks
- Continue button only appears after text finishes rendering
- Player can take as long as they want to read
- Clicking advances to next beat immediately

---

## Button Repurposing

The system reuses the first choice button ("TONE_button") as the continue button:

```
Before: Shows 4 choice buttons (Trust, Observation, Narrative, Empathy)
During NPC response: Shows 1 continue button (using TONE_button area)
After continue: Hides button, shows next beat's choices
```

This avoids needing a dedicated continue button UI element.

---

## Future Improvements

1. **Custom continue button** - If you want dedicated continue button instead of reusing choice buttons
2. **Click anywhere to continue** - Overlay that dismisses on any click (see Hades)
3. **Auto-advance option** - Toggle between manual/auto advance in settings
4. **Keyboard support** - Space or E to continue (via input system)

---

## Summary

The dialogue system now properly waits for player acknowledgment of NPC responses before advancing. This:
- ✅ Fixes visibility issues (no more guessing delays)
- ✅ Gives players control (read at own pace)
- ✅ Uses standard game dialogue pattern
- ✅ Requires no new UI elements (reuses existing buttons)

Test it now and adjust if needed!
