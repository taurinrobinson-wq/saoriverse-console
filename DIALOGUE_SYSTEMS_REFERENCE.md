# Dialogue Systems in Unity - Reference Guide

**Source:** https://gamedevbeginner.com/dialogue-systems-in-unity/

## Core Dialogue System Architecture

A dialogue system consists of three main elements:
1. **Authoring** - How you write and store dialogue lines
2. **Dialogue UI** - How text is displayed on screen
3. **Dialogue System** - Scripts that connect UI, player, and NPCs

---

## 1. Writing and Storing Dialogue

### Simple String Storage
```csharp
[TextArea]
public string dialogue;
```

### String Array (Multiple lines)
```csharp
[TextArea]
public string[] lines;
```

### Scriptable Objects (Recommended for complex dialogue)
```csharp
[CreateAssetMenu]
public class DialogueAsset : ScriptableObject
{
    [TextArea]
    public string[] dialogue;
}
```

**Benefits of Scriptable Objects:**
- Centralized asset management
- Easy to reuse dialogue across NPCs
- Can be edited in Inspector without finding objects
- Scales better as dialogue content grows

---

## 2. Basic Dialogue UI Display

### Simple Dialogue Box Controller
```csharp
using UnityEngine.UI;
using System;
using TMPro;

public class DialogueBoxController : MonoBehaviour
{
    public static DialogueBoxController instance;

    [SerializeField] TextMeshProUGUI dialogueText;
    [SerializeField] TextMeshProUGUI nameText;
    [SerializeField] CanvasGroup dialogueBox;

    public static event Action OnDialogueStarted;
    public static event Action OnDialogueEnded;
    bool skipLineTriggered;

    private void Awake()
    {
        if (instance == null) {
            instance = this;
        }
        else {
            Destroy(this);
        }
    }

    public void StartDialogue(string[] dialogue, int startPosition, string name)
    {
        nameText.text = name + "...";
        dialogueBox.gameObject.SetActive(true);
        StopAllCoroutines();
        StartCoroutine(RunDialogue(dialogue, startPosition));
    }

    IEnumerator RunDialogue(string[] dialogue, int startPosition)
    {
        skipLineTriggered = false;
        OnDialogueStarted?.Invoke();

        for(int i = startPosition; i < dialogue.Length; i++)
        {
            dialogueText.text = dialogue[i];
            while (skipLineTriggered == false)
            {
                yield return null;
            }
            skipLineTriggered = false;
        }

        OnDialogueEnded?.Invoke();
        dialogueBox.gameObject.SetActive(false);
    }

    public void SkipLine()
    {
        skipLineTriggered = true;
    }
}
```

---

## 3. Multiple Choice Dialogue (Branching)

### Data Structures for Dialogue Trees

```csharp
[CreateAssetMenu]
public class DialogueTree : ScriptableObject
{
    public DialogueSection[] sections;
}

[System.Serializable]
public struct DialogueSection
{
    [TextArea]
    public string[] dialogue;
    public bool endAfterDialogue;
    public BranchPoint branchPoint;
}

[System.Serializable]
public struct BranchPoint
{
    [TextArea]
    public string question;
    public Answer[] answers;
}

[System.Serializable]
public struct Answer
{
    public string answerLabel;
    public int nextElement;  // Index of next DialogueSection
}
```

