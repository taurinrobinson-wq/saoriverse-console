# Character Pipeline: 2D Sprites → 3D Game Ready

## Your Current Assets

You have **multi-angle character turntables** (from ezgif-split) showing:
- Multiple rotations (5-8 different angles)
- Multiple frames per rotation (animation sequence)
- Color variations and silhouettes

**This is perfect for sprite-based 3D games.** Professional studios use this exact approach.

---

## Fastest Path: Sprite Sheet → Billboard Character

### What You're Creating
A character that appears 3D by:
1. Showing different sprite based on player's view angle
2. Supporting multiple animations (idle, walk, talk)
3. Simple quad geometry with texture mapping

### Visual Result
- Looks pseudo-3D in gameplay
- Character rotates naturally as player walks around them
- Smooth animation transitions
- Perfect for story-driven games (Disco Elysium, Kentucky Route Zero use similar)

---

## Step-by-Step Conversion Workflow

### Phase 1: Sprite Sheet Export (YOUR PART)

**Input:** Your GIF animation files (each character has multiple rotations)  
**Output:** Single sprite sheet PNG per character

#### Process:
1. **Open your GIF in your sprite sheet tool** (or manually in Photoshop/GIMP):
   - Adobe Illustrator turntable GIFs
   - Or your ezgif-split frame images

2. **Organize as grid:**
   ```
   Columns = Rotation angles (5-8 angles, e.g., front, 3/4, side, back, etc.)
   Rows = Animation frames (idle = 1 frame, walk = 4-6 frames, talk = 3-4 frames)
   
   Example for Ravi:
   Col 1: Front angle
   Col 2: Front-right angle
   Col 3: Right angle
   Col 4: Back-right angle
   Col 5: Back angle
   (repeat for idle, walk, talk animations)
   ```

3. **Export settings:**
   - **Size:** 512x512 or 1024x1024 per sprite cell
   - **Grid:** Ensure uniform spacing
   - **Format:** PNG with transparency
   - **Naming:** `Ravi_Sprites.png`, `Nima_Sprites.png`, etc.

4. **Create a simple text file documenting the layout:**
   ```
   Ravi_Sprites.png:
   - Columns: Front, Front-Right, Right, Back-Right, Back (5 angles)
   - Rows:
     - Row 0-1: Idle (2 frames)
     - Row 2-5: Walk (4 frames)
     - Row 6-8: Talk (3 frames)
   - Frame size: 512x512
   - Total grid: 5 columns × 9 rows
   ```

**Deliverable:** One PNG file per character + documentation file

---

### Phase 2: Unity Setup (I CAN HELP WITH THIS)

**Input:** Your sprite sheet PNG + documentation  
**Output:** Game-ready NPC prefab

#### What Gets Built:

**1. Sprite Mapper Prefab:**
```
GameObject "NPCCharacter_Ravi"
├── SpriteRenderer (displays current frame)
├── AngleLOD script (selects frame based on camera angle)
├── AnimationController script (manages idle/walk/talk states)
├── Collider (for interaction)
└── SortingOrder (ensures correct layering)
```

**2. Angle Detection System:**
```csharp
// Pseudo-code
void UpdateDisplayFrame() {
    float angleToCamera = Vector3.Angle(transform.forward, playerCamera.forward);
    
    if (angleToCamera < 36°)       use Column 0 (front)
    else if (angleToCamera < 72°)  use Column 1 (front-right)
    else if (angleToCamera < 108°) use Column 2 (right)
    else if (angleToCamera < 144°) use Column 3 (back-right)
    else                           use Column 4 (back)
    
    // Then pick animation frame based on current state
    if (isIdle)   show row 0 + frame counter
    if (isWalking) show row 2 + frame counter
    if (isTalking) show row 6 + frame counter
}
```

**3. Animation State Machine:**
```
States: Idle → Walk → Talk → Idle
Transitions trigger on:
- Player distance change (walk when far, idle when close)
- Dialogue start (talk when speaking)
```

**Deliverable:** Working NPC prefab, usable in any scene

---

## Detailed Example: Creating Ravi

### Your Job:
1. Take your Ravi animation GIF frames
2. Arrange in sprite sheet:
   ```
   5 rotation angles × 9 animation frames = 45 total frames
   Organized as 5 columns × 9 rows grid
   Export as single PNG, 2560×4608 pixels (512×512 per cell)
   ```
3. Create documentation file noting:
   - Which rows = idle/walk/talk
   - Which columns = which angles
   - Frame duration (e.g., 0.1 seconds per frame)

### My Job:
1. Create `RaviCharacterController.cs` script
2. Set up sprite mapper to read your grid
3. Implement angle-based sprite selection
4. Wire to dialogue system (triggers talk animation)
5. Create `Ravi_Prefab` for dropping into scenes

### Result in Game:
```
Player walks around Ravi
→ Front view shows front-facing sprite
→ Walk around to side
→ Sprite smoothly switches to side angle
→ Player starts dialogue
→ Ravi animation switches to talk loop
→ Player leaves dialogue
→ Ravi returns to idle
```

---

## Advanced: Supporting Pose Variations

**Optional enhancement:** If your character has emotional states

