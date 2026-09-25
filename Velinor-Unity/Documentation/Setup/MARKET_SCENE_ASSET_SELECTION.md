# Market Scene - Asset Selection Quick Reference

## Which Specific Models to Use

### Background Mountains (Kyle's Rock Pack)

**Folder:** `Assets/Kyle's Rock Pack/Models/`

**Select these models (examples - adjust to taste):**
- `Rocky_Terrain_Large_01.fbx` - Main mountain mass
- `Rocky_Terrain_Large_02.fbx` - Secondary mountain
- `Rocky_Mountain_Peak_01.fbx` - Peak texture
- `Rock_Formation_Medium_01.fbx` - Mid-distance detail
- `Rock_Outcrop_Medium_01.fbx` - Variety piece

**Scaling Strategy:**
- Main mountains: Scale 0.8-1.2 (natural size for distance)
- Adjust Y position: +5 to +15m
- Space Z-wise: +20 to +35m away from player
- No shadows on mountains (too far, performance)

---

### Market Stalls (Mediterranean Ruins Kit)

**Folder:** `Assets/EmbersStorm – Mediterranean Ruins Building Kit/Models/`

**Stall Assembly Pattern 1 - Simple Covered Stall:**
- `Arch_01.fbx` - Base structure
- `RoofTile_Corner_01.fbx` + `RoofTile_01.fbx` x2 - Roof covering
- `Column_Small_01.fbx` - Support post
- **Assembly:** Column → Arch spans between → Roof on top
- **Position:** Z=6-8m, scattered X -6 to +6
- **Scale:** 1.0 (full size)

**Stall Assembly Pattern 2 - Enclosed Shop:**
- `WallSegment_01.fbx` - Left wall
- `WallSegment_01.fbx` - Right wall (rotated 90°)
- `Doorway_01.fbx` - Front opening
- `RoofTile_01.fbx` x4 - Roof frame
- **Assembly:** Create L-shape with walls, add door, cap with roof
- **Position:** Z=10-12m, offset to side
- **Scale:** 1.0

**Stall Assembly Pattern 3 - Mixed/Decorative:**
- Combine smaller pieces: `Pillar_Small_01.fbx`, broken wall sections
- Add wooden stall counter prop if available
- Create organic, varied silhouette
- **Position:** Z=7-9m, clustered near other stalls

**Pro Tips for Assembly:**
- Don't align perfectly - offset pieces slightly for worn look
- Mix 2-3 different styles for visual interest
- Leave some gaps (players can see "into" stalls)
- Some pieces can be rotated 45° for variety

---

### Ground Elements (Kyle's Rock Pack)

**Folder:** `Assets/Kyle's Rock Pack/Models/`

**Scattered Ground Detail (pick 4-6 models):**
- `Rock_Small_Scattered_01.fbx` - Pebble clusters
- `Rock_Medium_Jagged_01.fbx` - Medium rock
- `Rock_Medium_Jagged_02.fbx` - Different shape
- `Boulder_Small_01.fbx` - Round stone
- `Rocky_Terrain_Small_01.fbx` - Miniature terrain
- Any `Stone_*` models for variety

**Placement Strategy:**
- Spread 10-15 instances randomly in foreground
- Z-range: -1 to +4m (immediate player area)
- X-range: -6 to +6m (left-right variation)
- Y offset: -0.2 to +0.3 (sit naturally on ground)
- Rotation: Random (important for natural look!)
- Scale: 0.3-0.8 (variety of sizes)

---

### Environmental Props & Detail

**Modular SciFi Pack (if adding technical/industrial touch):**
- `SciFi_Lamp_Post_01.fbx` - Street lighting
- `SciFi_Crate_01.fbx` - Storage/cargo boxes
- `SciFi_Bench_01.fbx` - Seating

**Or stick with Mediterranean theme:**
- Look for: planters, urns, decorative pieces in Mediterranean Ruins kit
- Use multiple instances of same piece (scaled differently)
- Add near stalls for market character

**ALP Assets (Secondary buildings):**
- `Folder: Assets/ALP_Assets/Models/Buildings/`
- Pick 1-2 larger structures for background midground
- Position at Z=15-18m for visible but not focal

---

## Layer Assignment Setup

