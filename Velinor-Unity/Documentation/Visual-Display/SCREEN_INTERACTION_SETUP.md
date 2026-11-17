# Screen Interaction System - Setup Guide

## Overview
This system creates an interactive screen in the cave that players can access by pressing E. It follows the same pattern as the TriglyphPuzzleController but focuses on screen interaction instead of puzzle solving.

**Flow:**
1. Player approaches screen → sees "Press E to Access Screen" prompt
2. Player presses E → Codex opens on Mind Log Primary Screen
3. Mind Log Primary Screen displays with interactive buttons
4. Complex sequence unfolds (animations, FX, SFX - to be designed)

## Components

### ScreenInteractionController
**File:** `Assets/Scripts/ScreenInteractionController.cs`

Manages the screen interaction workflow:
- Detects when player is near the screen collider
- Shows/hides interaction prompt
- Opens Codex and Mind Log Primary Screen on E press
- Prepares structure for complex sequences

**Key Features:**
- Proximity-based interaction (collider trigger)
- Notification panel prompt system
- Input handling (E key)
- Reset mechanism for re-interaction
- TODO comments for future sequence development

## Setup Instructions

### Step 1: Create Screen Interaction Collider

In `MachinesCave_02.unity`:

1. **Create a new GameObject** → Name it `ScreenInteractionTrigger`
2. **Position it** near the Triglyph Monster Screen (in front of it)
3. **Add a Collider component** (Box Collider recommended)
   - Make it large enough that player can interact from a few units away
   - Check **Is Trigger** (must be checked!)
4. **Add a Tag** (if not already exists):
   - Click the Tag dropdown → Add Tag → Name it `ScreenTrigger`
   - Apply the tag to the GameObject

### Step 2: Add ScreenInteractionController Script

1. **To the ScreenInteractionTrigger GameObject**, add the ScreenInteractionController script
2. **In the Inspector, configure references:**

**References:**
- **Codex Controller:** Drag the CodexController from your scene
- **Codex Panel:** Drag the Codex panel GameObject
- **Screen Collider:** Drag this ScreenInteractionTrigger GameObject
- **Mind Log Primary Screen:** Drag the Mind Log Primary Screen panel

**Interaction Settings:**
- **Interaction Prompt:** "Press E to Access Screen" (default)
- **Interaction Distance:** 3.0 (adjust as needed)

### Step 3: Verify Mind Log Primary Screen Setup

1. **Find the Mind Log Primary Screen** panel in your scene hierarchy
   - Usually under Codex/UI hierarchy
2. **Make sure it's disabled by default** (not active in scene)
   - The script will activate it when player accesses the screen
3. **Configure any buttons** on this screen for future interactions

### Step 4: Test in Play Mode

1. **Press Play**
2. **Move player near the screen collider**
   - Should see "Press E to Access Screen" prompt
3. **Press E**
   - Codex should open
   - Mind Log Primary Screen should appear
4. **Press Escape to close** (or however your Codex closes)

## Configuration Parameters

### Interaction Settings
- **Interaction Prompt:** Text shown when player is near screen
- **Interaction Distance:** How close player needs to be (collider size controls this)

### References
- **Codex Controller:** The main codex system
- **Codex Panel:** The codex UI panel
- **Screen Collider:** The trigger collider for this interaction
- **Mind Log Primary Screen:** The panel to show on access

## Current Limitations & TODOs

The current implementation covers basic interaction. Future enhancements will include:

- **Animations:** Screen opening, panel transitions
- **Visual Effects:** Glow, focus effects, transitions
- **Sound Effects:** Button clicks, screen activation SFX
- **Button Interactions:** Interactive buttons on the Mind Log screen
- **Complex Sequences:** Multi-stage interactions with timing

These will be added as you design the complete sequence.

## Script Methods

### Public Methods

**ResetScreenAccess()**
- Allows the screen to be interacted with again
- Call after sequence completes

**IsScreenAccessGranted** (property)
- Returns true if screen is currently being accessed
- Can be used to prevent other interactions

### Internal Methods

**OnTriggerEnter/OnTriggerExit**
- Handles proximity detection

**ShowAccessPrompt/HideAccessPrompt**
- Manages notification panel display

**OnAccessScreen**
- Triggered by E key press
- Opens Codex and activates Mind Log screen

## Integration with Future Sequences

When you're ready to add the complex sequence:

1. **Add your animation/FX/SFX code** in the OnAccessScreen method (marked with TODO)
2. **Call ResetScreenAccess()** when sequence completes
3. **Use IsScreenAccessGranted** property to gate other interactions
4. **Add buttons to Mind Log Primary Screen** with callbacks to your sequence

## Troubleshooting

### Prompt not showing
- Verify NotificationPanelController exists in scene
- Check that player has "Player" tag

### E key not working
- Make sure Input System is enabled (or using Input Manager KeyCode fallback)
- Verify player is within collider bounds
- Check that "Is Trigger" is checked on collider

### Mind Log screen not appearing
- Verify Mind Log Primary Screen reference is set
- Make sure screen is disabled by default (not active at start)
- Check that screen GameObject hierarchy is correct

### Player can access multiple times without reset
- Call ResetScreenAccess() after sequence completes
- Add logic to prevent re-access during sequence

## Next Steps

1. Set up the collider and ScreenInteractionController script
2. Test basic prompt and screen opening
3. Design the complete interaction sequence
4. Add animations, FX, and SFX
5. Implement button interactions
