# Velinor-Unity: Phase 1 Implementation Checklist

**Goal:** Establish core systems and scaffolding for the vertical slice.  
**Duration:** Weeks 1-2  
**Deliverable:** A test scene where player can walk, interact, trigger dialogue, and update emotional state.

---

## PHASE 1.1: Core Architecture Setup (Week 1)

### ☐ Scene Setup

- [ ] Create a new scene: `Assets/Scenes/TestScene.unity`
- [ ] Add main camera (third-person perspective)
- [ ] Add empty GameObject for player (tag it "Player")
- [ ] Add Canvas for UI (dialogue, prompts, Codex feedback)

### ☐ Player Controller Implementation

- [ ] Create PlayerController.cs in Assets/Scripts/Core/ (already provided)
- [ ] Add CharacterController component to player GameObject
- [ ] Create simple player model (cube or low-poly character mesh)
- [ ] Wire up WASD movement
- [ ] Test movement in play mode

**Test Checklist:**
- [ ] Player can move forward/backward
- [ ] Player can strafe left/right
- [ ] Player rotates toward movement direction
- [ ] Camera follows smoothly

### ☐ Camera System

- [ ] Create CameraFollow.cs script
- [ ] Position camera over-the-shoulder (not first-person)
- [ ] Add smooth damping/follow
- [ ] Test camera collision (avoid clipping into walls)

**Test Checklist:**
- [ ] Camera is positioned over-the-shoulder
- [ ] Camera follows player smoothly
- [ ] Camera doesn't clip into geometry

### ☐ Interaction System

- [ ] Implement IInteractable interface in Core scripts
- [ ] Create simple InteractionPrompt UI (small icon or text near objects)
- [ ] Add E key input for interaction
- [ ] Test interaction raycast

**Test Checklist:**
- [ ] Raycast detects objects in front of player
- [ ] Interaction prompt appears when near object
- [ ] E key triggers interaction

### ☐ CodexManager (Emotional State)

- [ ] Implement CodexSystem.cs (already provided)
- [ ] Create CodexManager GameObject in scene
- [ ] Set up emotional tag system
- [ ] Test tag addition/removal via console or debug UI

**Test Checklist:**
- [ ] Can add/remove tags programmatically
- [ ] Resonance updates correctly
- [ ] Events fire when tags change

---

## PHASE 1.2: Dialogue System (Week 1)

### ☐ Dialogue UI Setup

- [ ] Create DialogueUIPanel in Canvas
  - [ ] Speaker name text field
  - [ ] Dialogue text field
  - [ ] Choices container (for buttons)
- [ ] Style with minimal aesthetic (diegetic, readable)

### ☐ DialogueManager Implementation

- [ ] Implement DialogueSystem.cs (already provided)
- [ ] Connect to UI panel references
- [ ] Test dialogue playback with hardcoded sequence

**Test Checklist:**
- [ ] Dialogue appears on screen
- [ ] Text reveals character-by-character
- [ ] Dialogue auto-advances after delay
- [ ] Dialogue closes on final line

### ☐ Emotional Tag Integration

- [ ] Dialogue lines emit emotional tags
- [ ] Tags are added to Codex when dialogue plays
- [ ] Debug output confirms tag additions

**Test Checklist:**
- [ ] Dialogue line says "tag: Empathy"
- [ ] CodexManager receives tag addition
- [ ] Resonance updates

### ☐ Choice System (Optional for Week 1)

- [ ] Create dialogue choice buttons
- [ ] Player can select from multiple responses
- [ ] Selection triggers appropriate dialogue branch and tags

**Test Checklist:**
- [ ] Choice buttons appear
- [ ] Selecting choice advances to correct line
- [ ] Tags from choice are applied

---

## PHASE 1.3: Pedestal System (Week 1-2)

### ☐ Pedestal Prefab Creation

- [ ] Create Pedestal.cs (already provided)
- [ ] Create Pedestal GameObject prefab
  - [ ] 3D model (simple stone/metal base)
  - [ ] Light component (for state visualization)
  - [ ] Particle system (for activation effects)
- [ ] Add Pedestal script to GameObject

### ☐ Pedestal Visual States

- [ ] Implement dormant state (dim, no particles)
- [ ] Implement flickering state (pulsing light, faint glyph)
- [ ] Implement active state (bright, particles, sound)
- [ ] Implement spent state (stable, warm glow)

**Test Checklist:**
- [ ] Add pedestal to test scene
- [ ] Manually set required tags
- [ ] Verify visual transitions

### ☐ Codex-Pedestal Integration

- [ ] Pedestal queries CodexManager to check activation requirements
- [ ] Pedestal awakens when player has correct tags
- [ ] Pedestal updates state reactively as tags are added

**Test Checklist:**
- [ ] Dormant pedestal in scene
- [ ] Add matching tag to Codex
- [ ] Pedestal transitions to flickering/active
- [ ] When player approaches, pedestal responds

### ☐ Interaction with Pedestal

- [ ] Pedestal implements IInteractable
- [ ] Player can press E near active pedestal
- [ ] Interaction triggers glyph chamber transition

**Test Checklist:**
- [ ] E key near active pedestal triggers interaction
- [ ] Console logs "Pedestal activated"

---

