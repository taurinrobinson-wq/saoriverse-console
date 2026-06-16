# CODESPACE IMPLEMENTATION PLAN — VELHARA WORLD SYSTEM

**Production-grade instruction set for integrating all 25+ assets into Velinor's world architecture**

**Status:** Authoritative Master Plan | **Updated:** 2026-06-16 | **Assets:** 25+ packages  
**Replaces:** Previous piecemeal integration approach  
**Target:** Complete biome system with seamless transitions

---

## Overview

This plan structures **all 25+ Unity Store assets** into a cohesive **6-biome world system** with:
- Full vegetation library (trees, plants, undergrowth, decay)
- All architectural kits (ruins, sci-fi, industrial, residential)
- Specialized cave/underground systems
- Biome-specific lighting, fog, audio
- Smooth transition mechanics
- URP performance optimization

---

## SECTION 1 — CREATE THE WORLD FOLDER ARCHITECTURE

Create the following folder structure under `Assets/World/`:

```
Assets/World/
├── RuralVelhara/
│   ├── Prefabs/
│   ├── Materials/
│   ├── Scenes/
│   ├── Vegetation/
│   ├── Terrain/
│   └── Props/
├── RuinedVelhara/
│   ├── Prefabs/
│   ├── Materials/
│   ├── Scenes/
│   ├── Architecture/
│   ├── Vegetation/
│   ├── Terrain/
│   └── Props/
├── DeepPlaces/
│   ├── Prefabs/
│   ├── Materials/
│   ├── Scenes/
│   ├── Caves/
│   ├── Bioluminescence/
│   ├── Vegetation/
│   └── Props/
├── Corelink/
│   ├── Prefabs/
│   ├── Materials/
│   ├── Scenes/
│   ├── Architecture/
│   ├── FX/
│   └── Props/
├── DesertVelhara/
│   ├── Prefabs/
│   ├── Materials/
│   ├── Scenes/
│   ├── Vegetation/
│   ├── Terrain/
│   └── Props/
└── SwampVelhara/
    ├── Prefabs/
    ├── Materials/
    ├── Scenes/
    ├── Vegetation/
    ├── Terrain/
    └── Props/
```

---

## SECTION 2 — IMPORT & NORMALIZE ALL ASSETS

For **every** Unity package in [VELINOR_ASSET_INDEX.md](VELINOR_ASSET_INDEX.md):

### Step 1: Import Raw Package
```
1. Open Velinor-Unity project
2. Assets → Import Package → Custom Package
3. Navigate to D:\Velinor\Asset Store-5.x\[Creator]/[Category]/[Package]
4. Select ALL components
5. Import into: Assets/_ImportedRaw/[PackageName]/
```

### Step 2: Move & Organize by Type
After import, move assets to correct biome based on type:

| Asset Type | Destination |
|-----------|-------------|
| Trees, deciduous plants | RuralVelhara/Vegetation/ |
| Undergrowth, ferns, low plants | RuralVelhara/Vegetation/ + RuinedVelhara/Vegetation/ |
| Dead/decaying trees, cracked trunks | RuinedVelhara/Vegetation/Decay/ |
| Tree stumps, logs | RuralVelhara/Props/ + RuinedVelhara/Props/ |
| Rock formations, cliffs, boulders | RuralVelhara/Terrain/ + RuinedVelhara/Terrain/ |
| Mediterranean ruins columns, stonework | RuinedVelhara/Architecture/ |
| Lava tube structures | DeepPlaces/Caves/ |
| Sci-fi modular pieces | Corelink/Architecture/ |
| Industrial metallic structures | Corelink/Architecture/ |
| Succulents, desert plants | DesertVelhara/Vegetation/ |
| Country house interior/exterior | RuralVelhara/Props/Interiors/ |
| Car garage/workshop | RuralVelhara/Props/Industrial/ |

### Step 3: Rename All Assets
Use consistent naming convention: `[Biome]_[Category]_[OriginalName]`

**Examples:**
```
Rural_Tree_OakStandard01
Rural_Tree_OakStandard02
Ruined_Architecture_ColumnBrokenA
Ruined_Architecture_ColumnBrokenB
Ruined_Decay_TreeTrunkCracked01
Ruined_Terrain_RockCliff02
Deep_Cave_LavaWallSmooth01
Deep_Cave_CrystalFormation01
Corelink_Architecture_PanelWall01
Corelink_Architecture_DoorFrame01
Desert_Vegetation_SuculentCluster01
Rural_Prop_StumpDecay01
Rural_Prop_CountryHouseBeam01
```

