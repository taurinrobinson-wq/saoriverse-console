# Triglyph Monster Projector - Simple Setup Guide

## Overview
This guide shows how to display the Triglyph Monster projection floating within the projector beam. Simply assign a texture to the TriglyphMonsterProjector component, and it handles the rest with a floating animation and projector color sync.

**Usage Pattern:**
- Start with `MachinesCave_02.unity` with Stage 01 image
- Copy the scene for Stage 02, swap the texture
- Copy for Stage 03, swap the texture
- Copy for Stage 04, swap the texture

## Component

### TriglyphMonsterProjector (Main Controller)
**File:** `Assets/Scripts/TriglyphMonsterProjector.cs`

Displays a single texture floating within the projector beam. Features:
- **Floating animation** - subtle up/down motion to appear suspended in light
- **Projector color sync** - blends with projector's spectral color cycle
- **Simple one-texture design** - just swap the texture field per scene variant

## Setup Instructions

### Step 1: Create Canvas Structure in MachinesCave_02

1. Open `MachinesCave_02.unity`
2. Right-click in hierarchy → Create → UI → Canvas (World Space)
3. Name it `TriglyphProjectionDisplay`
4. **Parent it to the `Triglyph_Projector` GameObject**

### Step 2: Configure Canvas

Select the canvas and set these properties:

**RectTransform:**
- Size Delta: (192, 108) - *Small canvas size; adjust if needed*
- Position: (0, 0, 0.5) - *Adjust Z to position image within beam*
- Scale: (1, 1, 1)
- Rotation: (0, 0, 0)

**Canvas component:**
- Render Mode: World Space
- Add CanvasScaler component
  - UI Scale Mode: Scale with Screen Size

### Step 3: Add Projection Image

1. Right-click canvas in hierarchy → UI → Raw Image
2. Name it `ProjectionImage`
3. Select it and configure RectTransform:
   - Anchor Min: (0, 0)
   - Anchor Max: (1, 1)
   - Offset Min: (0, 0)
   - Offset Max: (0, 0)
   - This makes it fill the entire canvas

### Step 4: Add TriglyphMonsterProjector Script

1. Select the Canvas GameObject
2. Add Component → TriglyphMonsterProjector
3. In the inspector, configure:

**Projection Display:** Drag the `ProjectionImage` RawImage

**Stage Texture (Swap per variant):** Drag `Stage01-3d.png` from Assets/Graphics/Overlays/TriglyphMonsters/

**Animation:**
- Floating Amount: 0.1
- Floating Speed: 1.0

**Lighting Integration:**
- Projector Controller: Drag the `Triglyph_Projector` from hierarchy
- Tint With Projector Color: true

### Step 5: Test in Play Mode

- Press Play
- The Stage 01 image should appear floating in the projector beam
- It will gently bob up and down
- Colors will shift with the projector's spectral cycle

### Step 6: Create Scene Variants

For Stage 02, Stage 03, Stage 04:

1. **File → Save As...** to create `MachinesCave_02_Stage02.unity`
2. Select the TriglyphProjectionDisplay canvas
3. Select the script component
4. Change **Stage Texture** to `Stage02-3d.png`
5. Save and repeat for stages 03 and 04

## Configuration Parameters

### Animation
- **Floating Amount:** How far up/down the image moves (0.1 = gentle motion)
- **Floating Speed:** Frequency of floating (1.0 Hz = one complete cycle per second)

### Lighting Integration
- **Tint With Projector Color:** Blends the image with the projector's spectral color cycle (recommended: true)
- **Projector Controller:** Reference to the ProjectorEffectController component on the Triglyph_Projector

## Visual Details

### Floating Animation
- Creates a subtle up-and-down motion
- Makes the image appear suspended in the projector light cone
- Continuous and smooth

### Color Tinting
- Automatically syncs with the ProjectorEffectController's color cycle
- 30% blend with projector color (70% original image color)
- Creates unified lighting between beam and image

### Positioning Tips

**To adjust where the image appears within the beam:**
1. Select the canvas
2. Change RectTransform Position Z value
   - Smaller Z = closer to projector (more centered in beam)
   - Larger Z = farther from projector (within the light cone)
3. Adjust Scale to make image larger/smaller
4. Test in Play mode and iterate

## Usage

## Usage

### In Scene

The TriglyphMonsterProjector automatically displays the Stage Texture when the scene loads. The image will float gently within the projector beam with color tinting from the projector's spectral cycle.

No code needed - just assign the texture and it works!

### From Code (Optional)

If you want to control the projection:

```csharp
// Get reference
TriglyphMonsterProjector projector = GetComponent<TriglyphMonsterProjector>();

// Change the texture at runtime
projector.GetComponent<RawImage>().texture = newTexture;
```

### Create Variants

**Quick scene copy workflow:**

1. Open `MachinesCave_02.unity`
2. File → Save As... → `MachinesCave_02_Stage02.unity`
3. Select the TriglyphProjectionDisplay canvas
4. In the TriglyphMonsterProjector component, drag `Stage02-3d.png` to Stage Texture
5. Save
6. Repeat for Stage 03 and Stage 04

## Troubleshooting

### Image not visible
- Check that Stage Texture is assigned in the inspector
- Verify Canvas is set to World Space
- Ensure the RawImage component exists under the Canvas

### Image looks flat or in wrong position
- Adjust canvas Position Z (try values between 0.3-0.8)
- Adjust Scale to resize the projection
- Verify the canvas is parented to Triglyph_Projector

### Floating animation not working
- Verify Floating Amount > 0 (try 0.1)
- Check Floating Speed is set (try 1.0)
- Make sure the script is enabled

### Color not matching projector
- Enable "Tint With Projector Color"
- Verify ProjectorEffectController reference is set
- Check that ProjectorEffectController is active in the scene
