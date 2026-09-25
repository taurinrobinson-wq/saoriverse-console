# Asset Material Rendering Crisis - Root Cause Analysis & Fix Guide

**Last Updated:** 2026-07-06  
**Status:** CRITICAL — 203+ broken materials across 7 asset packs

---

## ROOT CAUSE

### The Problem: Hidden/InternalErrorShader

The diagnostic report shows:
```
Project SRP active: False
[PROBLEM] Assets/Kyle's Rock Pack/.../rock_6_br.prefab 
          Shader: Hidden/InternalErrorShader
          Notes: broken shader, no _MainTex texture
```

**What this means:**
1. **Hidden/InternalErrorShader** = broken GUID reference to a shader that no longer exists
2. Asset packs were designed for **Universal Render Pipeline (URP)**
3. Project is using **Standard Render Pipeline (Built-in)**
4. When prefabs load, they try to find the URP shader GUID → GUID doesn't exist in this project → fallback to "Hidden/InternalErrorShader" (pink rendering)
5. Many materials also have **missing _MainTex texture** (texture GUID also broken)

### Why This Happened

1. **Asset packs provided HDRP/URP versions** but stored shader GUIDs in .meta files
2. **GUID mapping is baked into prefabs** when they're packaged
3. Importing into a Standard Pipeline project breaks those GUIDs
4. Manual fixes (replacing shader on material) don't propagate to already-serialized prefabs

---

## IMMEDIATE FIX WORKFLOW

### **Step 1: Rebuild GUID Database**
```
In Unity Editor:
Assets → Reimport All
```
Wait ~2-5 minutes. This forces Unity to:
- Re-scan all .meta files
- Rebuild internal GUID → asset mappings
- Reserialize prefab references

### **Step 2: Run Comprehensive Asset Repair**
```
In Unity Editor:
Tools → Asset Repair → [STEP 1] Comprehensive Repair All Asset Packs
```

