# Unity Cave Machines Scene Setup Guide

Complete setup instructions for creating the machine cave scene with visual effects.

## Overview

This guide walks you through setting up a Unity scene featuring:

- Glowing cyan cave machines with visual effects
- Background image of the cave environment
- Connected wires with sparking effects
- Proper lighting and atmosphere

## Quick Setup (Automated)

1. **Add the Scene Setup Script**
   - Create an empty GameObject in your scene
   - Add the `MachinesCaveSceneSetup` component to it
   - Assign the background image to the `backgroundImage` field
   - In the Inspector, click "Setup Scene" to auto-configure everything

2. **Assign Machine Prefabs** (if using prefabs)
   - Drag your machine prefabs to `machineLeftPrefab` and `machineRightPrefab`
   - Adjust positions in the Inspector as needed

## Manual Setup Steps

### Step 1: Import Background Image

1. **Save image to project:**
   - Place the cave image in `Assets/Resources/` or `Assets/Textures/`
   - Name it something like `cave_machines_bg.png`

2. **Import settings:**
   - Select image in project
   - Inspector → Texture Type: `Default`
   - Enable `Read/Write Enabled`
   - Compression: `High Quality` or `Normal`
   - Click Apply

### Step 2: Create Background

#### Option A: Canvas Background (Recommended for 2D/UI)

1. Right-click in Hierarchy → UI → Panel
2. Rename to "BackgroundCanvas"
3. On Canvas component:
   - Render Mode: `Screen Space - Camera`
   - Assign Main Camera to the Camera field
