# DialogueManager Canonical Field Reference

**This file defines the EXACT fields that DialogueManager expects. Use this as a reference when wiring BuildingPrefab.scene or when instructing Unity AI.**

---

## Canonical Field Declarations

```csharp
public class DialogueManager : MonoBehaviour
{
    // ===== ROOT PANEL =====
    [SerializeField] private Canvas dialogueCanvas;
    public GameObject dialoguePanel => dialogueCanvas != null ? dialogueCanvas.gameObject : null;

    // ===== TEXT FIELDS =====
    [SerializeField] private TextMeshProUGUI bodyText;              // Dialogue prompt/passage
    [SerializeField] private TextMeshProUGUI npcNameText;           // NPC speaker name
    [SerializeField] private TextMeshProUGUI sharedBeatText;        // Narrative beats display

    // ===== CHOICE BUTTONS =====
    [SerializeField] private Button btnT;                           // Trust button
    [SerializeField] private Button btnO;                           // Observation button
    [SerializeField] private Button btnN;                           // NarrativePresence button
    [SerializeField] private Button btnE;                           // Empathy button

    // ===== BUTTON LABELS =====
    [SerializeField] private TextMeshProUGUI txtT;                  // Trust choice text
    [SerializeField] private TextMeshProUGUI txtO;                  // Observation choice text
    [SerializeField] private TextMeshProUGUI txtN;                  // NarrativePresence choice text
    [SerializeField] private TextMeshProUGUI txtE;                  // Empathy choice text

    // ===== FALLBACK (Dynamic Spawning) =====
    [SerializeField] private Transform choiceButtonContainer;       // Container for dynamic buttons
    [SerializeField] private GameObject _choiceButtonPrefab;        // Prefab for dynamic buttons
}
```

---

## Inspector Assignment Checklist

Use this checklist when assigning fields in Unity Inspector:

### Root Panel
- [ ] **dialogueCanvas** → Drag Canvas object from scene hierarchy

### Text Fields
- [ ] **bodyText** → Drag "DialogueBodyText" TextMeshProUGUI
- [ ] **npcNameText** → Drag "NPCLineText" TextMeshProUGUI  
- [ ] **sharedBeatText** → Drag "SharedBeatText" TextMeshProUGUI (initially disabled)

### Choice Buttons
- [ ] **btnT** → Drag "ChoiceButton_T" Button component
- [ ] **btnO** → Drag "ChoiceButton_O" Button component
- [ ] **btnN** → Drag "ChoiceButton_N" Button component
- [ ] **btnE** → Drag "ChoiceButton_E" Button component

### Button Labels
- [ ] **txtT** → Drag child Text of ChoiceButton_T
- [ ] **txtO** → Drag child Text of ChoiceButton_O
- [ ] **txtN** → Drag child Text of ChoiceButton_N
- [ ] **txtE** → Drag child Text of ChoiceButton_E

### Fallback (Optional)
- [ ] **choiceButtonContainer** → (Leave empty if using static buttons)
- [ ] **choiceButtonPrefab** → (Leave empty if using static buttons)

---

## Field Purpose Reference

| Field | Type | Purpose | Required? |
|-------|------|---------|-----------|
| dialogueCanvas | Canvas | Root container for all UI | YES |
| bodyText | TextMeshProUGUI | Shows dialogue passage text | YES |
| npcNameText | TextMeshProUGUI | Shows NPC name/speaker | YES |
| sharedBeatText | TextMeshProUGUI | Shows narrative beats after choices | YES |
| btnT | Button | Trust choice button | YES* |
| btnO | Button | Observation choice button | YES* |
| btnN | Button | NarrativePresence choice button | YES* |
| btnE | Button | Empathy choice button | YES* |
| txtT | TextMeshProUGUI | Label for Trust button | YES* |
| txtO | TextMeshProUGUI | Label for Observation button | YES* |
| txtN | TextMeshProUGUI | Label for NarrativePresence button | YES* |
| txtE | TextMeshProUGUI | Label for Empathy button | YES* |
| choiceButtonContainer | Transform | Container for dynamic buttons | NO** |
| _choiceButtonPrefab | GameObject | Prefab for dynamic button spawning | NO** |

*YES = Required if using static button mode (preferred)
**NO** = Only needed if NOT using static buttons

---

## Validation Code

When validating wiring, use this method:

