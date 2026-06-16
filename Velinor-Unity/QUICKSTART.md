# Velinor-Unity: Quick Start — Getting Phase 1 Running

**Time to First Test:** 30 minutes  
**Objective:** Get player movement + interaction working in a test scene

**Framework:** Uses proven StarterAssets framework (tested, working third-person controller)

---

## Step 1: Import TMPro (5 min)

- Open Velinor-Unity project in Unity
- Window → TextMeshPro → Import TMP Essential Resources
- (This enables TextMeshPro UI for dialogue)

---

## Step 2: Create Test Scene (5 min)

- Right-click in `Assets/Scenes/` → Create → Scene → name it `TestScene`
- Open the scene
- Right-click in hierarchy → 3D Object → Plane
  - Scale to 20x20 (this is your ground)
  - Position at (0, 0, 0)
  - **Important:** Select the Plane → In Inspector, find "Mesh Collider" and **delete it** (right-click component → Remove Component). If you see an error saying "module has been force excluded", this is the fix.

---

## Step 3: Add Ground Collider

- Select **Plane** in hierarchy
- Add Component → **Box Collider**
  - Make sure "Is Trigger" is **UNCHECKED** (it needs to be solid ground)

---

## Step 4: Create Player (5 min)

- Right-click in hierarchy → Create Empty → name it "Player"
- **Position: (0, 0, 0)**
- Add Component → **Character Controller**
  - Set Height to 2
  - Set Radius to 0.4
  - Center: (0, 1, 0)
- Add Component → **Animator**
  - (No controller needed yet—just attach the component)
- Add Component → **StarterAssetsInputs**
  - (This handles WASD input automatically)
- Add Component → **VelinorPlayerController**
  - This is the working third-person movement system
- Add a **visual child cube**: Right-click Player → 3D Object → Cube
  - Scale cube to (0.4, 1, 0.4) to match controller
  - Position at (0, 0.5, 0)
  - Remove the Box Collider from the cube (right-click → Remove Component)
- **Tag the Player:** Select Player, set Tag to "Player"

---

## Step 5: Setup Camera (5 min)

- Select **Main Camera**
  - Position: (0, 1, 0)
  - Parent it to **nothing** (keep it separate from Player)
  - Tag it as "MainCamera"
- Right-click in hierarchy → Create Empty → name it "CinemachineCameraTarget"
  - Parent it to **Player**
  - Position: (0, 0.6, 0)
  - Rotation: (0, 0, 0)
- Select **Player** → Select **VelinorPlayerController** component
  - Drag **CinemachineCameraTarget** into the **Cinemachine Camera Target** field

---

## Step 6: Add CodexManager to Scene (5 min)

- Right-click in hierarchy → Create Empty → name it "CodexManager"
- **Click on "CodexManager"** in the Hierarchy
- In the Inspector, click **Add Component**
- Search for "CodexManager" and click it

---

## Step 7: Test Movement (5 min)

- Press Play
- Try moving with **WASD**
- Use **Mouse** to look around
- Character should move smoothly across the plane

**Expected result:** Player cube moves around the plane, camera follows your look direction.

---

## Step 8: Add a Simple NPC (5 min)

- Right-click in hierarchy → 3D Object → Cylinder
- Name it "NPC_Tala"
- Position at (5, 0, 5)
- Scale to (0.5, 1.5, 0.5)
- Add Component → **Box Collider**
  - Set "Is Trigger" to **CHECKED**
  - Adjust the size to roughly match the cylinder

---

## Step 9: Create Interaction System (10 min)

Create a file: `Assets/Scripts/Core/SimpleNPC.cs`

```csharp
using UnityEngine;
using Velinor.Core;

public class SimpleNPC : MonoBehaviour, IInteractable
{
    public string npcName = "Tala";

    public void Interact(GameObject player)
    {
        Debug.Log($"Interacting with {npcName}");
        
        // Hardcoded test dialogue
        var sequence = new DialogueSequence
        {
            sequenceId = "test_dialogue",
            npcName = npcName,
            lines = new System.Collections.Generic.List<DialogueLine>
            {
                new DialogueLine 
                { 
                    speakerId = npcName, 
                    text = "Hello, stranger. I am Tala.",
                    emotionalTags = new System.Collections.Generic.List<string> { "Trust" }
                },
                new DialogueLine 
                { 
                    speakerId = npcName, 
                    text = "My daughter was lost in the Collapse.",
                    emotionalTags = new System.Collections.Generic.List<string> { "Grief" }
                },
                new DialogueLine 
                { 
                    speakerId = npcName, 
                    text = "Do you remember what it was like before?",
                    emotionalTags = new System.Collections.Generic.List<string>()
                }
            }
        };

        DialogueManager.Instance.StartDialogue(sequence);
    }
}
```

