# Animation-Driven Footstep System - Implementation Guide

## Overview

This system uses **Animation Events** (not timers) to trigger footsteps at the exact frame when each foot touches the ground. Surface detection happens via invisible **2D trigger colliders** that overlay the player's movement space, allowing flexible audio based on the fictional material beneath the player.

**Key advantages:**
- ✅ Perfectly synced with animation frames
- ✅ No timing drift when animation speed changes
- ✅ Priority system handles overlapping surface zones
- ✅ No physical colliders blocking player movement
- ✅ Invisible zones = clean scene hierarchy

---

## Step 1: Create the FootstepSurface Layer

This layer exclusively holds invisible surface-zone colliders. This keeps surface detection clean and prevents interference with other colliders.

1. **Edit → Project Settings → Tags and Layers**
2. Under **Layers**, find an empty slot and name it: `FootstepSurface`
3. **Close** Project Settings

---

## Step 2: Create the Foot Probe

The foot probe is an invisible point positioned at where the player's feet visually contact the ground. Surface detection happens at this location.

1. Select your **Player** GameObject in the Hierarchy
2. **Right-click → Create Empty**
3. Name it: `FootstepProbe`
4. Set its local position to approximately where the feet touch the ground visually
   - For a character centered at (0, 0), this might be (0, -0.5) or similar
   - **Exact position depends on your sprite and animation**
5. **Keep it as a child** of the Player

**Why:** The probe moves/scales with the player and stays at the exact detection point.

---

## Step 3: Configure FootstepManager

1. Select your **Player** GameObject
2. Add Component → **FootstepManager**

**Audio Setup:**
- Drag the existing AudioSource (or one will be created)
- Set **Master Footstep Volume**: 0.7 (adjust as needed)
- Set **Volume Variation**: 0.08 (adds natural randomness)

**Surface Detection:**
- **Foot Probe**: Drag the FootstepProbe GameObject you just created
- **Surface Check Radius**: 0.15 (increase slightly if detection misses zone edges)
- **Surface Layer**: Select `FootstepSurface` (the layer you created)
- **Default Surface**: Dirt (fallback if no zone detected)

**Movement Validation:**
- **Require Movement**: ON (prevents footsteps during idle animations)
- **Speed Parameter**: "Speed" (matches your Animator parameter)
- **Minimum Movement Speed**: 0.05

**Debug:**
- **Show Debug Messages**: ON (initially, for testing)

---

## Step 4: Create the Surface Audio Sets

In the **FootstepManager** inspector:

**Surface Audio Sets** array:
1. Set size to the number of surface types (e.g., 6 for Dirt, Grass, Mud, Water, Stone, Metal)
2. For each entry:
   - **Surface**: Select from dropdown (Dirt, Grass, Mud, ShallowWater, Stone, Metal, Wood, etc.)
   - **Footstep Clips**: Create an array and drag audio clips for that surface (3-6 clips per surface)
   - **Volume Multiplier**: Adjust volume relative to master volume

**Recommended Volume Multipliers:**
```
Dirt:          0.85  (soft, earthy)
Grass:         0.75  (muted)
Mud:           0.90  (heavy, slightly louder)
ShallowWater:  0.95  (wet, splashy)
Stone:         1.00  (normal reference)
Metal:         1.10  (sharp, prominent)
Wood:          0.90  (hollow, medium)
```

**Audio Source Settings** (auto-configured, verify):
- Play On Awake: **OFF**
- Loop: **OFF**
- Spatial Blend: **0** (fully 2D audio)

---

## Step 5: Create Invisible Surface Zones

For every materially distinct walkable region:

### Single Surface Zone Example (Dirt)

1. **Create → Empty GameObject**
2. Name it: `Surface_Dirt_MainArea`
3. Set **Layer** to `FootstepSurface`
4. Add **BoxCollider2D** (or PolygonCollider2D for irregular shapes)
   - **Size/vertices**: Cover the walkable area where the player can move
   - **Is Trigger**: ✅ ON (must be a trigger!)
5. Add **SurfaceType** component
   - **Surface Type**: Dirt
   - **Priority**: 0 (default, lowest)

**Shape the collider to match the player's actual movement space**, not the visual appearance in the PNG. The player might appear to be walking through a 1000px wide area, but only move across 10 Unity units—size the collider accordingly.

### Zone Hierarchy Example (Market Scene with Multiple Materials)

