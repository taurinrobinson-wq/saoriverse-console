# Dialogue Flow Trace: Player Always Chooses E

## Current Implementation

### BEAT 1 (player_posture)
```
Display:
  - Prompt: "You stand before two figures..."
  - Choices: T/O/N/E (each has result_text, NO npc_response)
  
Player selects E:
  1. ClearButtons()
  2. Show result_text: "You move closer..."
  3. WaitForDisplayComplete()
  4. Apply tone/remnants effects
  5. Check npc_response: EMPTY → skip
  6. Advance to next_beat_id = 2
```

### BEAT 2 (npc_turn - Nima)
```
Display:
  - Speaker: "Nima"
  - Prompt: "What do you want anyway? We don't trust outsiders."
  - Choices: T/O/N/E (each has result_text AND npc_response)
  
Player selects E:
  1. ClearButtons()
  2. Show result_text: "" (EMPTY) → skip
  3. WaitForDisplayComplete()
  4. Apply tone/remnants effects
  5. Check npc_response: "Everyone out here has a long road behind them..."
     → YES, show it
     → ShowSpeaker("Nima")
     → ShowText(npc_response)
     → WaitForDisplayComplete() ✓
     → WaitForPlayerContinue() ← WAITS HERE FOR SPACE/CLICK
  6. Advance to next_beat_id = 3
```

⚠️ **PROBLEM**: ClearButtons() was called in step 1. So when WaitForPlayerContinue() waits, there are NO buttons on screen. The player has to press SPACE to continue. There's no E button visible.

### BEAT 3 (npc_turn - Ravi)
```
Display:
  - Speaker: "Ravi"
  - Prompt: "You should be careful about who you reveal yourself to..."
  - Choices: 1 option (E "Continue" with NO npc_response)
  
DisplayBeat checks:
  1. Is there tone_choices? YES (1 choice: E)
  2. ShowChoices() called
     → FindToneButtons() returns T, O, N, E
     → ClearButtons() hides all 4
     → Loop through tone_choices (only 1: E)
       → Map tone "E" → button index 3
       → Activate ONLY button E
       → Set text: "Continue"
       → Listener: invoke onChoiceSelected
  
Player clicks E button:
  1. ClearButtons()
  2. Show result_text: "" (EMPTY) → skip
  3. Apply tone/remnants effects
  4. Check npc_response: "" (EMPTY) → skip
  5. Advance to next_beat_id = 3.1
```

✓ Works correctly - E button visible, player clicks it

### BEAT 3.1 (npc_turn - Nima)
```
Display:
  - Speaker: "Nima"
  - Prompt: "Ravi, take your own advice."
  - Choices: 1 option (E "Continue" with NO npc_response)
  
DisplayBeat checks:
  1. Is there tone_choices? YES (1 choice: E)
  2. ShowChoices() called → shows only E button
  
Player clicks E button:
  1. ClearButtons()
  2. Show result_text: "" (EMPTY) → skip
  3. Apply tone/remnants effects
  4. Check npc_response: "" (EMPTY) → skip
  5. Advance to next_beat_id = (not set) → defaults to 3.1 + 1 = 4.1?
```

## Summary of Problem

**Beat 2** has the issue:
- Player selects tone → npc_response displays
- ClearButtons() was called, so NO BUTTONS VISIBLE
- WaitForPlayerContinue() waits for Space/Click
- But there's no visual button to click!
- Player has to know to press Space

**Beats 3 & 3.1** work correctly:
- Only E button visible
- Player can see and click it
- Flow continues

## The Question

Beat 2 needs to show the E "Continue" button after the npc_response displays, so the player can click it (not press Space). Options:

**Option A**: Don't clear buttons after showing npc_response in beat 2
- But then old buttons are still visible

**Option B**: Create a beat 2.1 that shows the npc_response as the prompt with only E choice
- Requires restructuring beat 2's tone_choices to NOT have npc_response
- Instead, tone_choice.target = 2.1

**Option C**: Add ShowChoices() back after showing npc_response in beat 2
- Display ONLY E "Continue" button before WaitForPlayerContinue()

**Option D**: Keep the current behavior - it's actually correct, just not obvious that Space continues
- The NPC response displays, player presses Space to continue to next beat

Which makes sense to you?