## PHASE 1.4: Glyph Chamber System (Week 2)

### ☐ GlyphChamberManager Implementation

- [ ] Implement GlyphChamber.cs (already provided)
- [ ] Create manager GameObject in scene
- [ ] Set up fade canvas
- [ ] Test basic fade in/out

**Test Checklist:**
- [ ] Screen fades out when entering chamber
- [ ] Screen fades back in after chamber

### ☐ Chamber Scene Creation

- [ ] Create new scene: `Assets/Scenes/GlyphChamber_Test.unity`
- [ ] Add simple geometry (floating platforms, abstract shapes)
- [ ] Add lighting (atmospheric, emotional)
- [ ] Add ChamberController script

**Test Checklist:**
- [ ] Chamber scene loads without errors
- [ ] Scene is visually distinct from world

### ☐ Chamber Sequence

- [ ] Implement basic chamber sequence (3-5 second duration)
- [ ] Add optional ambient effects (fog, particles, audio)
- [ ] Test full transition loop: World → Fade → Chamber → Fade → World

**Test Checklist:**
- [ ] Full chamber experience takes 5-10 seconds
- [ ] Player returns to exact position in world
- [ ] Glyph is marked as resolved

---

## PHASE 1.5: Save/Load System (Week 2)

### ☐ Save State Structure

- [ ] Define GameSaveState class (from DATA_SCHEMA.md)
- [ ] Implement serialization (CodexState → JSON)
- [ ] Test save to disk

**Test Checklist:**
- [ ] Can save CodexState to file
- [ ] JSON is readable and well-formatted

### ☐ Load System

- [ ] Implement load from disk
- [ ] Restore CodexState from JSON
- [ ] Restore scene state

**Test Checklist:**
- [ ] Can load saved state
- [ ] Restored tags match original
- [ ] Pedestal states match

---

## Integration Test: Full Loop (Week 2)

### Step-by-Step Walkthrough

1. **Scene 1: Player enters test scene**
   - Player spawns at origin
   - Can walk and look around
   - Sees dormant pedestal in distance

2. **Scene 2: Player finds NPC**
   - Player approaches NPC
   - E key triggers dialogue
   - NPC tells emotional story
   - Dialogue emits "Grief" tag

3. **Scene 3: Codex Resonates**
   - Grief tag added to Codex
   - Nearby pedestal flickers to life
   - Resonance UI shows update

4. **Scene 4: Pedestal Activation**
   - Player approaches pedestal
   - Pedestal transitions to active (bright, particles)
   - Interaction prompt appears

5. **Scene 5: Glyph Chamber**
   - Player presses E
   - Screen fades out
   - Chamber scene loads
   - Camera pans through symbolic space
   - Audio plays

6. **Scene 6: Return to World**
   - Chamber fades out
   - Player back in original world
   - Pedestal is now spent (stable, warm)
   - New tag in Codex ("Sorrow")

**Success Criteria:**
- [ ] Full loop completes without errors
- [ ] Emotional resonance drives pedestal activation
- [ ] World state persists after chamber

---

## Code/Asset Checklist

### Already Provided

- [x] CodexSystem.cs
- [x] Pedestal.cs
- [x] GlyphChamber.cs
- [x] DialogueSystem.cs
- [x] PlayerController.cs
- [x] DATA_SCHEMA.md

### Need to Create

- [ ] CameraFollow.cs
- [ ] InteractionPrompt.cs
- [ ] TestScene.unity
- [ ] Player prefab with animator
- [ ] Pedestal prefab with models
- [ ] GlyphChamber_Test scene
- [ ] Simple NPC model or sprite

### Need to Configure

- [ ] Player input bindings (WASD, E, etc.)
- [ ] Camera settings (distance, height, smoothing)
- [ ] Pedestal required tags (match dialogue emissions)
- [ ] UI styling (fonts, colors, layout)

---

## Debugging Tips

### Console Checks

```csharp
// Check if CodexManager is active
Debug.Log(CodexManager.Instance.State.ActiveTags.Count);

// Check pedestal state
Debug.Log($"Pedestal state: {pedestal.CurrentState}");

// Check resonance
Debug.Log($"Resonance: {CodexManager.Instance.State.ResonanceLevel}");
```

### Visual Debugging

- Add gizmo drawing to show pedestal activation radius (already in Pedestal.cs)
- Add text overlay showing current tags
- Add color coding to pedestals (green = active, yellow = flickering, red = dormant)

### Common Issues

1. **Pedestal doesn't activate:**
   - Check that dialogue is emitting correct tags
   - Check that required tags match emitted tags
   - Check player is within activation radius

2. **Chamber doesn't load:**
   - Verify chamber scene name matches GlyphChamberManager prefix
   - Check scene is added to Build Settings

3. **Dialogue doesn't appear:**
   - Check DialogueManager is in scene
   - Check UI panel references are assigned
   - Check TextMeshPro is imported

---

## Next Steps After Phase 1

Once this checklist is complete, you have:

- ✅ Working player movement
- ✅ Functional dialogue system
- ✅ Codex emotional state tracking
- ✅ Pedestal activation logic
- ✅ Glyph chamber transitions
- ✅ Save/load infrastructure

**Phase 2:** Block out the Market Ruins environment and populate with real NPCs and pedestals.