### Multiple Choice Dialogue Controller
```csharp
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using System;

public class DialogueBoxControllerMulti : MonoBehaviour
{
    public static DialogueBoxControllerMulti instance;

    [SerializeField] TextMeshProUGUI dialogueText;
    [SerializeField] TextMeshProUGUI nameText;
    [SerializeField] GameObject dialogueBox;
    [SerializeField] GameObject answerBox;
    [SerializeField] Button[] answerObjects;  // Array of answer buttons

    public static event Action OnDialogueStarted;
    public static event Action OnDialogueEnded;

    bool skipLineTriggered;
    bool answerTriggered;
    int answerIndex;

    private void Awake()
    {
        if (instance == null)
        {
            instance = this;
        }
        else
        {
            Destroy(this);
        }
    }

    public void StartDialogue(DialogueTree dialogueTree, int startSection, string name)
    {
        ResetBox();
        nameText.text = name + "...";
        dialogueBox.SetActive(true);
        OnDialogueStarted?.Invoke();
        StartCoroutine(RunDialogue(dialogueTree, startSection));
    }

    IEnumerator RunDialogue(DialogueTree dialogueTree, int section)
    {
        // Display all dialogue lines in this section
        for (int i = 0; i < dialogueTree.sections[section].dialogue.Length; i++)
        {
            dialogueText.text = dialogueTree.sections[section].dialogue[i];
            while (skipLineTriggered == false)
            {
                yield return null;
            }
            skipLineTriggered = false;
        }

        // Check if conversation ends here
        if (dialogueTree.sections[section].endAfterDialogue)
        {
            OnDialogueEnded?.Invoke();
            dialogueBox.SetActive(false);
            yield break;
        }

        // Show answer options
        dialogueText.text = dialogueTree.sections[section].branchPoint.question;
        ShowAnswers(dialogueTree.sections[section].branchPoint);

        // Wait for player to select answer
        while (answerTriggered == false)
        {
            yield return null;
        }
        answerBox.SetActive(false);
        answerTriggered = false;

        // Continue dialogue from selected answer path
        StartCoroutine(RunDialogue(dialogueTree, 
            dialogueTree.sections[section].branchPoint.answers[answerIndex].nextElement));
    }

    void ResetBox()
    {
        StopAllCoroutines();
        dialogueBox.SetActive(false);
        answerBox.SetActive(false);
        skipLineTriggered = false;
        answerTriggered = false;
    }

    void ShowAnswers(BranchPoint branchPoint)
    {
        answerBox.SetActive(true);
        for (int i = 0; i < answerObjects.Length; i++)
        {
            if (i < branchPoint.answers.Length)
            {
                answerObjects[i].GetComponentInChildren<TextMeshProUGUI>().text = branchPoint.answers[i].answerLabel;
                answerObjects[i].gameObject.SetActive(true);
            }
            else 
            {
                answerObjects[i].gameObject.SetActive(false);
            }
        }
    }

    public void SkipLine()
    {
        skipLineTriggered = true;
    }

    public void AnswerQuestion(int answer)
    {
        answerIndex = answer;
        answerTriggered = true;
    }
}
```

---

## 4. NPC and Player Integration

### NPC Script Pattern
```csharp
public class NPC : MonoBehaviour
{
    [SerializeField] bool firstInteraction = true;
    [SerializeField] int repeatStartPosition;

    public string npcName;
    public DialogueAsset dialogueAsset;

    [HideInInspector]
    public int StartPosition {
        get
        {
            if (firstInteraction)
            {
                firstInteraction = false;
                return 0;
            }
            else
            {
                return repeatStartPosition;
            }
        }
    }
}
```

### Player Interaction Script Pattern
```csharp
public class Player : MonoBehaviour
{
    [SerializeField] float talkDistance = 2;
    bool inConversation;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.E))
        {
            Interact();
        }
    }

    void Interact()
    {
        if (inConversation)
        {
            DialogueBoxController.instance.SkipLine();
        }
        else
        {
            if (Physics.Raycast(new Ray(transform.position, transform.forward), 
                out RaycastHit hitInfo, talkDistance))
            {
                if (hitInfo.collider.gameObject.TryGetComponent(out NPC npc))
                {
                    DialogueBoxController.instance.StartDialogue(
                        npc.dialogueAsset.dialogue, npc.StartPosition, npc.npcName);
                }
            }
        }
    }

    void JoinConversation()
    {
        inConversation = true;
    }

    void LeaveConversation()
    {
        inConversation = false;
    }

    private void OnEnable()
    {
        DialogueBoxController.OnDialogueStarted += JoinConversation;
        DialogueBoxController.OnDialogueEnded += LeaveConversation;
    }

    private void OnDisable()
    {
        DialogueBoxController.OnDialogueStarted -= JoinConversation;
        DialogueBoxController.OnDialogueEnded -= LeaveConversation;
    }
}
```

