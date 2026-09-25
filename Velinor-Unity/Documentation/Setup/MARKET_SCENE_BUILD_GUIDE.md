# Market Scene Construction Guide

## Overview
Build a full market scene with proper depth layering using three distinct zones: **Background** (distant horizon), **Midground** (market stalls), and **Foreground** (ground level).

---

## Scene Hierarchy Structure

```
MarketScene (Empty GameObject)
├── Background (Empty - Layer: "Background")
│   ├── Sky (Sphere with sky material - HIGH position, e.g., Y=50)
│   ├── Mountains (Kyle's Rock Pack - distant, Y=5-10)
│   └── Horizon (Low-poly terrain plane - Y=-1)
│
├── Midground (Empty - Layer: "Midground")
│   ├── MarketStalls (Mediterranean Ruins Kit elements)
│   │   ├── Stall_A (Column + roof piece + awning)
│   │   ├── Stall_B (Arch structure)
│   │   ├── Stall_C (Wall segment + window)
│   │   └── Stall_D (Scattered decorative pieces)
│   │
│   ├── Buildings (ALP Assets or Mediterranean Ruins)
│   │   └── Market_Building_01
│   │
│   └── EnvironmentProps (Modular SciFi or scattered assets)
│       ├── Lamp_post
│       ├── Market_bench
│       └── Barrel
│
├── Foreground (Empty - Layer: "Foreground")
│   ├── Ground (Plane or terrain - Y=0)
│   │   └── Material: weathered stone or dirt
│   │
│   ├── GroundProps (Kyle's Rock Pack)
│   │   ├── Rock_pile_01
│   │   ├── Rock_pile_02
│   │   └── Scattered_pebbles
│   │
│   └── ImmediateItems (Close-proximity gameplay objects)
│       ├── Market_stand
│       └── Debris
│
├── Characters (Empty - Layer: "Default")
│   ├── Player (Player capsule or model - Y=1.5m)
│   └── NPCs (SimpleNPC instances)
│       ├── Merchant_01
│       └── Guard_01
│
├── Effects (Empty - Layer: "Effects")
│   ├── Particle_dust
│   ├── Fog_volume
│   └── Post_processing_overlay
│
└── Managers (Empty - Layer: "Default")
    ├── Main Camera (Positioned: X=0, Y=1.5, Z=-5)
    ├── Cinemachine Virtual Camera (if using)
    ├── Lighting
    │   └── Directional Light (Dusk angle: 45°, 315°, 0°)
    ├── MarketSceneSetup (Script component)
    └── DialogueManager / InteractionManager
```

---

## Asset Import & Placement

### Phase 1: Background Setup

