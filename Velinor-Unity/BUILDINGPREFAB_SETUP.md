# BuildingPrefab.unity - Dialogue System Setup Guide

**Purpose:** Complete wiring guide for integrating the canonical DialogueManager into BuildingPrefab.unity using safe, explicit field assignments.

**File Location:** `Assets/Scenes/BuildingPrefab.unity`

---

## Overview

The DialogueManager uses a **canonical wiring approach** that prevents Unity AI from introducing terminology drift or misbinding fields. All fields are explicitly assigned in the Inspector — no automatic binding, no fuzzy matching, no guessing.

---

## Step 1: Scene Hierarchy Structure

Your BuildingPrefab.unity should have this hierarchy:

```
BuildingPrefab
├── Canvas (DialogueCanvas)
│   └── DialoguePanel
│       ├── DialogueBodyText (TextMeshProUGUI)
│       ├── NPCLineText (TextMeshProUGUI)
│       ├── SharedBeatText (TextMeshProUGUI)
│       ├── ChoiceButton_T (Button)
│       │   └── Text (TextMeshProUGUI) → btnT label
│       ├── ChoiceButton_O (Button)
│       │   └── Text (TextMeshProUGUI) → btnO label
│       ├── ChoiceButton_N (Button)
│       │   └── Text (TextMeshProUGUI) → btnN label
│       └── ChoiceButton_E (Button)
│           └── Text (TextMeshProUGUI) → btnE label
├── DialogueManager (Script)
└── StatManager (Script)
```

### Key Names (MUST MATCH EXACTLY)
- Button names: `ChoiceButton_T`, `ChoiceButton_O`, `ChoiceButton_N`, `ChoiceButton_E`
- Text field names: `DialogueBodyText`, `NPCLineText`, `SharedBeatText`
- Canvas name: Anything (but must be a Canvas component)

---

## Step 2: Create and Configure Canvas

1. **Create Canvas**
   - Right-click → UI → Canvas
   - Rename to "DialogueCanvas"
   - Set Canvas to overlay mode

2. **Add DialoguePanel (Panel component)**
   - Inside Canvas, create new empty GameObject
   - Rename to "DialoguePanel"
   - Add RectTransform (already has it)
   - Set dimensions: Full screen or your desired dialogue area

---

## Step 3: Add Text Fields

Inside DialoguePanel, create these TextMeshProUGUI elements:

### 3.1 DialogueBodyText
- **Name:** `DialogueBodyText`
- **Purpose:** Main dialogue prompt/passage text
- **Font Size:** 36
- **Alignment:** Top-Left
- **Position:** Top area of panel

### 3.2 NPCLineText
- **Name:** `NPCLineText`
- **Purpose:** NPC name/speaker identification
- **Font Size:** 24
- **Alignment:** Top-Left
- **Position:** Just above or beside DialogueBodyText

### 3.3 SharedBeatText
- **Name:** `SharedBeatText`
- **Purpose:** Narrative beats shown after choices
- **Font Size:** 28
- **Alignment:** Center
- **Position:** Center of panel
- **Default:** DISABLED (set Active = false)

---

## Step 4: Create Choice Buttons

Inside DialoguePanel, create 4 Button components:

### 4.1 ChoiceButton_T (Trust)
- **Name:** `ChoiceButton_T`
- **Type:** Button - TextMeshProUGUI
- Add child TextMeshProUGUI → Rename to "Text"
- Set text color to indicate Trust (e.g., Gold/Yellow)

### 4.2 ChoiceButton_O (Observation)
- **Name:** `ChoiceButton_O`
- **Type:** Button - TextMeshProUGUI
- Add child TextMeshProUGUI → Rename to "Text"
- Set text color to indicate Observation (e.g., Blue)

### 4.3 ChoiceButton_N (NarrativePresence)
- **Name:** `ChoiceButton_N`
- **Type:** Button - TextMeshProUGUI
- Add child TextMeshProUGUI → Rename to "Text"
- Set text color to indicate NarrativePresence (e.g., Purple)

### 4.4 ChoiceButton_E (Empathy)
- **Name:** `ChoiceButton_E`
- **Type:** Button - TextMeshProUGUI
- Add child TextMeshProUGUI → Rename to "Text"
- Set text color to indicate Empathy (e.g., Green)

---

## Step 5: Add DialogueManager Script

1. **Create empty GameObject** in root of BuildingPrefab
   - Name: "DialogueManager"
   - Attach script: `DialogueManager.cs`

