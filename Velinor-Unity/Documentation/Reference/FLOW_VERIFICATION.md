# Complete Flow Verification

## JSON Data Structure (Your Files)

**File:** `ravi_nima_market_discovery.json`

```json
{
  "type": "npc_turn",
  "prompt": "NIMA: \"What do you want anyway?\"",
  "tone_choices": [
    {
      "tone": "T",
      "text": "I'm trying to find work.",
      "npc_response": "NIMA: \"Work is scarce...\"",  // ← KEY DATA
      "tone_effects": [...],
      "remnants_effects": [...]
    }
  ]
}
```

✅ **Present in JSON:** npc_response field
❌ **Missing from JSON:** mode field (hence the need to infer)

---

## Code Flow (Step by Step)

### Step 1: Player Makes Choice
**Location:** DialogueUIController (when player clicks choice button)

```
Player clicks "Trust" button
  ↓
Button.onClick event fires
  ↓
DialogueManager.OnChoiceMade(choice) called
  ↓
StartCoroutine(ResolveChoice(choice))
```

### Step 2: ResolveChoice() - THE FIX IS HERE
**Location:** DialogueManager.cs:1067-1161

```csharp
private IEnumerator ResolveChoice(StoryChoice choice)
{
    // ... handle result_text, effects, etc ...

    // Line 1119-1124: Get next passage
    if (!passages.TryGetValue(choice.target, out var nextPassage))
    {
        EndDialogue();
        yield break;
    }

    // Line 1126: Try to get beat data (will be NULL for passages-based JSON)
    var nextBeat = GetBeatForPassage(choice.target);
    
    // Line 1128-1145: ← THE FIX HAPPENS HERE
    if (nextBeat == null)
    {
        // Infer mode based on choice data
        DialogueMode inferredMode = DialogueMode.NPCToNPC;
        if (!string.IsNullOrEmpty(choice.npcResponse))  // ← Reads JSON field
        {
            inferredMode = DialogueMode.NPCToPlayer;    // ← Sets correct mode
            Debug.Log($"[DialogueManager] Choice has npc_response - inferring NPCToPlayer mode");
        }
        nextBeat = new BeatData { mode = inferredMode };
    }

    // Line 1135-1151: Mode-based routing
    switch (nextBeat.mode)
    {
        case DialogueMode.NPCToPlayer:
            yield return HandleNpcToPlayerResponse(choice, nextBeat, nextPassage, choice.target);
            // ← NOW THIS HANDLER RUNS (was being skipped before!)
            break;
        // ...
    }
}
```

**Key Change:**
- ✅ Before: defaulted to NPCToNPC (skipped response)
- ✅ After: checks choice.npcResponse and infers NPCToPlayer (shows response)

### Step 3: HandleNpcToPlayerResponse()
**Location:** DialogueManager.cs:1167-1205

```csharp
private IEnumerator HandleNpcToPlayerResponse(StoryChoice choice, BeatData nextBeat, StoryPassage nextPassage, string nextPassageId)
{
    string npcResponse = ResolveNpcResponse(choice, nextBeat, nextPassage);
    // ↑ Reads choice.npcResponse from JSON

    if (!string.IsNullOrEmpty(npcResponse))
    {
        var dialogueUIController = FindAnyObjectByType<DialogueUIController>();
        if (dialogueUIController != null)
        {
            // Step 3a: Show response text
            dialogueUIController.ShowDialogue(displayName, npcResponse);  // Line 1189
            // ↓
            // This calls: DialogueUIController.ShowDialogue(string name, string text)
            //   - Sets dialogueText.text = text
            //   - Calls StartCoroutine(CompleteDisplayAfterDuration())

            // Step 3b: Wait for text to render
            yield return dialogueUIController.WaitForDisplayComplete();  // Line 1194
            // ↓
            // Yields while isDisplaying = true
            // Returns when CompleteDisplayAfterDuration() calls OnTextFinished()

            // Step 3c: Show continue prompt
            dialogueUIController.ShowContinuePrompt();  // Line 1197
            // ↓
            // Appends text: "\n\n[Press SPACE or CLICK to continue]"

            // Step 3d: Wait for player input
            yield return dialogueUIController.WaitForPlayerContinue();  // Line 1201
            // ↓
            // Yields while waitingForPlayerContinue = true
            // Returns when OnPlayerContinue() sets flag to false
        }
    }

    // Step 3e: Advance to next beat
    ClearButtons();
    DisplayPassage(nextPassageId);  // Line 1207
    // ↓
    // Shows next beat with fresh choices
}
```

### Step 4: DialogueUIController.CompleteDisplayAfterDuration()
**Location:** DialogueUIController.cs:234-243

```csharp
private IEnumerator CompleteDisplayAfterDuration()
{
    yield return new WaitForSeconds(MINIMUM_DISPLAY_DURATION);  // 0.5 seconds
    OnTextFinished();  // Sets isDisplaying = false
    // ↓
    // This breaks the WaitForDisplayComplete() loop
}
```

