# Velhara Transport Ring - Setup Guide

This guide explains how to set up the transparent torus transport ring with cargo boxes for the Velhara concept visualization.

## Overview

The system consists of:
- **Central Tube**: A cylinder representing the main walkway where residents travel
- **Transport Torus**: A donut-shaped ring that rolls along the tube
- **Cargo Boxes**: Small containers arranged around the torus for transporting goods
- **Transparent Materials**: Both the torus and boxes use semi-transparent materials for visualization

---

## Setup Steps

### Step 1: Create the Central Tube

1. In your scene, create an empty GameObject named `VelharaTransportSystem`
2. Create a child cylinder:
   - Right-click in Hierarchy → 3D Object → Cylinder
   - Name it `CentralTube`
   - Scale it to your desired dimensions (e.g., Scale: X=1, Y=5, Z=1 for a tall tube)
   - Position at (0, 0, 0)

3. Create a new Material for the tube:
   - In Project, create a Material named `TubeMaterial`
   - Set Shader to `Standard` (or `Universal Render Pipeline/Lit` if using URP)
   - Adjust Alpha to ~0.3-0.5 for transparency
   - Enable `Alpha Blending` in the material's render settings
   - Assign to the CentralTube renderer

### Step 2: Create the Transport Torus

1. Create an empty GameObject as a child of `VelharaTransportSystem`:
   - Name it `TransportRing`
   - Position at (0, 0, 0)

2. Add components to TransportRing:
   - Add Component → Mesh Filter
   - Add Component → Mesh Renderer
   - Add Component → Box Collider (optional, for physics)

3. Attach the `TorusGenerator` script:
   - Select TransportRing
   - Drag `TorusGenerator.cs` onto it, or Add Component → TorusGenerator
   - In Inspector, adjust parameters:
     - **R** (Major Radius): ~2-3 (controls overall ring size)
     - **r** (Minor Radius): ~0.4-0.6 (controls tube thickness)
     - **Segments**: 32 (smoothness around the ring) - increase for smoother look
     - **Tubes**: 16 (smoothness of the tube profile) - increase for smoother look

4. Create a transparent material for the torus:
   - Create a Material named `TorusMaterial`
   - Set Shader to `Standard` or URP equivalent
   - Set Color alpha to ~0.4-0.6
   - Enable transparency/blending
   - Assign to TransportRing's Mesh Renderer

### Step 3: Add Cargo Boxes

1. Create another empty GameObject as a child of `TransportRing`:
   - Name it `CargoSystem`
   - Position at (0, 0, 0)

2. Attach the `TorusCargoBoxGenerator` script:
   - Select CargoSystem
   - Add Component → TorusCargoBoxGenerator
   - Configure in Inspector:
     - **Torus R**: Match the R value from TorusGenerator
     - **Torus R Minor**: Match the r value from TorusGenerator
     - **Box Count**: 24 (number of cargo containers)
     - **Box Size**: (0.3, 0.2, 0.3) or adjust to your preference
     - **Distance From Torus Center**: ~0.7 (how far boxes stick out)

3. Create a material for cargo boxes:
   - Create Material named `CargoBoxMaterial`
   - Set Color to something distinct (e.g., orange or cyan)
   - Set Alpha to ~0.6-0.7
   - Enable transparency
   - Assign to the **Box Material** field in TorusCargoBoxGenerator

4. Press Play - the boxes should generate around the torus

### Step 4: Add Rolling Animation (Optional)

1. Select `TransportRing` and Add Component → `TorusRollingAnimation`
2. Configure animation settings:
   - **Roll Speed**: 30-100 (degrees per second for rotation)
   - **Tube Height**: Match your tube height
   - **Scroll Speed**: 1-5 (units per second along tube)

3. Press Play to see the torus roll and move along the tube

---

## Material Setup for Transparency

### For Standard Render Pipeline:

1. Create a new Material
2. Set Shader: `Standard`
3. In the material:
   - Set **Albedo** color and reduce Alpha value (0-1, where 1 is opaque)
   - Enable **Transparency** by setting render mode
   - May need to adjust **Smoothness** and **Metallic** for visual effect

### For URP (Universal Render Pipeline):

1. Create a new Material
2. Set Shader: `Universal Render Pipeline/Lit`
3. Configure:
   - Set **Base Color** and adjust Alpha (A slider)
   - Set **Surface Type** to `Transparent`
   - Set **Blend Mode** to `Alpha`
   - Adjust **Smoothness** for desired finish

---

## Fine-Tuning

| Parameter | Effect | Recommended Range |
|-----------|--------|-------------------|
| R (Torus Major) | Ring diameter | 2-5 |
| r (Torus Minor) | Ring thickness | 0.3-1.0 |
| Segments | Ring smoothness | 24-64 |
| Tubes | Cross-section smoothness | 12-32 |
| Box Count | Cargo containers around ring | 12-32 |
| Box Size | Container dimensions | 0.2-0.5 per axis |
| Distance From Torus | How far boxes extend | 0.5-1.0 |
| Roll Speed | Animation rotation speed | 10-100 |
| Scroll Speed | Along-tube movement speed | 0.5-5 |

---

## Performance Optimization

- **Reduce segments/tubes** if performance is poor
- **Disable box colliders** if not needed for gameplay
- **Combine meshes** if you have many boxes (use Unity's mesh combine tools)
- **Use LOD (Level of Detail)** for the torus at distance

---

## Visual Tweaks

- **Emissive Materials**: Add glow to boxes to represent active transport (Emission color in material)
- **Multiple Rings**: Duplicate TransportRing and rotate/scale for nested rings
- **Lighting**: Use point lights near boxes for sci-fi aesthetic
- **Post-Processing**: Add bloom/glow effects for a more ethereal look
