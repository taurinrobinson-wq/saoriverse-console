# Screen Image Display - Setup Guide

## Overview

When the player accesses the screen via ScreenInteractionController, you need to display the Triglyph Monster image on the **Mind Log Primary Screen** panel. This guide explains how to add and configure the image display.

## Option 1: Use TriglyphMonsterProjector Component (Recommended)

This is the simplest approach—reuse the floating animation system you already set up.

### Setup Steps

1. **Find or Create the Mind Log Primary Screen panel**
   - In your scene, locate the `MindLogPrimaryScreen` GameObject
   - If it doesn't exist, create a Canvas-based panel under your Codex hierarchy
   - Make sure it has a CanvasGroup component

2. **Create a World Space Canvas for the image** (inside Mind Log Primary Screen)
   - Right-click `MindLogPrimaryScreen` → UI → Canvas
   - Name it `ProjectionDisplay_Screen`
   - Select the Canvas and change **Render Mode** to **World Space**
   - Position it in front of the screen in world space

3. **Add the TriglyphMonsterProjector component**
   - Add `TriglyphMonsterProjector.cs` to the ProjectionDisplay_Screen GameObject
   - In the Inspector, assign:
     - **Stage Texture:** Set to your Stage 01-04 Triglyph image
     - **Projector Controller:** Reference your ProjectorEffectController
     - **Tint With Projector Color:** Check if you want it to glow with projector colors

4. **Configure the RawImage child component**
   - The TriglyphMonsterProjector will create/find a RawImage
   - Set its size to match your image aspect ratio (e.g., 5.03 x 6)
   - Check **Preserve Aspect** on the RawImage
   - Adjust the Z position to place it in the light cone

### Pros
- Reuses existing floating animation
- Consistent with projector beam display
- Easy to swap images per variant

### Cons
- Requires ProjectorEffectController in the scene
- May need additional lighting setup

---

## Option 2: Simple Image Panel (Quick Alternative)

If you want a simpler setup without the floating animation:

### Setup Steps

1. **Find the Mind Log Primary Screen panel**
   - Locate `MindLogPrimaryScreen` in your hierarchy

2. **Add an Image component to the panel**
   - Add a child UI element to MindLogPrimaryScreen
   - Name it `TriglyphImage`
   - Add an **Image** component (UI → Image)
   - Set **Source Image** to your Triglyph Monster texture

3. **Configure the Image**
   - Set **Image Type** to **Simple**
   - Check **Preserve Aspect** if the image isn't square
   - Adjust **Rect Transform** size to fit nicely on screen (e.g., 400 x 480)
   - Center it on the panel

4. **Optional: Add animation**
   - If you want floating animation, add a simple script:
     ```csharp
     private RectTransform rectTransform;
     private Vector2 basePosition;

     void Start()
     {
         rectTransform = GetComponent<RectTransform>();
         basePosition = rectTransform.anchoredPosition;
     }

     void Update()
     {
         float floatOffset = Mathf.Sin(Time.time * 1f) * 10f;
         rectTransform.anchoredPosition = basePosition + Vector2.up * floatOffset;
     }
     ```

### Pros
- Very simple setup
- No dependencies on ProjectorEffectController
- Easy to customize

### Cons
- No color tinting from projector
- Basic animation only
- Different feel from projector display

---

## Option 3: Canvas Scaler with Reference Resolution

For a responsive design that works across different screen sizes:

### Setup Steps

1. **Create the Mind Log Primary Screen Canvas** (if needed)
   - Right-click hierarchy → UI → Panel
   - Name it `MindLogPrimaryScreen`
   - Render Mode: **Screen Space - Overlay** (or Screen Space - Camera)

2. **Add Canvas Scaler**
   - Add **Canvas Scaler** component to the Canvas
   - Set **UI Scale Mode** to **Scale with Screen Size**
   - Set **Reference Resolution** to **1920 x 1080**

3. **Add Image child**
   - Right-click Canvas → UI → Image
   - Name it `TriglyphImage`
   - Set **Source Image** to your Triglyph texture
   - Configure size and position

4. **Make panel inactive by default**
   - Uncheck the checkbox next to MindLogPrimaryScreen in Inspector
   - ScreenInteractionController will activate it on E press

### Pros
- Responsive to different resolutions
- Works with standard UI canvas

### Cons
- Screen Space canvas vs World Space (different visual feel)
- May not match projector beam aesthetic

---

## Swapping Images Per Scene Variant

Since you're using scene variants (Stage01, Stage02, Stage03, Stage04), you'll want to swap the image per scene.

### For Option 1 (TriglyphMonsterProjector):

1. In each scene variant, select the `ProjectionDisplay_Screen` GameObject
2. In Inspector, assign the correct **Stage Texture** for that variant:
   - **Stage01:** Stage01_TriglyphImage
   - **Stage02:** Stage02_TriglyphImage
   - **Stage03:** Stage03_TriglyphImage
   - **Stage04:** Stage04_TriglyphImage

### For Option 2 (Simple Image):

1. In each scene variant, select the `TriglyphImage` child
2. Change the **Source Image** field to match the variant

---

## Integration with ScreenInteractionController

The ScreenInteractionController automatically:
1. Detects player approach (via collider)
2. Shows "Press E to Access Screen" prompt
3. On E press, opens Codex and activates Mind Log Primary Screen
4. Your image display component will then be visible

**No additional code changes needed!** Just set up the image in the panel, and it'll show when the screen is accessed.

---

## Positioning Tips

### For World Space Canvas (Option 1):
- Position the canvas so it floats in front of the screen
- Adjust Z depth to appear "inside" the light cone
- Scale down if it's too large (e.g., 0.02 scale)

### For Screen Space Canvas (Option 3):
- Use Rect Transform to center on screen
- Adjust size to fill desired portion of screen
- Consider adding a background panel for context

---

## Visual Polish Ideas

Once basic display is working:

1. **Add fade-in animation** when screen pops up
2. **Glow effect** around the image edges
3. **Particle effects** around the Triglyph
4. **Sound effect** when screen appears
5. **Parallax effect** for depth (tilt with player camera)

See PROJECTOR_INTERACTION_SETUP.md for advanced lighting integration ideas.

---

## Troubleshooting

### Image not appearing
- Check Mind Log Primary Screen is being activated (add debug log in ScreenInteractionController)
- Verify Image/RawImage component exists and has texture assigned
- Make sure the component is on an active GameObject

### Image too large/small
- Adjust RectTransform size or RawImage size
- Check Canvas scale and Canvas Scaler settings
- Verify "Preserve Aspect" is enabled if needed

### Image in wrong position
- Check Canvas/RectTransform anchors
- Verify parent GameObject positions
- For World Space canvas, check Transform position and scale

### Image doesn't match projector beam
- Use Option 1 (TriglyphMonsterProjector) for consistency
- Ensure same texture and aspect ratio
- Match the floating animation parameters

---

## Next Steps

1. Choose setup option (Option 1 recommended for consistency)
2. Add the image component to Mind Log Primary Screen
3. Test by accessing screen in play mode
4. Adjust size, position, and animation
5. Add visual polish (glow, fade-in, particles)
6. Test across all scene variants
