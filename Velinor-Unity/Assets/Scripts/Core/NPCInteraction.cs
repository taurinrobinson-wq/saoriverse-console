using UnityEngine;
using TMPro;
using UnityEngine.UI;

/// <summary>
/// NPCInteraction: Per-NPC GameObject script that detects player proximity and initiates dialogue.
/// 
/// Dual-Mode Operation:
/// - PRIMARY: Use DialogueManager if available (new system with JSON stories and stat tracking)
/// - FALLBACK: Simple hardcoded dialogue with state machine (when DialogueManager not found)
/// 
/// Responsibilities:
/// - Detect when player enters/exits trigger range
/// - Show/hide interaction prompt
/// - Listen for E-key press
/// - Call DialogueManager.StartDialogue() OR use simple dialogue fallback
/// </summary>
public class NPCInteraction : MonoBehaviour
{
    [SerializeField] private string npcId = "Ravi";
    [SerializeField] private string startingPassageId = "ravi_dialogue";

    private bool playerInRange = false;
    
    // Simple dialogue fallback (when DialogueManager not available)
    private int dialogueState = 0;
    private Canvas dialogueCanvas;
    private TextMeshProUGUI dialogueBodyText;
    private Button optionButton1;
    private Button optionButton2;

    void Start()
    {
        // Cache dialogue UI elements for fallback mode
        dialogueCanvas = FindAnyObjectByType<Canvas>();
        if (dialogueCanvas != null && dialogueCanvas.name == "DialogueCanvas")
        {
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            if (panelTransform != null)
            {
                dialogueBodyText = panelTransform.Find("DialogueBodyText")?.GetComponent<TextMeshProUGUI>();
                Transform containerTransform = panelTransform.Find("ChoiceButtonContainer");
                if (containerTransform != null && containerTransform.childCount >= 2)
                {
                    optionButton1 = containerTransform.GetChild(0)?.GetComponent<Button>();
                    optionButton2 = containerTransform.GetChild(1)?.GetComponent<Button>();
                }
            }
        }
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = true;
            Debug.Log($"🟣 Player entered {npcId} interaction trigger");
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = false;
            Debug.Log($"🟣 Player left {npcId} interaction trigger");
            HideInteractionPrompt();
            CloseDialogue();
        }
    }

    void Update()
    {
        if (!playerInRange) return;

        // Check for E key to open dialogue
        if (Input.GetKeyDown(KeyCode.E))
        {
            Debug.Log($"🟣 E-KEY PRESSED - Talking to {npcId}");
            OpenDialogue();
        }
        
        // Show prompt while in range
        ShowInteractionPrompt();
    }

    void ShowInteractionPrompt()
    {
        Canvas interactionCanvas = GameObject.Find("InteractionCanvas")?.GetComponent<Canvas>();
        if (interactionCanvas != null)
        {
            TextMeshProUGUI promptText = interactionCanvas.transform.Find("PromptText")?.GetComponent<TextMeshProUGUI>();
            if (promptText != null)
            {
                promptText.text = $"Press E to talk to {npcId}";
            }
        }
    }

    void HideInteractionPrompt()
    {
        Canvas interactionCanvas = GameObject.Find("InteractionCanvas")?.GetComponent<Canvas>();
        if (interactionCanvas != null)
        {
            TextMeshProUGUI promptText = interactionCanvas.transform.Find("PromptText")?.GetComponent<TextMeshProUGUI>();
            if (promptText != null)
            {
                promptText.text = "";
            }
        }
    }

    void OpenDialogue()
    {
        // Try DialogueManager first (new system with JSON stories)
        DialogueManager dialogueManager = FindAnyObjectByType<DialogueManager>();
        if (dialogueManager != null)
        {
            Debug.Log($"✅ Using DialogueManager for {npcId}");
            dialogueManager.StartDialogue(npcId, startingPassageId);
            return;
        }

        // Fallback: Use simple hardcoded dialogue
        Debug.Log($"⚠️ DialogueManager not found, using simple fallback dialogue for {npcId}");
        UseSimpleDialogue();
    }

    void UseSimpleDialogue()
    {
        if (dialogueCanvas == null)
        {
            Debug.LogWarning("No DialogueCanvas found for simple dialogue fallback!");
            return;
        }

        Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
        if (panelTransform != null)
            panelTransform.gameObject.SetActive(true);

        if (dialogueState == 0)
        {
            // Initial greeting
            if (dialogueBodyText != null)
                dialogueBodyText.text = "Hello there, what can I do for you?";

            SetupButton(optionButton1, "What's your name?", () =>
            {
                dialogueState = 1;
                UseSimpleDialogue();
            });

            SetupButton(optionButton2, "I don't need anything.", CloseDialogue);
        }
        else if (dialogueState == 1)
        {
            // Response to name question
            if (dialogueBodyText != null)
                dialogueBodyText.text = $"It's {npcId}. I gotta go.";

            SetupButton(optionButton1, "Okay.", CloseDialogue);
            if (optionButton2 != null)
                optionButton2.gameObject.SetActive(false);
        }
    }

    void SetupButton(Button button, string buttonText, UnityEngine.Events.UnityAction action)
    {
        if (button == null) return;

        button.gameObject.SetActive(true);
        TextMeshProUGUI btnTextComponent = button.GetComponentInChildren<TextMeshProUGUI>();
        if (btnTextComponent != null)
            btnTextComponent.text = buttonText;

        button.onClick.RemoveAllListeners();
        button.onClick.AddListener(action);
    }

    void CloseDialogue()
    {
        Debug.Log($"🟣 CloseDialogue called for {npcId}");
        
        if (dialogueCanvas != null)
        {
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            if (panelTransform != null)
                panelTransform.gameObject.SetActive(false);  // HIDE the dialogue panel
        }

        // Reset dialogue state
        dialogueState = 0;

        // Hide prompt
        Canvas interactionCanvas = GameObject.Find("InteractionCanvas")?.GetComponent<Canvas>();
        if (interactionCanvas != null)
        {
            TextMeshProUGUI promptText = interactionCanvas.transform.Find("PromptText")?.GetComponent<TextMeshProUGUI>();
            if (promptText != null)
                promptText.text = "";
        }
    }
}

