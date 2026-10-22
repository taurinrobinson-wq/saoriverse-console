# Projector Interaction System - Setup Guide

## Overview

Complex multi-stage projector interaction system that evolves across scene variants:

**Stages 01-03:** Player approaches → presses E → Mind Log added with distorted description → can re-interact  
**Stage 04:** Player approaches → presses E → final Mind Log → collects Glyph → **Velinor sequence triggers** → door opens → final Mind Log

This creates a narrative arc of discovery culminating in a shocking reveal.

## Scene Variant Structure

Each variant has different behavior configured:
- `MachinesCave_02_Stage01.unity` - Stage 01 (distorted image)
- `MachinesCave_02_Stage02.unity` - Stage 02 (less distorted)
- `MachinesCave_02_Stage03.unity` - Stage 03 (two faces visible)
- `MachinesCave_02_Stage04.unity` - Stage 04 (resolved image + Velinor sequence)

## Setup Instructions

### Step 1: Create Projector Interaction Trigger

In each scene variant:

1. **Create a new GameObject** → Name it `ProjectorInteractionTrigger`
2. **Parent it to Triglyph_Projector** or position it near the projector base
3. **Add a Collider** (Box Collider recommended)
   - Size: Large enough for interaction proximity (2-3 units)
   - Check **Is Trigger**
4. **Ensure Player has "Player" tag** (used for trigger detection)

### Step 2: Add ProjectorInteractionController Script

1. **Add the ProjectorInteractionController script** to the ProjectorInteractionTrigger
2. **Configure Stage** in the Inspector:
   - Set **Current Stage** to match the variant:
     - Stage01, Stage02, Stage03, or Stage04
   - This is the PRIMARY setting that controls behavior

3. **Configure References:**
   - **Projector Collider:** Drag the ProjectorInteractionTrigger
   - **Codex Controller:** Drag CodexController from scene
   - **Projector Display:** Drag the TriglyphMonsterProjector Canvas
   - **Audio Source:** Drag or create an AudioSource

4. **Configure Mind Log Text:**
   - **Mind Log Text_Stage01:** "What is this machine? The image on it looks really distorted...maybe its broken"
   - **Mind Log Text_Stage02:** "The image looks less distorted, but I still don't know what it is."
   - **Mind Log Text_Stage03:** "It definitely looks more like a person but there's like two faces...What is this supposed to be."
   - **Mind Log Image_Stage04:** (assign image if different)
   - **Mind Log Text_Stage04_Initial:** "The image looks fully resolved now...It's even smiling like something has been resolved. But why am I seeing all of this? Oh looks like the machine is working now."
   - **Mind Log Text_Final:** "I... I don't know what just happened... the projector showed a woman I've never seen..."

5. **Stage 04 Specific Settings:**
   - **Triglyph Screen Panel:** Drag the screen/UI panel that shows Velinor
   - **Scene Transition Collider:** Drag the door collider (will be disabled to open)
   - **Door Open Sound:** Assign the door opening SFX
   - **Glyph Fade In Duration:** 1.0 (fade time for glyph appearance)
   - **Velinor Sequence Delay:** 2.0 (wait before sequence starts)
   - **Triglyph Screen Display Duration:** 3.0 (how long Velinor image shows)

### Step 3: Copy Script Across Variants

1. **For Stage 01 variant:**
   - Set **Current Stage** = Stage01
   - Save

2. **File → Save As** → Create Stage02 variant
   - Set **Current Stage** = Stage02
   - Save

3. **File → Save As** → Create Stage03 variant
   - Set **Current Stage** = Stage03
   - Save

4. **File → Save As** → Create Stage04 variant
   - Set **Current Stage** = Stage04
   - Set up Velinor references and sequence settings
   - Save

### Step 4: Test Each Variant

**Stage 01-03 variants:**
1. Press Play
2. Approach projector → See "Press E to Interact with Projector"
3. Press E → Mind Log appears
4. Can interact again

**Stage 04 variant:**
1. Press Play
2. Approach projector → See prompt
3. Press E → Initial Mind Log appears
4. Prompt changes to "Press E to collect the glyph"
5. Press E → **Sequence triggers:**
   - Projector image fades
   - Velinor sequence appears (Triglyph Screen)
   - Screen glitches out
   - Door opens
   - Final Mind Log appears