**First, create these layers in Project Settings → Layers:**
- Slot 9: `Background`
- Slot 10: `Midground`
- Slot 11: `Foreground`
- Slot 12: `Effects`

**Then assign models as you place them:**
```
Background layer:
- Sky sphere
- All Kyle's Rock mountains
- Horizon ground plane

Midground layer:
- All Mediterranean Ruins stalls
- Secondary buildings (ALP)
- Scattered Modular SciFi props (lamps, etc.)

Foreground layer:
- Main ground plane
- Scattered ground rocks
- Immediate gameplay props
```

**Script Reference:**
```csharp
// In MarketSceneSetup.cs, this assignment is automated:
MarketSceneSetup setup = GetComponent<MarketSceneSetup>();
setup.PlaceInLayer(marketStall, "Midground");
setup.PlaceInLayer(rockFormation, "Foreground");
```

---

## Material & Texture Assignments

### Dusk Color Palette

**For lighting materials/override:**
- Main Stall Color: Warm beige/tan (RGB: 0.9, 0.8, 0.6)
- Shadow areas: Warm brown (RGB: 0.5, 0.4, 0.2)
- Ground stone: Grey-brown (RGB: 0.6, 0.55, 0.5)
- Rock details: Dark stone (RGB: 0.3, 0.3, 0.3)

**How to apply:**
- Mediterranean Ruins kit should have proper materials
- If needed, adjust material colors in Inspector or create override materials
- Use `Edit → Rendering → Light Settings` to adjust scene ambient colors

---

## Performance Tips

**For Solo Developer Building 3D:**

1. **Keep it simple first pass:**
   - 4 market stalls (not 20)
   - Mountains: 5 large rocks (not detailed mountain range)
   - Ground: One simple plane + 10 rock details (not complex terrain)

2. **Optimize as you go:**
   - Check FPS in Game view (press Play)
   - If FPS < 60, reduce rock count or mountain distance
   - Use LOD levels on far-away assets if available

3. **Colliders:**
   - Most assets already have colliders imported
   - If performance is issue, convert some far-away colliders to simple box/sphere

4. **Shadows:**
   - Keep shadows OFF for background mountains (too far)
   - Shadows ON for midground and foreground
   - Adjust shadow distance in Lighting settings if FPS drops

5. **Batch Count:**
   - Combine static meshes in midground if possible (Scene → Bake)
   - Keep character/NPC separate (needs to move/animate)

---

## Quick Scene Build Checklist

- [ ] Project Settings → Layers: Created Background/Midground/Foreground/Effects
- [ ] Background: Sky sphere + 5 mountains + horizon plane
- [ ] Midground: 4-5 Mediterranean stalls assembled and positioned
- [ ] Foreground: Ground plane + 10-15 scattered rocks
- [ ] Camera: Positioned at (0, 1.5, -5) looking forward
- [ ] Lighting: Dusk directional light at 45°/315°/0°
- [ ] MarketSceneSetup: Component added to scene
- [ ] Played scene and confirmed: 3 depth zones visible, good atmosphere
- [ ] NPCs: Simple character placeholder in foreground for scale reference

---

## If You Get Stuck

**Problem:** Stalls look too small/far away
- **Solution:** Reduce Z-distance (move to Z=8 instead of Z=12) or increase scale to 1.5

**Problem:** Can't see mountains behind stalls
- **Solution:** Stalls too tall - reduce their Y-scale or move them closer (Z=8-10)

**Problem:** Too much clipping/weird overlaps
- **Solution:** Check layer assignments - mountains should be on "Background" layer only

**Problem:** Scene too dark/too bright
- **Solution:** Adjust light intensity (0.5-1.0) or ambient light values

**Problem:** FPS too low
- **Solution:** Reduce rock/stall count, or turn off shadows on background

---

## Inspiration Reference

The goal: Create a **market at dusk** that feels:
- **Alive but quiet** - Built structures, but no busy crowds
- **Weathered and organic** - Imperfect, worn stonework
- **Atmospheric** - Strong warm lighting creates mood
- **Layered** - Player can see depth: ground → stalls → mountains → sky

Think: **Tuscan marketplace at sunset** or **Greek island village dusk**

This is your stage for Malrik and Elenya's story. The setting should make their dialogue *feel* more impactful.
