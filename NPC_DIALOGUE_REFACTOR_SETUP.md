# NPC Dialogue Architecture Refactor - Complete Setup Guide

## ✅ COMPLETED CODE CHANGES

The following scripts have been created/updated:

### New Scripts
1. **Assets/Scripts/Core/NPCDialogueDriver.cs** ✓
   - Generic dialogue trigger (replaces SaoriNPC functionality)
   - Configurable JSON file loading
   - Multi-NPC scene support
   - All original billboard/collider/scale features

2. **Assets/Scripts/Core/NPCController.cs** ✓
   - Movement driver for NPCs (no input handling)
   - Methods: MoveTo(), LookAt(), StopMovement(), PlayAnimation()
   - Animator integration
   - CharacterController physics

### Modified Scripts
1. **Assets/Scripts/Core/DialogueManager.cs** ✓
   - Added: `StartDialogue(TextAsset jsonFile, string conversationId, string npcName, bool isMultiNpcScene, ...)`
   - Maintains backward compatibility
   - Supports TextAsset-based dialogue loading

2. **Assets/Scripts/UI/DialogueUIController.cs** ✓
   - Updated to use NPCDialogueDriver
   - Falls back to legacy SaoriNPC if needed
   - Preserves all existing functionality

---

## 🎯 MANUAL SETUP REQUIRED IN UNITY EDITOR

### Step 1: Create NPCController Prefab
1. Open Project window → Assets/Prefabs
2. Find **Player.prefab** and **duplicate it**
3. Rename duplicate to **NPCController.prefab**
4. Double-click NPCController.prefab to open it for editing
5. In the Hierarchy, select the root gameobject (NPCController)
6. In Inspector, **remove these components**:
   - VelinorPlayerController
   - VelinorStarterAssetsInputs
   - Keep: CharacterController, Animator, Mesh Renderer
7. **Add** NPCController.cs component (drag script or Add Component → Scripts/Core/NPCController)
8. Configure in Inspector:
   - Move Speed: 2.0
   - Rotation Speed: 5.0
   - Ground Layers: Default (or your NPC layer)