Then in Unity:
- **Click on "NPC_Tala"** in the Hierarchy
- In the Inspector, click **Add Component**
- Search for "SimpleNPC" and click it

---

## Step 10: Add Dialogue Manager (5 min)

- Right-click in hierarchy → Create Empty → name it "DialogueManager"
- **Click on "DialogueManager"**
- In the Inspector, click **Add Component**
- Search for "DialogueManager" and click it
- Create the UI under it:
  - Right-click "DialogueManager" → UI → Panel
  - Rename the panel to "DialoguePanel"
  - Inside DialoguePanel, create text elements:
    - Right-click DialoguePanel → UI → Text - TextMeshPro (rename to "SpeakerName")
    - Right-click DialoguePanel → UI → Text - TextMeshPro (rename to "DialogueText")
    - Right-click DialoguePanel → UI → Panel (rename to "ChoicesContainer")
- Select "DialogueManager" again, assign these references:
  - Drag "DialoguePanel" into **Dialogue UI Panel** field
  - Drag "SpeakerName" into **Speaker Name Text** field
  - Drag "DialogueText" into **Dialogue Text** field
  - Drag "ChoicesContainer" into **Choices Container** field

---

## Step 11: Test Interaction (5 min)

- Press Play
- Walk near NPC with WASD
- Press **E** to interact
- Dialogue should appear!

**Expected result:** Dialogue plays, "Grief" tag is added to Codex.

---

## Step 12: Add a Pedestal (10 min)

- Right-click in hierarchy → 3D Object → Cube → name it "Pedestal"
- Scale to (1, 2, 1)
- Position at (10, 0, 10)
- **Click on "Pedestal"**
- In the Inspector, click **Add Component**
- Search for "Pedestal" and click it
- Configure the fields:
  - **Pedestal Id**: "pedestal_test_001"
  - **Linked Glyph Id**: "glyph_test_001"
  - **Required Tags**: Click the **+** button and add "Grief"
  - **Activation Radius**: 5
  - Add a **Light** component (click Add Component → Light)
  - Drag the Light into **Pedestal Light** field
  - Add a **Particle System** component
  - Drag it into **Activation Particles** field

---

## Step 13: Test Pedestal Activation (5 min)

- Press Play
- Walk near NPC and trigger dialogue (Grief tag added)
- Walk toward pedestal
- Watch as it transitions from Dormant → Flickering → Active

**Expected result:** Pedestal glows and particles activate when you have the Grief tag.

---

## What You've Built

✅ Player movement (WASD)  
✅ Camera control (Mouse look)  
✅ NPC interaction (E key)  
✅ Dialogue system with emotional tags  
✅ Codex emotional state tracking  
✅ Pedestal that responds to emotional tags  

**This is Phase 1 in miniature.**

---

## Troubleshooting

### Player doesn't move
- Check Player has **StarterAssetsInputs** component
- Check Player has **VelinorPlayerController** component
- Check Player has **CharacterController** component
- Check Player is tagged as "Player"
- Check Plane has **Box Collider** (not trigger, is solid)

### Camera doesn't follow mouse
- Check **CinemachineCameraTarget** is a child of Player
- Check it's assigned in VelinorPlayerController **Cinemachine Camera Target** field
- Make sure **Main Camera** is tagged as "MainCamera"

### Dialogue doesn't appear
- Check DialogueManager is in scene
- Check UI references are assigned in DialogueManager component
- Check TextMeshPro is imported (Step 1)

### E key doesn't work
- Check NPC has **SimpleNPC** component
- Check NPC has **Box Collider** set to trigger
- Check you're pressing E (not E key on numpad)

---

## Next Steps

1. ✅ Complete this quick start
2. Follow PHASE_1_CHECKLIST.md for full implementation
3. Build Market Ruins blockout (Phase 2)
4. Create real dialogue sequences from JSON data (Phase 3)

