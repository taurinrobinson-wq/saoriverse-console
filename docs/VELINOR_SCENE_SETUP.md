# Velinor Narrative Engine - Scene Setup Guide

This guide walks you through integrating StatManager, DialogueManager, and NPCInteraction for the first playable test.

## Phase 1: Project Structure

### 1.1 JSON File Placement

**Option A: Resources Folder (Recommended)**
```
Assets/
  Resources/
    velinor/
      stories/
        sample_story.json          ← DialogueManager loads this
      data/
        npc_state.json             ← StatManager loads this
```

**Option B: StreamingAssets Folder (Alternative)**
```
Assets/
  StreamingAssets/
    velinor/
      stories/
        sample_story.json
      data/
        npc_state.json
```

**How to Choose:**
- **Resources**: Easier integration with `Resources.Load<TextAsset>()`, automatically included in builds
- **StreamingAssets**: Easier to modify post-build, requires additional path handling in DialogueManager

**For this guide, we use Resources (Option A).**

### 1.2 Required JSON Files

**sample_story.json** - Story structure exported from `story_definitions.py`
```
python velinor/stories/build_story.py
# Generates: velinor/stories/sample_story.json
```

**npc_state.json** - Initial NPC state (can be empty or use existing)
```json
{
  "npc_profiles": {
    "Ravi": { "resolve": 0.5, "empathy": 0.6, "memory": 0.5, "nuance": 0.4, "authority": 0.6, "need": 0.3, "trust": 0.7, "skepticism": 0.2 },
    "Nima": { "resolve": 0.7, "empathy": 0.4, "memory": 0.7, "nuance": 0.6, "authority": 0.5, "need": 0.2, "trust": 0.5, "skepticism": 0.6 }
  },
  "influence_map": {
    "Ravi": { "Nima": -0.08 },
    "Nima": { "Ravi": 0.05 }
  },
  "history": []
}
```

**Place both files in the Resources structure above.**

---

## Phase 2: Scene Setup

### 2.1 Create New Scene
1. **File → New Scene** (or Ctrl+N)
2. **Save as**: `Marketplace.unity` (in `Assets/Scenes/`)
3. Keep default Camera and EventSystem

### 2.2 Add StatManager to Scene
1. **Create empty GameObject**: `StatManager`
2. **Attach script**: `Assets/Scripts/Core/StatManager.cs`
3. **Inspector settings**:
   - Make sure it's at root of scene (not nested)
   - No specific serialized fields to configure (loads JSON internally)
4. **Verify**: Scene root should show `StatManager (Script)` component

