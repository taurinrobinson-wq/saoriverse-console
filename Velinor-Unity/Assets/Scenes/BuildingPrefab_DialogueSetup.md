# BuildingPrefab.unity - Saori Dialogue System Setup

## Overview
This guide provides step-by-step instructions to add the dialogue UI system to BuildingPrefab.unity for the Saori encounter vertical slice.

## Prerequisites
- BuildingPrefab.unity is open in Unity Editor
- DialogueManager and StatManager already exist in the scene (or will be auto-instantiated)
- TextMeshPro is imported in your project

---

## UI Setup Instructions

### 1. Create the DialoguePanel (Bottom Center - 900×350)

**Step 1.1: Create Main Panel**
- Right-click in Hierarchy → UI → Panel (TextMeshPro)
- Rename: `DialoguePanel`
- **RectTransform Settings:**
  - **Anchor Preset:** Bottom-Center (hold Shift + Alt, click bottom-center)
  - **Position:** X = 0, Y = 175 (half of 350 height)
  - **Size:** Width = 900, Height = 350
  - **Pivot:** (0.5, 0)

**Step 1.2: Style the Panel**
- Select the Image component
- **Color:** Set to semi-transparent dark (e.g., #000000CC - 80% opacity)
- **Image Type:** Simple
- Remove the border or set border to 0

---

### 2. Add DialoguePanel Children

#### 2.1 NPCLineText
- Right-click DialoguePanel → TextMeshPro - Text (UI)
- Rename: `NPCLineText`
- **RectTransform:**
  - **Anchor:** Stretch-Top (left/right 20, top 20)
  - **Left:** 20, Right: 20, Top: -20, Bottom: 0
  - **Height:** ~120 (flexible)
- **TextMeshProUGUI:**
  - Font Size: 36
  - Alignment: TopLeft
  - Color: White
  - Enable word wrapping

#### 2.2 ChoiceButtons (T, O, N, E)
Create **4 buttons** with consistent layout:

**Button Template (repeat 4 times with different labels):**
- Right-click DialoguePanel → Button (TextMeshPro)
- Rename: `ChoiceButton_T` (then `_O`, `_N`, `_E`)
- **RectTransform:**
  - **Anchor:** Bottom-Stretch (anchor to bottom, fill horizontally)
  - **Left:** 20, Right: 20
  - **Height:** 50
  - **Y Position:** -60 (first), -120 (second), -180 (third), -240 (fourth)
- **Button Component:**
  - **Normal Color:** #4A7BA7 (blue)
  - **Hover Color:** #6A9BC7 (lighter blue)
  - **Pressed Color:** #2A5B87 (darker blue)
  - **Disabled Color:** #808080 (gray)
- **Text Child:**
  - Font Size: 24
  - Text: "T - Empathy" (or respective tone name)
  - Alignment: Center

**Spacing Guide:**
```
DialoguePanel (900×350)
├─ NPCLineText (top ~120px)
├─ ChoiceButton_T (y=-60, h=50)
├─ ChoiceButton_O (y=-120, h=50)
├─ ChoiceButton_N (y=-180, h=50)
└─ ChoiceButton_E (y=-240, h=50)
```

#### 2.3 SharedBeatText (Optional, Disabled by Default)
- Right-click DialoguePanel → TextMeshPro - Text (UI)
- Rename: `SharedBeatText`
- **RectTransform:**
  - **Anchor:** Center
  - **Size:** 800×200
- **TextMeshProUGUI:**
  - Font Size: 32
  - Alignment: Center
  - Color: Yellow or special effect color
- **Disable this GameObject by default** (uncheck the checkbox)

---

### 3. Create CodexPanel (Left-Center)

**Step 3.1: Create Panel**
- Right-click in Hierarchy → UI → Panel (TextMeshPro)
- Rename: `CodexPanel`
- **RectTransform Settings:**
  - **Anchor Preset:** Left-Center (hold Shift + Alt, click left-center)
  - **Position:** X = 250, Y = 0
  - **Size:** Width = 500, Height = 600
  - **Pivot:** (0, 0.5)

**Step 3.2: Add Image (Glyph_Codex2.svg)**
- Right-click CodexPanel → UI → Image
- Rename: `CodexImage`
- **RectTransform:**
  - **Anchor:** Stretch (fill entire panel)
  - **Left/Right/Top/Bottom:** 0
- **Image Component:**
  - **Source Image:** Drag `Glyph_Codex2.svg` here from `Assets/UI/Overlays/`
  - **Image Type:** Simple
  - **Color:** White (full opacity initially)

**Step 3.3: Add CanvasGroup**
- Select CodexPanel
- **Add Component:** CanvasGroup
- **Set Alpha:** 0 (hidden by default)

---

### 4. Create DiaryPanel (ScrollView)

**Step 4.1: Create ScrollView**
- Right-click in Hierarchy → UI → Scroll View (TextMeshPro)
- Rename: `DiaryPanel`
- **RectTransform Settings:**
  - **Anchor Preset:** Right-Center
  - **Position:** X = -300, Y = 0
  - **Size:** Width = 500, Height = 600
  - **Pivot:** (1, 0.5)

**Step 4.2: Configure Scroll View**
- Select the `Viewport` child
- In the ScrollRect component:
  - **Scroll Sensitivity:** 5
  - **Horizontal:** Unchecked
  - **Vertical:** Checked
  - **Elastic:** Checked
  - **Deceleration:** 0.95

**Step 4.3: Add CanvasGroup**
- Select DiaryPanel (the root)
- **Add Component:** CanvasGroup
- **Set Alpha:** 0 (hidden by default)

**Step 4.4: Configure Content**
- Select the `Content` child inside Viewport
- **RectTransform:**
  - **Size Delta:** Width = 450, Height = auto (expand with content)
  - **Vertical Layout Group:**
    - Add Component → Vertical Layout Group
    - **Child Force Expand:** Height = Checked
    - **Spacing:** 10

---

### 5. Create NotificationPanel

**Step 5.1: Create Panel**
- Right-click in Hierarchy → UI → Panel (TextMeshPro)
- Rename: `NotificationPanel`
- **RectTransform Settings:**
  - **Anchor Preset:** Top-Center
  - **Position:** X = 0, Y = -50
  - **Size:** Width = 600, Height = 80
  - **Pivot:** (0.5, 1)

**Step 5.2: Add TextMeshPro Text**
- Right-click NotificationPanel → TextMeshPro - Text (UI)
- Rename: `NotificationText`
- **RectTransform:**
  - **Anchor:** Stretch
  - **Margins:** 10 all around
- **TextMeshProUGUI:**
  - Font Size: 24
  - Alignment: Center
  - Color: White
  - Text: "Diary updated. Press [N] to access."

**Step 5.3: Add CanvasGroup**
- Select NotificationPanel
- **Add Component:** CanvasGroup
- **Set Alpha:** 0 (hidden by default)

---

### 6. Wire Up the DialogueManager

**Step 6.1: Find or Create DialogueManager**
- Search Hierarchy for "DialogueManager"
- If it exists, select it
- If not, create: GameObject → name it "DialogueManager"
  - Add Component: DialogueManager.cs

**Step 6.2: Assign UI References**
In the DialogueManager inspector, find these fields and assign:
- **Dialogue Canvas:** (the main Canvas that contains DialoguePanel)
- **Choice Button Container:** DialoguePanel (the parent containing the 4 buttons)
- **Choice Button Prefab:** Any of the ChoiceButton_T/O/N/E (the system will clone these, but if your system uses single buttons, leave empty)
- **Passage Text:** NPCLineText
- **Dialogue Panel:** DialoguePanel

---

## Input Bindings Setup

Add these input bindings to your Input System (Edit → Project Settings → Input Manager or new Input System Package):

```
Action Name: "Toggle_Codex"
Binding: Key → C

Action Name: "Toggle_Diary"  
Binding: Key → N

Action Name: "Interact"
Binding: Key → E
```

Or if using the newer Input System (InputAction Asset):
1. Create InputActions asset in Assets/
2. Add actions: ToggleCodex (C), ToggleDiary (N), Interact (E)
3. Assign to InputManager in DialogueManager

---

## Script Extensions (If Needed)

The existing systems handle most of this, but if you need custom methods:

### DialogueManager Extensions (Optional)
```csharp
// Load Saori-specific dialogue
public void LoadSaoriDesertDialogue()
{
    LoadStoryFromResources("velinor/stories/Dialogue_Saori_Desert");
    StartDialogue("Saori", "saori_beat_1");
}

// Show notification
public void ShowNotification(string text)
{
    notificationText.text = text;
    StartCoroutine(FadeCanvasGroup(notificationPanel, 1f, 0.1f));
    StartCoroutine(FadeCanvasGroup(notificationPanel, 0f, 3f, 1f)); // Fade out after 3s
}

// Trigger system events
public void TriggerSystemEvent(string eventName)
{
    switch(eventName)
    {
        case "give_device":
            ShowNotification("??? Obtained. Press [C] to access Codex.");
            break;
        case "diary_update":
            ShowNotification("Diary updated. Press [N] to access.");
            break;
    }
}
```

### Input Handler (Attach to a manager script)
```csharp
void Update()
{
    if (Input.GetKeyDown(KeyCode.C))
    {
        ToggleCodex();
    }
    if (Input.GetKeyDown(KeyCode.N))
    {
        ToggleDiary();
    }
    if (Input.GetKeyDown(KeyCode.E))
    {
        TryInteract();
    }
}

void ToggleCodex()
{
    CanvasGroup cg = codexPanel.GetComponent<CanvasGroup>();
    cg.alpha = cg.alpha > 0.5f ? 0f : 1f;
}

void ToggleDiary()
{
    CanvasGroup cg = diaryPanel.GetComponent<CanvasGroup>();
    cg.alpha = cg.alpha > 0.5f ? 0f : 1f;
}
```

---

## Testing Checklist

- [ ] DialoguePanel displays NPC line text
- [ ] All 4 choice buttons are visible and clickable
- [ ] Pressing a choice button advances the dialogue
- [ ] Tone stats update when choices are made (check StatManager)
- [ ] Pressing C toggles CodexPanel alpha (fade in/out)
- [ ] Pressing N toggles DiaryPanel alpha
- [ ] Notifications appear when system triggers fire
- [ ] Saori dialogue loads from Dialogue_Saori_Desert.json
- [ ] Saori NPC profile applies remnant effects

---

## Flow Summary

1. **Scene loads** → DialogueManager initializes
2. **Player approaches Saori** → Trigger dialogue start
3. **Beat 1 displays** → "You came. Not many follow the echoes..."
4. **Player chooses T/O/N/E** → Tone shifts, NPC resonance applies
5. **Shared beat fires** → Device materializes, notification shows
6. **Press C** → Codex fades in, displays glyph info
7. **Continue dialogue** → Beat 2 begins
8. **Second choice** → Wind sound, diary updated
9. **Press N** → Diary fades in, shows entries
10. **Encounter ends** → Saori remnants locked into StatManager

---

## Important Notes

- **CanvasGroup.alpha = 0** keeps UI functional but invisible (perfect for toggle)
- **Anchor presets** are critical—use Shift + Alt to access full presets menu
- **TextMeshPro is required**—if not imported, add via Window → TextMeshPro → Import TMP Essentials
- **RectTransform values** should match the layout shown—test in Scene view
- **Dialogue JSON path**: `Resources/velinor/stories/Dialogue_Saori_Desert.json`

---

## Reference Files

- **DialogueManager:** `Velinor-Unity/Assets/Scripts/Core/DialogueManager.cs`
- **StatManager:** `Velinor-Unity/Assets/Scripts/Core/StatManager.cs`
- **Dialogue JSON:** `Velinor-Unity/Assets/Resources/velinor/stories/Dialogue_Saori_Desert.json`
- **Scene:** `Velinor-Unity/Assets/Scenes/BuildingPrefab.unity`