**Skybox / Sky Sphere:**
- Use a simple sphere at Y=50 (very high)
- Material: Gradient shader (orange to purple for dusk)
- Scale: 200 (makes it extremely large so player can't see edge)
- Disable cast/receive shadows

**Mountains (Kyle's Rock Pack):**
- Import: `Assets/Kyle's Rock Pack/`
- Select large rock formations (~5-10 pieces)
- Position in a rough line at Z=20-30 (far distance), Y=5-15
- Scale down to 0.5-0.7 to create distance illusion
- Layer: Background
- Disable: Cast shadows (optional - depends on performance)

**Horizon Ground Plane:**
- Create flat plane (1000x1 sized)
- Position: Y=-1 (slightly below player)
- Material: Simple stone/earth texture
- Extends to create visible ground in distance
- Layer: Background

---

### Phase 2: Midground - Market Stalls

**Mediterranean Ruins Kit Assets:**
- Import: `Assets/EmbersStorm – Mediterranean Ruins Building Kit/`
- Use modular pieces to assemble 4-5 market stalls

**Stall Assembly (repeat 4-5 times):**
1. **Stall_A** (Simple covered stall):
   - Base: Arch or column piece
   - Top: Roof/awning element
   - Position: X=-3, Y=0, Z=8 (adjust X for each stall)
   - Rotation: Varies to face market area
   - Layer: Midground

2. **Stall_B** (Enclosed shop):
   - Walls: 2-3 wall segments arranged in L-shape
   - Door: Doorway opening
   - Roof: Top covering
   - Position: X=3, Y=0, Z=12
   - Layer: Midground

3. **Environmental Variety** (ALP or scattered pieces):
   - Add 2-3 different Mediterranean structure types
   - Mix in lamp posts, benches from Modular SciFi
   - Create asymmetrical, organic placement

**Position Guide:**
- Z-depth: 5-15 (between player and horizon)
- X-spread: -8 to +8 (create left-right variation)
- Y: Always on ground (0)
- Scale: 1.0-1.5 (full size, visible detail)
- Layer: Midground

---

### Phase 3: Foreground - Ground & Immediate Props

**Ground Plane:**
- Create or use terrain plane at Y=0
- Size: 50x50 (encompasses player movement area)
- Material: Stone/cobble texture (weathered, dusk lighting)
- Layer: Foreground
- Cast/Receive shadows: Yes

**Scattered Rocks & Debris (Kyle's Rock Pack):**
- Place 8-12 small rock formations at Z=-2 to +5
- Vary sizes: 0.3 scale (small) to 0.8 scale (medium)
- Scatter left/right (X: -6 to +6)
- Add slight Y-offset for natural ground variation (+/- 0.2)
- Layer: Foreground

**Immediate Gameplay Props:**
- Market stand for vendor interaction
- Small debris pile
- Maybe a well or fountain centerpiece
- Layer: Foreground

---

## Camera & Depth Configuration

### Main Camera Setup
```
Position: X=0, Y=1.5, Z=-5
Rotation: X=5, Y=0, Z=0 (slight down tilt to show ground)
FOV: 60 (standard, can adjust for dramatic effect)
```

### Depth Layering via Rendering

**Layer Sorting (in order of visual depth):**
1. **Layer 9 (Background)** - Rendered first (furthest back)
   - Mountains, sky, horizon plane
   - Render distance: Far (>100m)

2. **Layer 10 (Midground)** - Rendered middle
   - Market stalls, buildings
   - Render distance: Medium (50-100m)

3. **Layer 11 (Foreground)** - Rendered third
   - Ground, rocks, immediate items
   - Render distance: Near (10-50m)

4. **Layer 0 (Default)** - Rendered last (closest/interactive)
   - Player, NPCs, interactive objects
   - Render distance: Close (<20m)

**Camera Culling Mask:**
- Configure in Inspector: 
- Visible layers: Background, Midground, Foreground, Default, Effects
- Hidden layers: UI (unless showing UI separately)

---

## Lighting Setup (Dusk Aesthetic)

**Main Directional Light:**
- Angle: 45° around player, angled down from behind left
  - Rotation: X=45, Y=315, Z=0
- Color: Warm orange/amber (RGB: 1.0, 0.7, 0.4)
- Intensity: 0.8-1.0
- Shadow Type: Soft (SoftShadows)
- Shadow Distance: 30-50m

**Ambient Lighting:**
- Ambient Sky Color: Purple-blue (0.3, 0.2, 0.5)
- Ambient Equator: Warm orange (0.8, 0.5, 0.3)
- Ambient Ground: Dark brown (0.2, 0.15, 0.1)
- Ambient Intensity: 0.5-0.7

**Optional Additional Lights:**
- Small point lights in/near stalls (warm yellow, intensity 0.5)
- Soft blue fill light from above (intensity 0.3)

---

## Visual Depth Effects

### Post-Processing (Optional but Recommended)

If using URP with Rendering Features:

1. **Depth of Field:**
   - Focus distance: 15-20m (on midground stalls)
   - Aperture: 16 (slight blur on background)
   - Focal length: 50mm
   - Result: Mountains go soft, stalls stay sharp, creates atmosphere

2. **Color Grading:**
   - Boost warm tones (orange, amber)
   - Reduce saturation slightly (10-15%)
   - Increase contrast slightly (+10%)
   - Creates dusk mood

3. **Fog:**
   - Linear fog start: 30m
   - Linear fog end: 80m
   - Fog color: Warm amber (matches dusk light)
   - Result: Distant mountains fade into haze

---

## Step-by-Step Build Process

1. **Scene Setup:**
   - Create new Scene or work in Marketplace.unity
   - Create empty GameObjects for Background, Midground, Foreground, Characters, Managers
   - Add MarketSceneSetup component to Managers root

2. **Background (10 min):**
   - Create sky sphere + material
   - Import and place rock mountains
   - Create horizon ground plane

3. **Midground (30-45 min):**
   - Import Mediterranean Ruins Kit (if not already)
   - Build 4-5 market stalls from modular pieces
   - Position with Z-depth to create distance
   - Assign to Midground layer

4. **Foreground (15 min):**
   - Create main ground plane
   - Scatter Kyle's Rock Pack elements
   - Add immediate props

5. **Camera & Lighting (10 min):**
   - Position main camera
   - Set up dusk lighting
   - Configure ambient light
   - Test depth effect

6. **Polish (15 min):**
   - Adjust camera angle/FOV
   - Fine-tune lighting colors
   - Add fog if desired
   - Test from player perspective

**Total Build Time: 90-120 minutes for a solid first pass**

---

## Testing Checklist

- [ ] Background mountains visible but feel distant
- [ ] Market stalls clearly read as the focal point
- [ ] Ground plane properly scaled under player feet
- [ ] Camera shows all three depth zones clearly
- [ ] Dusk lighting creates warm, atmospheric mood
- [ ] No z-fighting or layer clipping issues
- [ ] Player can walk around without colliding with background
- [ ] FPS performance acceptable (use Profiler if needed)

---

## Asset Folders Quick Reference

| Asset Pack | Folder | Best For | Import Status |
|-----------|--------|----------|---|
| Kyle's Rock Pack | `Assets/Kyle's Rock Pack/` | Mountains, ground rocks | ✅ Imported |
| Mediterranean Ruins | `Assets/EmbersStorm – Mediterranean Ruins/` | Market stalls, buildings | ✅ Imported |
| ALP Assets | `Assets/ALP_Assets/` | Buildings, props | ✅ Imported |
| Modular SciFi Pack | `Assets/Modular_SciFi_Pack/` | Lamps, technical elements | ✅ Imported |
| 3 English Oak Set | `Assets/3 English Oak Set/` | Trees (if adding greenery) | ✅ Imported |

---

## Next Steps After Scene Completion

1. **Add NPCs** - Instantiate SimpleNPC in Midground area
2. **Add Interactions** - Attach Interactable component to stalls
3. **Add Dialogue** - Link to DialogueManager for vendor conversations
4. **Sound** - Place audio emitters (market ambience from your soundtracks)
5. **Polish** - VFX, particles, final lighting tweaks

---

## Notes for Solo Development

- Don't be perfect. A rougher, more organic arrangement of stalls often looks better than symmetrical
- Use the same modular pieces multiple times (rotated/scaled) - players won't notice repetition
- Trust your lighting - good dusk lighting sells the atmosphere more than perfect geometry
- Test from the player's eye level - what looks good in top-down editor often looks different in-game