```
Market_Scene
├─ Player (with PlayerController2D5, FootstepManager, Animator)
│  └─ FootstepProbe
├─ [Background images, NPCs, etc.]
├─ Surface_Dirt_Main (BoxCollider2D, priority 0, covering main path)
├─ Surface_Wood_Planks (BoxCollider2D, priority 10, over wooden boards)
├─ Surface_Mud_Damp (BoxCollider2D, priority 10, over muddy patches)
└─ Surface_Water_Puddle (BoxCollider2D, priority 20, over visible puddles)
```

**The player walks where these colliders overlap. The highest priority wins.**

---

## Step 6: Create the Audio Clip Organization

Organize your footstep audio files logically:

```
Assets/Audio/Footsteps/
├─ Dirt/
│  ├─ dirt_step_01.wav
│  ├─ dirt_step_02.wav
│  ├─ dirt_step_03.wav
│  └─ dirt_step_04.wav
├─ Grass/
│  ├─ grass_step_01.wav
│  ├─ grass_step_02.wav
│  └─ grass_step_03.wav
├─ Metal/
│  ├─ metal_step_01.wav
│  ├─ metal_step_02.wav
│  └─ metal_step_03.wav
├─ Mud/
│  ├─ mud_step_01.wav
│  ├─ mud_step_02.wav
│  └─ mud_step_03.wav
├─ Stone/
│  ├─ stone_step_01.wav
│  ├─ stone_step_02.wav
│  └─ stone_step_03.wav
└─ Wood/
   ├─ wood_step_01.wav
   ├─ wood_step_02.wav
   └─ wood_step_03.wav
```

**Audio Quality Tips:**
- 3-6 clips per surface for good variation
- Clip length: 0.2-0.5 seconds
- Normalize volumes in audio editor before importing
- Distinct characteristics per surface:
  - **Stone**: Hard attack, natural reverb
  - **Metal**: Higher pitch, metallic ring
  - **Dirt**: Soft, dull tone
  - **Water**: Splashy, wet
  - **Wood**: Hollow, creaky

---

## Step 7: Add Animation Events

Animation Events trigger the footstep methods at exact animation frames. This is where the synchronization happens.

### For Each Walk Animation Clip:

1. Select your **Player** in Hierarchy
2. Open **Window → Animation → Animation**
3. Select a walking animation clip from the dropdown
4. Play through slowly (use the scrubber)
5. **Find the frame where the RIGHT foot visibly plants on the ground**
6. **Right-click on that frame → Add Event**
7. Set the function to: **PlayRightFootstep**
8. **Find the frame where the LEFT foot plants**
9. **Right-click → Add Event**
10. Set the function to: **PlayLeftFootstep**

**Repeat for every walk animation:**
- Walk forward
- Walk backward
- Walk left
- Walk right
- Run (if exists)
- Any other movement animation with footsteps

**For running or faster animations:**
- Footsteps may occur more frequently
- The same method names apply; adjust event placement only

### Verification

After adding events:
- Play the animation in the Animation window
- Watch the event markers (red flags) line up with foot contact frames
- They should be **centered on the contact point**, not early or late

---

## Step 8: First Test (Simple Scene)

Before configuring the entire route, test with one small scene:

**Setup:**
1. Create one large **Dirt zone** (priority 0)
2. Create one smaller **Metal zone** inside it (priority 20)
3. Assign 3 Dirt clips to FootstepManager
4. Assign 3 Metal clips to FootstepManager
5. Enable **Show Debug Messages** on FootstepManager

**Test:**
1. Enter Play Mode
2. Walk your character back and forth across the boundary
3. Watch the **Console** for messages:

```
[FootstepManager] Right foot on Dirt using dirt_step_01
[FootstepManager] Left foot on Dirt using dirt_step_03
[FootstepManager] Right foot on Metal using metal_step_02
[FootstepManager] Left foot on Metal using metal_step_01
```

✅ If you see this, the system works!

**If nothing happens:**
- Check Animation Events are added and function names are correct
- Verify FootstepManager has an AudioSource
- Confirm audio clips are assigned
- Check that Speed parameter reaches > 0.05 during movement
- Ensure FootstepProbe is a child of Player and positioned correctly

---

## Step 9: Scene Layout Examples

### Market/Fork Scene (Foreground to Damp Terrain)

```
Surface zones:
├─ Dirt (priority 0) - covers most of walking area
├─ Wood (priority 10) - wooden plank patches
├─ Grass (priority 10) - grassy right fork
└─ ShallowWater (priority 20) - visible puddles
```