4. Right-click on Canvas → UI → Image
5. Rename to "BackgroundImage"
6. On Image component:
   - Source Image: Drag your imported image
   - Raycast Target: `Unchecked` (so it doesn't block clicks)
7. Select Image and stretch it full screen:
   - Right-click → `Stretch` preset
   - Set to all corners (full screen)
8. Move Image to first child (send backward)

#### Option B: Quad Background (3D, recommended for 3D scenes)

1. GameObject → 3D Object → Quad
2. Rename to "BackgroundQuad"
3. Position: Z = 100 (far back)
4. Scale: X = 10, Y = 8 (adjust for aspect ratio)
5. Create Material:
   - Right-click in Assets → Material
   - Name it "BackgroundMaterial"
   - Shader: `Standard`
   - Drag image to Albedo
   - Set Smoothness to 0
6. Drag material onto Quad

### Step 3: Set Up Lighting

1. **Ambient Light:**
   - Window → Rendering → Lighting → Environment
   - Ambient Color: Dark cyan/teal `(51, 77, 89)` or `#334d59`
   - Ambient Intensity: 0.5

2. **Main Directional Light:**
   - Create directional light from cave opening
   - Rotation: X=45, Y=-30, Z=0
   - Intensity: 0.4-0.6
   - Color: White

### Step 4: Create Machines

Create two machine orbs (cylinders with glow effect):

**Machine Left:**

1. GameObject → 3D Object → Cylinder
2. Name: "Machine_Left"
3. Position: (-3, 0, 0)
4. Scale: (1.5, 2, 1.5)
5. Create glowing material:
   - Right-click → Material → "MachineGlowMaterial"
   - Shader: `Standard`
   - Albedo: Cyan `(0, 255, 255)`
   - Metallic: 0.8
   - Smoothness: 0.8
   - Emission: Enable
   - Emission Color: Bright Cyan
   - Assign to cylinder
6. Add Point Light as child:
   - Color: Cyan
   - Intensity: 2
   - Range: 10
   - Position: (0, 0.5, 0)
7. Add Components:
   - `MachinePulseGlow.cs`
   - `MachineShimmer.cs`
8. Configure in Inspector:
   - GlowLight: Assign the Point Light
   - GlowMaterial: Assign MachineGlowMaterial
   - Shimmer Materials: Size 1, add MachineGlowMaterial

**Machine Right:**

- Duplicate Machine_Left
- Rename to "Machine_Right"
- Position: (3, 0, 0)

### Step 5: Set Up Wires

1. Create empty GameObject: "Wires"
2. Add LineRenderer component:
   - Material: Create new or use particles material
   - Start Width: 0.1
   - End Width: 0.1
   - Position Count: 4
3. Set positions:
   - Pos 0: (-3, 2, 0)
   - Pos 1: (-3, 3, 3)
   - Pos 2: (3, 3, 3)
   - Pos 3: (3, 2, 0)
4. Add `WireSparks.cs` component:
   - Wire Line Renderer: Assign the LineRenderer
   - Spark Particle Prefab: Create spark particle system (see below)
   - Spark Count: 2-3
   - Spark Interval: 0.5

### Step 6: Create Spark Particle System

1. GameObject → Effects → Particle System
2. Rename: "SparkPrefab"
3. Configure in Inspector:
   - Duration: 0.5 (or your preference)
   - Looping: Disabled
   - Particle System → Start Lifetime: 0.5
   - Start Size: 0.1
   - Start Color: Yellow-orange
   - Emission:
     - Rate over time: 20
     - Rate over distance: 0
4. Add Renderer:
   - Material: Create particles/spark material
   - Shader: `Particles/Standard Unlit`
   - Blend Mode: Additive
5. Drag to Assets folder to create prefab
6. Delete from scene

### Step 7: Finalize Scene

1. **Camera Setup:**
   - Main Camera position: (0, 1.5, -8)
   - Field of View: 60
   - Background color: Black `(0, 0, 0)`

2. **Save Scene:**
   - File → Save Scene As
   - Name: "MachinesCave" or similar
   - Location: `Assets/Scenes/`

## Advanced Configuration

### Adjusting Visual Effects at Runtime

```csharp
// Increase pulse speed when machines are stressed
MachinePulseGlow glow = machineLeft.GetComponent<MachinePulseGlow>();
glow.SetPulseSpeed(5f);

// Increase shimmer intensity during alert state
MachineShimmer shimmer = machineLeft.GetComponent<MachineShimmer>();
shimmer.SetShimmerIntensity(0.5f);

// Make sparks more frequent
WireSparks sparks = wiresObject.GetComponent<WireSparks>();
sparks.SetSparkFrequency(0.3f);
```

### Performance Optimization

| Setting | Optimization |
| --- | --- |
| Real-time Lights | Limit to 4-8 per machine |
| Particles | Max 50 per spark system |
| Background Draw Calls | Use single quad or canvas |
| Shadow Quality | Low for machines, off for background |

### Customization Tips

- **Change Machine Color:** Modify glowColor in `MachinePulseGlow.cs` or Material Albedo
- **Adjust Glow Intensity:** Change minIntensity/maxIntensity values (range 0-3)
- **Faster Pulse:** Increase pulseSpeed (typical: 1-5)
- **Wire Spark Frequency:** Lower sparkInterval for more sparks
- **Lighting Mood:** Adjust ambient color and intensity for different atmospheres

## Troubleshooting

| Issue | Solution |
| --- | --- |
| Background not visible | Check quad is behind machines (Z distance), or canvas is set to Screen Space |
| Machines not glowing | Verify material has emission enabled, Light component assigned, script configured |
| Sparks not showing | Ensure LineRenderer has positions, ParticleSystem prefab is valid |
| Poor performance | Reduce particle count, limit lights, bake lighting, use LOD groups |
| Lighting too dark/bright | Adjust RenderSettings.ambientLight and Light component intensities |

## Scene Hierarchy Structure

```
Scene
├── Camera (Main Camera)
├── Lighting
│   └── DirectionalLight
├── BackgroundQuad or BackgroundCanvas
├── Machine_Left
│   ├── PointLight
│   ├── Renderer (with Material)
│   ├── MachinePulseGlow
│   └── MachineShimmer
├── Machine_Right
│   ├── PointLight
│   ├── Renderer (with Material)
│   ├── MachinePulseGlow
│   └── MachineShimmer
└── Wires
    ├── LineRenderer
    └── WireSparks
```

## Next Steps

1. Set up the scene using steps above or automated script
2. Tweak colors and intensities to match your vision
3. Test particle effects and light positions
4. Optimize performance based on your target platform
5. Create interaction systems (e.g., activating machines on click)
6. Save as prefab for reuse

## Assets Checklist

- [ ] Background image imported and configured
- [ ] Materials created (Glow, Background, Wire)
- [ ] Machines set up with lights and scripts
- [ ] Wires connecting machines
- [ ] Spark particle system created
- [ ] Lighting configured
- [ ] Scene saved and working