### Step 4: Convert All Materials to URP
For each material in imported assets:
```
1. Right-click material
2. Check shader: must start with "Universal Render Pipeline/"
3. If legacy shader: reassign to equivalent URP shader
4. Verify in Scene view: material displays correctly
```

**Common Conversions:**
- Standard → Universal Render Pipeline/Lit
- Standard (Specular) → Universal Render Pipeline/Lit (with Specular map)
- Particles/Standard → Universal Render Pipeline/Particles/Lit

### Step 5: Delete Temporary Folder
```
Delete: Assets/_ImportedRaw/
```

---

## SECTION 3 — CREATE BIOME PREFAB LIBRARIES

For each biome folder, create a `ScriptableObject` reference library:

### Create ScriptableObject Class

**Assets/Scripts/Systems/BiomePrefabLibrary.cs**
```csharp
using UnityEngine;
using System.Collections.Generic;

[CreateAssetMenu(fileName = "BiomePrefabLibrary", menuName = "Velinor/Biome/Prefab Library")]
public class BiomePrefabLibrary : ScriptableObject
{
    [System.Serializable]
    public class PrefabCategory
    {
        public string categoryName;
        public List<GameObject> prefabs = new List<GameObject>();
    }

    public string biomeName;
    public List<PrefabCategory> categories = new List<PrefabCategory>();

    public GameObject GetRandomPrefab(string categoryName)
    {
        var category = categories.Find(c => c.categoryName == categoryName);
        if (category != null && category.prefabs.Count > 0)
        {
            return category.prefabs[Random.Range(0, category.prefabs.Count)];
        }
        return null;
    }
}
```

### Create Asset Files

Create one for each biome:

```
Assets/World/RuralVelhara/RuralBiomePrefabLibrary.asset
Assets/World/RuinedVelhara/RuinedBiomePrefabLibrary.asset
Assets/World/DeepPlaces/DeepBiomePrefabLibrary.asset
Assets/World/Corelink/CorelinkBiomePrefabLibrary.asset
Assets/World/DesertVelhara/DesertBiomePrefabLibrary.asset
Assets/World/SwampVelhara/SwampBiomePrefabLibrary.asset
```

### Populate Each Library

For **RuralBiomePrefabLibrary.asset**, add categories:

1. **Trees**
   - Rural_Tree_OakStandard01
   - Rural_Tree_OakStandard02
   - URP_Tree_Pine01
   - URP_Tree_Birch01

2. **Vegetation**
   - Skog_Plant_Fern01
   - Skog_Plant_Mushroom01
   - Essential_Plant_Grass01

3. **Terrain**
   - Kyle_Rock_Boulder01
   - Kyle_Rock_Cliff02

4. **Props**
   - Rural_Prop_Stump01
   - Rural_Prop_CountryHouseBeam01

---

## SECTION 4 — CREATE TEMPLATE SCENES FOR ALL BIOMES

Create one template scene per biome:

```
Assets/World/RuralVelhara/Scenes/Rural_Template.unity
Assets/World/RuinedVelhara/Scenes/Ruined_Template.unity
Assets/World/DeepPlaces/Scenes/Deep_Template.unity
Assets/World/Corelink/Scenes/Corelink_Template.unity
Assets/World/DesertVelhara/Scenes/Desert_Template.unity
Assets/World/SwampVelhara/Scenes/Swamp_Template.unity
```

### Each Template Scene Must Include:

1. **Terrain**
   - Plane with scale (50, 1, 50)
   - Material: Biome-specific ground shader

2. **Lighting**
   - Directional Light (angle adjusted per biome)
   - Ambient light color (biome-specific)

3. **Environment**
   - Skybox (biome-specific)
   - Post-processing Volume (empty, to be filled by BiomeManager)
   - Fog settings (biome-specific)

4. **Player**
   - Player spawn point (empty GameObject at center)

5. **Manager**
   - BiomeManager instance
   - Set to apply settings on play

### Biome-Specific Lighting Presets

