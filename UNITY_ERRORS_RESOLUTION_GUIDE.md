# Unity Errors Resolution Guide

This guide addresses all the Unity errors reported in your project.

---

## 1. Self-Intersecting Mesh Errors ❌➡️✅

### Error Summary
```
A polygon of Mesh 'Ruins_WallCap_A.1' ... is self-intersecting and has been discarded.
A polygon of Mesh 'Door_Left_01' ... is self-intersecting and has been discarded.
```

These are **import warnings** caused by geometry issues in the FBX files. The meshes are being cleaned up by Unity's import pipeline.

### Solutions (in order of preference):

#### Option 1: Disable Self-Intersection Warnings (Quickest)
This suppresses the warnings without fixing the underlying geometry:

1. Select the problematic FBX file in Project folder
2. In Inspector, go to **Model** settings
3. Check: **Meshes** > **Optimize Mesh Data** (enable)
4. Check: **Meshes** > **Weld Vertices** (enable)
5. Set **Normals & Tangents** > **Normals** to `Compute Normals`
6. Apply and re-import

**Files to fix:**
- `Assets/EmbersStorm – Mediterranean Ruins Building Kit/Meshes/EmbersStorm – Mediterranean Ruins Building Kit.fbx`
- `Assets/Creepy_Cat/3D Scifi Kit Starter Kit_HD/Meshes/Doors/Door_Left_01.FBX`
- `Assets/Creepy_Cat/3D Scifi Kit Starter Kit_HD/Meshes/Doors/Door_Right_01.FBX`

#### Option 2: Fix in 3D Editor (Most Robust)
If you have access to the model files:

1. Open the FBX in Blender or your 3D editor
2. Select all geometry: `A` (Blender)
3. Run **Mesh** > **Clean Up** > **Remove Doubles**
4. Run **Mesh** > **Cleanup** > **Delete Loose** (vertices/edges/faces)
5. Re-export the FBX file
6. Re-import in Unity

#### Option 3: Create Collision-Only Versions
Use simple collision meshes instead of the broken render meshes:

1. Import with **Import BlendShapes** disabled
2. Create simplified collision meshes manually
3. Use Mesh Collider with simplified geometry

### Risk Assessment
- ✅ These warnings are **safe to ignore** - they don't break gameplay
- ⚠️ Affected geometry is discarded but collision/rendering still works
- 📊 Monitor performance if many meshes are affected

---

## 2. Input Manager Deprecation Warning ⚠️➡️✅

### Error Summary
```
This project uses Input Manager, which is marked for deprecation. 
Use the Input System package instead.
```

### Solution: Migrate to Input System

#### Step 1: Install Input System Package
1. **Window** > **TextureImporter** > **Package Manager**
2. Click `+` > **Add package by name**
3. Enter: `com.unity.inputsystem`
4. Click Add

#### Step 2: Update Input Scripts
The following files need migration (**58 matches found in 14 files**):

**Priority Files (Core Gameplay):**
- `Assets/Scripts/Core/PlayerController.cs`
- `Assets/Scripts/Core/SimplePlayerMovement.cs`
- `Assets/Scripts/StarterAssets/StarterAssetsInputs.cs`
- `Assets/Scripts/Core/NPCInteraction.cs`
- `Assets/Scripts/Core/DialogueSystem.cs`

**Example Migration:**

**OLD (Input Manager):**
```csharp
float horizontal = Input.GetAxis("Horizontal");
float vertical = Input.GetAxis("Vertical");
bool jump = Input.GetKeyDown(KeyCode.Space);
```

**NEW (Input System):**
```csharp
using UnityEngine.InputSystem;

InputAction moveAction = new InputAction(binding: "<Gamepad>/leftStick");
InputAction jumpAction = new InputAction(binding: "<Keyboard>/space");

float horizontal = moveAction.ReadValue<Vector2>().x;
float vertical = moveAction.ReadValue<Vector2>().y;
bool jump = jumpAction.WasPressedThisFrame();
```