Example Ravi might show:
- Idle (neutral)
- Idle (concerned - worried about daughter)
- Talk (explaining situation)
- Talk (emotional - remembering)
- Grief (slumped shoulders)

Each would be a separate section in the sprite sheet:
```
Rows 0-1:   Idle (neutral)
Rows 2-3:   Idle (concerned)
Rows 4-7:   Walk
Rows 8-10:  Talk (normal)
Rows 11-13: Talk (emotional)
Rows 14-16: Grief (post-boss)
```

Script toggles which row block based on `CodexManager.emotionalTags`.

---

## File Formats & Tools Reference

### Creating Sprite Sheets from GIFs:

**Option 1: Free Tools**
- **TexturePacker (free version):** Drag GIFs in, auto-generates sprite sheet
- **Aseprite:** $20, specifically designed for this
- **GIMP:** Free, manual but works
- **Photoshop:** Drag frames in, export as grid

**Option 2: Command Line**
```bash
# ImageMagick (free, installed on most systems)
montage input_*.png -tile 5x9 -geometry 512x512+0+0 output_spritesheet.png
```

**Option 3: Online**
- **SpritesheetPacker.com** - Free web tool
- Upload frames → Download spritesheet

---

## Technical Specifications for Unity

### Sprite Import Settings:
```
Texture Type: Sprite (2D and UI)
Sprite Mode: Multiple
Pixels Per Unit: 100 (adjust to taste)
Filter Mode: Point (pixel art) or Bilinear (smooth)
Compression: None (or ETC2 if space matters)
Wrap Mode: Clamp
```

### Prefab Structure:
```
Ravi_NPC (GameObject)
├── Model (Sprite Renderer)
│   ├── Sprite: Ravi_Sprites (your PNG)
│   ├── Order in Layer: 5 (above ground)
│   └── Material: Lit/Default Sprite
├── Collider (CapsuleCollider2D)
│   └── Is Trigger: true
├── InteractionZone (your existing script)
├── RaviController (new sprite controller)
│   ├── Sprite sheet reference
│   ├── Animation speeds
│   ├── Angle LOD settings
│   └── State machine
└── DialogueNPC (inherits from SimpleNPC)
    └── Ravi's dialogue lines
```

---

## Animation Timing

### Frame Rates (adjust to your preference):
```
Idle animation:   1-2 frames, 0.5-1.0 sec per frame (slow, contemplative)
Walk animation:   4-6 frames, 0.08-0.12 sec per frame (natural pace)
Talk animation:   3-4 frames, 0.15-0.25 sec per frame (lip-sync visual)
```

---

## Quality Levels

### Minimum (for fast demo):
- 1 animation per character (idle only)
- 5 rotation angles (8-directional)
- Simple spritesheet grid
- **Time: 3-4 hours for 4 characters**

### Recommended (for polished demo):
- 3 animations per character (idle, walk, talk)
- 5-8 rotation angles
- Organized spritesheet with documentation
- **Time: 8-12 hours for 4 characters**

### Full Polish (after demo):
- 5+ animations per character (idle, walk, talk, emote, hurt, victory, etc.)
- 8 rotation angles (perfect circle)
- Per-animation frame rate tuning
- Emotional state variations
- **Time: 20+ hours for full cast**

---

## Workflow Summary

```
Your GIF frames
    ↓
Organize into sprite sheet grid (5 angles × N frames)
    ↓
Export as single PNG per character
    ↓
Create documentation (which rows = which animations)
    ↓
[I create the Unity prefab & scripts]
    ↓
Drop prefab into scene
    ↓
Character appears, rotates with camera angle, animates on cue
```

---

## Questions to Answer Now

1. **How many frames per character do you have?**
   - Just idle? Or idle+walk+talk?
   - If animated GIF, how many total frames?

2. **How many angles does your turntable show?**
   - 5 (front, F-right, right, B-right, back)?
   - 8 (full circle)?
   - More?

3. **Animation frame rates:**
   - How fast should idle play? (Saori might be slower/more meditative)
   - Ravi & Nima realistic walk?
   - Kaelen nervous/quick?

4. **Emotional variations:**
   - Should characters change pose based on story beats?
   - (E.g., Ravi slumped after learning about Ophina)

5. **Do you have a boss creature**
   - Or should we design that?
   - Sprite-based or 3D model priority?

---

## Deliverables from You (This Week)

For demo to start building:
1. [ ] Saori sprite sheet (or single frame if idle-only)
2. [ ] Ravi sprite sheet
3. [ ] Nima sprite sheet
4. [ ] Kaelen sprite sheet
5. [ ] Documentation file listing animation frames for each
6. [ ] (Optional) Boss creature concept/image

**That's it.** Everything else is scripting, which is done.

---

## Timeline

- **Today/Tomorrow:** Export sprite sheets
- **Day 3-4:** Build Saori + Scene 1
- **Day 5-6:** Build Ravi/Nima + Scene 2
- **Day 7-8:** Build Kaelen + Scene 3
- **Parallel:** Environments + boss design

**Total character setup time: 2-3 days**

---

This is fast, professional, and perfect for solo indie dev. Let me know what you need!
