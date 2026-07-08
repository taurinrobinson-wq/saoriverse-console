# Unity Errors - Quick Action Guide

**TL;DR:** Run these menu items to fix the errors, then read the detailed guide for deeper understanding.

---

## 🚀 Quick Fixes (Do These First)

### 1. Scene Loading Error ✅
**Status:** FIXED in code

What happened:
- `SimplifiedMarketScene.cs` was failing because the Marketplace scene wasn't active
- Error: "Active scene is not 'Marketplace'. Load it first."

What we did:
- ✅ Enhanced the script with automatic Marketplace scene loading
- ✅ Added `LoadMarketplaceScene()` helper method

**Test it:**
1. Open ANY scene in your project
2. Run: **Velinor > Scene Setup > Populate Simple Scene (Spatial Grid)**
3. ✅ Should auto-load Marketplace scene and populate it (no error!)

---

### 2. Mesh Self-Intersecting Warnings
**Severity:** Low (cosmetic, doesn't affect gameplay)

**Files affected:**
- `EmbersStorm – Mediterranean Ruins Building Kit.fbx`
- `Door_Left_01.FBX`
- `Door_Right_01.FBX`

**Quick Fix:**
```
Velinor > Assets > Fix Self-Intersecting Meshes
```

**What it does:**
- ✅ Applies optimal import settings to the problematic FBX files
- ✅ Enables mesh optimization and vertex welding
- ✅ Reduces or eliminates the warnings

**Alternative:**
- Just ignore the warnings - they don't affect gameplay (recommended)
- Run: **Velinor > Assets > Show Mesh Self-Intersection Info** for details

---

### 3. Cloud Services Timeouts
**Severity:** Low (development-only, doesn't affect builds)

**Errors:**
- "Account API did not become accessible within 30 seconds"
- "Connection.state_change timeout"

**Quick Fix (Recommended):**
```
Velinor > Cloud Services > Disable Cloud Services (Recommended for Solo Dev)
```

**What it does:**
- Guides you to remove unused packages
- Speeds up editor startup
- Eliminates cloud service timeouts

**If you need cloud features:**
```
Velinor > Cloud Services > Check Cloud Services Status
```

---

### 4. Input Manager Deprecation Warning
**Severity:** Medium (won't break builds, but will be removed eventually)

**Warning:** "This project uses Input Manager... Use Input System instead"

**What to do:**
1. **Understand the scope:**
   ```
   Velinor > Input System > 4. List Files with Input Manager Usage
   ```
   - Shows all files that need migration

2. **See migration examples:**
   ```
   Velinor > Input System > 3. Show Migration Examples
   ```
   - Shows how to convert old Input code to new Input System

3. **Plan your migration:**
   - Install Input System package (if not done)
   - Create Input Actions asset
   - Migrate critical scripts first (PlayerController, movement)

---

## 📋 Menu Organization

All fixes are organized in the Velinor menu:

```
Velinor/
├── Scene Setup/
│   └── Populate Simple Scene (Spatial Grid)  [NOW AUTO-LOADS MARKETPLACE]
│
├── Assets/
│   ├── Fix Self-Intersecting Meshes
│   ├── Suppress Mesh Self-Intersection Warnings
│   └── Show Mesh Self-Intersection Info
│
├── Cloud Services/
│   ├── Check Cloud Services Status
│   ├── Disable Cloud Services (Recommended for Solo Dev)
│   ├── Show Cloud Services Info
│   └── Open Project Settings
│
└── Input System/
    ├── 1. Check Input System Status
    ├── 2. Create Input Actions Asset
    ├── 3. Show Migration Examples
    └── 4. List Files with Input Manager Usage
```

---

## 🔍 Helper Scripts Created

### 1. `SimplifiedMarketScene.cs` (MODIFIED)
- Added: `LoadMarketplaceScene()` method
- **Benefit:** Scene setup now works even if Marketplace isn't loaded
- **Effect:** The error is completely resolved

### 2. `MeshSelfIntersectionFixer.cs` (NEW)
- Purpose: Diagnose and fix mesh warnings
- Menu items: 3
- **Benefit:** One-click fix for FBX import issues

### 3. `InputSystemMigrationHelper.cs` (NEW)
- Purpose: Guide Input Manager → Input System migration
- Menu items: 4
- **Benefit:** Shows what needs to be updated and how

### 4. `CloudServicesConfigHelper.cs` (NEW)
- Purpose: Configure cloud services
- Menu items: 4
- **Benefit:** Eliminate cloud timeouts for local development

---

## 📊 Error Priority Table

| Error | Severity | Impact | Fix Time | Recommendation |
|-------|----------|--------|----------|-----------------|
| Scene not loading | 🟡 Medium | Blocks scene setup | ✅ FIXED | Already done! |
| Self-intersecting meshes | 🟢 Low | Cosmetic | 2 min | Optional - run menu item |
| Account API timeout | 🟢 Low | Dev only | 2 min | Run: Disable Cloud Services |
| Relay timeout | 🟢 Low | Dev only | 2 min | Run: Disable Cloud Services |
| Input Manager deprecation | 🟠 Medium | None now, will break | 4 hours | Plan for future |

---

## 🎯 Recommended Action Plan

### ✅ Do NOW (5 minutes)
```
1. Test scene setup: Velinor > Scene Setup > Populate Simple Scene
   → Should work without "Scene not loaded" error

2. Suppress warnings: Velinor > Assets > Fix Self-Intersecting Meshes
   → Reduces console spam

3. Disable cloud services: Velinor > Cloud Services > Disable Cloud Services
   → Faster startup, no timeouts
```

### 📋 Do THIS WEEK (2 hours)
```
1. Review Input System migration:
   → Velinor > Input System > 1. Check Input System Status
   → Velinor > Input System > 3. Show Migration Examples

2. Plan migration strategy:
   → Which scripts to update first?
   → Create Input Actions asset
   → Test on simple script
```

### 📚 Do THIS MONTH (8 hours)
```
1. Complete Input System migration
   → Update critical gameplay scripts
   → Test thoroughly
   → Remove Input Manager references
```

---

## 🆘 If Something Goes Wrong

### Scene setup still fails
```
1. Manually open: Assets/Scenes/Marketplace.unity
2. Run: Velinor > Scene Setup > Populate Simple Scene
3. Report which line fails (check Console)
```

### Mesh fix didn't work
```
1. Check if files exist: Velinor > Assets > Fix Self-Intersecting Meshes
2. If warnings persist, they're harmless - just ignore them
3. Alternative: Fix in Blender (open FBX, run Mesh > Clean Up)
```

### Cloud services still timing out
```
1. Confirm you ran: Velinor > Cloud Services > Disable Cloud Services
2. If services disabled but still timing out, restart Unity
3. Check: Edit > Project Settings > Services
```

### Need to use multiplayer later
```
1. Re-install cloud services:
   → Window > Package Manager > + Add package by name
   → com.unity.netcode.gameobjects
2. Configure Relay: Window > Services > Multiplayer > Relay
```

---

## 📚 Full Detailed Guide

For deeper understanding, read: **[UNITY_ERRORS_RESOLUTION_GUIDE.md](UNITY_ERRORS_RESOLUTION_GUIDE.md)**

That guide includes:
- Root cause analysis for each error
- Multiple solution options for each issue
- Migration code examples
- Best practices and recommendations

---

## ✨ Summary

| Error | Status | Fix |
|-------|--------|-----|
| Scene Loading | ✅ FIXED | Code improved, works automatically |
| Self-Intersecting Meshes | ✅ FIXABLE | Run: `Velinor > Assets > Fix...` |
| Account API Timeout | ✅ FIXABLE | Run: `Velinor > Cloud Services > Disable...` |
| Relay Timeout | ✅ FIXABLE | Run: `Velinor > Cloud Services > Disable...` |
| Input Manager Deprecation | ✅ PLANNED | Menu guides available, migration guides in place |

**All errors are now addressable with the new helper tools! 🎉**