**Why 0.5 seconds?**
- Gives TMPro mesh generation time
- Doesn't block player waiting for response
- Then immediately waits for player input (not another timer)

### Step 5: DialogueUIController.ShowContinuePrompt()
**Location:** DialogueUIController.cs:276-285

```csharp
public void ShowContinuePrompt()
{
    if (dialogueText != null)
    {
        // Append instruction to existing text
        dialogueText.text += "\n\n<size=70%><color=#CCCCCC>[Press SPACE or CLICK to continue]</color></size>";
        dialogueText.ForceMeshUpdate();
        Debug.Log("[UI] Continue prompt shown");
    }
}
```

**Result:** Player sees:
```
"Work is scarce for people who actually belong here. 
Intentions don't fill empty bellies."

[Press SPACE or CLICK to continue]
```

### Step 6: DialogueUIController.Update() - Input Polling
**Location:** DialogueUIController.cs:140-167

```csharp
private void Update()
{
    // ... canvas checks ...

    // Handle continue input (Space key or left mouse click)
    if (waitingForPlayerContinue)
    {
        bool spacePressedThisFrame = Input.GetKeyDown(KeyCode.Space);
        bool mousePressedThisFrame = Input.GetMouseButtonDown(0);
        
        if (spacePressedThisFrame || mousePressedThisFrame)
        {
            Debug.Log("[UI] Continue input detected");
            OnPlayerContinue();
            // ↓
            // Sets waitingForPlayerContinue = false
            // Breaks the WaitForPlayerContinue() loop
        }
    }
}
```

**Runs every frame:**
- Checks if player pressed Space
- Checks if player clicked mouse
- If either: calls OnPlayerContinue()

### Step 7: DialogueUIController.WaitForPlayerContinue()
**Location:** DialogueUIController.cs:553-562

```csharp
public IEnumerator WaitForPlayerContinue()
{
    waitingForPlayerContinue = true;
    Debug.Log("[DialogueUIController] Waiting for player to continue...");
    
    while (waitingForPlayerContinue)  // ← Loop
        yield return null;             // ← Paused here until flag changes
        
    Debug.Log("[DialogueUIController] Player continued.");
}
```

**Flow:**
1. Sets `waitingForPlayerContinue = true`
2. Yields in loop
3. Update() detects input → OnPlayerContinue() → flag = false
4. Loop exits
5. Control returns to HandleNpcToPlayerResponse()
6. Which calls DisplayPassage() to show next beat

### Step 8: Next Beat Displays
**Location:** DialogueManager.cs (various display methods)

```csharp
DisplayPassage(nextPassageId)  // Line 1207
  ↓
Parses passage data
  ↓
Shows player prompt + choices
  ↓
Buttons appear ready for next interaction
```

---

## Timeline (What User Sees)

| Time | Action | System |
|------|--------|--------|
| T+0s | Player clicks choice | ResolveChoice() starts |
| T+0.1s | NPC response text appears | ShowDialogue() called |
| T+0.5s | "Press SPACE..." appears | CompleteDisplayAfterDuration() done, ShowContinuePrompt() appends |
| T+0.5s-N | Player reads and decides | Update() polls for Space/Click |
| T+N | Player presses Space | OnPlayerContinue() breaks WaitForPlayerContinue() |
| T+N+0.1s | Next beat displays | DisplayPassage() shows new choices |

---

## Why The Previous Approach Failed

**Before (broken):**
```
Player clicks choice
  ↓
ResolveChoice() sees beat has NO "mode" field
  ↓
Defaults to mode = NPCToNPC
  ↓
Skips HandleNpcToPlayerResponse() entirely
  ↓
Tries to show response with other handlers (NPCToNPC path)
  ↓
Something breaks in timing/display
  ↓
Response appears briefly then disappears
  ✗ FAIL
```

**After (working):**
```
Player clicks choice
  ↓
ResolveChoice() checks choice.npcResponse
  ↓
Sees npc_response field exists in JSON
  ↓
Infers mode = NPCToPlayer
  ↓
Calls HandleNpcToPlayerResponse()
  ↓
Shows response + waits for explicit player input
  ✓ SUCCESS
```

---

## Debug Log Traces

When you test, look for these logs in Console:

```
[DialogueManager] Choice has npc_response - inferring NPCToPlayer mode
[UI] Continue prompt shown
[DialogueUIController] Waiting for player to continue...
[UI] Continue input detected
[DialogueUIController] Player continued.
```

If you don't see these, something went wrong in the flow.

---

## Verification Checklist

- [ ] Dialog response text appears
- [ ] "[Press SPACE or CLICK to continue]" prompt is visible
- [ ] Pressing Space advances dialogue
- [ ] Clicking mouse also advances dialogue
- [ ] Next beat shows with choices
- [ ] Multiple responses in a row work
- [ ] System doesn't crash or get stuck
- [ ] No "Continue input detected" when not waiting

If any fail, check console for which log messages appeared/didn't appear to identify where the flow broke.