#### Step 3: Generate Input Actions Asset
1. **Create** > **Input System** > **Input Actions**
2. Name it `Controls`
3. Add Action Maps for:
   - Player (Movement, Jump, Interact)
   - UI (Navigate, Select)
   - Camera (Look)

#### Step 4: Reference in Scripts
Replace manual migration with Input Actions asset:

```csharp
public class PlayerController : MonoBehaviour
{
    private PlayerControls controls;
    
    private void Awake()
    {
        controls = new PlayerControls();
    }
    
    private void OnEnable()
    {
        controls.Enable();
    }
    
    private void OnDisable()
    {
        controls.Disable();
    }
    
    private void Update()
    {
        Vector2 moveInput = controls.Player.Move.ReadValue<Vector2>();
        float horizontal = moveInput.x;
        float vertical = moveInput.y;
    }
}
```

#### Migration Priority
1. **Critical:** `PlayerController.cs`, `StarterAssetsInputs.cs` (main player input)
2. **Important:** `SimplePlayerMovement.cs`, `NPCInteraction.cs` (gameplay systems)
3. **Low:** Sample scripts in `Assets/Samples/` (can leave as-is for reference)

---

## 3. Account API Timeout ⚠️➡️ℹ️

### Error Summary
```
Account API did not become accessible within 30 seconds. 
This may be due to network issues or editor focus.
```

