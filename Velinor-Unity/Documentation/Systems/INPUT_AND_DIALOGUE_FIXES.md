# Input System & DialogueManager Fixes - Implementation Guide

## Overview
This document explains the two critical fixes applied to resolve:
1. **NullReferenceException** in PlayerInput when resolving Move bindings
2. **Missing Inspector assignments** in DialogueManager causing warnings

---

## FIX #1: PlayerInput InputActionAsset Assignment

### Problem
```
NullReferenceException while resolving binding 'Move:<Keyboard>/w[KeyboardMouse]' 
in action map 'InputSystem_Actions (UnityEngine.InputSystem.InputActionAsset):Player'
UnityEngine.InputSystem.PlayerInput:OnEnable()
```

**Root Cause:** When PlayerInput component was added to a GameObject, the InputActionAsset reference was not assigned, causing the Input System to fail when trying to resolve bindings.

### Solution
Updated **VelinorGameplaySetup.cs** (line 171-190) to automatically assign and configure PlayerInput:

```csharp
PlayerInput playerInput = player.GetComponent<PlayerInput>();
if (playerInput == null)
{
    playerInput = player.AddComponent<PlayerInput>();
}

// Load and assign the InputActionAsset to prevent NullReferenceException
InputActionAsset inputActionsAsset = AssetDatabase.LoadAssetAtPath<InputActionAsset>(
    "Assets/StarterAssets/InputSystem_Actions.inputactions");

if (inputActionsAsset != null)
{
    playerInput.actions = inputActionsAsset;
    playerInput.defaultControlScheme = "KeyboardMouse";
    playerInput.defaultActionMap = "Player";
    Debug.Log("✓ Assigned InputActionAsset to PlayerInput with 'Player' action map");
}
```

### What This Does
- **Loads** `InputSystem_Actions.inputactions` from `Assets/StarterAssets/`
- **Assigns** it to the PlayerInput component
- **Sets** the correct control scheme ("KeyboardMouse") and action map ("Player")
- **Prevents** the Input System from throwing NullReferenceException

### When It Runs
This fix is automatically applied when you run:
- **Menu:** Velinor → Setup Gameplay Scene (Third Person)
- In the GamplayScene.unity setup

### Affected Scenes
- ✅ GamplayScene.unity (auto-fixed when using Setup menu)
- ⚠️ BuildingPrefab.unity (if using PlayerInput component - requires manual assignment)
- ⚠️ Other scenes using PlayerInput (requires manual assignment OR running setup menu)

### Manual Fix for Other Scenes
If you're adding PlayerInput to another scene:

**Option A: Run the Setup Menu**
1. Open your scene
2. Go to **Velinor → Setup Gameplay Scene (Third Person)**
3. The PlayerInput will be configured automatically

**Option B: Manual Assignment in Inspector**
1. Select the GameObject with PlayerInput component
2. In the Inspector, drag `Assets/StarterAssets/InputSystem_Actions.inputactions` into the **Actions** field
3. Set **Default Control Scheme** to `KeyboardMouse`
4. Set **Default Action Map** to `Player`

---

## FIX #2: DialogueManager Inspector Setup

### Problem
```
[DialogueManager] sharedBeatText is not assigned in Inspector.
[DialogueManager] btnT (Trust button) is not assigned in Inspector.
[DialogueManager] btnO (Observation button) is not assigned in Inspector.
[DialogueManager] btnN (NarrativePresence button) is not assigned in Inspector.
[DialogueManager] btnE (Empathy button) is not assigned in Inspector.
[DialogueManager] txtT (Trust label) is not assigned in Inspector.
[DialogueManager] txtO (Observation label) is not assigned in Inspector.
[DialogueManager] txtN (NarrativePresence label) is not assigned in Inspector.
[DialogueManager] txtE (Empathy label) is not assigned in Inspector.
```

**Root Cause:** DialogueManager has 9 required UI fields (Canvas, TextMeshPro elements, Buttons) that must be assigned in the Inspector. Manual assignment is error-prone.

### Solution
Created **DialogueManagerSetup.cs** - An Editor tool that automatically finds and assigns all UI elements.

