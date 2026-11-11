# Project Overview
- Game Title: Velinor
- High-Level Concept: Narrative-driven 3D exploration and social simulation.
- Players: Single player
- Target Platform: PC (StandaloneWindows64)
- Render Pipeline: URP (Ultra settings)

# Game Mechanics
- Core Gameplay Loop: Exploration, interaction with NPCs, and narrative choices.
- Controls and Input Methods: Third-person movement, interaction prompt.

# UI
- Dialogue UI and Interaction prompts.

# Key Asset & Context
- `Assets/Shaders/PlayerCustomBody.shader`: Custom shader for the player that currently ignores shadows and probes.
- `Willy_Sprite`: NPC with an unlit sprite shader.
- `Glyph_Pickup_Sorrow`: Interactive object that needs to emit light.
- `Assets/Rocks and Vegetation Pack/Shaders/Rock_Procedural.shadergraph`: Shader for rocks that needs better environmental integration.

# Implementation Steps

## 1. Upgrade Player Shader
- **Description**: Update `Assets/Shaders/PlayerCustomBody.shader` to support URP's lighting system (Shadows, Additional Lights, and SH Probes/APV).
- **Assigned role**: developer
- **Dependencies**: None
- **Parallelizable**: Yes

## 2. Upgrade Willy's Sprite Shader
- **Description**: Change the shader on Willy's `[SpriteVisual]` from `Universal Render Pipeline/2D/Sprite-Unlit-Default` to a lit version. Since the scene is 3D, we will use a custom `Sprite3DLit` shader or `Universal Render Pipeline/Simple Lit` with Alpha Clipping to ensure he reacts to the Directional Light and shadows.
- **Assigned role**: developer
- **Dependencies**: None
- **Parallelizable**: Yes

## 3. Add Light to Glyph_Pickup_Sorrow
- **Description**: Add a Point Light component to `Glyph_Pickup_Sorrow`. Configure its color and range to illuminate the player when they approach.
- **Assigned role**: developer
- **Dependencies**: None
- **Parallelizable**: Yes

## 4. Improve Rock Lighting
- **Description**: Adjust the material parameters of the rocks or the `Rock_Procedural` shader settings to better sample environmental lighting (SH/Probes). If the shader graph is the issue, we will attempt to find a workaround using Material properties.
- **Assigned role**: developer
- **Dependencies**: None
- **Parallelizable**: Yes

# Verification & Testing
- **Visual Check**: Use `Unity.EditorWindow.CaptureScreenshot` to verify that Willy and the Player now receive shadows from the environment.
- **Light Interaction**: Walk the player near `Glyph_Pickup_Sorrow` to ensure the new light affects the player model.
- **Shadow Check**: Place Willy and the Player in the shadow of a large object (e.g., a wall or rock) and verify they darken appropriately.