### Analysis
- **Severity:** Low (development-only, doesn't affect builds)
- **Cause:** Unity AI Assistant trying to connect to cloud services
- **Impact:** None on gameplay or editor functionality

### Solutions (in order):

#### Option 1: Disable AI Assistant (Simplest)
1. **Window** > **AI Assistant** > Close the panel
2. Or disable package: **Window** > **Package Manager**
3. Search: `com.unity.ai.assistant`
4. Click gear icon > **Remove**

#### Option 2: Disable in Project Settings
1. **Edit** > **Project Settings** > **AI Toolkit**
2. Uncheck **Enable API Features**
3. Uncheck **Use Cloud Features**

#### Option 3: Check Network Connection
If you need AI features:
1. Verify internet connection
2. Check Unity account login (Cloud > Sign in)
3. Wait longer (increase timeout in Editor settings)

#### Option 4: Wait for Cloud Services
If just starting Unity:
- This is often a startup delay
- Can be safely ignored (typically resolves within 1 minute)

---

## 4. Connection State Change Failure ❌➡️ℹ️

### Error Summary
```
connection.state_change
oldState=Connecting newState=Failed error=timeout (500ms) (after 10 attempts)
```

### Analysis
- **Source:** Unity Relay Service (cloud networking)
- **Severity:** Low if not using multiplayer
- **Impact:** Offline/single-player gameplay unaffected

### Solutions:

#### Option 1: Disable Relay (If Not Using)
1. **Window** > **Package Manager**
2. Search: `com.unity.netcode.gameobjects`
3. Click gear > **Remove** (if not needed)

#### Option 2: Check Relay Configuration
If using multiplayer:
1. **Netcode for GameObjects** > **Relay Settings**
2. Configure correct Relay Project ID
3. Verify Unity Services connection

#### Option 3: Increase Timeout
In `Library/PackageCache/com.unity.ai.assistant*/Modules/Unity.AI.Toolkit.Accounts/Services/States/ApiAccessibleState.cs`:
- Timeout: 30 seconds (default)
- Can increase if network is slow

**Recommended:** Disable if not using cloud services - reduces startup time.

---

## 5. Scene Loading Error (SimplifiedMarketScene) ❌➡️✅

### Error Summary
```
❌ Active scene is not 'Marketplace'. Load it first.
UnityEngine.Debug:LogError (object)
Velinor.Editor.SimplifiedMarketScene:PopulateSimpleScene ()
```

### Root Cause
The menu item `Velinor/Scene Setup/Populate Simple Scene (Spatial Grid)` requires the **Marketplace** scene to be active.

### Solution

#### Fix 1: Load Scene Before Running Menu Item
1. Open the scene selector (top of hierarchy)
2. Find and load: **Scenes/Marketplace** (or similar)
3. Once loaded, run: **Velinor** > **Scene Setup** > **Populate Simple Scene (Spatial Grid)**

#### Fix 2: Improve the Script
Create an enhanced version that loads the scene automatically:

Edit `Assets/Scripts/Editor/SimplifiedMarketScene.cs` and replace the `PopulateSimpleScene()` method:

```csharp
[MenuItem("Velinor/Scene Setup/Populate Simple Scene (Spatial Grid)")]
public static void PopulateSimpleScene()
{
    Debug.Log("\n🏗️  CREATING STRUCTURED VELINOR MARKETPLACE\n");

    if (EditorApplication.isUpdating)
    {
        Debug.LogWarning("⚠️  SimplifiedMarketScene: Assets still reimporting. Scene population skipped.");
        return;
    }

    Scene activeScene = SceneManager.GetActiveScene();
    
    // AUTO-LOAD MARKETPLACE SCENE IF NOT ALREADY ACTIVE
    if (activeScene.name != "Marketplace")
    {
        Debug.LogWarning("⚠️  Marketplace scene not active. Searching for it...");
        
        string[] sceneGuids = AssetDatabase.FindAssets("Marketplace t:Scene");
        if (sceneGuids.Length == 0)
        {
            Debug.LogError("❌ Marketplace scene not found in project. Create it first.");
            return;
        }
        
        string scenePath = AssetDatabase.GUIDToAssetPath(sceneGuids[0]);
        Debug.Log($"✅ Loading Marketplace scene from: {scenePath}");
        
        if (EditorSceneManager.SaveScene(activeScene, "", false) == false)
        {
            Debug.LogWarning("⚠️  Could not save current scene. Proceeding anyway.");
        }
        
        EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
        activeScene = SceneManager.GetActiveScene();
    }

    Debug.Log($"✅ Active scene confirmed: {activeScene.name}");
    
    // Rest of the method continues as before...
    // [Include existing code for asset verification and population]
}
```

#### Fix 3: Create a Setup Wizard
Alternatively, create an EditorWindow that guides users:

```csharp
[MenuItem("Velinor/Scene Setup/Auto-Setup Marketplace")]
public static void AutoSetupMarketplace()
{
    // 1. Find or create Marketplace scene
    // 2. Load it
    // 3. Run PopulateSimpleScene()
    // 4. Save the scene
    Debug.Log("✅ Marketplace setup complete!");
}
```

### Quick Workaround
Until you fix the script, manually:
1. Open **Assets/Scenes/Marketplace.unity**
2. Run **Velinor** > **Scene Setup** > **Populate Simple Scene (Spatial Grid)**
3. Scene will populate successfully

---

## Summary: Priority Order

| Error | Severity | Fix Time | Recommendation |
|-------|----------|----------|-----------------|
| **Self-Intersecting Meshes** | 🟡 Low | 5 min | Option 1 (suppress warnings) |
| **Input Manager Deprecation** | 🟠 Medium | 2-4 hours | Plan migration, doesn't block builds |
| **Account API Timeout** | 🟢 Low | 2 min | Option 1 (disable AI Assistant) |
| **Relay Connection Failure** | 🟢 Low | 2 min | Disable if not using multiplayer |
| **Scene Loading Error** | 🟡 Medium | 10 min | Fix 2 (improve the script) |

---

## Next Steps

### Immediate (Today)
- [ ] Suppress mesh warnings (5 min)
- [ ] Disable AI Assistant timeout (2 min)
- [ ] Fix SimplifiedMarketScene script (10 min)

### Short-term (This Week)
- [ ] Plan Input System migration
- [ ] Create Input Actions asset
- [ ] Migrate 2-3 critical scripts

### Long-term (This Month)
- [ ] Complete Input System migration
- [ ] Test with Input System extensively
- [ ] Remove Input Manager from build settings

---

## References

- [Unity Input System Documentation](https://docs.unity3d.com/Packages/com.unity.inputsystem@latest)
- [FBX Import Settings](https://docs.unity3d.com/Manual/FBXImporter-Model.html)
- [AI Toolkit Docs](https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.ai.assistant.html)