**RuralVelhara:**
- Directional Light rotation: (50, -30, 0)
- Intensity: 1.2
- Ambient light: (0.8, 0.8, 0.7)
- Fog: ON, density 0.01, color (0.7, 0.7, 0.6)

**RuinedVelhara:**
- Directional Light rotation: (45, -60, 0)
- Intensity: 0.9
- Ambient light: (0.6, 0.6, 0.65)
- Fog: ON, density 0.015, color (0.5, 0.5, 0.55)

**DeepPlaces:**
- Directional Light rotation: (30, 0, 0)
- Intensity: 0.4
- Ambient light: (0.2, 0.3, 0.4) (blue-shifted, cave-like)
- Fog: ON, density 0.05, color (0.1, 0.15, 0.25) (deep blue)

**Corelink:**
- Directional Light rotation: (45, -45, 0)
- Intensity: 1.5 (bright tech facility)
- Ambient light: (0.9, 0.95, 1.0) (cool white)
- Fog: ON, density 0.005, color (0.8, 0.85, 1.0) (cool white fog)

**DesertVelhara:**
- Directional Light rotation: (70, -30, 0) (high, hot sun)
- Intensity: 1.3
- Ambient light: (1.0, 0.95, 0.7) (warm yellow)
- Fog: ON, density 0.008, color (0.95, 0.9, 0.7) (dusty yellow)

**SwampVelhara:**
- Directional Light rotation: (35, -45, 0)
- Intensity: 0.7
- Ambient light: (0.5, 0.6, 0.5) (greenish)
- Fog: ON, density 0.03, color (0.4, 0.5, 0.3) (murky green)

---

## SECTION 5 — IMPLEMENT BIOME MANAGERS

### Create Base BiomeManager

**Assets/Scripts/Systems/BiomeManager.cs**

```csharp
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public class BiomeManager : MonoBehaviour
{
    [SerializeField] protected string biomeName;
    [SerializeField] protected Color ambientLightColor = Color.white;
    [SerializeField] protected Color fogColor = Color.white;
    [SerializeField] protected float fogDensity = 0.01f;
    [SerializeField] protected Volume postProcessingVolume;
    [SerializeField] protected AudioClip ambientAudio;
    protected AudioSource ambientAudioSource;

    protected virtual void Start()
    {
        ApplyBiomeSettings();
    }

    public virtual void ApplyBiomeSettings()
    {
        // Lighting
        RenderSettings.ambientLight = ambientLightColor;
        
        // Fog
        RenderSettings.fog = true;
        RenderSettings.fogColor = fogColor;
        RenderSettings.fogDensity = fogDensity;

        // Post-processing (if assigned)
        if (postProcessingVolume != null)
        {
            postProcessingVolume.enabled = true;
        }

        // Audio
        if (ambientAudio != null && ambientAudioSource == null)
        {
            ambientAudioSource = gameObject.AddComponent<AudioSource>();
            ambientAudioSource.clip = ambientAudio;
            ambientAudioSource.loop = true;
            ambientAudioSource.volume = 0.3f;
            ambientAudioSource.Play();
        }

        Debug.Log($"[BiomeManager] Applied {biomeName} settings");
    }

    public virtual void OnBiomeExit()
    {
        if (ambientAudioSource != null)
        {
            ambientAudioSource.Stop();
        }
    }
}
```

### Create Biome-Specific Managers

**Assets/Scripts/Systems/RuralBiomeManager.cs**
```csharp
using UnityEngine;

public class RuralBiomeManager : BiomeManager
{
    private void Awake()
    {
        biomeName = "Rural Velhara";
        ambientLightColor = new Color(0.8f, 0.8f, 0.7f);
        fogColor = new Color(0.7f, 0.7f, 0.6f);
        fogDensity = 0.01f;
    }
}
```

**Assets/Scripts/Systems/RuinedBiomeManager.cs**
```csharp
using UnityEngine;

public class RuinedBiomeManager : BiomeManager
{
    private void Awake()
    {
        biomeName = "Ruined Velhara";
        ambientLightColor = new Color(0.6f, 0.6f, 0.65f);
        fogColor = new Color(0.5f, 0.5f, 0.55f);
        fogDensity = 0.015f;
    }
}
```