**File Location:** `Assets/Editor/DialogueManagerSetup.cs`

### How to Use

#### For BuildingPrefab.unity
1. **Open BuildingPrefab.unity** in the Unity Editor
2. **Go to menu:** Tools → Setup DialogueManager UI
3. The tool will:
   - Find your DialogueManager in the scene
   - Locate the DialogueCanvas
   - Search for all required UI elements by name
   - Assign them using reflection

#### Expected Output
```
✓ Assigned dialogueCanvas to DialogueCanvas
✓ Assigned bodyText
✓ Assigned npcNameText
✓ Assigned sharedBeatText
✓ Assigned btnT (Trust)
✓ Assigned btnO (Observation)
✓ Assigned btnN (NarrativePresence)
✓ Assigned btnE (Empathy)
✓ Assigned txtT (Trust label)
✓ Assigned txtO (Observation label)
✓ Assigned txtN (NarrativePresence label)
✓ Assigned txtE (Empathy label)
```

### Required Hierarchy Structure
For the tool to work, your DialogueCanvas must follow this naming convention:

```
DialogueCanvas (Canvas component)
├─ DialogueBodyText (TextMeshProUGUI)
├─ NPCLineText (TextMeshProUGUI)
├─ SharedBeatText (TextMeshProUGUI)
├─ ChoiceButton_T (Button)
│  └─ Text (TextMeshProUGUI child)
├─ ChoiceButton_O (Button)
│  └─ Text (TextMeshProUGUI child)
├─ ChoiceButton_N (Button)
│  └─ Text (TextMeshProUGUI child)
└─ ChoiceButton_E (Button)
   └─ Text (TextMeshProUGUI child)
```

**Reference:** See `Assets/Scenes/BuildingPrefab_DialogueSetup.md` for detailed UI setup instructions.

### Manual Assignment (Alternative)
If you prefer manual assignment or the tool fails:

1. **Find or create DialogueCanvas** in your scene hierarchy
2. **Select the DialogueManager GameObject**
3. **In the Inspector:**
   - Drag Canvas → **dialogueCanvas** field
   - Drag TextMeshProUGUI objects:
     - DialogueBodyText → **bodyText**
     - NPCLineText → **npcNameText**
     - SharedBeatText → **sharedBeatText**
   - Drag Buttons:
     - ChoiceButton_T → **btnT**
     - ChoiceButton_O → **btnO**
     - ChoiceButton_N → **btnN**
     - ChoiceButton_E → **btnE**
   - Drag Text children of buttons:
     - ChoiceButton_T's Text → **txtT**
     - ChoiceButton_O's Text → **txtO**
     - ChoiceButton_N's Text → **txtN**
     - ChoiceButton_E's Text → **txtE**

---

## Testing Instructions

### Test 1: Verify PlayerInput Fix (GamplayScene)

1. **Open GamplayScene.unity**
2. **Run Setup:** Velinor → Setup Gameplay Scene (Third Person)
3. **Press Play** in the Editor
4. **Expected Results:**
   - ✅ No NullReferenceException in Console
   - ✅ No "Move:<Keyboard>/w" binding errors
   - ✅ WASD keys work to move the player
   - ✅ Movement is smooth and responsive

**Console Output Should Show:**
```
✓ Assigned InputActionAsset to PlayerInput with 'Player' action map
✅ Gameplay Scene setup complete!
🎮 Player: Position (0, 1, 0) - BLUE Capsule
⚠️ Movement: WASD | Sprint: Shift | Jump: Space | Look: Mouse
```

### Test 2: Verify DialogueManager Fix (BuildingPrefab)

1. **Open BuildingPrefab.unity**
2. **Run Setup:** Tools → Setup DialogueManager UI
3. **Check the Console** - Should see all 12 "✓ Assigned" messages
4. **Expected Results:**
   - ✅ No "[DialogueManager]" warnings in Console
   - ✅ All UI fields assigned in the Inspector
   - ✅ DialogueManager.Awake() completes without warnings

