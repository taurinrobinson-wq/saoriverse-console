# Project Overview
- Game Title: Velinor
- High-Level Concept: Narrative-driven RPG/Adventure with a unique "Tone" and "Remnants" dialogue system.
- Players: Single player
- Target Platform: PC (StandaloneWindows64)
- Render Pipeline: Ultra (URP)
- Input System: New Input System

# Problem Analysis
The dialogue choice buttons (specifically the "Continue" button in the second set of choices for the "Older Man" / Willy) appear pure white instead of having their intended hue. This is likely due to an incomplete color restoration across all prefab variants and scene instances, combined with how uGUI Button transitions multiply colors.

# Proposed Fix
Synchronize the color settings across all relevant Dialogue Panel prefabs and scene instances.
The standard setup will be:
- **Image component color**: Set to the specific Hue (Blue for T, Orange for O, Green for N, Purple for E).
- **Button component transition**:
    - Normal Color: White (1, 1, 1, 1) - allows the Image color to show through purely.
    - Highlighted Color: Off-White (0.9, 0.9, 0.9, 1)
    - Pressed Color: Gray (0.7, 0.7, 0.7, 1)
    - Selected Color: White (1, 1, 1, 1)
    - Disabled Color: Standard gray with alpha (0.78, 0.78, 0.78, 0.5)

# Key Assets & Context
- `Assets/Prefabs/UI/UI_Canvas.prefab`: The primary UI container used in the scene.
- `Assets/Prefabs/DialoguePanel.prefab`: A standalone variant that should be kept in sync.
- `DialogueUIController.cs`: The script managing these buttons.

# Implementation Steps
1. **Fix UI_Canvas Prefab**: Update the `DialoguePanel` children (`ChoiceButton_T/O/N/E`) inside `Assets/Prefabs/UI/UI_Canvas.prefab`.
    - Set `Image.color` to the appropriate tone hue.
    - Set `Button.colors` to the white-based tint palette.
2. **Fix Standalone DialoguePanel Prefab**: Update `Assets/Prefabs/DialoguePanel.prefab` with the same settings.
3. **Verify Scene Instances**: Ensure the `DialoguePanel` instance in the active scene (`InsideMarket_02`) has these changes applied and no lingering overrides.
4. **Cleanup**: Verify that `DialogueUIController.cs` doesn't have any hardcoded color overrides that might interfere.

# Verification & Testing
- Inspect the prefabs in the inspector to confirm `Image.color` is the hue and `Button.normalColor` is White.
- Enter Play Mode and advance dialogue to the "Older Man" (Willy) encounter to verify the "Continue" button has the correct blue hue (Tone T).