### 2.3 Add DialogueManager to Scene
1. **Create empty GameObject**: `DialogueManager`
2. **Attach script**: `Assets/Scripts/Core/DialogueManager.cs`
3. **Inspector settings** - Assign these serialized fields:
   - **npcNameText**: Reference to TextMeshProUGUI (we'll create UI next)
   - **bodyText**: Reference to TextMeshProUGUI (we'll create UI next)
   - **choiceButtonContainer**: Reference to Transform (we'll create UI next)
   - **choiceButtonPrefab**: Reference to a button prefab (we'll create UI next)
   - **dialogueCanvasGroup**: Reference to CanvasGroup (we'll create UI next)
   - **dialogueCanvas**: Reference to Canvas (we'll create UI next)

---

## Phase 3: DialogueCanvas UI Setup

### 3.1 Create UI Canvas

1. **Hierarchy → Right-click → UI → Canvas - TextMeshPro**
   - Creates Canvas + TextMeshPro helper objects
   - Rename to: `DialogueCanvas`

2. **Canvas Component Settings**:
   - **Render Mode**: Screen Space - Overlay
   - **Sorting Order**: 100 (above gameplay)

### 3.2 Add CanvasGroup Component

1. **Select DialogueCanvas**
2. **Add Component → CanvasGroup**
3. **Settings**:
   - **Alpha**: 1
   - **Interactable**: true
   - **Blocks Raycasts**: true

### 3.3 Create DialoguePanel (Child of Canvas)

1. **Select DialogueCanvas**
2. **Create → Panel - TextMeshPro**
   - Rename to: `DialoguePanel`

3. **RectTransform Settings**:
   - **Anchors**: stretch (fill canvas)
   - **Offset Left/Right/Top/Bottom**: all 0
   - **Position**: (0, 0, 0)

4. **Image Component**:
   - **Source Image**: white square (built-in)
   - **Color**: Black with ~80% opacity (adjust for readability)
   - **Material**: Default UI Material

### 3.4 Add NPC Name Text (Child of DialoguePanel)

1. **Select DialoguePanel**
2. **Create → Text - TextMeshPro**
   - Rename to: `NPCNameText`

3. **RectTransform Settings**:
   - **Anchors**: Top-Left
   - **Position**: (50, -30, 0)
   - **Size**: (400, 60)

4. **TextMeshProUGUI Component**:
   - **Text**: "NPC Name" (placeholder)
   - **Font Size**: 36
   - **Color**: White
   - **Alignment**: Top-Left
   - **Enable Rich Text**: true

### 3.5 Add Body Text (Child of DialoguePanel)

1. **Select DialoguePanel**
2. **Create → Text - TextMeshPro**
   - Rename to: `BodyText`

3. **RectTransform Settings**:
   - **Anchors**: stretch
   - **Position**: (0, 0, 0)
   - **Offset Left**: 50, **Right**: 50, **Top**: 100, **Bottom**: 200

4. **TextMeshProUGUI Component**:
   - **Text**: "Dialogue text goes here..." (placeholder)
   - **Font Size**: 24
   - **Color**: White
   - **Alignment**: Top-Left
   - **Enable Rich Text**: true
   - **Wrapping**: enabled

### 3.6 Create Choice Button Container (Child of DialoguePanel)

1. **Select DialoguePanel**
2. **Create → Panel**
   - Rename to: `ChoiceButtonContainer`

3. **RectTransform Settings**:
   - **Anchors**: Bottom-Stretch
   - **Position**: (0, 20, 0)
   - **Size**: (width: -100, height: 150)
   - **Offset Left**: 50, **Right**: 50, **Bottom**: 20

4. **Image Component**:
   - **Source Image**: None (transparent background)
   - **Color**: Transparent or None (set alpha to 0)

5. **Layout Group**:
   - **Add Component → Vertical Layout Group**
   - **Child Force Expand**:
     - **Width**: unchecked
     - **Height**: checked
   - **Child Control Size**:
     - **Width**: checked
     - **Height**: unchecked
   - **Spacing**: 10

### 3.7 Create Choice Button Prefab (Child of ChoiceButtonContainer)

1. **Select ChoiceButtonContainer**
2. **Create → Button - TextMeshPro**
   - Rename to: `ChoiceButtonPrefab`

3. **RectTransform Settings**:
   - **Size**: (width: -100, height: 60)
   - **Position**: (0, 0, 0)

4. **Button Component**:
   - **Interactable**: true
   - **Transition**: Color Tint
   - **Normal Color**: (0.7, 0.7, 0.7, 1)
   - **Highlighted Color**: (1, 1, 1, 1)
   - **Pressed Color**: (0.5, 0.5, 0.5, 1)
   - **Selected Color**: (1, 1, 1, 1)

5. **TextMeshProUGUI (Text component inside button)**:
   - **Text**: "Choice Text"
   - **Font Size**: 20
   - **Color**: Black
   - **Alignment**: Center-Middle

6. **Convert to Prefab**:
   - **Drag ChoiceButtonPrefab from Hierarchy to Assets/Resources/Prefabs/**
   - Rename prefab: `ChoiceButtonPrefab.prefab`
   - **Delete the instance from scene** (we only need the prefab reference)

### 3.8 Wire DialogueManager References

1. **Select DialogueManager in Hierarchy**
2. **Inspector → DialogueManager (Script) component**
3. **Assign serialized fields**:
   - **NPC Name Text**: Drag `NPCNameText` from Hierarchy
   - **Body Text**: Drag `BodyText` from Hierarchy
   - **Choice Button Container**: Drag `ChoiceButtonContainer` from Hierarchy
   - **Choice Button Prefab**: Drag `ChoiceButtonPrefab` from Assets/Resources/Prefabs/
   - **Dialogue Canvas Group**: Drag `DialogueCanvas` (CanvasGroup) from Hierarchy
   - **Dialogue Canvas**: Drag `DialogueCanvas` (Canvas) from Hierarchy

4. **Verify all references are assigned** (no empty slots)

---

## Phase 4: Player Setup

### 4.1 Player Collider Configuration

**Ensure Player GameObject has:**
1. **CharacterController component** (for movement)
2. **Collider component set to trigger** for NPC proximity detection:
   - **Collider Type**: Capsule or Sphere
   - **Radius/Height**: Fits player size (~1-2 units)
   - **Is Trigger**: **checked**
   - **Tag**: "Player" (create tag if needed)

**Example hierarchy:**
```
Player
├── CharacterController (for movement)
├── CapsuleCollider (is Trigger, tag: "Player")
├── Camera
└── ... other components
```

### 4.2 Create or Locate Player GameObject

If you don't have a Player yet:
1. **Create → Capsule**
   - Rename: `Player`
2. **Add Component → CharacterController**
3. **Add CapsuleCollider** (the built-in one):
   - **Is Trigger**: checked
   - **Tag**: "Player"
4. **Add Camera** as child:
   - Position: (0, 0.6, 0) (head height)
   - Create script to handle mouse look and WASD input

---

## Phase 5: NPC Setup

### 5.1 Create NPC GameObject (Ravi Example)

1. **Create → Cube**
   - Rename: `Ravi`
   - **Position**: (5, 1, 0)
   - **Scale**: (1, 2, 1)
   - **Color**: Purple or any distinct color

2. **Add Components**:
   - **BoxCollider** (NOT trigger, for static collision)
   - **SphereCollider** (NEW, for proximity trigger):
     - **Radius**: 3
     - **Is Trigger**: **checked**
     - **Tag**: (leave empty or use "NPC")

3. **Attach NPCInteraction script**:
   - **Add Component → NPCInteraction**

4. **Configure NPCInteraction serialized fields**:
   - **NPC Id**: `"Ravi"` (must match npc_profiles.json key)
   - **Starting Passage Id**: `"ravi_dialogue"` (must match passage_id in sample_story.json)
   - **Interaction Range**: `3.0`

### 5.2 Create Second NPC (Nima Example)

1. **Create → Cube**
   - Rename: `Nima`
   - **Position**: (8, 1, 0)
   - **Scale**: (1, 2, 1)
   - **Color**: Different from Ravi (blue or green)

2. **Add Components**:
   - **BoxCollider** (NOT trigger)
   - **SphereCollider** (trigger):
     - **Radius**: 3
     - **Is Trigger**: checked

3. **Attach NPCInteraction script**:
   - **Add Component → NPCInteraction**

4. **Configure NPCInteraction serialized fields**:
   - **NPC Id**: `"Nima"` (must match npc_profiles.json key)
   - **Starting Passage Id**: `"nima_dialogue"` (must match passage_id in sample_story.json)
   - **Interaction Range**: `3.0`

---

## Phase 6: Integration Checklist

### ✅ File Placement
- [ ] `Assets/Resources/velinor/stories/sample_story.json` exists
- [ ] `Assets/Resources/velinor/data/npc_state.json` exists
- [ ] Both files can be loaded via `Resources.Load<TextAsset>()`

### ✅ Scene Hierarchy
- [ ] `StatManager` GameObject in root with StatManager script
- [ ] `DialogueManager` GameObject in root with DialogueManager script
- [ ] `DialogueCanvas` with CanvasGroup component
- [ ] UI elements under DialogueCanvas:
  - [ ] `DialoguePanel`
  - [ ] `NPCNameText` (TextMeshProUGUI)
  - [ ] `BodyText` (TextMeshProUGUI)
  - [ ] `ChoiceButtonContainer` (empty panel with VerticalLayoutGroup)
- [ ] `ChoiceButtonPrefab` in Assets/Resources/Prefabs/

### ✅ DialogueManager Wiring
- [ ] **NPC Name Text** → NPCNameText assigned
- [ ] **Body Text** → BodyText assigned
- [ ] **Choice Button Container** → ChoiceButtonContainer assigned
- [ ] **Choice Button Prefab** → ChoiceButtonPrefab.prefab assigned
- [ ] **Dialogue Canvas Group** → DialogueCanvas (CanvasGroup) assigned
- [ ] **Dialogue Canvas** → DialogueCanvas (Canvas) assigned

### ✅ Player Configuration
- [ ] Player GameObject exists with tag "Player"
- [ ] Player has **CharacterController** component
- [ ] Player has **CapsuleCollider** with:
  - [ ] **Is Trigger**: checked
  - [ ] **Tag**: "Player"

### ✅ NPC Configuration (for each NPC)
- [ ] NPC GameObject exists (e.g., Ravi)
- [ ] NPC has **BoxCollider** (NOT trigger, for visual collision)
- [ ] NPC has **SphereCollider** with:
  - [ ] **Is Trigger**: checked
  - [ ] **Radius**: 3
- [ ] NPC has **NPCInteraction** script with:
  - [ ] **NPC Id**: matches npc_profiles.json key (e.g., "Ravi")
  - [ ] **Starting Passage Id**: matches passage_id in sample_story.json
  - [ ] **Interaction Range**: 3.0

### ✅ Code Verification
- [ ] StatManager.cs: 0 compilation errors
- [ ] DialogueManager.cs: 0 compilation errors
- [ ] NPCInteraction.cs: 0 compilation errors
- [ ] InteractionUI singleton exists (for ShowPrompt/HidePrompt)
- [ ] PlayerController script handles WASD input

---

## Phase 7: First Test

### 7.1 Pre-Test Verification
1. Open the Marketplace scene
2. Press Play in Unity Editor
3. **Verify Console shows**:
   - `[StatManager] Singleton initialized`
   - `[StatManager] State loaded from npc_state.json`
   - `[DialogueManager] Story loaded successfully. X passages found.`

### 7.2 Gameplay Test
1. Move player towards an NPC (WASD)
2. **Verify**:
   - Prompt appears: "Press E to talk to [NPC Name]"
3. Press E
4. **Verify**:
   - DialoguePanel appears
   - NPC name displayed
   - Dialogue text shown
   - Choice buttons rendered
5. Click a choice button
6. **Verify**:
   - Passage changes
   - New text and buttons appear
   - Stats are being applied (check Console logs)
7. Continue choices until dialogue ends
8. **Verify**:
   - DialoguePanel disappears
   - Player can move again
   - Cursor is locked

### 7.3 Debug Output Expected
```
[NPCInteraction] Player entered range of NPC 'Ravi'
[DialogueManager] Dialogue started with NPC 'Ravi' at passage 'ravi_dialogue'
[DialogueManager] Displayed passage: ravi_dialogue
[DialogueManager] Created choice button: Step toward them openly
[DialogueManager] Choice selected: Step toward them openly
[DialogueManager] Applied tone effect: courage += 0.15
[DialogueManager] Applied resonance: Ravi += 0.2
[StatManager] Encounter logged. History length: 1
[DialogueManager] Displayed passage: meet_ravi_nima
```

---

## Phase 8: Troubleshooting

### "DialogueManager not found" error
- **Cause**: DialogueManager GameObject not in scene
- **Fix**: Add DialogueManager GameObject with DialogueManager script attached

### "Story loaded but no passages found"
- **Cause**: sample_story.json not in correct path or not properly formatted
- **Fix**: Verify JSON is at `Assets/Resources/velinor/stories/sample_story.json`
- **Verify**: Run `python velinor/stories/build_story.py` to regenerate JSON

### "Dialogue panel doesn't appear"
- **Cause**: Serialized field references not assigned in DialogueManager
- **Fix**: Check Inspector → DialogueManager component, assign all 6 UI references

### "E-key doesn't trigger dialogue"
- **Cause**: Player collider not trigger, or missing "Player" tag
- **Fix**: Verify NPC SphereCollider has "Is Trigger" checked
- **Fix**: Verify Player has tag "Player"

### "Buttons don't appear in dialogue"
- **Cause**: choiceButtonPrefab not assigned or prefab missing Button component
- **Fix**: Ensure ChoiceButtonPrefab is a prefab with Button + TextMeshProUGUI
- **Fix**: Assign prefab to DialogueManager.choiceButtonPrefab

### "Player can't move during dialogue"
- **Cause**: PlayerController not disabled in DialogueManager.StartDialogue()
- **Fix**: Verify PlayerController script exists and is enabled
- **Fix**: Check DialogueManager calls `playerController.enabled = false`

### "JSON deserialization error"
- **Cause**: JSON format doesn't match expected schema
- **Fix**: Regenerate sample_story.json from story_definitions.py
- **Fix**: Check npc_state.json follows REMNANTS key format (resolve, empathy, etc.)

---

## Summary

**When completed, you have:**
1. StatManager managing all narrative state (TONE, REMNANTS, cascades)
2. DialogueManager displaying story and applying player choices
3. NPCInteraction triggering dialogue when player interacts
4. UI system showing passages and allowing choice selection
5. JSON files as authoritative sources for story and NPC state

**No simplification. Full architecture preserved.**

Ready to test the first complete dialogue flow!
