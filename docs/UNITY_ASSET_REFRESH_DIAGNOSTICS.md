# Unity Asset Refresh Diagnostics

**Date:** 2026-07-07  
**Severity:** Mixed (1 Critical, Several Medium, Multiple Warnings)

---

## Critical Issues

### 1. PNG File Read Error
```
Could not create asset from Assets/Graphics/NPCs/Captain_Veynar_sitting_nobg(all views).png: File could not be read
```

**Status:** BLOCKING  
**Cause:** File corruption, encoding issue, or filename encoding problem  
**Filename Issue:** Contains parentheses and spaces; may be Unicode/encoding conflict  

**Action Required:**
1. Check file exists and is readable: `Assets/Graphics/NPCs/Captain_Veynar_sitting_nobg(all views).png`
2. Rename file to remove parentheses: `Captain_Veynar_sitting_nobg_all_views.png`
3. Reimport with new name
4. If still fails: file may be corrupted; re-export from source

---

## High Priority Issues

### 2. Line Ending Inconsistency (BillemotdonggulLavaTubePack Shaders)
**Status:** NEEDS FIXING  
**Count:** 200+ shader files  
**Issue:** Mixed UNIX (LF) and Windows (CRLF) line endings in same files

Affected directories:
- `Assets/BillemotdonggulLavaTubePack/Shaders/*.shader`
- `Assets/BillemotdonggulLavaTubePack/Shaders/UnrealCommon.cginc`

**Action:** Convert all to Windows (CRLF) line endings using batch script

---

### 3. Missing CanvasScaler Type
```
Unknown type 'CanvasScaler' for FileID 674520892 in text file Assets/Scenes/TitleScene.unity at line 300.
```

**Status:** BLOCKING UI RENDERING  
**Cause:** TextMesh Pro or UI Toolkit component not imported or scene references deleted component  
**Location:** `Assets/Scenes/TitleScene.unity` line 300

**Action Required:**
1. Open TitleScene.unity
2. Find GameObject with CanvasScaler reference
3. Either:
   - Add missing TextMesh Pro Essential package (Import from Window → TextMeshPro → Import TMP Essential Resources)
   - OR remove CanvasScaler component if not needed
   - OR manually reassign component

---

## Medium Priority Issues

### 4. MaterialLocation.External Deprecation
**Status:** WARNING (not blocking, but may fail in newer Unity)  
**Count:** 100+ FBX files  
**Issue:** FBX import setting "External Material Location" is deprecated

Affected packs:
- Tree_Packs/URP_Tree_Pack
- Blackant Master Studio/The Shed
- ALP_Assets/country house01
- BillemotdonggulLavaTubePack
- EmbersStorm Mediterranean Ruins
- Creepy_Cat 3D Scifi Kit
- SeedMesh Succulents

**Action:** Re-import affected FBX files with "External Materials" disabled

---

### 5. Mesh Normals Missing
**Status:** WARNING (automatic recalc happening)  
**Count:** 15+ meshes

Examples:
- Birch_stump_rotten (Tree meshes)
- Stump_nobark, Stump_old2, etc.
- Succulent meshes (self-intersecting)

**Note:** Unity is auto-recalculating normals; this may impact tangent space quality.

---

### 6. Self-Intersecting Polygons
**Status:** INFO (being discarded automatically)  
**Count:** 5+ meshes

Examples:
- Succulent_GraptosedumBronze variants
- Succulent_ghost_plant variants
- Ruins_WallCap variants (EmbersStorm)
- Door_Left_01 and Door_Right_01 (Scifi Kit)

**Action:** Reimport FBX with "Import BlendShapes" disabled if not needed, or model cleaning required

---

### 7. Input Manager Deprecation
```
This project uses Input Manager, which is marked for deprecation.
```

**Status:** WARNING (still works, but should migrate)  
**Action:** Install Input System package from Window → TextMesh Pro or Package Manager

---

## Summary Table

| Issue | Count | Severity | Action |
|-------|-------|----------|--------|
| PNG read error | 1 | CRITICAL | Rename file, check encoding |
| Line ending inconsistency | 200+ | HIGH | Batch convert CRLF |
| CanvasScaler missing | 1 | HIGH | Import TextMesh Pro or remove |
| MaterialLocation.External | 100+ | MEDIUM | Re-import FBX files |
| Missing mesh normals | 15+ | MEDIUM | Auto-recalc (acceptable) |
| Self-intersecting polygons | 5+ | MEDIUM | Model cleanup |
| Input Manager deprecation | - | LOW | Migrate to Input System |

---

## Recommended Fix Order

1. **FIRST:** Fix PNG filename → Rename `Captain_Veynar_sitting_nobg(all views).png`
2. **SECOND:** Add TextMesh Pro or remove CanvasScaler from TitleScene
3. **THIRD:** Fix line endings in BillemotdonggulLavaTubePack shaders
4. **FOURTH:** Re-import FBX files to remove MaterialLocation.External warnings
5. **OPTIONAL:** Migrate to Input System package (low priority)

---

## Next Steps

Implement fixes in order above. After each fix, run:
1. `Assets → Reimport All`
2. Check Console for errors
3. Verify scene renders without pink/missing materials