**Footstep experience:**
- Walk main path: dirt
- Step on wooden boards: immediate shift to wood
- Approach wet areas: transition to grass/mud
- Wade into puddle: splashy water sounds

### Wet Industrial Approach (Red Dirt to Damp Terrain)

```
Surface zones:
├─ Dirt (priority 0) - foreground and central
├─ Mud (priority 10) - damp central patches
├─ Grass (priority 10) - grass-heavy edges
└─ ShallowWater (priority 20) - water channels
```

### Makeshift Dock Approach (Multi-Material Platform)

```
Surface zones:
├─ Mud (priority 0) - approach area
├─ Wood (priority 10) - dock platform (broad zone)
├─ Metal (priority 20) - metal plates/grating (smaller zones inside wood)
└─ ShallowWater (priority 20) - water edge if walkable
```

---

## Step 10: Troubleshooting

### No Footsteps at All

**Checklist:**
1. ✓ FootstepManager on the same GameObject as Animator?
2. ✓ AudioSource component exists on player?
3. ✓ Audio clips assigned in Surface Audio Sets?
4. ✓ Animation Events added and function names correct?
5. ✓ Speed parameter in Animator > 0.05 during movement?
6. ✓ FootstepProbe positioned at visual ground contact point?
7. ✓ Surface zones on FootstepSurface layer?
8. ✓ Show Debug Messages enabled? (Check console)

**Debug steps:**
- Temporarily disable **Require Movement** to test if events work at all
- Select FootstepManager and check cyan gizmo (wire circle) is visible in Scene view
- Verify Foot Probe position with Gizmo (scene view)

### Everything Sounds Like Dirt

The system is not detecting overlapping zones correctly.

**Checklist:**
1. ✓ All surface zones are on **FootstepSurface** layer?
2. ✓ FootstepManager Surface Layer set to **FootstepSurface**?
3. ✓ Metal zone priority > Dirt zone priority?
4. ✓ Metal zone **Is Trigger** enabled?
5. ✓ Metal zone actually overlaps player position?
6. ✓ Show Debug Messages shows "Dirt" even on metal?

**Fix:**
- Increase Surface Check Radius slightly (0.15 → 0.20)
- Expand zone colliders to fully overlap walking area
- Verify zone priorities are set correctly

### Surface Changes Too Late/Early

The player walks past the visual boundary before audio changes.

**Solution:**
- Adjust the zone collider boundaries to match where the visual material changes
- The collider boundary should align with where the painted material boundary appears
- In 2.5D scenes with fake perspective, this is an artistic choice—adjust until it feels right

### No Surface Detected (Using Default)

The foot probe never enters any zone.

**Checklist:**
1. ✓ Foot Probe positioned at visual ground level?
2. ✓ Zone colliders actually contain the probe position in 3D space?
3. ✓ Increase Surface Check Radius to 0.25-0.30?
4. ✓ Zone colliders not rotated or scaled strangely?

### Footsteps During Idle/Transition

Events are firing when player isn't moving.

**Fix:**
- Ensure **Require Movement** is ON
- Verify Speed parameter is 0 during idle animations
- Check that transition animations don't have events

---

## Advanced: Surface Overrides

For special cases, manually override the surface:

```csharp
FootstepManager manager = GetComponent<FootstepManager>();

// Force metal sounds temporarily
manager.SetSurfaceOverride(SurfaceType.Surface.Metal);

// Return to auto-detection
manager.ClearSurfaceOverride();

// Check current surface
SurfaceType.Surface current = manager.GetCurrentSurface();
Debug.Log("Player on: " + current);
```

---

## Performance Notes

- **Surface detection:** Runs only when Animation Events fire (not every frame)
- **Overlap queries:** One OverlapCircleAll per footstep
- **Audio playback:** Native AudioSource.PlayOneShot (no overhead)
- **Memory:** Dictionary lookups are O(1)

This system is **lightweight and efficient** for typical gameplay.

---

## Final Checklist

Before declaring the system complete:

- [ ] FootstepManager component added to Player
- [ ] Foot Probe created and assigned
- [ ] Surface zones created for all material areas
- [ ] All zones on FootstepSurface layer
- [ ] Surface Audio Sets configured with clips
- [ ] Animation Events added to walk/run animations
- [ ] Test scene created and working
- [ ] Console shows correct material names when walking
- [ ] Audio transitions smoothly between zones
- [ ] Show Debug Messages disabled for production
- [ ] Volumes tuned to balance with dialogue/music

You're ready to build the full route! 🎵
