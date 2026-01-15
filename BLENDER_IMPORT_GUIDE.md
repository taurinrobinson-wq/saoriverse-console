# Blender 4.2 Velinorian Structures Import Guide

## Quick Start

### Option 1: Run Python Script in Blender (Recommended)
1. **Open Blender 4.2.16 LTS**
2. **Switch to Scripting workspace** (top-right dropdown)
3. **Text > Open Text Block** → select `tools/blender_import_velinorian.py`
4. **Run Script** (Alt+P) or click the Play button

This will:
- Create a "Velinorian_Settlement" collection
- Import all 18 MGAIA structures as merged geometry
- Apply Velinorian materials (brick, wood, glass, roof, moss)
- Frame all objects in the 3D viewport

### Option 2: Import glTF Files
1. **File > Import > glTF 2.0 (.glb/.gltf)**
2. Navigate to `velinor/assets/`
3. Select any `*_velinorian.glb` file (e.g., `brickhouse-entrance_velinorian.glb`)
4. Import and scale as needed

### Option 3: Command Line
```bash
blender --python tools/blender_import_velinorian.py
```

---

## Generated Assets

**Location:** `velinor/assets/`

### JSON Structure Files (18 total)
- `structures/*.json` — block-by-block geometry and Minecraft block types
- Each has 847–1210 voxel blocks organized by position (x, y, z)

### 3D Export Formats

#### OBJ + MTL (Universal, no materials preserved)
- `brickhouse-entrance_velinorian.obj`
- `brickhouse-entrance_velinorian.mtl`
- Open in any 3D software (Blender, Maya, Unity, Unreal, etc.)

#### glTF 2.0 Binary (Modern, optimized for real-time)
- `brickhouse-entrance_velinorian.glb`
- Recommended for Blender, game engines, web viewers
- Single file; includes mesh geometry

---

## Velinorian Material Aesthetic

The Python scripts apply a unified color palette:

| Material | RGB | Roughness | Use Case |
|----------|-----|-----------|----------|
| **Brick** | (180, 100, 60) | 0.8 | Walls, facades |
| **Dark Wood** | (60, 40, 20) | 0.6 | Beams, doors, frames |
| **Glass** | (100, 150, 180) | 0.05 | Windows |
| **Roof** | (51, 51, 51) | 0.95 | Roofing |
| **Moss** | (100, 120, 100) | 0.95 | Overgrown accent |

---

## Customize Further in Blender

### Edit Materials
1. **Shading workspace**
2. Select an object (e.g., `brick_merged`)
3. **Material Properties** → Adjust color, roughness, metallic, subsurface
4. Add textures (Principled BSDF nodes)

### Add Details
- **Modifiers** → Add displacement, normal maps for weathering
- **Geometry Nodes** → Procedural moss, vines, cracks
- **Sculpting** → Hand-craft decay, battle damage

### Render & Export
- **Render Engine:** Cycles (realistic) or Eevee (real-time)
- **File > Export As** → glTF, FBX, Alembic, USD, etc.

---

## Troubleshooting

**Q: Materials not appearing?**
- Ensure **Viewport Shading** is set to **Material Preview** (Z key → Material Preview)
- Or switch to **Rendered** view (Z → Rendered)

**Q: Objects not visible?**
- Check **Outliner** (right panel) — ensure collections are expanded and eye icons visible
- Frame all objects with **Home** key or Numpad . (period)

**Q: Import slow?**
- If importing all 18 structures at once, consider importing one at a time
- Reduce viewport shading quality (**Preferences > Viewport > VRAM Budget**)

**Q: How do I merge all structures into one?**
- Select all objects (A key)
- **Object > Join** (Ctrl+J)
- Or use **Modifiers > Boolean** for destructive merges

---

## Next Steps

- **Physics/Simulation:** Add gravity, wind, destruction
- **Animation:** Rig damage states, collapse sequences
- **Shaders:** Create weather effects (rain, moss growth over time)
- **Integration:** Export to your game engine (Unreal, Unity, custom engine)