**Console Output Should Show:**
```
✓ Assigned dialogueCanvas to DialogueCanvas
✓ Assigned bodyText
✓ Assigned npcNameText
✓ Assigned sharedBeatText
✓ Assigned btnT (Trust)
✓ Assigned btnO (Observation)
✓ Assigned btnN (NarrativePresence)
✓ Assigned btnE (Empathy)
✓ Assigned txtT (Trust label)
✓ Assigned txtO (Observation label)
✓ Assigned txtN (NarrativePresence label)
✓ Assigned txtE (Empathy label)
✅ DialogueManager setup complete!
Assigned 12 UI elements.
```

### Test 3: Run Gameplay with Dialogue

1. **In BuildingPrefab.unity:** Verify all DialogueManager assignments complete
2. **Press Play**
3. **Expected Results:**
   - ✅ No NullReferenceException errors
   - ✅ No InputSystem binding errors
   - ✅ No DialogueManager field warnings
   - ✅ Dialogue UI responds to player choices
   - ✅ WASD movement works in scene
   - ✅ Player can interact with NPCs using 'E' key

---

## Troubleshooting

### Issue: "Could not find InputSystem_Actions.inputactions"
**Solution:**
- Verify file exists at: `Assets/StarterAssets/InputSystem_Actions.inputactions`
- If missing, re-import StarterAssets package from Unity Asset Store
- Run the setup menu again

### Issue: DialogueManagerSetup tool says "DialogueManager not found"
**Solution:**
- Ensure DialogueManager GameObject exists in the scene
- Ensure DialogueManager component is attached to it
- Check that you're running the tool in the correct scene

### Issue: DialogueManagerSetup shows "Could not find DialogueCanvas"
**Solution:**
- Create a Canvas in your scene manually (UI → Canvas)
- Rename it to `DialogueCanvas`
- Create the required UI children following the hierarchy above
- Run the setup tool again

### Issue: Still getting NullReferenceException on Play
**Solution:**
- **Verify InputActionAsset is assigned:**
  1. Select Player GameObject
  2. Check PlayerInput component in Inspector
  3. Ensure **Actions** field is filled with InputSystem_Actions
  4. Ensure **Default Action Map** is set to "Player"
  5. Ensure **Default Control Scheme** is set to "KeyboardMouse"

- **Restart Unity Editor**
  - Sometimes the Input System caches old bindings
  - Close and reopen the project

- **Regenerate C# Wrapper:**
  1. Open `Assets/StarterAssets/InputSystem_Actions.inputactions`
  2. In the Input Actions window, click "Generate C# Class"
  3. Save the generated class
  4. Restart Unity

---

## Summary of Changes

### Files Modified
1. **Assets/Scripts/Editor/VelinorGameplaySetup.cs**
   - Lines 171-190: Added InputActionAsset assignment logic
   - Now ensures PlayerInput has valid InputActions on scene setup

### Files Created
1. **Assets/Editor/DialogueManagerSetup.cs**
   - New Editor tool for automatic UI assignment
   - Accessible via Tools → Setup DialogueManager UI menu
   - Finds and assigns 12 UI elements using reflection

### Reference Documents
- **DIALOGUEMANAGER_CANONICAL_FIELDS.md** - Field reference
- **BuildingPrefab_DialogueSetup.md** - UI hierarchy guide

---

## Next Steps

1. ✅ **Open your scene** (GamplayScene or BuildingPrefab)
2. ✅ **Run the appropriate setup:**
   - For GamplayScene: **Velinor → Setup Gameplay Scene (Third Person)**
   - For BuildingPrefab: **Tools → Setup DialogueManager UI**
3. ✅ **Check the Console** for success messages
4. ✅ **Press Play** and test the fixes
5. ✅ **Verify no errors appear** during gameplay

---

## Questions?

Refer to:
- `DIALOGUEMANAGER_CANONICAL_FIELDS.md` - Exact field definitions
- `BuildingPrefab_DialogueSetup.md` - Detailed UI setup with screenshots/guides
- Unity Input System Documentation: https://docs.unity3d.com/Packages/com.unity.inputsystem@latest/