**Assets/Scripts/Systems/DeepBiomeManager.cs**
```csharp
using UnityEngine;

public class DeepBiomeManager : BiomeManager
{
    private void Awake()
    {
        biomeName = "Deep Places";
        ambientLightColor = new Color(0.2f, 0.3f, 0.4f);
        fogColor = new Color(0.1f, 0.15f, 0.25f);
        fogDensity = 0.05f;
    }
}
```

**Assets/Scripts/Systems/CorelinkBiomeManager.cs**
```csharp
using UnityEngine;

public class CorelinkBiomeManager : BiomeManager
{
    private void Awake()
    {
        biomeName = "Corelink";
        ambientLightColor = new Color(0.9f, 0.95f, 1.0f);
        fogColor = new Color(0.8f, 0.85f, 1.0f);
        fogDensity = 0.005f;
    }
}
```

**Assets/Scripts/Systems/DesertBiomeManager.cs**
```csharp
using UnityEngine;

public class DesertBiomeManager : BiomeManager
{
    private void Awake()
    {
        biomeName = "Desert Velhara";
        ambientLightColor = new Color(1.0f, 0.95f, 0.7f);
        fogColor = new Color(0.95f, 0.9f, 0.7f);
        fogDensity = 0.008f;
    }
}
```

**Assets/Scripts/Systems/SwampBiomeManager.cs**
```csharp
using UnityEngine;

public class SwampBiomeManager : BiomeManager
{
    private void Awake()
    {
        biomeName = "Swamp Velhara";
        ambientLightColor = new Color(0.5f, 0.6f, 0.5f);
        fogColor = new Color(0.4f, 0.5f, 0.3f);
        fogDensity = 0.03f;
    }
}
```

---

## SECTION 6 — CREATE BIOME TRANSITION SYSTEM

### Create Transition Trigger

**Assets/Scripts/Systems/BiomeTransitionTrigger.cs**

```csharp
using UnityEngine;
using System.Collections;

public class BiomeTransitionTrigger : MonoBehaviour
{
    [SerializeField] private BiomeManager targetBiomeManager;
    [SerializeField] private float transitionDuration = 2f;
    private BiomeManager currentBiomeManager;
    private bool isTransitioning = false;

    private void Start()
    {
        currentBiomeManager = FindObjectOfType<BiomeManager>();
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player") && !isTransitioning)
        {
            StartCoroutine(TransitionToBiome());
        }
    }

    private IEnumerator TransitionToBiome()
    {
        isTransitioning = true;
        float elapsedTime = 0f;

        // Fade out current biome audio
        if (currentBiomeManager != null)
        {
            currentBiomeManager.OnBiomeExit();
        }

        // Lerp to new biome settings
        while (elapsedTime < transitionDuration)
        {
            elapsedTime += Time.deltaTime;
            float t = elapsedTime / transitionDuration;

            // Lerp fog
            RenderSettings.fogDensity = Mathf.Lerp(
                RenderSettings.fogDensity,
                targetBiomeManager.GetComponent<BiomeManager>().fogDensity,
                t
            );

            yield return null;
        }

        // Apply final biome settings
        targetBiomeManager.ApplyBiomeSettings();
        currentBiomeManager = targetBiomeManager;
        isTransitioning = false;
    }
}
```

### Usage

1. Create an empty GameObject with a SphereCollider (isTrigger: true) at biome boundary
2. Add `BiomeTransitionTrigger` script
3. Drag the target biome's BiomeManager into the inspector
4. Tag player with "Player"

---

## SECTION 7 — VEGETATION INTEGRATION RULES

Integrate vegetation following these priorities:

| Vegetation Pack | Primary Use | Backup Use |
|-----------------|------------|-----------|
| **URP Tree Models** | Main forest trees (default performance) | All dense vegetation |
| **Tree Collection 2017** | Background distant forests | Mid-range tree variation |
| **Free English Oak Set** | Hero/scenic trees (focal points) | Character landmark trees |
| **Skog Temperate** | Forest floor (ferns, undergrowth) | Lush biome detail |
| **Dry Trees** | RuinedVelhara decay areas | Post-apocalyptic zones |
| **Cracked Tree Trunk** | RuinedVelhara storytelling | Environmental decay |
| **Succulents Package** | DesertVelhara vegetation | Interior decoration |
| **Scan Stump Vol2** | Props (forest floor evidence) | RuralVelhara detail |
| **Dream Tree 2 HDRP** | **DO NOT USE** | Not compatible with URP |

### Implementation Pattern

