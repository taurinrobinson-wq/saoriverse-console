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
                    
                    Debug.Log($"🟣 NPCInteraction ({npcId}): Found DialogueCanvas UI elements");
                    Debug.Log($"  - Body text: {(dialogueBodyText != null ? "✅" : "❌")}");
                    Debug.Log($"  - Button 1: {(optionButton1 != null ? "✅" : "❌")}");
                    Debug.Log($"  - Button 2: {(optionButton2 != null ? "✅" : "❌")}");
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
        // Check for player in range using overlap sphere (more reliable than trigger collider on child)
        Collider[] colliders = Physics.OverlapSphere(transform.position, 2f);
        bool playerDetected = false;
        
        foreach (Collider col in colliders)
        {
            if (col.CompareTag("Player"))
            {
                playerDetected = true;
                break;
            }
        }
        
        if (playerDetected && !playerInRange)
        {
            playerInRange = true;
            Debug.Log($"🟣 Player detected near {npcId}");
        }
        else if (!playerDetected && playerInRange)
        {
            playerInRange = false;
            Debug.Log($"🟣 Player left {npcId}");
            HideInteractionPrompt();
            CloseDialogue();
        }

        if (!playerInRange) return;

        // Show prompt while in range
        ShowInteractionPrompt();

        // Check for E key to open dialogue
        if (Input.GetKeyDown(KeyCode.E))
        {
            Debug.Log($"🟣 E-KEY PRESSED - Talking to {npcId}");
            OpenDialogue();
        }
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
        {
            panelTransform.gameObject.SetActive(true);
            Debug.Log($"🟣 Panel activated for {npcId}");
            
            // Debug panel state
            RectTransform panelRect = panelTransform.GetComponent<RectTransform>();
            if (panelRect != null)
            {
                Debug.Log($"📊 DialoguePanel: size={panelRect.sizeDelta}, pos={panelRect.anchoredPosition}");
            }
        }

        if (dialogueState == 0)
        {
            // Initial greeting
            if (dialogueBodyText != null)
            {
                dialogueBodyText.text = "Hello there, what can I do for you?";
                Debug.Log($"🟣 Set dialogue text to greeting");
            }

            SetupButton(optionButton1, "What's your name?", () =>
            {
                Debug.Log($"🟢 Button 1 clicked");
                dialogueState = 1;
                UseSimpleDialogue();
            });

            SetupButton(optionButton2, "I don't need anything.", () =>
            {
                Debug.Log($"🟢 Button 2 clicked");
                CloseDialogue();
            });
            
            // Force layout rebuild to ensure buttons are positioned correctly
            if (optionButton1 != null && optionButton2 != null)
            {
                LayoutRebuilder.ForceRebuildLayoutImmediate(panelTransform as RectTransform);
                Debug.Log($"🟢 Layout rebuilt for dialogue panel");
            }
        }
        else if (dialogueState == 1)
        {
            // Response to name question
            if (dialogueBodyText != null)
            {
                dialogueBodyText.text = $"It's {npcId}. I gotta go.";
                Debug.Log($"🟣 Set dialogue text to response");
            }

            SetupButton(optionButton1, "Okay.", () =>
            {
                Debug.Log($"🟢 Okay button clicked");
                CloseDialogue();
            });
            
            if (optionButton2 != null)
                optionButton2.gameObject.SetActive(false);
        }
    }

    void SetupButton(Button button, string buttonText, UnityEngine.Events.UnityAction action)
    {
        if (button == null)
        {
            Debug.LogWarning($"🔴 Button is null! Cannot set up button for text: {buttonText}");
            return;
        }

        button.gameObject.SetActive(true);
        TextMeshProUGUI btnTextComponent = button.GetComponentInChildren<TextMeshProUGUI>();
        if (btnTextComponent != null)
        {
            btnTextComponent.text = buttonText;
            Debug.Log($"🟢 Set button text: {buttonText}");
        }
        else
        {
            Debug.LogWarning($"🔴 Could not find TextMeshProUGUI in button!");
        }

        button.onClick.RemoveAllListeners();
        button.onClick.AddListener(action);
        
        // Debug button visibility
        RectTransform btnRect = button.GetComponent<RectTransform>();
        if (btnRect != null)
        {
            Debug.Log($"📊 Button '{buttonText}' properties:");
            Debug.Log($"  - Size: {btnRect.sizeDelta}");
            Debug.Log($"  - Position: {btnRect.anchoredPosition}");
            Debug.Log($"  - LocalScale: {btnRect.localScale}");
            Debug.Log($"  - Active: {button.gameObject.activeSelf}");
            Debug.Log($"  - Image color: {button.GetComponent<Image>()?.color}");
            Debug.Log($"  - Text color: {btnTextComponent?.color}");
        }
        
        Debug.Log($"🟢 Button '{buttonText}' is now interactive");
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

