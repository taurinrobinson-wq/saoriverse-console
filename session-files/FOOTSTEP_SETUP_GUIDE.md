# Complete Footstep System Setup for Unity 6.000.4.11f1

**This guide assumes you have no prior experience with Unity layers, components, or animation events. Every step is broken down with exact menu paths and what to look for.**

---

## Part 1: Layer Setup (5 minutes)

Layers are categories that organize GameObjects. We're creating one exclusively for surface zones.

### Step 1.1: Open Project Settings

1. At the top menu bar, click: **Edit** (top-left corner)
2. In the dropdown menu, scroll down and click: **Project Settings**
3. A settings window opens in the editor
4. On the left side, you'll see categories. Click: **Tags and Layers**

**You should now see:**
- A panel on the left with categories
- Two columns on the right: "Tags" and "Layers"
- The Layers column shows slots 0-31 with some already filled (like "Default", "TransparentFX", "Water", etc.)

### Step 1.2: Create the FootstepSurface Layer

1. In the **Layers** column, look for an **empty slot** (you'll see blank lines)
2. Click on the first empty slot you find (usually around slot 6, 7, or 8)
3. Type: `FootstepSurface` (exactly this, one word, capital F and S)
4. Press **Enter**

**Result:** You now have a new layer called "FootstepSurface"

5. Close the Project Settings window (X button, top-right)

---

## Part 2: Create the Foot Probe (3 minutes)

The foot probe is an invisible point where the player's feet touch the ground. It's how the system knows what surface the player is standing on.

### Step 2.1: Select Your Player

1. In the **Hierarchy** panel (left side of editor), find your Player GameObject
2. Click on "Player" to select it
3. You should see it highlighted in blue in the Hierarchy

**Note:** Your player might be called "Player", "Lioren", "PlayerCharacter", or similar. It's the main character GameObject with a sprite and animator.

### Step 2.2: Create a Child GameObject

1. Right-click on the Player in the Hierarchy
2. In the context menu, hover over: **Create Empty**
3. Click on **Create Empty**
4. A new GameObject appears as a child under Player (indented slightly)
5. It's named "GameObject" by default

**What it looks like:**
```
Player
  └─ GameObject  ← This is your new child
```

### Step 2.3: Rename It

1. The new GameObject should be selected
2. In the **Inspector** panel (right side), at the very top, you'll see a text field with "GameObject"
3. Click on that field, clear it, and type: `FootstepProbe`
4. Press **Enter**

**Now it looks like:**
```
Player
  └─ FootstepProbe
```

### Step 2.4: Position the Foot Probe

The probe needs to be positioned at the visual ground contact point—where the player's feet appear to touch the ground in the sprite.

1. Make sure FootstepProbe is selected (highlighted in blue)
2. In the **Inspector**, find the **Transform** component (at the top)
3. Look for **Position** - it shows X, Y, Z values
4. For now, set:
   - **X**: 0
   - **Y**: -0.5  (adjust this based on your sprite—try -0.5 first, then adjust if needed)
   - **Z**: 0

**To adjust:**
- If your character sprite is 2 units tall and centered at (0,0), the feet might be at Y = -1
- Play the game and watch where your feet touch the ground visually
- Adjust Y so the probe is at that point

5. Press **Enter** after each value

---

## Part 3: Configure FootstepManager Component (5 minutes)

### Step 3.1: Add the Component

1. Select your **Player** GameObject (not FootstepProbe—the actual Player)
2. In the **Inspector** (right side), look for a button: **Add Component** (near the bottom of the Transform component)
3. Click **Add Component**
4. A search box appears
5. Type: `FootstepManager` (or start typing "foot..." and it will autocomplete)
6. Click on **FootstepManager** when it appears

**Result:** A new FootstepManager component appears in the Inspector

### Step 3.2: Configure Audio Source

1. In the FootstepManager component, find the **Audio** header
2. Look for the field: **Footstep Audio Source**
3. This field should already be filled with your player's AudioSource
4. If it's empty, do this:
   - Click the circle icon to the right of the field
   - A pop-up appears with a list of GameObjects
   - Find and click your Player (or Animator object if that's where the AudioSource is)
5. Leave the other audio settings as-is for now

### Step 3.3: Configure Surface Detection

1. Find the **Surface Detection** section in FootstepManager
2. Look for **Foot Probe** (empty circle icon)
3. Click the circle icon
4. In the pop-up, find and click **FootstepProbe** (the child object you created)

**Now you should see:**
- Foot Probe: FootstepProbe (assigned)

**Find Surface Layer dropdown:**
1. Next to "Surface Layer", click the dropdown (shows "Nothing" or "Default")
2. A list of layers appears
3. Scroll down and find: **FootstepSurface**
4. Click it

**Now you should see:**
- Surface Layer: FootstepSurface

5. Leave Surface Check Radius at: 0.15 (you can adjust later if detection fails)

### Step 3.4: Configure Movement Validation

Find the **Movement Validation** section:

1. **Require Movement**: Should be ✓ checked (enabled)
2. **Speed Parameter**: Should be "Speed" (matches your Animator parameter)
3. **Minimum Movement Speed**: Leave at 0.05

### Step 3.5: Initial Audio Volume Setup

Find the **Audio** section:

1. **Master Footstep Volume**: Set to 0.7 (medium volume)
2. **Volume Variation**: Leave at 0.08

---

## Part 4: Create Test Audio Sets (5 minutes)

**Start small.** Don't configure all six surface types yet. We'll do just Dirt and Metal to test the system.

### Step 4.1: Expand the Audio Sets Array

1. In FootstepManager, find **Surface Audio Sets** header
2. Next to it, there's a size field (looks like "Size: 0" or "Size: 6")
3. Click the number and change it to: **2** (just Dirt and Metal for now)

**You should now see:**
```
Surface Audio Sets
 Element 0
 Element 1
```

### Step 4.2: Configure Dirt Audio Set

**Element 0 (Dirt):**

1. Click the arrow next to "Element 0" to expand it
2. Find **Surface** dropdown - click it
3. Select: **Dirt**
4. Find **Footstep Clips** - click the arrow to expand
5. Set **Size** to: 2 (start with just 2 clips for testing)
6. Click the first slot (Element 0) under Footstep Clips
7. Click the circle icon and select a dirt footstep audio file
8. Click the second slot (Element 1) and assign another dirt clip
9. Find **Volume Multiplier** - set to: 0.85

### Step 4.3: Configure Metal Audio Set

**Element 1 (Metal):**

1. Click the arrow next to "Element 1" to expand it
2. Find **Surface** dropdown - click it
3. Select: **Metal**
4. Find **Footstep Clips** - set **Size** to: 2
5. Assign 2 metal audio clips to the slots
6. Find **Volume Multiplier** - set to: 1.10

**You can add Grass, Mud, Water, Stone, Wood later after the test passes.**

---

## Part 5: Create the Scene Hierarchy for Surface Zones (5 minutes)

Surface zones must be **stationary in scene space**. They should NOT be children of the Player, or they'll move with the player and defeat the entire purpose.

### Step 5.1: Create a Parent Container

This keeps your scene organized.

1. In the **Hierarchy**, right-click on an empty area (not on Player)
2. Click: **Create Empty**
3. A new GameObject appears
4. Name it: `FootstepSurfaceZones`
5. Leave it in scene space (not parented to anything)

**Your Hierarchy now looks like:**
```
Player
FootstepSurfaceZones
```

### Step 5.2: Create the Dirt Test Zone

1. Right-click on **FootstepSurfaceZones** in the Hierarchy
2. Click: **Create Empty**
3. Name it: `Surface_Dirt_Test`
4. This becomes a child of FootstepSurfaceZones

**Hierarchy:**
```
Player
FootstepSurfaceZones
  └─ Surface_Dirt_Test
```

### Step 5.3: Configure the Dirt Zone

1. With `Surface_Dirt_Test` selected
2. In the **Inspector**, find the **Layer** dropdown (currently says "Default")
3. Click the dropdown and select: **FootstepSurface**
4. Click: **Add Component**
5. Search for and select: **BoxCollider2D**
6. Enable **Is Trigger** (check the box ✓)

### Step 5.4: Shape the Collider

1. In the Scene view (the game preview window), you should see a green rectangle outline around your player
2. This is the BoxCollider2D you just added
3. Click: **Edit Collider** (a button in the BoxCollider2D component in the Inspector)
4. The collider now has green handles you can drag
5. Resize and reposition it so it covers the area where your character actually walks
   - Look at where your player sprite appears to contact the ground
   - The collider should cover approximately that region
   - **Don't overthink it—just make it roughly match the walkable area**
6. When finished, click **Edit Collider** again to deselect

### Step 5.5: Add SurfaceType to Dirt Zone

1. Still with `Surface_Dirt_Test` selected
2. Click: **Add Component**
3. Search for and select: **SurfaceType**
4. Find **Surface** dropdown - select: **Dirt**
5. Find **Priority** - set to: **0**

**Result:** This zone is now "Dirt" with priority 0

---

## Part 6: Create the Metal Test Zone

Repeat Part 5, but for Metal:

### Step 6.1: Create the Metal Zone

1. Right-click on **FootstepSurfaceZones**
2. Click: **Create Empty**
3. Name it: `Surface_Metal_Test`

### Step 6.2: Configure Layer and Collider

1. Layer: **FootstepSurface**
2. Add Component: **BoxCollider2D**
3. Enable: **Is Trigger** ✓
4. Click **Edit Collider**
5. Make this collider **smaller and positioned inside the Dirt zone** (so they overlap)
6. Click **Edit Collider** again when done

### Step 6.3: Add SurfaceType

1. Add Component: **SurfaceType**
2. Surface: **Metal**
3. Priority: **20** (higher than Dirt, so Metal wins when overlapping)

**Your zone hierarchy is now:**
```
Player
FootstepSurfaceZones
  ├─ Surface_Dirt_Test (priority 0)
  └─ Surface_Metal_Test (priority 20, overlaps Dirt)
```

---

## Part 7: Add Animation Events to One Walk Animation (10 minutes)

You only need to test with ONE walking animation to prove the system works. We'll add more animations later.

### Step 7.1: Open the Animation Window

1. At the top menu, click: **Window**
2. Scroll down to find: **Animation**
3. Click: **Animation** 
4. A panel opens (might appear at the bottom, top, or sides)

**You should see:**
- Animation timeline with a blue playhead
- Play/pause buttons
- Animation name selector

### Step 7.2: Select a Walk Animation

1. Select your **Player** in the Hierarchy
2. In the Animation window, find the animation dropdown
3. Find a walking animation (might be called "Walk_Forward", "Walk", "move", etc.)
4. Click it to load that animation in the timeline

**The timeline now shows this animation's frames**

### Step 7.3: Find the Right Foot Contact Frame

1. Use the **scrubber** (the slider on the timeline) to slowly play through the animation
2. Watch the sprite and find the frame where the **right foot** appears to plant on the ground
3. It's usually about 1/4 to 1/3 through the walk cycle
4. Click exactly on that frame in the timeline to position the playhead

**You should see:**
- A red vertical line (scrubber) on that frame
- Frame number displayed (like "Frame 12")

### Step 7.4: Add an Animation Event

**Method 1: Using the Add Event Button**
1. Look for the **Add Event** button in the Animation window
2. Click it
3. The event appears at the playhead position

**Method 2: Right-click the Event Line**
1. Right-click on the **Event line** (the horizontal line where events appear)
2. Select: **Add Animation Event**

**Either way, an event marker appears on the timeline**

### Step 7.5: Configure the Event Function

1. The event marker should now be selected (highlighted)
2. In the **Inspector** (right side), find the event in the list
3. Find the **Function** field (or dropdown)
4. Type or select: `PlayRightFootstep` (exactly this)

### Step 7.6: Add Left Foot Event

Repeat Steps 7.3-7.5, but:
1. Find the frame where the **left foot** plants (usually about halfway through)
2. Add an event at that frame
3. Set the function to: `PlayLeftFootstep`

**Result:** You now have two event markers on the timeline at the foot contact frames

---

## Part 8: Enable Debug and Test (5 minutes)

### Step 8.1: Enable Debug Messages

1. Select your **Player**
2. Find the **FootstepManager** component
3. Find **Debug** section → **Show Debug Messages**: Check ✓

### Step 8.2: Play and Listen

1. Press **Play** (top-center, big play button)
2. Walk your character around
3. **Listen for footsteps**
4. Walk from the Dirt zone into the Metal zone
5. The audio should change

### Step 8.3: Check the Console

1. At the bottom of the editor, find the **Console** window (might be next to Project window)
2. When walking, you should see messages like:
   ```
   [FootstepManager] Right foot on Dirt using dirt_step_01
   [FootstepManager] Left foot on Dirt using dirt_step_02
   [FootstepManager] Right foot on Metal using metal_step_01
   [FootstepManager] Left foot on Metal using metal_step_02
   ```

✅ **If you see these messages and hear sounds:** Your system works!

❌ **If not, check:**
- Animation Events are added and function names are correct
- AudioSource component exists on Player
- Audio clips are assigned in Audio Sets
- Surface zones are on FootstepSurface layer
- Foot Probe is positioned correctly
- Speed parameter rises above 0.05 during movement

### Step 8.4: Disable Debug for Production

Once everything works:
1. Select Player
2. Find FootstepManager → **Show Debug Messages**: Uncheck ☐

---

## Part 9: Expand to Full Route (Do This After Testing)

Once your Dirt + Metal test passes, add the remaining surface types:

### Step 9.1: Add More Audio Sets

1. In FootstepManager, change **Surface Audio Sets Size** to: 6
2. Add entries for: Grass, Mud, ShallowWater, Stone, Wood
3. For each, assign 3-6 audio clips and set volume multipliers:
   - Grass: 0.75
   - Mud: 0.90
   - ShallowWater: 0.95
   - Stone: 1.00
   - Wood: 0.90

### Step 9.2: Create Surface Zones for Your Route

Based on your scenes:

**Market/Fork Scene:**
- Surface_Dirt_Main (priority 0)
- Surface_Wood_Planks (priority 10)
- Surface_Grass_RightFork (priority 10)
- Surface_Water_Puddle01 (priority 20)

**Wet Industrial Approach:**
- Surface_Dirt_Foreground (priority 0)
- Surface_Mud_Central (priority 10)
- Surface_Grass_Edges (priority 10)
- Surface_Water_Channel (priority 20)

**Makeshift Dock:**
- Surface_Mud_Approach (priority 0)
- Surface_Wood_Dock (priority 10)
- Surface_Metal_Plate (priority 20)

### Step 9.3: Add Animation Events to All Walk Animations

Once the system is working, add Animation Events to:
- Walk forward
- Walk backward
- Walk left
- Walk right
- Run (if exists)

---

## Troubleshooting Quick Reference

### No Sound at All
- ☐ AudioSource on Player?
- ☐ Audio clips assigned in Audio Sets?
- ☐ Animation Events added to animation?
- ☐ Enable Show Debug Messages and check Console

### Wrong Surface Detected
- ☐ Zones on FootstepSurface layer?
- ☐ Zones have "Is Trigger" ✓?
- ☐ Zones actually overlap player position?
- ☐ Priorities set correctly (higher = wins)?

### Surface Not Changing at Zone Boundary
- Expand zone colliders to fully overlap walking area
- Increase Surface Check Radius from 0.15 to 0.20
- Verify priorities (Metal should be > Dirt)

---

## Checklist - Testing Phase

- ☐ FootstepSurface layer created
- ☐ FootstepProbe created as Player child
- ☐ FootstepManager added to Player
- ☐ Dirt and Metal audio sets configured
- ☐ Surface_Dirt_Test zone created
- ☐ Surface_Metal_Test zone created (overlapping Dirt)
- ☐ Animation Events added to one walk animation
- ☐ Play mode: Footsteps sound when walking
- ☐ Play mode: Audio changes from Dirt to Metal
- ☐ Console shows correct surface names

✅ **Once all checked, your system is proven. Then expand to the full route.**

---

## Final Notes

- Surface zones are **invisible during gameplay**—they're just detection areas
- Zones stay **stationary in scene space**—never parent them to Player
- Priority system handles overlapping zones—highest priority wins
- Animation Events fire at exact animation frames—perfectly synced audio
- **Test with 2 surfaces first** before building the whole route

You're ready! 🎵

Layers are categories that organize GameObjects. We're creating one exclusively for surface zones.

### Step 1.1: Open Project Settings

1. At the top menu bar, click: **Edit** (top-left corner)
2. In the dropdown menu, scroll down and click: **Project Settings**
3. A settings window opens in the editor
4. On the left side, you'll see categories. Click: **Tags and Layers**

**You should now see:**
- A panel on the left with categories
- Two columns on the right: "Tags" and "Layers"
- The Layers column shows slots 0-31 with some already filled (like "Default", "TransparentFX", "Water", etc.)

### Step 1.2: Create the FootstepSurface Layer

1. In the **Layers** column, look for an **empty slot** (you'll see blank lines)
2. Click on the first empty slot you find (usually around slot 6, 7, or 8)
3. Type: `FootstepSurface` (exactly this, one word, capital F and S)
4. Press **Enter**

**Result:** You now have a new layer called "FootstepSurface"

5. Close the Project Settings window (X button, top-right)

---

## Part 2: Create the Foot Probe (3 minutes)

The foot probe is an invisible point where the player's feet touch the ground. It's how the system knows what surface the player is standing on.

### Step 2.1: Select Your Player

1. In the **Hierarchy** panel (left side of editor), find your Player GameObject
2. Click on "Player" to select it
3. You should see it highlighted in blue in the Hierarchy

**Note:** Your player might be called "Player", "Lioren", "PlayerCharacter", or similar. It's the main character GameObject with a sprite and animator.

### Step 2.2: Create a Child GameObject

1. Right-click on the Player in the Hierarchy
2. In the context menu, hover over: **Create Empty**
3. Click on **Create Empty**
4. A new GameObject appears as a child under Player (indented slightly)
5. It's named "GameObject" by default

**What it looks like:**
```
Player
  └─ GameObject  ← This is your new child
```

### Step 2.3: Rename It

1. The new GameObject should be selected
2. In the **Inspector** panel (right side), at the very top, you'll see a text field with "GameObject"
3. Click on that field, clear it, and type: `FootstepProbe`
4. Press **Enter**

**Now it looks like:**
```
Player
  └─ FootstepProbe
```

### Step 2.4: Position the Foot Probe

The probe needs to be positioned at the visual ground contact point—where the player's feet appear to touch the ground in the sprite.

1. Make sure FootstepProbe is selected (highlighted in blue)
2. In the **Inspector**, find the **Transform** component (at the top)
3. Look for **Position** - it shows X, Y, Z values
4. For now, set:
   - **X**: 0
   - **Y**: -0.5  (adjust this based on your sprite—try -0.5 first, then adjust if needed)
   - **Z**: 0

**To adjust:**
- If your character sprite is 2 units tall and centered at (0,0), the feet might be at Y = -1
- Play the game and watch where your feet touch the ground visually
- Adjust Y so the probe is at that point

5. Press **Enter** after each value

---

## Part 3: Configure FootstepManager Component (5 minutes)

### Step 3.1: Add the Component

1. Select your **Player** GameObject (not FootstepProbe—the actual Player)
2. In the **Inspector** (right side), look for a button: **Add Component** (near the bottom of the Transform component)
3. Click **Add Component**
4. A search box appears
5. Type: `FootstepManager` (or start typing "foot..." and it will autocomplete)
6. Click on **FootstepManager** when it appears

**Result:** A new FootstepManager component appears in the Inspector

### Step 3.2: Configure Audio Source

1. In the FootstepManager component, find the **Audio** header
2. Look for the field: **Footstep Audio Source**
3. This field should already be filled with your player's AudioSource
4. If it's empty, do this:
   - Click the circle icon to the right of the field
   - A pop-up appears with a list of GameObjects
   - Find and click your Player (or Animator object if that's where the AudioSource is)
5. Leave the other audio settings as-is for now

### Step 3.3: Configure Surface Detection

1. Find the **Surface Detection** section in FootstepManager
2. Look for **Foot Probe** (empty circle icon)
3. Click the circle icon
4. In the pop-up, find and click **FootstepProbe** (the child object you created)

**Now you should see:**
- Foot Probe: FootstepProbe (assigned)

**Find Surface Layer dropdown:**
1. Next to "Surface Layer", click the dropdown (shows "Nothing" or "Default")
2. A list of layers appears
3. Scroll down and find: **FootstepSurface**
4. Click it

**Now you should see:**
- Surface Layer: FootstepSurface

5. Leave Surface Check Radius at: 0.15 (you can adjust later if detection fails)

### Step 3.4: Configure Movement Validation

Find the **Movement Validation** section:

1. **Require Movement**: Should be ✓ checked (enabled)
2. **Speed Parameter**: Should be "Speed" (matches your Animator parameter)
3. **Minimum Movement Speed**: Leave at 0.05

### Step 3.5: Initial Audio Volume Setup

Find the **Audio** section:

1. **Master Footstep Volume**: Set to 0.7 (medium volume)
2. **Volume Variation**: Leave at 0.08

---

## Part 4: Create Surface Audio Sets (10 minutes)

This is where you assign the actual audio files to different surface types.

### Step 4.1: Understand the Setup

The FootstepManager needs to know:
- "When the player is on dirt, play these dirt sounds"
- "When on metal, play these metal sounds"
- etc.

You do this by creating "audio sets" for each surface type.

### Step 4.2: Expand the Audio Sets Array

1. In FootstepManager, find **Surface Audio Sets** header
2. Next to it, there's a size field (looks like "Size: 0" or "Size: 6")
3. Click the number and change it to: **6** (for Dirt, Grass, Mud, Metal, Stone, Water)

**You should now see:**
```
Surface Audio Sets
 Element 0
 Element 1
 Element 2
 Element 3
 Element 4
 Element 5
```

Each element is expandable.

### Step 4.3: Fill in Each Audio Set

**Element 0 (Dirt):**

1. Click the arrow next to "Element 0" to expand it
2. Find **Surface** dropdown - click it
3. Select: **Dirt**
4. Find **Footstep Clips** - click the arrow to expand
5. Set **Size** to: 3 (you'll add 3 dirt sound clips)
6. Click each numbered slot (Element 0, Element 1, Element 2)
7. For each slot, click the circle icon and drag/select a dirt footstep audio file
8. Find **Volume Multiplier** - set to: 0.85

**Repeat for each surface type:**

**Element 1 (Grass):**
- Surface: Grass
- Footstep Clips Size: 3
- Assign 3 grass sound files
- Volume Multiplier: 0.75

**Element 2 (Mud):**
- Surface: Mud
- Footstep Clips Size: 3
- Assign 3 mud sound files
- Volume Multiplier: 0.90

**Element 3 (ShallowWater):**
- Surface: ShallowWater
- Footstep Clips Size: 2-3
- Assign water sound files
- Volume Multiplier: 0.95

**Element 4 (Stone):**
- Surface: Stone
- Footstep Clips Size: 3
- Assign stone sound files
- Volume Multiplier: 1.00

**Element 5 (Metal):**
- Surface: Metal
- Footstep Clips Size: 3
- Assign metal sound files
- Volume Multiplier: 1.10

**How to assign audio clips:**
1. Click the circle icon next to a slot
2. A file browser opens
3. Find your audio file in Assets/Audio/Footsteps/ (or wherever you have them)
4. Click the file
5. It assigns to that slot

---

## Part 5: Create Surface Zone Colliders (15 minutes)

Surface zones are invisible colliders that mark different surface materials in your scene.

### Step 5.1: Create the First Surface Zone (Dirt)

1. In the **Hierarchy**, right-click on your Scene (or on the Player)
2. Click: **Create Empty**
3. A new GameObject appears
4. Name it: `Surface_Dirt_Main`

### Step 5.2: Set Its Layer

1. With `Surface_Dirt_Main` selected
2. In the **Inspector**, at the top, find the **Layer** dropdown (currently says "Default")
3. Click the dropdown
4. Select: **FootstepSurface**

**Result:** This GameObject is now on the FootstepSurface layer

### Step 5.3: Add a Collider

1. Still in Inspector, click: **Add Component**
2. Search for: `BoxCollider2D` (for rectangular areas) or `PolygonCollider2D` (for irregular shapes)
3. Select **BoxCollider2D** for now (easier to start with)
4. It appears in the Inspector

### Step 5.4: Configure the Collider

1. Find the **BoxCollider2D** component
2. Find **Is Trigger** - check this box ✓
3. Adjust the **Size** to cover the walkable area:
   - **Size X**: How wide the area is (try 20)
   - **Size Y**: How tall the area is (try 5)
4. Adjust the **Offset** to position it correctly:
   - **Offset X**: 0
   - **Offset Y**: 0 (adjust if the box isn't centered where players walk)

**How to know if it's right:**
- Play the game
- Look at the Scene view while moving
- The collider should roughly cover where your character walks
- It's invisible during gameplay—it's just detection

### Step 5.5: Add SurfaceType Component

1. Still in Inspector, click: **Add Component**
2. Search for: `SurfaceType`
3. Select it
4. It appears in Inspector

### Step 5.6: Configure SurfaceType

1. Find the **SurfaceType** component
2. Find **Surface** dropdown
3. Select: **Dirt**
4. Find **Priority** - set to: 0 (default, lowest priority)

**Result:** This zone is now marked as "Dirt" surface with priority 0

### Step 5.7: Create Additional Zones

Repeat Steps 5.1-5.6 for each additional surface type you need in your scene:

**Example for Metal Zone:**
1. Create Empty → Name: `Surface_Metal_Platform`
2. Layer: FootstepSurface
3. Add BoxCollider2D (is Trigger ✓)
4. Size: appropriate for the metal area
5. Add SurfaceType → Surface: Metal, Priority: 20

**Priority System:**
- Dirt zones: Priority 0
- Grass/Mud zones: Priority 10
- Water/Metal zones: Priority 20
- Higher priority wins if zones overlap

---

## Part 6: Add Animation Events (10 minutes)

Animation events are markers in the animation timeline that trigger the footstep sounds.

### Step 6.1: Open the Animation Window

1. At the top menu, click: **Window**
2. Scroll down to find: **Animation**
3. Click: **Animation** (or **Animation → Animation**)
4. A panel opens (might appear at the bottom, top, or sides)

**You should see:**
- Animation timeline
- Play/pause controls
- A list of animations

### Step 6.2: Select a Walk Animation

1. Select your **Player** in the Hierarchy
2. In the Animation window, find the dropdown showing animations
3. Find a walking animation (might be called "Walk_Forward", "Walk", "move", etc.)
4. Click it to select it

**The timeline now shows this animation's frames**

### Step 6.3: Find the Right Foot Contact Frame

1. Use the **scrubber** (the slider on the timeline) to slowly play through the animation
2. Watch the sprite and find the frame where the **right foot** appears to plant on the ground
3. It's usually about 1/4 to 1/3 through the walk cycle
4. Click exactly on that frame in the timeline

**You should see:**
- A red vertical line (scrubber) on that frame
- Frame number displayed (like "Frame 12")

### Step 6.4: Add an Animation Event

1. Right-click on the timeline at that frame
2. A context menu appears
3. Click: **Add Event**
4. A small window pops up asking for the function name
5. Type: `PlayRightFootstep` (exactly this)
6. Click outside or press Enter

**Result:** A small red flag appears on the timeline at that frame

### Step 6.5: Find and Add Left Foot Event

1. Continue scrubbing through the animation
2. Find the frame where the **left foot** plants (usually about halfway through)
3. Right-click on that frame
4. Click: **Add Event**
5. Type: `PlayLeftFootstep`
6. Press Enter

**Result:** Another red flag appears at the left foot contact frame

### Step 6.6: Repeat for Other Walk Animations

You need to do this for EVERY walk animation:
- Walk Forward
- Walk Backward
- Walk Left
- Walk Right
- Run (if it exists)
- Any other movement animations

---

## Part 7: First Test (5 minutes)

### Step 7.1: Create a Simple Test Scene

Before testing on the full route, create one tiny test:

1. In Hierarchy, create two zones:
   - `Surface_Dirt_Test` (large, priority 0)
   - `Surface_Metal_Test` (small, priority 20, inside the dirt)
2. Configure each with their surface types
3. Assign just 2-3 clips per surface to FootstepManager

### Step 7.2: Enable Debug Messages

1. Select your Player
2. Find FootstepManager component
3. Find **Debug** section → **Show Debug Messages**: Check ✓

### Step 7.3: Play and Test

1. Press **Play** (top-center of editor)
2. Walk your character around
3. Watch the **Console** window (bottom of editor)
4. You should see messages like:
   ```
   [FootstepManager] Right foot on Dirt using dirt_step_01
   [FootstepManager] Left foot on Dirt using dirt_step_02
   [FootstepManager] Right foot on Metal using metal_step_01
   ```

**If you see these messages:** ✅ Your system works!

**If you don't:**
- Check that Animation Events are added
- Verify speed is > 0.05 during movement (Animator Speed parameter)
- Confirm audio clips are assigned
- Make sure zones are on FootstepSurface layer

### Step 7.4: Disable Debug for Production

Once working:
1. Select Player
2. Find FootstepManager → **Show Debug Messages**: Uncheck ☐

---

## Part 8: Troubleshooting Quick Fixes

### No Sound at All

**Checklist:**
1. ☐ AudioSource component on Player?
2. ☐ Audio clips assigned in Surface Audio Sets?
3. ☐ Animation Events added to walk animations?
4. ☐ Show Debug Messages ON → Check console for errors?
5. ☐ FootstepManager on the same GameObject as Animator?

### Wrong Surface Detected

**Checklist:**
1. ☐ Surface zones on FootstepSurface layer?
2. ☐ Zones have "Is Trigger" ✓ enabled?
3. ☐ Zones actually overlap where player walks?
4. ☐ FootstepManager Surface Layer set to FootstepSurface?
5. ☐ Show Debug Messages → Check which surface is detected

### Surface Not Changing at Boundary

1. Expand the zone colliders slightly to ensure overlap
2. Increase Surface Check Radius from 0.15 to 0.20
3. Verify priorities (highest number wins)

---

## Checklist Before Declaring Success

- ☐ FootstepManager component added to Player
- ☐ Foot Probe created and positioned
- ☐ FootstepSurface layer created
- ☐ Audio sets configured with clips
- ☐ At least 2 surface zones created and tested
- ☐ Animation events added to walk animations
- ☐ Console shows correct surface names
- ☐ Footstep sounds play when walking
- ☐ Audio changes when stepping on different surfaces

✅ You're ready to build the full route!

