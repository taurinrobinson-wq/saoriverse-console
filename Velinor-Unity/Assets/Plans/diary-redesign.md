# Project Overview
- Game Title: Velinor
- High-Level Concept: Narrative-driven exploration where player choices reshape NPC traits.
- Players: Single-player
- Inspiration / Reference Games: 
- Tone / Art Direction: Atmospheric, Ruined world
- Target Platform: PC (StandaloneWindows64)
- Screen Orientation / Resolution: Landscape (1920x1080)
- Render Pipeline: URP

# Game Mechanics
## Core Gameplay Loop
The player explores, interacts with NPCs, and makes choices that affect the world. The Diary serves as a record of these interactions and story progression.
## Controls and Input Methods
- **Toggle Diary**: [N] key.
- **Navigation**: Left and Right arrows at the bottom of the UI, or Keyboard Left/Right arrow keys.

# UI
The Diary UI will be simplified from a two-page "book" layout to a single-page "sheet" layout.
- **Background**: `Assets/Diary/Sprites/Diary.png` (Instance ID: 83174).
- **Content**: A single TextMeshPro overlay for the entry content.
- **Navigation**: Two buttons (Left Arrow, Right Arrow) positioned at the bottom of the page to cycle through entries.
- **Responsive**: The diary remains centered on screen, sliding up/down when toggled.

# Key Asset & Context
- `Assets/Diary/Scripts/DiaryController.cs`: The main controller for diary UI and animation.
- `Assets/Prefabs/UI/DiarySystem.prefab`: The UI prefab to be modified.
- `Assets/Diary/Sprites/Diary.png`: The texture for the diary background.
- `Assets/Scripts/UI/DialogueUIController.cs`: Triggers the diary UI updates.

# Implementation Steps
## Step 1: Refactor DiaryController.cs
- **Description**: Update the script to handle a single page index instead of page pairs. Replace `textLeft`/`textRight` with `textDisplay`. Replace page-turning animations with simple fade or instant updates. Add `UnityEvent` or `Button` references for navigation.
- **Assigned role**: developer
- **Dependencies**: None
- **Parallelizable**: Yes

## Step 2: Update DiarySystem Hierarchy
- **Description**: Modify the `DiarySystem` GameObject (and prefab).
    - Remove or disable `LeftPage` and `RightPage` child objects.
    - Set `BookBackground` Image sprite to `Diary.png`. Adjust its RectTransform to match the sprite's aspect ratio.
    - Create a new `Content` object with a `TextMeshProUGUI` component for the entry text.
    - Add `PrevButton` and `NextButton` at the bottom. Use TMP characters (`<` and `>`) for the icons.
- **Assigned role**: developer
- **Dependencies**: None
- **Parallelizable**: Yes

## Step 3: Wire up DiaryController
- **Description**: Assign the new UI components to the `DiaryController` fields in the inspector. Configure the buttons to call `DiaryController.PrevPage()` and `NextPage()`.
- **Assigned role**: developer
- **Dependencies**: Step 1, Step 2
- **Parallelizable**: No

## Step 4: Verify Integration
- **Description**: Test the diary by pressing [N] in the `MachinesCave_01` scene. Ensure entries are loaded correctly from `DiaryManager` and that navigation buttons work.
- **Assigned role**: developer
- **Dependencies**: Step 3
- **Parallelizable**: No

# Verification & Testing
- **Manual Check**: Open diary with [N]. Click next/prev arrows. Verify text changes.
- **Edge Case**: Verify behavior with 0, 1, and many entries.
- **Input Check**: Verify keyboard Left/Right arrow keys still work for navigation.
