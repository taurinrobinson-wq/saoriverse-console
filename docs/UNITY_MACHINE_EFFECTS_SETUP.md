# Unity Machine Animation Effects Setup Guide

This guide explains how to implement pulsing glow, shimmering, and wire sparking effects on your machines.

## Overview

Three C# scripts work together to create the visual effects:

1. **MachinePulseGlow.cs** - Smooth pulsing light and emission
2. **MachineShimmer.cs** - Flickering shimmer effect
3. **WireSparks.cs** - Sporadic sparks along wires

## Setup Instructions

### 1. Machine Glow Setup (MachinePulseGlow)

**Requirements:**

- The machine orb 3D model with a Renderer component
- A Light component (Point Light recommended)
- An emission-enabled material

**Steps:**

1. Select your machine orb GameObject
2. Add Component → Script → `MachinePulseGlow`
3. In the Inspector, configure:
   - **Glow Light**: Drag the Point Light from hierarchy
   - **Glow Material**: Assign the material with emission
   - **Min/Max Intensity**: 0.5 to 2.0 (adjust for brightness)
   - **Pulse Speed**: 2.0 (lower = slower pulse, higher = faster)
   - **Glow Color**: Set to cyan or your preferred color
   - **Min/Max Emission**: Controls material emission strength

**Material Setup:**

- Use Standard Shader with Emission enabled
- Set Emission color to a bright cyan or white
- Adjust Smoothness/Metallic for desired look

### 2. Machine Shimmer Setup (MachineShimmer)

**Requirements:**

- Machine orb with Renderer component
- One or more materials with emission enabled

**Steps:**

1. Select your machine orb GameObject
2. Add Component → Script → `MachineShimmer`
3. In the Inspector, configure:
   - **Shimmer Materials**: Set array size and add materials from your machine
   - **Shimmer Speed**: 2.0 (controls animation speed)
   - **Shimmer Intensity**: 0.3 (subtle variation, 0.0-1.0)
   - **Base Emission Value**: 1.0 (starting brightness)
   - **Enable Flicker**: Toggle for extra visual interest
   - **Flicker Chance**: 0.15 (probability each frame)
   - **Base Color**: Cyan
   - **Shimmer Color**: White or bright color

**Pro Tips:**

- Combine with MachinePulseGlow for layered effects
- Lower shimmer intensity for subtle effects, higher for dramatic
- Adjust flickerChance to control how often flickers occur

### 3. Wire Sparks Setup (WireSparks)

**Requirements:**

- A LineRenderer component representing the wires
- A Particle System prefab for spark effects
- Script attached to wire GameObject

**LineRenderer Setup:**

1. Create empty GameObject named "Wires"
2. Add Component → LineRenderer
3. Configure:
   - **Material**: Use particles/spark material or standard
   - **Width**: 0.1 to 0.2 (wire thickness)
   - **Positions**: Set number of positions connecting machines
   - Manually set positions in world space OR
   - Use script to connect two GameObjects dynamically

**Particle System Setup:**

1. Create a new Particle System for sparks
2. Configure settings:
   - **Start Lifetime**: 0.5 seconds
   - **Start Size**: 0.05 to 0.2
   - **Start Color**: Yellow-orange or white
   - **Emission Rate**: 20 particles/second
   - **Shape**: Sphere or Point
   - **Renderer**: Use material with glow/additive shader

3. Make it a prefab (drag to Assets folder)

**WireSparks Script Setup:**

1. Select wire GameObject
2. Add Component → Script → `WireSparks`
3. Configure:
   - **Wire Line Renderer**: Drag the LineRenderer
   - **Spark Particle Prefab**: Drag your spark particle system prefab
   - **Spark Count**: 2-4 (simultaneous active sparks)
   - **Spark Interval**: 0.5 (seconds between spark bursts)
   - **Spark Interval Randomness**: 0.3 (0-1, adds variation)
   - **Min/Max Position On Wire**: 0.1 to 0.9 (where on wire sparks occur)
   - **Position Randomness**: 0.1 (spread along wire)

## Advanced Customization

### Dynamic Spark Frequency

```csharp
// In your game manager or control script
WireSparks wireSparks = GetComponent<WireSparks>();

// Make sparks more frequent when machines are stressed
wireSparks.SetSparkFrequency(0.3f); // More frequent
wireSparks.SetSparkFrequency(1.0f); // Less frequent
```

### Pulse Speed Control

```csharp
MachinePulseGlow machineGlow = GetComponent<MachinePulseGlow>();

// Speed up pulse during critical moments
machineGlow.SetPulseSpeed(5f); // Faster
machineGlow.SetPulseSpeed(1f); // Slower
```

### Shimmer Intensity Control

```csharp
MachineShimmer machineShimmer = GetComponent<MachineShimmer>();

// Adjust shimmer intensity at runtime
machineShimmer.SetShimmerIntensity(0.5f); // More intense
machineShimmer.SetShimmerIntensity(0.1f); // Subtle
```

### Enable/Disable Effects

```csharp
// Disable sparks when machines power down
wireSparks.SetSparkingActive(false);

// Re-enable on restart
wireSparks.SetSparkingActive(true);
```

## Performance Optimization

- **Particle Count**: Limit spark particles to 20-50 per effect
- **Material Count**: Use material atlases to reduce draw calls
- **Light Count**: Limit to 4-8 real-time lights per machine
- **Update Rate**: Animations use Update() which is frame-dependent
  - For network multiplayer, consider moving to FixedUpdate

## Troubleshooting

| Issue | Solution |
| --- | --- |
| Sparks not appearing | Check LineRenderer has positions set; ensure ParticleSystem is valid |
| Glow not visible | Verify material has emission enabled; check light is set correctly |
| Too much shimmer | Reduce shimmerIntensity value (0.1-0.2 recommended) |
| Flicker too frequent | Lower flickerChance value (0.05-0.15 range) |
| Performance lag | Reduce particle count; check light count on scene |

## Asset Recommendations

- **Spark Material**: Use `Particles/Standard Unlit` shader with additive blend mode
- **Glow Material**: Use `Standard` shader with emission and high metallic value
- **Wire Material**: Use `Sprites/Default` or simple opaque shader
- **Colors**: Cyan (#00FFFF), Bright White (#FFFFFF), Electric Orange (#FF6B00)

## Example Scene Structure

```yaml
Scene/
├── Machine_Left
│   ├── Orb (Mesh)
│       ├── MachinePulseGlow.cs
│       ├── MachineShimmer.cs
│   └── Light (Point)
├── Machine_Right
│   ├── Orb (Mesh)
│       ├── MachinePulseGlow.cs
│       ├── MachineShimmer.cs
│   └── Light (Point)
└── Wires
    ├── LineRenderer (wire mesh)
    └── WireSparks.cs
```

## Next Steps

1. Assign scripts to GameObjects
2. Configure all required fields in Inspector
3. Play scene and tweak values until satisfied
4. Use prefabs for consistency across multiple machines
5. Create animation state machine for different "modes" (idle, active, critical)