2. **Assign Fields in Inspector**

   ### Root Panel
   - **dialogueCanvas:** Drag the Canvas object

   ### Text Fields
   - **bodyText:** Drag DialogueBodyText
   - **npcNameText:** Drag NPCLineText
   - **sharedBeatText:** Drag SharedBeatText

   ### Choice Buttons
   - **btnT:** Drag ChoiceButton_T Button component
   - **btnO:** Drag ChoiceButton_O Button component
   - **btnN:** Drag ChoiceButton_N Button component
   - **btnE:** Drag ChoiceButton_E Button component

   ### Button Labels
   - **txtT:** Drag ChoiceButton_T → Text (child TextMeshProUGUI)
   - **txtO:** Drag ChoiceButton_O → Text (child TextMeshProUGUI)
   - **txtN:** Drag ChoiceButton_N → Text (child TextMeshProUGUI)
   - **txtE:** Drag ChoiceButton_E → Text (child TextMeshProUGUI)

   ### Fallback (leave empty if using static buttons above)
   - **choiceButtonContainer:** (Optional, only if dynamic spawning)
   - **choiceButtonPrefab:** (Optional, only if dynamic spawning)

---

## Step 6: Verify Wiring

1. **Select DialogueManager in Inspector**
2. **Right-click on script component header**
3. **Select "ValidateDialoguePanel"**

Expected output in Console:
```
═══════════════════════════════════════════════════════════
VALIDATING DIALOGUE PANEL WIRING
═══════════════════════════════════════════════════════════
✓ DialogueCanvas: ASSIGNED
✓ bodyText: ASSIGNED
✓ npcNameText: ASSIGNED
✓ sharedBeatText: ASSIGNED

CHOICE BUTTONS:
  ✓ btnT (Trust): ASSIGNED
  ✓ btnO (Observation): ASSIGNED
  ✓ btnN (NarrativePresence): ASSIGNED
  ✓ btnE (Empathy): ASSIGNED

BUTTON LABELS:
  ✓ txtT (Trust label): ASSIGNED
  ✓ txtO (Observation label): ASSIGNED
  ✓ txtN (NarrativePresence label): ASSIGNED
  ✓ txtE (Empathy label): ASSIGNED

✓ ALL VALIDATION CHECKS PASSED - DialoguePanel is properly wired!
═══════════════════════════════════════════════════════════
```

If you see ✗ errors, fix the missing assignments and re-run validation.

---

## Step 7: Test the Dialogue System in BuildingPrefab.unity

1. **Add NPCInteraction script** to Saori (or target NPC)
2. **In Start(), call:**
   ```csharp
   DialogueManager.Instance.StartDialogue("Saori", "market_entry", "velinor/stories/sample_story");
   ```

3. **Play BuildingPrefab.unity**
4. **Interact with NPC** → DialoguePanel should appear
5. **Verify:**
   - Dialogue text displays correctly
   - Buttons show up with proper labels
   - Clicking a button applies stat changes (TONE → REMNANTS)
   - Shared beats display after choices

---

## Step 8: Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Panel doesn't appear | dialogueCanvas not assigned | Drag Canvas to Inspector |
| Text doesn't show | bodyText not assigned | Drag DialogueBodyText to Inspector |
| Buttons don't appear | btnT/O/N/E not assigned | Drag all 4 buttons to Inspector |
| Buttons don't respond | onClick listeners not binding | Check Console for errors; re-run ValidateDialoguePanel |
| Wrong text on buttons | txtT/O/N/E not assigned | Drag button labels (child TextMeshProUGUI) to Inspector |
| TONE not applying | StatManager not in scene | Add StatManager to scene with correct NPC profiles |

---

## Canonical Code Guarantees

This wiring provides:
- ✅ **No string-based routing** — Uses ToneType enum
- ✅ **No fuzzy text matching** — Uses explicit field assignment
- ✅ **No accidental TONE/REMNANTS mixing** — Clear one-directional flow
- ✅ **No terminology drift** — Unity AI cannot override enum values
- ✅ **Type safety** — Compiler enforces correct structure
- ✅ **Self-documenting** — Field names explain their purpose

---

## Script Methods

### StartDialogue()
```csharp
// Start dialogue with Saori using sample_story
DialogueManager.Instance.StartDialogue("Saori", "market_entry", "velinor/stories/sample_story");
```

### EndDialogue()
```csharp
// End current dialogue and hide panel
DialogueManager.Instance.EndDialogue();
```

### IsDialogueActive
```csharp
// Check if dialogue is running
if (DialogueManager.Instance.IsDialogueActive)
{
    // Do something
}
```

### ValidateDialoguePanel()
```csharp
// Run validation (or right-click in Inspector)
DialogueManager.Instance.ValidateDialoguePanel();
```

---

## Next Steps

1. ✅ Wire BuildingPrefab.unity following this guide
2. ✅ Run ValidateDialoguePanel to verify
3. ✅ Add Saori NPC with interaction trigger
4. ✅ Test with sample dialogue
5. ✅ Monitor Console for any warnings/errors
6. ✅ If issues arise, run ValidateDialoguePanel to diagnose

---

**This guide ensures BuildingPrefab.unity is properly configured for the canonical dialogue system without any AI-introduced errors or drift.**