```csharp
[ContextMenu("ValidateDialoguePanel")]
public void ValidateDialoguePanel()
{
    bool allValid = true;

    // Canvas validation
    if (dialogueCanvas != null) 
        Debug.Log("✓ DialogueCanvas: ASSIGNED");
    else 
    {
        Debug.LogError("✗ DialogueCanvas: NOT ASSIGNED");
        allValid = false;
    }

    // Text fields validation
    if (bodyText != null) 
        Debug.Log("✓ bodyText: ASSIGNED");
    else 
    {
        Debug.LogError("✗ bodyText: NOT ASSIGNED");
        allValid = false;
    }

    // ... (same for npcNameText, sharedBeatText)

    // Button validation
    if (btnT != null) Debug.Log("✓ btnT: ASSIGNED"); else { Debug.LogError("✗ btnT: NOT ASSIGNED"); allValid = false; }
    if (btnO != null) Debug.Log("✓ btnO: ASSIGNED"); else { Debug.LogError("✗ btnO: NOT ASSIGNED"); allValid = false; }
    if (btnN != null) Debug.Log("✓ btnN: ASSIGNED"); else { Debug.LogError("✗ btnN: NOT ASSIGNED"); allValid = false; }
    if (btnE != null) Debug.Log("✓ btnE: ASSIGNED"); else { Debug.LogError("✗ btnE: NOT ASSIGNED"); allValid = false; }

    // Button label validation
    if (txtT != null) Debug.Log("✓ txtT: ASSIGNED"); else { Debug.LogError("✗ txtT: NOT ASSIGNED"); allValid = false; }
    if (txtO != null) Debug.Log("✓ txtO: ASSIGNED"); else { Debug.LogError("✗ txtO: NOT ASSIGNED"); allValid = false; }
    if (txtN != null) Debug.Log("✓ txtN: ASSIGNED"); else { Debug.LogError("✗ txtN: NOT ASSIGNED"); allValid = false; }
    if (txtE != null) Debug.Log("✓ txtE: ASSIGNED"); else { Debug.LogError("✗ txtE: NOT ASSIGNED"); allValid = false; }

    if (allValid)
        Debug.Log("✓ ALL VALIDATION CHECKS PASSED");
    else
        Debug.LogError("✗ VALIDATION FAILED - Fix missing assignments");
}
```

---

## Scene Hierarchy Names (MUST MATCH)

These names are used by DialogueManager to locate fallback UI if fields aren't explicitly assigned:

```
Canvas (any name, but assigned to dialogueCanvas field)
└── DialoguePanel
    ├── DialogueBodyText     ← bodyText
    ├── NPCLineText          ← npcNameText
    ├── SharedBeatText       ← sharedBeatText
    ├── ChoiceButton_T       ← btnT
    │   └── Text             ← txtT (child TextMeshProUGUI)
    ├── ChoiceButton_O       ← btnO
    │   └── Text             ← txtO (child TextMeshProUGUI)
    ├── ChoiceButton_N       ← btnN
    │   └── Text             ← txtN (child TextMeshProUGUI)
    └── ChoiceButton_E       ← btnE
        └── Text             ← txtE (child TextMeshProUGUI)
```

---

## How DialogueManager Uses These Fields

### DisplayPassage()
1. Sets `bodyText.text` = dialogue passage
2. Sets `npcNameText.text` = active NPC name
3. Maps choices to buttons by ToneType:
   - Choice with `tone = Trust` → `btnT.text = choice.playerLine`
   - Choice with `tone = Observation` → `btnO.text = choice.playerLine`
   - Choice with `tone = NarrativePresence` → `btnN.text = choice.playerLine`
   - Choice with `tone = Empathy` → `btnE.text = choice.playerLine`
4. Binds button clicks to choice handler

### OnChoiceMade()
1. Applies tone drift via StatManager
2. Shows `sharedBeatText` with narrative beat
3. Calls `FindTextMeshInCanvas()` to locate text fields if not explicitly assigned

### ClearButtons()
1. Sets all 4 buttons to inactive
2. Or destroys dynamically spawned buttons (fallback mode)

---

## Important: No String Matching

DialogueManager **never** searches for buttons by text matching like:
```csharp
// ✗ WRONG - Don't do this:
if (choice.text.Contains("(T)")) targetBtn = btnT;

// ✓ CORRECT - Uses enum value:
switch (choice.tone)
{
    case ToneType.Trust:
        targetBtn = btnT;
        break;
    // ...
}
```

This prevents Unity AI from accidentally introducing terminology drift.

---

## Quick Unity AI Instruction

> **Instruction for Unity AI:**
> 
> Do NOT auto-bind DialogueManager fields. Do NOT search for buttons by name. 
> Do NOT parse choice text to determine tone.
> 
> **ONLY:** Explicitly assign fields from the Inspector following the canonical field reference.
> 
> Fields to assign:
> - dialogueCanvas (Canvas)
> - bodyText, npcNameText, sharedBeatText (TextMeshProUGUI)
> - btnT, btnO, btnN, btnE (Button)
> - txtT, txtO, txtN, txtE (TextMeshProUGUI labels)
> 
> Verify with ValidateDialoguePanel() method.

---

This reference ensures DialogueManager is wired exactly as designed, preventing any AI-introduced errors.
