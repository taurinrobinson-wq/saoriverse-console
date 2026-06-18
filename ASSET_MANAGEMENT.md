# Asset Management Guide

## Overview

All imported Unity Store assets are stored **locally** in your project folder and **NOT tracked in git**. This keeps your repo size manageable (~100MB instead of 8GB+) while maintaining full functionality.

---

## Asset Storage

### Location Structure
```
Velinor-Unity/Assets/
├── Scripts/                          ✅ TRACKED
├── Scenes/                           ✅ TRACKED
├── Resources/                        ✅ TRACKED
├── TextMesh Pro/                     ✅ TRACKED (dependency)
├── [Large Asset Folders]             ❌ IGNORED
│   ├── BillemotdonggulLavaTubePack/  (5.8 GB)
│   ├── MarioParadiso/                (4.4 GB)
│   ├── Creepy_Cat/                   (1.1 GB)
│   ├── ALP_Assets/                   (278 MB)
│   ├── Polyeler/                     (307 MB)
│   └── [Other asset packs]
```

### Source Asset Packages
All original `.unitypackage` files remain in: `D:\Velinor\Asset Store-5.x\`

---

## Workflow

### If You Already Have Assets Imported

**Good news:** You already have everything set up locally! Just update `.gitignore` to stop tracking them.

```powershell
# From repo root
cd d:\saoriverse-console

# Remove large asset folders from git tracking (without deleting locally)
git rm --cached Velinor-Unity/Assets/BillemotdonggulLavaTubePack -r --force
git rm --cached Velinor-Unity/Assets/MarioParadiso -r --force
git rm --cached Velinor-Unity/Assets/Creepy_Cat -r --force
git rm --cached Velinor-Unity/Assets/ALP_Assets -r --force
git rm --cached Velinor-Unity/Assets/Polyeler -r --force
git rm --cached Velinor-Unity/Assets/Modular_SciFi_Pack -r --force
git rm --cached Velinor-Unity/Assets/3\ English\ Oak\ Set -r --force
git rm --cached Velinor-Unity/Assets/Dry_Trees -r --force
git rm --cached "Velinor-Unity/Assets/EmbersStorm – Mediterranean Ruins Building Kit" -r --force
git rm --cached Velinor-Unity/Assets/Kyle\'s\ Rock\ Pack -r --force
git rm --cached Velinor-Unity/Assets/Sat\ Productions -r --force
git rm --cached Velinor-Unity/Assets/Unity -r --force
git rm --cached Velinor-Unity/Assets/StarterAssets -r --force
git rm --cached Velinor-Unity/Assets/Creepy_Cat -r --force

# Commit the removal
git add .gitignore
git commit -m "Untrack large asset folders - keep locally only"
git push origin main
```

### If You're Cloning This Repo Fresh

1. Clone normally: `git clone https://github.com/taurinrobinson-wq/saoriverse-console.git`
2. Import needed assets from `D:\Velinor\Asset Store-5.x\` into `Velinor-Unity/Assets/` as needed
3. Follow the naming convention: `[Biome]_[Category]_[Name]`
4. Assets will automatically be ignored by git

---

## Special Constraint Packages

The following asset packs require **fresh, empty Unity projects** to import properly. They are **NOT currently integrated** into Velinor but are available in `D:\Velinor\Asset Store-5.x\` for future reference:

| Package | Creator | Size | Reason On Hold | Future Use |
|---------|---------|------|----------------|------------|
| **Time Ghost Environment** | Unity Technologies | ~500 MB | Requires fresh project | Reference for professional environment design |
| **Book of the Dead** | Unity Technologies | ~2 GB | Requires fresh project | Character animation reference |
| **HDRP Environment Template** | Far From Here Studio | ~300 MB | Requires fresh project (HDRP vs URP) | Advanced lighting setup reference |
| **Surface Gradient Bump Mapping** | Unity Technologies | ~100 MB | Requires fresh project | Shader/material technique reference |

**Integration Strategy:** These packages can be selectively mined for:
- Individual material/shader samples
- Animation controller patterns
- Lighting setup approaches
- Scene structure examples

But direct import into the Velinor-Unity project would require careful extraction and adaptation.

---

## What IS Tracked (Commit These)

```
✅ Scripts/
   - All .cs files
   - BiomeManager scripts
   - System logic