## Configuration Parameters

### Stage Configuration
- **Current Stage:** Determines interaction flow
  - Stage01-03: Add Mind Log, allow re-interaction
  - Stage04: Full sequence with glyph + Velinor reveal

### Mind Log Text
Customize for each variant (examples provided):
- Stage 01: Distorted/confused description
- Stage 02: Slightly clearer but still confused
- Stage 03: Recognizes humanoid shape but two faces
- Stage 04 Initial: Resolved image, asks why seeing it
- Final: Horror at seeing Velinor, unease about location

### Stage 04 Sequence Timing
- **Glyph Fade In Duration:** How long glyph takes to appear
- **Velinor Sequence Delay:** Pause before shocking reveal
- **Triglyph Screen Display Duration:** How long Velinor image stays visible

## Behavior Flowchart

### Stages 01-03:
```
Player approaches
    ↓
"Press E to Interact with Projector" prompt
    ↓
Player presses E
    ↓
Mind Log added (stage-specific text)
    ↓
Prompt re-enabled after 1 second
    ↓
(Can interact again)
```

### Stage 04:
```
Player approaches
    ↓
"Press E to Interact with Projector" prompt
    ↓
Player presses E (FIRST)
    ↓
Mind Log added (resolved image text)
    ↓
"Press E to collect the glyph" prompt
    ↓
Player presses E (SECOND)
    ↓
Glyph added to Codex
    ↓
Projector image fades
    ↓
Velinor sequence appears (Triglyph Screen)
    ↓
Screen glitches/disappears
    ↓
Projector turns off
    ↓
Door opens
    ↓
Final Mind Log added (horror + unease)
```

## Glyph Integration

Currently logs that glyph is collected, but needs connection to your Codex system:

```csharp
// In CollectGlyph() method, integrate with your glyph data:
// Example pseudocode:
var glyphData = new GlyphData 
{ 
    name = "Contained Loss",
    sprite = glyphSprite,
    description = "A glyph representing trapped consciousness"
};
codexController.AddGlyph(glyphData);
```

## Velinor Sequence Details

The shocking moment when Velinor appears:
1. Projector image fades (TriglyphMonsterProjector calls HideProjection)
2. Triglyph Screen (with Velinor) suddenly appears
3. Creates unsettling effect with glitching/timing
4. Screen disappears after 3 seconds
5. Projector stays off
6. Door opens, trapping players must leave
7. Final Mind Log adds narrative closure + mystery

## Audio Setup

**Door Open Sound:**
1. Assign an AudioClip to Door Open Sound field
2. Ensure AudioSource is configured
3. Sound plays when sequence completes

## Mind Log Images

Configure different images for different context:
- **Stage 01-03:** Same distorted image (or vary if you want)
- **Stage 04 Initial:** Same projector image
- **Final Mind Log:** Velinor portrait (the woman from sequence)

## TODO Items

- [ ] Integrate with actual GlyphData system for Codex
- [ ] Add animations to glyph appearance
- [ ] Add visual glitch effects to Velinor sequence (shader or post-processing)
- [ ] Consider screen shake or audio distortion during Velinor moment
- [ ] Test narrative pacing and emotional impact

## Troubleshooting

### Prompt not showing
- Verify NotificationPanelController exists
- Player tag must be set on player character

### E key not working
- Check InputSystem vs Input Manager fallback
- Verify collider "Is Trigger" is checked

### Mind Log not appearing
- Verify MindLogController exists and is found
- Check mind log text fields are populated

### Stage 04 sequence not playing
- Verify Triglyph Screen Panel reference is set
- Verify Scene Transition Collider reference is set
- Check Audio Source is configured
- Ensure door opening sound clip is assigned

### Glyph not being collected
- Integrate CollectGlyph() method with your Codex system
- Verify GlyphData structure matches your system

## Next Steps

1. Set up trigger and script in Stage 01 variant
2. Test basic interaction and Mind Log appearance
3. Copy to Stage 02 and Stage 03, adjust text
4. Set up Stage 04 with Velinor references
5. Test full sequence and timing
6. Adjust narrative text and timing until impactful
7. Add sound effects and visual polish