```csharp
// Example: RuralVelhara forest setup
void PopulateForest(BiomePrefabLibrary library)
{
    // Background trees (distance)
    for (int i = 0; i < 50; i++)
    {
        GameObject tree = Instantiate(
            library.GetRandomPrefab("Trees"),
            GetRandomForestPosition(),
            Quaternion.identity
        );
        tree.transform.localScale = Vector3.one * 0.8f; // distance scale-down
    }

    // Foreground trees (hero trees)
    for (int i = 0; i < 5; i++)
    {
        GameObject tree = Instantiate(
            library.GetRandomPrefab("HeroTrees"), // Free English Oak Set
            GetRandomProminentPosition(),
            Quaternion.identity
        );
        tree.transform.localScale = Vector3.one * 1.2f; // hero emphasis
    }

    // Forest floor
    for (int i = 0; i < 100; i++)
    {
        Instantiate(
            library.GetRandomPrefab("Vegetation"),
            GetRandomForestFloorPosition(),
            Quaternion.identity
        );
    }
}
```

---

## SECTION 8 — ENVIRONMENT PACK INTEGRATION RULES

Integrate environment packs with explicit biome assignments:

```
Mediterranean Ruins → RuinedVelhara/Architecture/
  Purpose: Ancient temple silhouettes, weathered columns
  Rules: Use only architectural pieces, limit poly count
  
Lava Tube Pack → DeepPlaces/Caves/
  Purpose: Underground sanctuary, mystical geology
  Rules: Use in deep chamber sequences, apply bioluminescent shaders
  
Country House Pack → RuralVelhara/Props/Interiors/
  Purpose: Domestic interior spaces (if needed)
  Rules: Extract only furniture/structural elements
  
Metallic Building Kit → Corelink/Architecture/
  Purpose: Industrial/sci-fi facility interiors
  Rules: Use for high-tech aesthetic, combine with sci-fi pack
  
Modular Sci-Fi Pack (146 objects) → Corelink/Architecture/
  Purpose: Primary sci-fi facility construction
  Rules: Build modular room sets, use LOD variants, GPU instance
  
Car Garage/Workshop → RuralVelhara/Props/Industrial/
  Purpose: Environmental detail (if rural has technical aspects)
  Rules: Extract relevant mechanical props
  
Kyle's Rock Pack → RuralVelhara/Terrain/ + RuinedVelhara/Terrain/
  Purpose: Natural rock formations, cliffs
  Rules: Use as terrain detail, scatter across biomes
```

---

## SECTION 9 — SPECIALIZED SYSTEMS

Do **NOT** import these; use as reference only:

```
HDRP Environment Template
  → DO NOT IMPORT (URP project incompatible)
  → Reference for lighting concepts only

Surface Gradient Samples
  → Import into: Assets/Systems/Shaders/
  → Reference for material creation
  → Study for normal mapping techniques

Time Ghost Environment
  → DO NOT IMPORT (reference scene only)
  → Study complete scene composition
  → Extract lighting philosophy
```

---

## SECTION 10 — PERFORMANCE RULES

### Memory Budget

- Meshes: 200MB target
- Textures: 300MB target
- Materials: 50MB target

### Optimization Rules

```
1. USE URP Tree Models for dense forests
   - Standard LOD at distance
   - Cheaper shader cost
   
2. USE low-poly sci-fi kit for Corelink
   - Modular Sci-Fi Pack is already low-poly
   - Good shader optimization
   
3. LIMIT Mediterranean Ruins to silhouette pieces
   - Use only architectural columns/arches
   - Delete internal geometry
   
4. USE LOD Groups on all vegetation
   - High: 0-20m
   - Medium: 20-50m
   - Low: 50-100m
   - Culled: 100m+

5. ENABLE GPU Instancing on all materials
   - Right-click material → Enable GPU Instancing
   - Reduces draw calls

6. BATCH trees and rocks
   - Mark as "Static" in inspector
   - Enable GPU Instancing
   - Use same material variants

7. CULL distant foliage
   - Disable rendering beyond 80m
   - Use LOD0 only in camera range
```

### Example Performance Checklist