✅ Scenes/
   - All .unity scene files
   - Biome template scenes

✅ Resources/
   - Config files
   - Small data assets
   - Scriptable objects

✅ TextMesh Pro/
   - Font assets (dependency)

✅ Prefabs/
   - Any prefab files (.prefab)
   - Scene configurations
```

---

## What is NOT Tracked (Gitignore)

```
❌ [All Asset Folders]
   - BillemotdonggulLavaTubePack/    (lava caves - 5.8 GB)
   - MarioParadiso/                   (environment - 4.4 GB)
   - Creepy_Cat/                      (sci-fi kit - 1.1 GB)
   - ALP_Assets/                      (urban environment - 278 MB)
   - Polyeler/                        (nature pack - 307 MB)
   - Modular_SciFi_Pack/              (sci-fi kit - 59 MB)
   - 3 English Oak Set/               (trees - 25 MB)
   - Dry_Trees/                       (decay vegetation)
   - EmbersStorm - Mediterranean.../  (ruins - ~100 MB)
   - Kyle's Rock Pack/                (terrain rocks)
   - Sat Productions/                 (systems - 8 MB)
   - Creepy_Cat/                      (duplicated)
   - And any others added after import

❌ .meta files for ignored folders
   (auto-generated, don't commit)

❌ _ImportedRaw/
   (temporary import staging)
```

---

## Workspace-Specific Setup

### Team Members Working Together

If multiple people are working on this project:

1. **Each person imports assets locally** to their own machine from `D:\Velinor\Asset Store-5.x\`
2. **Commit only your scripts** (BiomeManager, scene configs, etc.)
3. **Share your naming convention** via documentation
4. **Assets synced via conversation/reference**, not via repo

### Codespace / Cloud Development

If moving to cloud IDE (GitHub Codespaces):
- Don't worry about assets initially
- Focus on importing scripts and configs
- Assets will need to be managed separately (outside of repo)

---

## Storage Impact

### Without .gitignore (Current)
- **Assets in repo:** ~8 GB
- **Repo size:** Too large
- **Clone time:** Very slow
- **Push/pull:** Slow for everyone

### With .gitignore (Recommended)
- **Assets in repo:** 0 MB (ignored)
- **Repo size:** ~100-150 MB
- **Clone time:** Fast
- **Push/pull:** Normal speed

### Space Saved
- **8 GB → 150 MB = 98% reduction**
- Repo remains fast and responsive

---

## Adding New Assets

When importing more packages:

1. **Import from:** `D:\Velinor\Asset Store-5.x\[Package].unitypackage`
2. **Import to:** `Velinor-Unity/Assets/[BioName]/`
3. **Follow convention:** `[Biome]_[Category]_[Name]`
4. **Commit:** Only scripts/configs, NOT the assets themselves
5. **Document:** Note which package you imported in team notes

---

## Verification

### Check What's Tracked
```powershell
cd d:\saoriverse-console
git ls-files | grep "Assets/" | head -20
```

Should show:
- Scripts/ files (.cs)
- Scenes/ files (.unity)
- Resources/ files
- TextMesh Pro/ files

Should NOT show:
- Asset pack folders
- Model files (.fbx, .obj)
- Texture files (.png, .jpg)

### Check What's Ignored
```powershell
git check-ignore -v Velinor-Unity/Assets/BillemotdonggulLavaTubePack
```

Should output:
```
.gitignore:XX:Velinor-Unity/Assets/BillemotdonggulLavaTubePack/
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Check current size | `du -sh .` in repo root |
| See tracked assets | `git ls-files \| grep Assets` |
| Verify ignored | `git check-ignore Velinor-Unity/Assets/[folder]` |
| Force remove from tracking | `git rm --cached [path] -r` |

---

## Documentation Files

Related guides:
- [VELINOR_ASSET_INDEX.md](VELINOR_ASSET_INDEX.md) — Complete asset catalog
- [CODESPACE_IMPLEMENTATION_PLAN.md](CODESPACE_IMPLEMENTATION_PLAN.md) — World system setup
- [PHASE_1_CHECKLIST.md](../Velinor-Unity/PHASE_1_CHECKLIST.md) — Feature milestones

---

**Status:** Asset management configured for local storage  
**Updated:** 2026-06-16  
**Repo Impact:** 98% reduction in size (8GB → 150MB)