9. Change material color to differentiate from player:
   - Select mesh child object
   - Change material color (e.g., blue tint instead of player's default)
10. Save the prefab (Ctrl+S)

### Step 2: Setup Saori Prefab
1. Find Saori prefab in scene or project (likely in Prefabs folder or inside a scene)
2. Open it for editing (double-click or "Open Prefab")
3. Select the Saori gameobject
4. In Inspector, **remove** SaoriNPC component (right-click → Remove Component)
5. **Add** NPCDialogueDriver component (Add Component → Scripts/Core/NPCDialogueDriver)
6. Configure NPCDialogueDriver fields:
   - **Dialogue JSON**: Drag sample_story.json from Assets/Resources/velinor/stories
   - **Conversation ID**: `saori_encounter_01`
   - **NPC Name**: `Saori`
   - **Start Passage ID**: `desert_intro`
   - **Is Multi NPC Scene**: false
   - **NPC Controller**: Drag NPCController prefab instance (or create instance in scene)
   - **Enable Billboard Effect**: true
   - **Scale/Collider settings**: Keep existing defaults

7. Configure Transform:
   - Keep existing position/scale/rotation
   - Position Y should be ~0.9 to stand on ground
   - Scale should be ~1.8x for Asuna model

8. Save prefab (Ctrl+S)

### Step 3: Setup InsideMarket_00 Scene
1. Open Scenes/InsideMarket_00.unity
2. Find or create Saori gameobject in scene
3. If using prefab instance:
   - Either use Saori prefab from step 2 above, OR
   - Manually add NPCDialogueDriver + NPCController to existing Saori in scene
4. Verify Saori has these components:
   - NPCDialogueDriver (configured as above)
   - NPCController (movement driver)
   - Capsule Collider (for interaction)
   - Animator
5. Test:
   - Press Play
   - Walk to Saori
   - Press E to trigger dialogue
   - Verify sample_story.json loads and first passage displays

### Step 4: Setup Other NPCs (Nima, Ravi, Willy, Kaelen)
Repeat process for each NPC:
- **Nima**: 
  - dialogueJson: nima_encounter_01.json
  - conversationId: nima_encounter_01
  - npcName: Nima
  
- **Ravi**:
  - dialogueJson: ravi_encounter_01.json (if converted to new format)
  - conversationId: ravi_encounter_01
  - npcName: Ravi

- **Willy**:
  - dialogueJson: willy_glyph_01.json
  - conversationId: willy_glyph_01
  - npcName: Willy

- **Kaelen**:
  - dialogueJson: kaelen_confession_01.json
  - conversationId: kaelen_confession_01
  - npcName: Kaelen

### Step 5: Multi-NPC Scenes (e.g., ravi_nima_market_discovery)
For scenes with multiple NPCs in same dialogue:
1. Create/duplicate scene with both Ravi and Nima
2. Add NPCDialogueDriver to both:
   - Both use **same JSON file**: ravi_nima_market_discovery.json
   - Both use **same conversationId**: ravi_nima_market_discovery
   - **Different npcName**: "Ravi" vs "Nima"
   - Both set **isMultiNpcScene: true**
3. Dialogue system will track activeNpcId per interaction
4. REMNANTS effects targeting "activeNpcId" will affect whoever initiated dialogue
5. Specific NPC names in effects (e.g., "Ravi") still work as side effects

---

## 🧪 TESTING CHECKLIST

- [ ] Saori dialogue triggers on E key press
- [ ] Dialogue text displays correctly
- [ ] T/O/N/E buttons appear and respond to clicks
- [ ] NPC speaker name shows correctly
- [ ] Dialogue transitions between passages
- [ ] Remnants stats update (check StatManager)
- [ ] Nima/Ravi encounters work individually
- [ ] Multi-NPC scene (Ravi + Nima) works together
- [ ] NPC can move with NPCController.MoveTo()
- [ ] NPC animations play (walk, idle, etc.)

---

## 📝 BACKWARD COMPATIBILITY

- **SaoriNPC still works** in legacy scenes
- **New NPCDialogueDriver** recommended for new content
- **DialogueManager** supports both old and new methods
- **No breaking changes** to existing dialogue system

---

## 🔗 NEXT STEPS

Once manual setup complete:
1. Format remaining dialogue files (nima_encounter_02.json, ravi_encounter_01.json) to new beats format
2. Wire up sample_story.json with full canonical TONE/REMNANTS mappings
3. Test full narrative flow with player stat tracking
4. Implement NPC movement animations for entrances/exits
5. Add system triggers for NPC-specific events (glyph discoveries, flags, etc.)

---

## ❓ TROUBLESHOOTING

**"NPCDialogueDriver not found" error in DialogueUIController:**
- This is a Unity compilation cache issue
- Open the project in Editor, wait for recompile
- Errors should resolve automatically

**"Dialogue JSON not loading":**
- Verify dialogueJson field is assigned in Inspector (drag TextAsset)
- Check conversationId matches JSON passage.conversationId field
- Check startPassageId exists in JSON

**"NPC not moving":**
- Verify NPCController component is assigned to npcController field
- Check CharacterController is enabled
- Ensure NPCController has valid ground layers configured

**"Interaction not triggering":**
- Verify NPCDialogueDriver implements IInteractable
- Check CapsuleCollider is enabled and not a trigger
- Verify player can raycast to NPC (use gizmo debug)

---

## 📚 KEY CONCEPTS

### activeNpcId vs active_speaker
- **activeNpcId**: Which NPC initiated dialogue (stored in DialogueManager)
- **active_speaker**: Who is currently speaking (in JSON passage)
- REMNANTS effects targeting "activeNpcId" affect the NPC who started dialogue
- Effects targeting "Ravi" or "Nima" by name work regardless of activeNpcId

### Dialogue Loading Paths
1. **Legacy**: DialogueManager.StartDialogue(npcId, startPid, storyPath)
2. **New**: DialogueManager.StartDialogue(TextAsset, conversationId, npcName, isMultiNpc)
3. NPCDialogueDriver auto-chooses based on CanLoadFromTextAsset()

### Conversation Grouping
- conversationId groups related passages
- Same JSON file can have multiple conversations
- Example: ravi_nima_market_discovery.json has one conversation with both NPCs