```csharp
void OptimizeScene()
{
    // Disable distant objects
    var allTrees = FindObjectsOfType<TreeRenderer>();
    foreach (var tree in allTrees)
    {
        var dist = Vector3.Distance(tree.transform.position, Camera.main.transform.position);
        tree.gameObject.SetActive(dist < 100f);
    }

    // Enable GPU instancing on all materials
    var allRenderers = FindObjectsOfType<Renderer>();
    foreach (var renderer in allRenderers)
    {
        foreach (var material in renderer.materials)
        {
            material.enableInstancing = true;
        }
    }
}
```

---

## SECTION 11 — SUCCESS METRICS

After each biome is complete, verify:

```
✅ All assets appear in Project folder
✅ All assets named per convention: [Biome]_[Category]_[Name]
✅ All materials converted to URP
✅ All materials GPU Instancing enabled
✅ BiomeManager script compiles
✅ Template scene loads without errors
✅ Post-processing volume renders correctly
✅ Biome transition trigger works smoothly
✅ FPS > 60 in play mode (measure in editor)
✅ No shader compilation errors in console
✅ All vegetation LODs render correctly
✅ Asset aesthetic aligns with biome tone
```

### Testing Script

**Assets/Scripts/Editor/BiomeValidation.cs**

```csharp
using UnityEditor;
using UnityEngine;

public class BiomeValidation : EditorWindow
{
    [MenuItem("Velinor/Validation/Check All Biomes")]
    public static void ValidateAllBiomes()
    {
        Debug.Log("=== BIOME VALIDATION ===");
        
        var biomeManagers = FindObjectsOfType<BiomeManager>();
        Debug.Log($"Found {biomeManagers.Length} biome managers");
        
        foreach (var manager in biomeManagers)
        {
            Debug.Log($"✓ {manager.GetComponent<BiomeManager>().GetType().Name}");
        }

        var materials = Resources.LoadAll<Material>("Materials");
        int gpuInstancedCount = 0;
        foreach (var mat in materials)
        {
            if (mat.enableInstancing)
                gpuInstancedCount++;
        }
        Debug.Log($"GPU Instancing enabled: {gpuInstancedCount}/{materials.Length} materials");
    }
}
```

---

## EXECUTION CHECKLIST

```
WEEK 1 — Setup & Import
[ ] Create folder architecture (Section 1)
[ ] Import all 25+ packages (Section 2, Step 1)
[ ] Organize by biome (Section 2, Step 2)
[ ] Rename all assets (Section 2, Step 3)
[ ] Convert all materials to URP (Section 2, Step 4)
[ ] Delete _ImportedRaw folder (Section 2, Step 5)

WEEK 2 — Libraries & Scenes
[ ] Create BiomePrefabLibrary.cs (Section 3)
[ ] Create .asset files for each biome (Section 3)
[ ] Populate each library (Section 3)
[ ] Create template scenes (Section 4)
[ ] Set biome-specific lighting (Section 4)

WEEK 3 — Managers & Transitions
[ ] Create BiomeManager.cs (Section 5)
[ ] Create all biome-specific managers (Section 5)
[ ] Create BiomeTransitionTrigger.cs (Section 6)
[ ] Test all biome transitions

WEEK 4 — Vegetation & Environment
[ ] Populate vegetation per rules (Section 7)
[ ] Integrate environment packs (Section 8)
[ ] Apply performance optimizations (Section 10)
[ ] Run validation script (Section 11)

WEEK 5 — Testing & Polish
[ ] Test FPS in all biomes (>60 target)
[ ] Verify all transitions work smoothly
[ ] Check all asset names follow convention
[ ] Verify all materials GPU Instancing enabled
[ ] Final aesthetic pass
```

---

## DEPENDENCIES & VERSIONS

- **Unity:** 6.4
- **Render Pipeline:** URP
- **Physics:** Enabled
- **JSON:** Enabled
- **All assets:** From D:\Velinor\Asset Store-5.x\

---

## REFERENCE DOCUMENTS

- [VELINOR_ASSET_INDEX.md](VELINOR_ASSET_INDEX.md) — Complete asset catalog
- [Velinor Architecture Docs](../Velinor-Unity/) — Project structure
- [Phase 1 Checklist](../Velinor-Unity/PHASE_1_CHECKLIST.md) — Feature milestones

---

**Maintained by:** Velinor Development Team  
**Last Updated:** 2026-06-16  
**Status:** Production-grade, ready for implementation  
**Authorization:** Approved for immediate Codespace execution