---

## 5. Design Patterns & Best Practices

### Singleton Pattern for Dialogue Controller
- Only one dialogue UI should exist at a time
- Other systems access it via static instance reference
- **Note:** Singletons can cause issues, but appropriate here since there's typically only one dialogue box

### Event System
```csharp
public static event Action OnDialogueStarted;
public static event Action OnDialogueEnded;
```

**Benefits:**
- Decouples systems (player movement, UI, etc.)
- Multiple systems can react to dialogue events
- Can disable player input, pause game, move camera, etc. during dialogue

### Separation of Concerns
- **NPCs store dialogue data** (who says what)
- **Player handles interaction triggers** (when to talk)
- **DialogueBoxController manages UI display** (how to show dialogue)
- **Events connect everything** (communication between systems)

---

## 6. Common UI Elements for Dialogue

### Character Name Display
- Show NPC name at top of dialogue box
- Format: "Name..."

### Dialogue Text
- Center-top aligned in panel
- Uses TextMeshPro for better formatting

### Answer Buttons
- Array of buttons (typically 2-4)
- Dynamically set text from dialogue data
- Use Navigation.Mode.None to prevent keyboard navigation conflicts
- AttachButton.onClick listeners for each choice

### Speaker Indicator
- Optional visual showing who's speaking
- Can be character portrait or name highlight

---

## 7. Advanced Features (For Later)

### Typewriter Effect
- Reveal text character-by-character
- Use coroutine with yield
- Can combine with auto-advance

### Character Portrait/Avatar
- Display image of speaking character
- Toggle based on who's talking

### Audio/Voice Lines
- Play sound clip when dialogue appears
- Sync with typewriter effect timing

### Conditional Dialogue
- Show different lines based on game state
- Track dialogue history
- Check player inventory or quest progress

### Dialogue Translation
- Store dialogue in external format (JSON)
- Import via localization system
- Tools: Articy, Ink

---

## 8. Recommended Assets

### Professional Dialogue Systems
- **Dialogue System for Unity** (Pixel Crushers)
  - Node-based visual editor
  - Highly customizable
  - Supports quests, callouts, audio
  - Integrates with other systems
  
- **Ink** (Inkle Studios)
  - Narrative design tool
  - Export to Unity
  - Good for complex branching stories

- **Articy** 
  - Professional dialogue tool
  - Visual editor
  - Unity integration plugin

---

## 9. Current Implementation Status

### ✅ Already Implemented
- Basic dialogue UI panel
- NPC interaction triggers
- Simple dialogue display
- Button onclick listeners
- EventSystem with StandaloneInputModule
- Button navigation set to None

### 🔄 Next Steps (Recommended Order)
1. Test current button click functionality
2. Add basic dialogue branching (multiple sections)
3. Implement Scriptable Object for dialogue storage
4. Add character name display
5. Implement typewriter effect
6. Add dialogue history tracking

### ❌ Not Yet Implemented
- Dialogue trees/branching
- Scriptable Object storage
- Portrait/avatar display
- Audio integration
- Advanced state management
- Localization/translation

---

## Notes for Future Work

- **Memory consideration:** For large dialogue systems, use dedicated assets (Dialogue System, Ink, Articy) rather than building custom
- **Testing:** Multiple choice dialogue needs thorough testing - button click detection is often buggy during development
- **Performance:** Coroutine-based systems are efficient for dialogue timing
- **Scalability:** Current hardcoded dialogue works for prototyping; use Scriptable Objects for production

