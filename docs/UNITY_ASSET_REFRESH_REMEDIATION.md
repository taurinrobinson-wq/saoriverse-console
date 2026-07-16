# Unity Asset Refresh - Remediation Steps

**Status:** Automated fixes complete. Manual actions required.  
**Last Updated:** 2026-07-07

---

## ✅ Completed Fixes

| Issue | Action | Result |
|-------|--------|--------|
| PNG filename error | Renamed `Captain_Veynar_sitting_nobg(all views).png` → `Captain_Veynar_sitting_nobg_all_views.png` | FIXED |
| Shader line endings | Normalized 134 shader files to Windows CRLF line endings | FIXED |
| Orphaned .meta file | Deleted old .meta file (will regenerate on reimport) | FIXED |

**Commit:** `307e89ed`

---

## ⚠️ Manual Actions Required

### Step 1: Reimport All Assets in Unity

**Location:** Unity Editor  
**Time:** 2-5 minutes

1. Open Velinor-Unity project in Unity Editor
2. Go to `Assets` menu → `Reimport All`
3. Wait for reimport to complete
4. Check Console for remaining errors (should be much fewer now)

**Expected Result:** 
- PNG file should load without errors
- Shaders should compile without line ending warnings
- 100+ MaterialLocation.External warnings may still appear (deprecated API)

---

### Step 2: Fix CanvasScaler Missing Type Error

**Location:** TitleScene.unity  
**Error:** Unknown type 'CanvasScaler' at line 300  
**Time:** 5 minutes

**Option A: Import TextMesh Pro (Recommended)**
1. In Unity Editor, go to `Window` → `TextMeshPro` → `Import TMP Essential Resources`
2. Click `Import` in the popup
3. Wait for import to complete
4. Go to `Assets` → `Reimport All`
5. Check if CanvasScaler error resolves

**Option B: Remove CanvasScaler Component**
1. Open TitleScene.unity in Unity Editor
2. In Hierarchy, find Canvas GameObject
3. In Inspector, locate CanvasScaler component
4. Click the ⋮ menu → `Remove Component`
5. Save scene

**Which to choose?**
- **Option A** if CanvasScaler is needed for UI scaling
- **Option B** if you don't need responsive canvas scaling

---

### Step 3: Fix MaterialLocation.External Deprecation

**Issue:** 100+ FBX files using deprecated external material location  
**Severity:** Warning (not blocking, but will fail in future Unity versions)  
**Time:** 20-30 minutes

#### Affected Packs:
- `Assets/Tree_Packs/URP_Tree_Pack/` (6 FBX files)
- `Assets/Blackant Master Studio/The Shed/` (8 FBX files)
- `Assets/ALP_Assets/country house01/` (3 FBX files)
- `Assets/BillemotdonggulLavaTubePack/Mesh/` (80+ FBX files)
- `Assets/EmbersStorm Mediterranean Ruins/` (2 FBX files)
- `Assets/Creepy_Cat/3D Scifi Kit/` (5 FBX files)

#### Fix for Each FBX:

1. In Project window, locate FBX file
2. Select the FBX and view Inspector
3. Expand **Materials** section
4. Change **Material Import Mode** from `Import via Materials Folder` to `Import Embedded Materials`
5. Click **Apply**
6. Reimport will happen automatically

**OR use this faster approach:**

1. Select all affected FBX files (use Ctrl+Click or shift-click in Project)
2. In Inspector, change **Material Import Mode** to `Import Embedded Materials`
3. Click **Apply** once
4. All selected files update at once

**Expected Result:** Materials embedded in FBX → no external material location needed

---

### Step 4: Address Mesh Warnings (Optional)

These are automatically handled by Unity and won't cause rendering issues:

- **Missing mesh normals** → Unity recalculates automatically
- **Self-intersecting polygons** → Discarded automatically (minor visual impact)
- **Tangent space issues** → Handled by shader system

**Action:** None required (informational only)

---

### Step 5: Migrate Input Manager (Optional)

**Issue:** Input Manager deprecated; should use Input System package  
**Severity:** Low (still works, but Unity recommends migration)  
**Time:** 30 minutes (depends on input binding complexity)

**Action:**
1. Install Input System package: `Window` → `Package Manager`
2. Search for "Input System"
3. Click `Install`
4. Read migration guide: https://docs.unity3d.com/Packages/com.unity.inputsystem@latest

**Decision:** Can defer this; not blocking for current development

---

## 📋 Quick Checklist

- [ ] Run `Assets → Reimport All` in Unity
- [ ] Check Console for errors (should see fewer now)
- [ ] Either import TextMesh Pro OR remove CanvasScaler from TitleScene
- [ ] Check TitleScene loads without CanvasScaler errors
- [ ] Select and re-import FBX files with embedded materials (20-30 min)
- [ ] Verify materials render correctly (no pink/missing textures)
- [ ] Optional: Migrate to Input System package

---

## 🧪 Verification Steps

After completing manual actions:

1. **Open a scene with materials** (should not be pink)
2. **Check Console** (no MaterialLocation errors for new imports)
3. **Play in Editor** (verify UI renders correctly)
4. **Check specific assets:**
   - Tent materials (should show solid colors, not pink)
   - Tree models (should show bark/leaf textures)
   - Building kits (should show stone/metal textures)

---

## 📝 Notes

- The PNG filename fix ensures Unicode/special character compatibility
- Line ending normalization prevents shader compiler confusion
- FBX material migration ensures forward compatibility with future Unity versions
- All changes have been committed to main branch (commit `307e89ed`)

---

## Support

If issues persist after completing these steps:

1. Check `UNITY_ASSET_REFRESH_DIAGNOSTICS.md` for detailed error categories
2. Review console errors for specific asset paths
3. Verify all file renaming/reimporting completed
4. Consider running `Assets → Delete Library` to fully clear cache, then reimport

