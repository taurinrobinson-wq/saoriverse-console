# 🎭 VELINOR SYSTEMS INTEGRATION GUIDE

**Status**: Full Suite (9 Scripts + 1 Shader) Ready for Integration  
**Target**: MachinesCave.unity and MachinesCave_02.unity  
**Last Updated**: [Session Date]

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Setup Checklist](#setup-checklist)
3. [Memory Sequence System](#memory-sequence-system)
4. [Machine Network System](#machine-network-system)
5. [Ambient Audio Layering](#ambient-audio-layering)
6. [Camera Shake System](#camera-shake-system)
7. [Cable Glow Animation](#cable-glow-animation)
8. [Glyph Resonance Shader](#glyph-resonance-shader)
9. [Machine Overload System](#machine-overload-system)
10. [Glyph Combination UI](#glyph-combination-ui)
11. [Ritual Sequence System](#ritual-sequence-system)
12. [Integration Examples](#integration-examples)
13. [Testing Checklist](#testing-checklist)

---

## 🎯 SYSTEM OVERVIEW

This suite adds **narrative pacing**, **environmental responsiveness**, **audiovisual impact**, and **ritual logic** to Velinor.

| System | Purpose | Key Script | Priority |
|--------|---------|-----------|----------|
| **Memory Sequence** | Camera pans, fade visions, glyph moments | MemorySequence.cs | Medium |
| **Machine Network** | Power cascades, chain reactions, multi-machine logic | MachineNode.cs | High |
| **Ambient Audio** | Layered soundscapes based on location/state | AmbientLayerController.cs | Medium |
| **Camera Shake** | Rumble feedback for events (singleton) | CameraShake.cs | High |
| **Cable Glow** | Animated conduit effects | CableGlow.cs | Low |
| **Glyph Resonance** | Shader-based supernatural pulsing | GlyphResonance.shader | Low |
| **Machine Overload** | Danger states, sparks, shutdowns, cascades | MachineOverload.cs | High |
| **Glyph Combination UI** | Puzzle feedback overlay | GlyphCombinationUI.cs | Medium |
| **Ritual Sequence** | Multi-step chamber logic, ordered puzzles | RitualSequence.cs | High |

---

## ✅ SETUP CHECKLIST

**Pre-Integration Steps:**

- [ ] All scripts copied to `Assets/Scripts/`
- [ ] GlyphResonance.shader copied to `Assets/Shaders/` (create folder if missing)
- [ ] Audio files imported (if needed)
- [ ] Scenes opened (MachinesCave.unity)

**Singletons (Scene-Level Setup):**

- [ ] CameraShake.cs added to Main Camera
- [ ] SceneTransitionManager.cs on persistent GameObject
- [ ] AmbientLayerController.cs on Scene Manager or persistent GameObject
- [ ] SceneGraph.cs on persistent GameObject (optional)

**Per-Machine Setup:**

- [ ] MachineNode.cs on each machine GameObject
- [ ] MachineOverload.cs on each machine GameObject
- [ ] CableGlow.cs on cable sprites
- [ ] GlyphVFX.cs on glyph sprites

**Per-Chamber Setup:**

- [ ] RitualSequence.cs on chamber GameObject
- [ ] GlyphCombinationUI.cs on Canvas
- [ ] DoorController.cs on door GameObject
- [ ] MemorySequence.cs on artifact/trigger

---

## 🧠 MEMORY SEQUENCE SYSTEM

**Purpose**: Narrative camera sequences with fade effects. Used for:

- Glyph visions (camera zoom + fade to white)
- Chamber revelations
- Emotional beats
- Environmental freeze moments

### Setup Steps

1. **Assign to Artifact/Trigger**
   - Select artifact GameObject (e.g., "GlyphArtifact" in chamber)
   - **Add Component** → MemorySequence.cs
   - In Inspector:
     - **Main Camera**: Drag Main Camera
     - **Fade Canvas**: Drag your FadeCanvas (from SceneTransitionManager)
     - **Memory Sound**: Optional AudioSource for vision audio
     - **Zoom Amount**: 2-3 (how much to zoom)
     - **Zoom Duration**: 1.5 (seconds)
     - **Fade Duration**: 1.0 (seconds)
     - **Freeze Player**: true (lock movement during vision)

2. **Trigger from GlyphPanel or Interaction**

   ```csharp
   // In GlyphPanel.cs or similar:
   private MemorySequence memorySequence;

   void Awake()
   {
       memorySequence = GetComponent<MemorySequence>();
   }

   void ActivateGlyph()
   {
       if (memorySequence != null)
           memorySequence.StartSequence();
   }
   ```

3. **Test**
   - Press E near artifact → should fade to white, freeze player, then return

### Properties Reference

| Property | Default | Purpose |
|----------|---------|---------|
| zoomAmount | 2f | Target camera size during zoom |
| zoomDuration | 1.5f | How long zoom takes |
| fadeDuration | 1f | How long fade takes |
| freezePlayer | true | Lock player movement during sequence |

---

## 🔌 MACHINE NETWORK SYSTEM

**Purpose**: Chain power through multiple machines. One machine powers another, which powers a door, etc.

### Setup Steps

1. **Add MachineNode to Each Machine**
   - Select machine GameObject
   - **Add Component** → MachineNode.cs
   - In Inspector:
     - **Is Powered**: false (starts unpowered)
     - **Outputs**: Array of MachineNode references (drag other machines)
     - **Power Particles**: Optional ParticleSystem
     - **Glow Light**: Optional Light component
     - **Power Sound**: Optional AudioSource

2. **Create Machine Chain**
   - Machine A → Outputs: [Machine B]
   - Machine B → Outputs: [Machine C, Door]
   - Door → Outputs: [] (end of chain)

3. **Trigger PowerUp from Glyph or Puzzle**

   ```csharp
   // In GlyphPanel.cs or similar:
   private MachineNode linkedMachine;

   void ActivateGlyph()
   {
       if (linkedMachine != null)
           linkedMachine.PowerUp();
   }
   ```

4. **Test**
   - Activate glyph → Machine A lights up
   - Machine A powers Machine B
   - Chain continues to door

### Properties Reference

| Property | Default | Purpose |
|----------|---------|---------|
| isPowered | false | Current power state |
| outputs | [] | Machines to power when this activates |
| powerParticles | null | VFX when powering up |
| glowLight | null | Light to enable on power |
| powerSound | null | Audio when powering |

---

## 🎵 AMBIENT AUDIO LAYERING

**Purpose**: Dynamic soundscapes. Different audio layers fade in/out based on location or chamber state.

### Setup Steps

1. **Create Scene Manager or use existing**
   - Select or create "SceneManager" GameObject
   - **Add Component** → AmbientLayerController.cs

2. **Assign Audio Sources**
   - In Inspector:
     - **Base Ambience**: Drag AudioSource with cave hum (looping)
     - **Machine Hum**: Drag AudioSource (looping)
     - **Chamber Tone**: Drag AudioSource (looping)
     - **Glyph Whisper**: Drag AudioSource (looping)
   - All should have **Loop** enabled
   - Set **volume = 0** initially

3. **Set Fade Speed**
   - **Fade Speed**: 2-3 (how quickly layers fade in/out)

4. **Trigger from Systems**

   ```csharp
   // In MachineNode.cs when powering up:
   ambientController.SetLayer("Machine", true);

   // In RitualSequence.cs:
   ambientController.SetLayer("Glyph", true);
   ambientController.SetLayer("Chamber", true);
   ```

5. **Test**
   - Move near machine → machine hum fades in
   - Leave machine → machine hum fades out
   - Activate glyph → glyph whisper fades in

### Methods Reference

```csharp
// Activate a layer (fade in)
ambientController.SetLayer("Machine", true);

// Deactivate a layer (fade out)
ambientController.SetLayer("Machine", false);

// Reset all layers to silent
ambientController.ResetAllLayers();
```

---

## 📷 CAMERA SHAKE SYSTEM

**Purpose**: Rumble feedback for machine activation, overload, chamber power surges.  
**Pattern**: Singleton (use `CameraShake.Instance.Shake()` from anywhere)

### Setup Steps

1. **Add to Main Camera**
   - Select **Main Camera** GameObject
   - **Add Component** → CameraShake.cs
   - In Inspector:
     - **Default Duration**: 0.4 (seconds)
     - **Default Magnitude**: 0.2 (intensity 0-1)

2. **Set as Singleton** (script handles this in Awake)
   - Don't manually assign Instance

3. **Trigger from Any System**

   ```csharp
   // In MachineNode.cs, MachineOverload.cs, or RitualSequence.cs:
   CameraShake.Instance.Shake(0.6f, 0.3f);
   // Duration 0.6s, Magnitude 0.3
   ```

4. **Intensity Guidelines**
   - **0.1 - 0.2**: Subtle (machine hum, minor activation)
   - **0.2 - 0.3**: Noticeable (machine powerup)
   - **0.3 - 0.5**: Strong (overload, danger)
   - **0.5+**: Intense (chamber collapse, critical event)

5. **Test**
   - Machine powers up → camera shakes subtly
   - Machine overloads → camera shakes heavily

### Usage Quick Reference

```csharp
// Simple shake with defaults
CameraShake.Instance.Shake();

// Custom duration and magnitude
CameraShake.Instance.Shake(0.8f, 0.4f);

// Quick subtle tremor
CameraShake.Instance.Shake(0.2f, 0.1f);
```

---

## 🔆 CABLE GLOW ANIMATION

**Purpose**: Animated cable/conduit glow effects. Continuous pulse + strong activation pulse.

### Setup Steps

1. **Add to Cable Sprites**
   - Select cable GameObject
   - **Add Component** → CableGlow.cs
   - In Inspector:
     - **Cable Sprite**: Drag SpriteRenderer of cable
     - **Glow Color**: Color.cyan (or custom)
     - **Pulse Speed**: 2 (oscillation frequency)
     - **Intensity**: 0.5 (how bright the glow)

2. **Trigger Strong Pulse on Activation**

   ```csharp
   // In MachineNode.cs or GlyphPanel.cs:
   cableGlow.ActivateStrongPulse();
   ```

3. **Test**
   - Cable should glow continuously (sine wave pulse)
   - Activate machine → cable flashes brightly
   - Fade back to normal pulse

### Properties Reference

| Property | Default | Purpose |
|----------|---------|---------|
| glowColor | cyan | Color of glow |
| pulseSpeed | 2f | Oscillation frequency (Hz) |
| intensity | 0.5f | Glow brightness (0-1) |

---

## ✨ GLYPH RESONANCE SHADER

**Purpose**: Supernatural pulsing glow on glyph sprites. Uses URP-friendly shader.

### Setup Steps

1. **Create Material**
   - Right-click in Project → **Create** → **Material**
   - Name: `Mat_GlyphResonance`
   - In Inspector → **Shader**: Select **Velinor/GlyphResonance**

2. **Customize Material**
   - **Glow Color**: Cyan or supernatural color
   - **Glow Strength**: 0.5-1.0
   - **Pulse Speed**: 2-4 (Hz)

3. **Apply to Glyph Sprite**
   - Select glyph GameObject
   - Drag material into SpriteRenderer's **Material** slot

4. **Optional: Boost on Activation**

   ```csharp
   // In GlyphVFX.cs or interaction script:
   public Material glyphMaterial;

   void ActivateGlyph()
   {
       glyphMaterial.SetFloat("_GlowStrength", 1.5f);
       StartCoroutine(ResetGlyphGlowRoutine());
   }

   IEnumerator ResetGlyphGlowRoutine()
   {
       yield return new WaitForSeconds(2f);
       glyphMaterial.SetFloat("_GlowStrength", 0.7f);
   }
   ```

5. **Test**
   - Glyph should pulse continuously
   - Optional: Boost glow on interaction

### Shader Properties

| Property | Range | Purpose |
|----------|-------|---------|
| _GlowColor | Any | Glow tint |
| _GlowStrength | 0-2 | Intensity of glow |
| _PulseSpeed | 0-10 | Oscillation frequency |

---

## ⚡ MACHINE OVERLOAD SYSTEM

**Purpose**: Danger states with sparks, smoke, flickering, shutdown, and chain reactions.

### Setup Steps

1. **Add to Each Machine**
   - Select machine GameObject
   - **Add Component** → MachineOverload.cs
   - In Inspector:
     - **Machine Light**: Drag Light component
     - **Sparks**: Drag ParticleSystem (sparks)
     - **Smoke**: Drag ParticleSystem (smoke/debris)
     - **Overload Sound**: Drag AudioSource
     - **Shutdown Sound**: Drag AudioSource
     - **Flicker Speed**: 0.1 (seconds between flickers)
     - **Overload Duration**: 2.0 (how long until shutdown)
     - **Linked Machines**: Array of other MachineOverload components

2. **Create Particle Systems (if needed)**
   - Select machine
   - Right-click → **Effects** → **Particle System**
   - Configure for sparks or smoke

3. **Trigger Overload from Puzzle or Ritual**

   ```csharp
   // In RitualSequence.cs or MachineNode.cs:
   machineOverload.TriggerOverload();
   ```

4. **Test**
   - Trigger overload → light flickers
   - Sparks play
   - Shake triggers
   - After 2s: light off, smoke plays, shutdown sound
   - If linked machines exist: they also overload

### Properties Reference

| Property | Default | Purpose |
|----------|---------|---------|
| flickerSpeed | 0.1f | Time between light toggles |
| overloadDuration | 2f | Duration until shutdown |
| linkedMachines | [] | Machines to cascade to |

---

## 🎮 GLYPH COMBINATION UI

**Purpose**: Puzzle feedback overlay showing player progress through glyph sequences.

### Setup Steps

1. **Create or Use Existing Canvas**
   - In Hierarchy: Select Canvas (or create new one)
   - Add child Image elements for glyph slots

2. **Add Component to Canvas**
   - Select Canvas
   - **Add Component** → GlyphCombinationUI.cs

3. **Configure UI Slots**
   - In Inspector:
     - **Glyph Slots**: Set size to number of glyphs in sequence (e.g., 4)
     - **Slot 0**: Drag Image_0
     - **Slot 1**: Drag Image_1
     - **Slot 2**: Drag Image_2
     - **Slot 3**: Drag Image_3
     - **Empty Slot Sprite**: Gray placeholder
     - **Correct Glyph Sprite**: Green checkmark or glyph icon
     - **Wrong Glyph Sprite**: Red X or error icon

4. **Set Colors**
   - **Correct Color**: Green
   - **Wrong Color**: Red
   - **Neutral Color**: White

5. **Integrate with Puzzle**

   ```csharp
   // In puzzle manager or glyph interaction:
   private GlyphCombinationUI glyphUI;

   void OnGlyphActivated(string glyphID)
   {
       bool isCorrect = (glyphID == correctSequence[currentIndex]);
       glyphUI.UpdateGlyphSlot(currentIndex, isCorrect);

       if (isCorrect)
           currentIndex++;
       else
       {
           currentIndex = 0;
           glyphUI.ResetUI();
       }
   }
   ```

6. **Test**
   - Activate correct glyph → slot 0 turns green
   - Activate wrong glyph → slot 0 turns red, reset
   - Complete sequence → all slots green

### Methods Reference

```csharp
// Update a single slot
glyphUI.UpdateGlyphSlot(0, true);  // Correct
glyphUI.UpdateGlyphSlot(0, false); // Wrong

// Reset all slots
glyphUI.ResetUI();

// Control visibility
glyphUI.SetSlotActive(0, true);
glyphUI.SetAllSlotsActive(false);
```

---

## 🔮 RITUAL SEQUENCE SYSTEM

**Purpose**: Multi-step chamber puzzles with ordered steps, environmental reactions, and unlocking.

### Setup Steps

1. **Add to Chamber**
   - Select chamber GameObject
   - **Add Component** → RitualSequence.cs
   - In Inspector:
     - **Steps**: Array of step names (default: ["PlaceGlyph", "ActivateMachine", "PowerConduit", "ResonateChamber"])
     - **Machine Node**: Drag main machine in chamber
     - **Overload System**: Drag machine overload component
     - **Inner Door**: Drag door to unlock
     - **Ambient Controller**: Drag AmbientLayerController (singleton)
     - **Require Sequence**: true (enforce order)

2. **Call PerformStep from Interactions**

   ```csharp
   // In GlyphPanel.cs or machine interaction:
   public RitualSequence ritual;

   void OnActivateGlyph()
   {
       ritual.PerformStep("PlaceGlyph");
   }

   void OnActivateMachine()
   {
       ritual.PerformStep("ActivateMachine");
   }
   ```

3. **Step Progression**
   - Step 1: "PlaceGlyph" → Powers up machine node, enables Glyph ambient layer
   - Step 2: "ActivateMachine" → Enables Machine ambient layer
   - Step 3: "PowerConduit" → Triggers camera shake, enables Chamber ambient layer
   - Step 4: "ResonateChamber" → Triggers machine overload, strong shake
   - **Complete**: Inner door unlocks with final shake

4. **Test**
   - Perform steps in order → each triggers appropriate effects
   - Perform wrong step → ritual resets
   - Complete all steps → door opens

### Methods Reference

```csharp
// Perform a step (must be in correct order if requireSequence=true)
ritual.PerformStep("PlaceGlyph");

// Get current progress
int current = ritual.CurrentStep;
int total = ritual.TotalSteps;

// Reset ritual
ritual.ResetRitual();
```

### Custom Step Logic

To add new steps, edit the switch statement in `ExecuteStep()`:

```csharp
private void ExecuteStep(string stepID)
{
    switch (stepID)
    {
        case "PlaceGlyph":
            OnPlaceGlyph();
            break;
        
        case "CustomStep":
            // Your custom logic here
            Debug.Log("Custom step executed!");
            break;
    }
}

private void OnCustomStep()
{
    // Custom effects
}
```

---

## 🎯 INTEGRATION EXAMPLES

### Example 1: Basic Machine Activation

**Scenario**: Player activates glyph → machine powers up → door opens

```csharp
// GlyphPanel.cs
public class GlyphPanel : MonoBehaviour
{
    public DoorController door;
    public MachineNode machine;

    private void ActivateGlyph()
    {
        // Power up the machine
        machine.PowerUp();
        
        // Open the door
        door.OpenDoor();
        
        // Shake camera
        CameraShake.Instance.Shake(0.4f, 0.2f);
    }
}
```

### Example 2: Chain Reaction Overload

**Scenario**: Machine A overloads → triggers Machine B → triggers Machine C

**Setup**:

1. Machine A: MachineOverload with Linked Machines = [Machine B]
2. Machine B: MachineOverload with Linked Machines = [Machine C]
3. Machine C: MachineOverload with Linked Machines = []

```csharp
// Trigger from anywhere:
MachineOverload machineA = GetComponent<MachineOverload>();
machineA.TriggerOverload();
// Automatically cascades to B, then C
```

### Example 3: Multi-Step Ritual with UI

**Scenario**: Chamber requires 4 glyphs in correct order to unlock

```csharp
public class ChamberPuzzle : MonoBehaviour
{
    public RitualSequence ritual;
    public GlyphCombinationUI glyphUI;
    
    private string[] requiredSequence = { "Fire", "Water", "Earth", "Air" };
    private int currentIndex = 0;

    public void OnGlyphActivated(string glyphID)
    {
        bool correct = (glyphID == requiredSequence[currentIndex]);
        
        glyphUI.UpdateGlyphSlot(currentIndex, correct);
        
        if (correct)
        {
            ritual.PerformStep(requiredSequence[currentIndex]);
            currentIndex++;
        }
        else
        {
            currentIndex = 0;
            glyphUI.ResetUI();
            ritual.ResetRitual();
        }
    }
}
```

### Example 4: Location-Based Ambient Layers

**Scenario**: Different areas of cave have different soundscapes

```csharp
// PlayerMovement.cs or proximity trigger
private AmbientLayerController ambient;

void OnTriggerEnter2D(Collider2D col)
{
    if (col.CompareTag("MachineZone"))
    {
        ambient.SetLayer("Machine", true);
        ambient.SetLayer("Glyph", false);
    }
    else if (col.CompareTag("ChamberZone"))
    {
        ambient.SetLayer("Machine", false);
        ambient.SetLayer("Chamber", true);
    }
}

void OnTriggerExit2D(Collider2D col)
{
    if (col.CompareTag("MachineZone"))
        ambient.SetLayer("Machine", false);
    else if (col.CompareTag("ChamberZone"))
        ambient.SetLayer("Chamber", false);
}
```

### Example 5: Glyph Vision Sequence

**Scenario**: Interact with artifact → freeze player, zoom camera, fade to white, show vision, return

```csharp
// On artifact GameObject:
// Add MemorySequence.cs component with all fields assigned

public class ArtifactInteraction : MonoBehaviour
{
    public MemorySequence visionSequence;
    public bool playerNearby = false;

    private void OnTriggerEnter2D(Collider2D col)
    {
        if (col.CompareTag("Player"))
            playerNearby = true;
    }

    private void OnTriggerExit2D(Collider2D col)
    {
        if (col.CompareTag("Player"))
            playerNearby = false;
    }

    private void Update()
    {
        if (playerNearby && Input.GetKeyDown(KeyCode.E))
            visionSequence.StartSequence();
    }
}
```

---

## ✅ TESTING CHECKLIST

### Pre-Launch Tests

- [ ] **CameraShake**: Trigger from console → camera shakes smoothly
- [ ] **MachineNode**: Power up machine → light glows, sound plays, outputs power up
- [ ] **MachineOverload**: Trigger overload → flickers, sparks, shakes, shuts down
- [ ] **CableGlow**: Cable should pulse continuously, strong pulse on command
- [ ] **AmbientLayerController**: Layer fade in/out smooth, no pops or clicks
- [ ] **MemorySequence**: Trigger vision → camera zooms, fades white, player frozen, returns
- [ ] **RitualSequence**: Perform steps in order → correct effects, wrong order resets
- [ ] **GlyphCombinationUI**: Slots update correctly, reset on wrong glyph
- [ ] **GlyphResonance**: Shader glows, pulsates, not too bright or dim

### Scene-Level Tests

- [ ] All singleton components only exist once (no duplicates)
- [ ] No console errors on scene load
- [ ] Player can move freely (no freezing except during sequences)
- [ ] Scene transitions still work (fade in/out)
- [ ] Audio doesn't overlap or cut off

### Gameplay Tests

- [ ] Glyph activation triggers appropriate effects
- [ ] Machine network cascades correctly
- [ ] Overload creates sense of danger
- [ ] Ambient layers respond to location
- [ ] Ritual sequences enforce correct order
- [ ] Door unlocks on successful puzzle
- [ ] Vision sequences feel impactful

### Performance Tests

- [ ] Frame rate stable during heavy effects (machine overload)
- [ ] No memory leaks (coroutines clean up)
- [ ] Particle systems don't stutter
- [ ] Audio layers fade smoothly

---

## 🐛 TROUBLESHOOTING

### Problem: CameraShake not found

**Solution**: Ensure CameraShake.cs is on Main Camera and no compilation errors

### Problem: AmbientLayerController audio overlaps

**Solution**: Start all audio at volume=0, let controller fade them in

### Problem: RitualSequence steps not progressing

**Solution**: Check that step names match EXACTLY (case-sensitive)

### Problem: MemorySequence freezes player permanently

**Solution**: Ensure PlayerMovement.cs is found correctly, check "Freeze Player" toggle

### Problem: GlyphResonance shader looks wrong

**Solution**: Check that shader is assigned to Material, not directly to SpriteRenderer

### Problem: Machine chain doesn't cascade

**Solution**: Ensure MachineOverload.linkedMachines array is populated correctly

---

## 📝 NEXT STEPS

1. **Test each system individually** (use checklist above)
2. **Integrate into MachinesCave scene** (add components, assign references)
3. **Connect glyph interactions** to machine network + ritual sequence
4. **Tune timing and intensity** (camera shake magnitude, fade speeds, audio volumes)
5. **Iterate on UX** (add UI feedback, adjust pacing)
6. **Build second chamber** using same architecture
7. **Commit to git** with message: "Add full audiovisual + ritual systems suite"

---

## 📚 REFERENCE: SCRIPT DEPENDENCIES

```
MemorySequence.cs
  └─ requires: Main Camera, CanvasGroup (fadeCanvas)
  └─ optional: PlayerMovement, AudioSource

MachineNode.cs
  └─ standalone (optional: Light, ParticleSystem, AudioSource)

AmbientLayerController.cs
  └─ requires: 4x AudioSource components
  └─ optional: other systems

CameraShake.cs (SINGLETON)
  └─ requires: Camera component
  └─ used by: MachineOverload, RitualSequence, custom code

CableGlow.cs
  └─ requires: SpriteRenderer

GlyphResonance.shader
  └─ requires: Material assigned to SpriteRenderer
  └─ URP-compatible

MachineOverload.cs
  └─ requires: Light component (optional)
  └─ optional: 2x ParticleSystem, 2x AudioSource
  └─ uses: CameraShake (singleton)

GlyphCombinationUI.cs
  └─ requires: Canvas with Image children
  └─ requires: 2x Sprites (empty, correct, wrong)

RitualSequence.cs
  └─ requires: MachineNode, MachineOverload, DoorController
  └─ optional: AmbientLayerController
  └─ uses: CameraShake (singleton)
```

---

**Status**: Ready for integration ✅  
**Estimated Setup Time**: 1-2 hours for full scene  
**Testing Time**: 30 mins per scene
