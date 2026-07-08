# URP Asset Compatibility Fix Guide

## Error Categories & Solutions

### 🔴 CRITICAL: MaterialLocation.External Deprecated

**Affected Assets:**
- URP_Tree_Pack (all LOD variants)
- Blackant Master Studio (The Shed)
- BillemotdonggulLavaTubePack
- ALP_Assets

**Root Cause:**
URP no longer supports external material locations. Materials must be:
1. Embedded in FBX files, OR
2. Stored as separate `.mat` files in Assets

**Fix Options:**

#### Option A: Auto-Fix via FBX Reimport Settings
1. Select each problematic FBX file
2. In Inspector → Model → Materials:
   - Set **Location** to `Embedded`
   - Set **Naming** to `From Model's Material`
3. Click **Apply**
4. Wait for reimport

#### Option B: Manual Material Assignment
1. For each affected model, create matching materials:
   ```
   Assets/Materials/URP/[ModelName].mat
   ```
2. Assign to MeshRenderer at runtime or in scene
3. Add to project ignore if from asset packs

#### Option C: Disable Problematic Asset Packs (Quickest)
```
Assets/Tree_Packs/URP_Tree_Pack/ → .gitignore
Assets/Blackant Master Studio/ → .gitignore
Assets/BillemotdonggulLavaTubePack/ → .gitignore
Assets/ALP_Assets/ → .gitignore
```
Then remove from project or mark as Optional in AssetPackManager.

---

### 🟡 HIGH PRIORITY: PNG File Read Error

**Error:**
```
Could not create asset from Assets/Graphics/NPCs/Captain_Veynar_sitting_nobg_all_views.png
```

**Troubleshooting:**
1. Check file exists: `Assets/Graphics/NPCs/Captain_Veynar_sitting_nobg_all_views.png`
2. Verify file permissions (not read-only)
3. Try opening in image editor to verify integrity
4. If corrupted, restore from backup or regenerate

**Quick Fix:**
```bash
# In project root (or Assets folder)
rm Assets/Graphics/NPCs/Captain_Veynar_sitting_nobg_all_views.png
# Re-add cleaned version, ensure <1024x1024 if mobile target
```

---

### 🟡 MEDIUM: Mesh Missing Normals

**Affected Models:**
- Birch_stump_* (multiple variants)
- Stump_* variants

**Cause:**
Assets exported without normals from 3D software.

**Fix in Unity:**
1. Select FBX file in Project
2. Inspector → Model → Normals and Tangents:
   - Set **Normals** to `Calculate`
   - Set **Tangents** to `Calculate`
3. Click **Apply**

---

### 🟡 MEDIUM: Self-Intersecting Polygons

**Affected Models:**
- Succulent_Graptoosedum variants
- Ruins_WallCap models
- Door_Left_01, Door_Right_01
- Succulent_ghost_plant variants

**Impact:** Unity discards bad triangles automatically (safe)

**Fix Options:**

**A) Accept Discard (Recommended if visual quality OK)**
- No action needed, just suppress warnings in Console

**B) Clean 3D Models**
1. Export model to Blender
2. Use **Mesh → Cleanup → Delete Loose** and **Merge by Distance**
3. Use **Mesh → Non-Manifold → Select All** to find issues
4. Re-export to FBX

**C) Disable Assets Generating Most Warnings**
Add to `.gitignore`:
```
Assets/SeedMesh/Succulents/
Assets/EmbersStorm – Mediterranean Ruins Building Kit/
```

---

### 🟢 LOW: Input Manager Deprecation

**Error:**
```
This project uses Input Manager, which is marked for deprecation.
```

**Fix:**
Install Input System package (already done with URP).

**Optional Upgrade (Future):**
1. Window → TextMesh Pro → Import TMP Examples & Extras
2. Window → Input System → Create Default Input Actions
3. Update controller scripts to use new Input System

---

### 🟢 LOW: Semantic URI Reference

**Error:**
```
Asset reference to GUID 'dace8ee3f59c99149ad4c1db64b635fe' 
was moved from 'Assets/Samples/Core RP Library/...' to 'Assets/Samples/Scriptable Render Pipeline Core/17.4.0/...'
```

**Fix:** Ignore or manually update if component breaks:
1. Right-click asset → Reimport
2. Or delete and add fresh from Package Manager

---

### 🟢 LOW: CanvasScaler Missing

**Error:**
```
Unknown type 'CanvasScaler' for FileID 674520892 in TitleScene.unity
```

**Fix:**
1. Open TitleScene.unity
2. Find Canvas in hierarchy
3. Add Component → Layout → Canvas Scaler
4. Configure for target resolution

---

## Recommended Remediation Order

1. **First Pass (10 min)** - Accept Benign Warnings
   - Discard self-intersecting polygons (visual impact minimal)
   - Ignore Input Manager deprecation warning (not blocking)

2. **Second Pass (30 min)** - Fix External Materials
   - Create cleanup script to reimport FBXs with embedded materials
   - OR disable problematic asset packs

3. **Third Pass (20 min)** - Fix Data Issues
   - Recalculate normals on affected meshes
   - Fix/regenerate PNG file

4. **Fourth Pass (10 min)** - Test Scene
   - Reload scene in URP
   - Check visual quality
   - Monitor Console for new errors

---

## Prevention Going Forward

### Import Settings Template
Create `.fbx` import preset:
1. Assets → Create → FBX Import Settings
2. Configure:
   - **Materials → Location:** `Embedded`
   - **Normals and Tangents:** `Calculate`
   - **Meshes → Read/Write Enabled:** `Off` (unless physics)
3. Apply to asset packs on import

### Asset Pack Guidelines
Require from vendors:
- ✅ URP-compatible shaders
- ✅ Embedded materials in FBX
- ✅ Clean normals (not custom)
- ✅ Manifold mesh topology
- ✅ Test import in blank URP project first

---

## Quick Diagnostics Command

```powershell
# Count unique errors in Console log
Get-Content -Path "path/to/editor.log" | 
  Select-String "MaterialLocation|missing normals|self-intersecting" | 
  Group-Object | 
  Sort-Object -Property Count -Descending
```

---

## Next Steps

1. **Run this now:**
   - Edit → Project Settings → Editor
   - Expand Console message options
   - Filter to show only Errors (hide Warnings temporarily)

2. **Create issue tracking:**
   - Document which asset packs cause 80% of warnings
   - Mark for replacement/removal in next update

3. **Test critical assets:**
   - Verify trees render correctly
   - Check material appearance in URP
   - Confirm physics colliders work