**What this does:**
- Scans ALL prefabs in affected packs (Kyle's Rock Pack, Medieval Props, etc.)
- For each MeshRenderer with broken materials:
  - Detects `Hidden/InternalErrorShader` or null materials
  - Replaces shader with built-in `Standard` shader
  - Searches the pack folder for textures matching patterns:
    - `*diffuse*`, `*albedo*`, `*base*` → `_MainTex`
    - `*normal*`, `*bump*` → `_BumpMap`
    - `*metallic*`, `*metal*`, `*specular*` → `_MetallicGlossMap`
    - `*occlusion*`, `*ao*` → `_OcclusionMap`
  - If textures found, assigns them automatically
  - If not found, uses white texture fallback (prevents pink rendering)
  - Reassigns fixed materials to MeshRenderers
  - Saves prefabs

**Output:**
- Console log with `[BROKEN-SHADER-FIXED]`, `[NULL-MAT-FIXED]`, `[DEFAULT-MAT-FIXED]` entries
- File: `ComprehensiveRepairReport.txt` in project root
- Summary: Prefabs scanned, Materials fixed, Textures assigned

### **Step 3: Verify in Scene**
Place any repaired prefab in the scene. Should render with Standard shader + textures, no pink.

---

## FOR TENT MATERIALS (Medieval Props Pack 01)

**Special Case:** Tent prefabs have Standard-shader materials in URP variant folder.

### **Step 3A: Extract FBX Materials (Manual)**
1. Navigate: `Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Meshes/`
2. Find: `Tent.fbx`, `Rope.fbx`, `Cloth.fbx`, `Wood.fbx` (or similar FBX names)
3. Select each FBX in Inspector
4. Click: **Extract Materials** button
5. Choose destination: Same folder or `Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Materials/`

### **Step 3B: Convert Extracted Tent Materials (After Comprehensive Repair)
```
In Unity Editor:
Tools → Diagnostics → Convert Tent Materials to URP
```

**What this does:**
- Finds extracted tent materials (Standard shader)
- Converts to `Universal Render Pipeline/Lit` (if URP active)
- Remaps texture properties:
  - `_MainTex` → `_BaseMap`
  - `_BumpMap` → `_BumpMap` (no change)
  - `_MetallicGlossMap` → `_MetallicMap`
  - `_OcclusionMap` → `_OcclusionMap`
- Reassigns to tent MeshRenderers: `Tent_Cloth_low`, `Tent_Rope_low`, `Tent_Wood_low`
- Saves prefabs

---

## MISSING PLAYER SCRIPT FIX

### Diagnostic: Scan for Missing Scripts
```
In Unity Editor:
Tools → Diagnostics → Scan Missing Scripts and Materials
```

**What this does:**
- Scans all scenes and prefabs
- Finds GameObjects named `Player` with missing script components
- Finds MeshRenderers with `null`, `Default-Material`, or `Hidden/InternalErrorShader` materials
- Logs results to console and `DiagnosticsReport.txt`

**Action (Manual):**
1. Open the Player prefab or scene
2. Inspect the Player GameObject
3. Look at the broken script reference (red "Missing" icon)
4. In the Inspector, click the asset picker icon
5. Search for the correct script (e.g., `PlayerController.cs`, `PlayerStats.cs`)
6. Assign it

**Do NOT try to auto-fix script references.** Only the developer knows which script should be attached.

---

## COMPLETE REPAIR SEQUENCE

```
1. Assets → Reimport All                    [Wait 2-5 min]
2. Tools → Asset Repair → Comprehensive...  [Wait ~30 sec]
3. Tools → Diagnostics → Scan...            [Verify results]
4. For tents: Extract FBX Materials         [Manual]
5. Tools → Diagnostics → Convert Tent...    [Auto-convert]
6. Manually reassign any missing scripts    [Manual]
7. Test in scenes
```

---

## IF PROBLEMS PERSIST

### Pink objects still showing?
1. Check `ComprehensiveRepairReport.txt` for `[BROKEN-SHADER-WHITE-FALLBACK]` entries
   - These mean textures weren't found in the pack folder
   - Manually check if textures exist elsewhere
2. Verify textures are in same pack folder or "Textures/" subfolder
3. Re-run: `Assets → Reimport All` then Comprehensive Repair again

### Shader dropdown doesn't show materials?
1. Standard Render Pipeline doesn't register shaders the same way as URP
2. Shaders show in Material inspector but not in dropdown selector
3. This is normal; material assignment still works fine
4. If URP is activated later, shaders will auto-register

### Objects only render when material is clicked?
1. This indicates material serialization issue
2. Fix: Select prefab → Save As Prefab (forces re-serialization)
3. Or: Re-run Comprehensive Repair with step 3B for affected prefabs

---

## FILES INVOLVED

| File | Purpose |
|------|---------|
| `ComprehensiveAssetRepair.cs` | Main repair tool: fixes Hidden/InternalErrorShader + assigns textures |
| `DiagnosticsScanner.cs` | Scans for missing scripts and broken materials |
| `TentMaterialConverter.cs` | Converts tent materials from Standard to URP Lit (if URP active) |
| `DiagnosticsMenu.cs` | Menu items under `Tools/Diagnostics/` and `Tools/Asset Repair/` |
| `ComprehensiveRepairReport.txt` | Output report from repair tool |
| `DiagnosticsReport.txt` | Output from diagnostic scanner |

---

## UNITY BEST PRACTICES APPLIED

1. **GUID Rebuild** - Reimport All forces Asset Database to rescan .meta files
2. **Fallback Shaders** - Standard is most universal, works in all pipeline contexts
3. **White Texture Fallback** - Prevents pink (indicates "no texture") vs broken shader (also pink)
4. **Manual Prefab Saving** - PrefabUtility.SaveAsPrefabAsset forces re-serialization
5. **EditorUtility.SetDirty** - Marks assets as changed for save/serialize
6. **Component Search** - GetComponentsInChildren with includeInactive=true catches all instances
7. **AssetDatabase API** - FindAssets, LoadAssetAtPath used consistently for GUID-safe operations

---

## NEXT STEPS

1. Run the repair sequence above in Unity
2. Share the output from `ComprehensiveRepairReport.txt` if issues persist
3. Check if URP should be activated (improves shader support for these assets)
4. Consider creating a custom import preset for future asset packs to avoid GUID issues
