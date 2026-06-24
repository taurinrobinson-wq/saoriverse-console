using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class NPCInteraction : MonoBehaviour
{
    public string npcName = "Male Villager";
    public Canvas dialogueCanvas;
    public TextMeshProUGUI dialogueText;
    public GameObject optionButton1;
    public GameObject optionButton2;
    
    private float interactionRange = 3f;
    private float dialogueInputCooldown = 0.15f;
    private float lastDialogueCloseTime = -1f;
    
    // === OPTIMIZATION: Cache references to avoid repeated GetComponent/Find calls ===
    private Transform dialoguePanel;
    private Button button1;
    private Button button2;
    private TextMeshProUGUI button1Text;
    private TextMeshProUGUI button2Text;
    private bool isDialogueOpen = false;
    private bool playerInRange = false;

    // === MULTI-NPC TRACKING: Only one NPC can be in dialogue at a time ===
    private static NPCInteraction currentActiveNPC = null;

    void Awake()
    {
        CacheDialogueReferences();
    }

    void CacheDialogueReferences()
    {
        // Cache panel reference once (not every frame with Transform.Find)
        if (dialogueCanvas != null)
            dialoguePanel = dialogueCanvas.transform.Find("DialoguePanel");

        // Cache button components (not every time we open dialogue)
        if (optionButton1 != null)
        {
            button1 = optionButton1.GetComponent<Button>();
            button1Text = optionButton1.GetComponentInChildren<TextMeshProUGUI>();
        }
        if (optionButton2 != null)
        {
            button2 = optionButton2.GetComponent<Button>();
            button2Text = optionButton2.GetComponentInChildren<TextMeshProUGUI>();
        }

        // Button listeners will be set up dynamically in OpenDialogue
        // This keeps performance optimized while allowing state-based listener updates
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
            playerInRange = true;
    }

    protected virtual void OnTriggerStay(Collider other)
    {
        // Only process if player is in range
        if (!other.CompareTag("Player"))
            return;

        // If another NPC is active, don't show this NPC's prompt
        if (currentActiveNPC != null && currentActiveNPC != this)
            return;

        // Show interaction prompt
        InteractionUI.Instance?.ShowPrompt($"Press E to talk to {npcName}");

        // Check debounce and E-key press
        bool canOpenDialogue = (Time.time - lastDialogueCloseTime) >= dialogueInputCooldown;
        if (Input.GetKeyDown(KeyCode.E) && canOpenDialogue)
        {
            Debug.Log($"🟣 E-KEY PRESSED - Talking to {npcName}");
            
            // Close any other active NPC dialogue first
            if (currentActiveNPC != null && currentActiveNPC != this)
                currentActiveNPC.CloseDialogue();
            
            OpenDialogue();
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = false;
            InteractionUI.Instance?.HidePrompt();
            
            // Only close if this NPC is the active one
            if (currentActiveNPC == this)
                CloseDialogue();
        }
    }

    void OpenDialogue()
    {
        isDialogueOpen = true;
        currentActiveNPC = this;  // Mark this NPC as the active dialogue partner
        Debug.Log($"🟣 OpenDialogue called for {npcName}");

        // Use cached panel reference instead of searching with Transform.Find
        if (dialoguePanel != null)
            dialoguePanel.gameObject.SetActive(true);

        if (dialogueText != null)
            dialogueText.text = "Hello there, what can I do for you?";

        // Use cached button references - no GetComponent calls
        if (optionButton1 != null)
        {
            optionButton1.SetActive(true);
            if (button1Text != null)
                button1Text.text = "What's your name?";
            
            // Reset Button 1 listener to initial state (AskName)
            if (button1 != null)
            {
                button1.onClick.RemoveAllListeners();
                button1.onClick.AddListener(AskName);
            }
        }

        if (optionButton2 != null)
        {
            optionButton2.SetActive(true);
            if (button2Text != null)
                button2Text.text = "I don't need anything.";
            
            // Set Button 2 listener to close dialogue
            if (button2 != null)
            {
                button2.onClick.RemoveAllListeners();
                button2.onClick.AddListener(CloseDialogue);
            }
        }

        Debug.Log($"🟢 Button 1 ready: {(button1 != null ? "YES" : "NO")}");
        Debug.Log($"🔴 Button 2 ready: {(button2 != null ? "YES" : "NO")}");
    }

    void AskName()
    {
        Debug.Log($"🟢 BUTTON 1 CLICKED");
        if (dialogueText != null)
            dialogueText.text = $"My name is {npcName}. Nice to meet you!";

        if (optionButton1 != null)
        {
            optionButton1.SetActive(true);
            if (button1Text != null)
                button1Text.text = "Thanks!";
            
            // Update button 1 listener for the "Thanks!" state to close dialogue
            if (button1 != null)
            {
                button1.onClick.RemoveAllListeners();
                button1.onClick.AddListener(CloseDialogue);
            }
        }

        if (optionButton2 != null)
            optionButton2.SetActive(false);
    }

    void CloseDialogue()
    {
        Debug.Log($"🟣 CloseDialogue called - Dialogue closing");
        isDialogueOpen = false;
        lastDialogueCloseTime = Time.time;

        // Only clear currentActiveNPC if this NPC is the one closing
        if (currentActiveNPC == this)
            currentActiveNPC = null;

        // Use cached panel reference instead of searching with Transform.Find
        if (dialoguePanel != null)
            dialoguePanel.gameObject.SetActive(false);

        if (optionButton1 != null)
            optionButton1.SetActive(false);
        if (optionButton2 != null)
            optionButton2.SetActive(false);
    }
}
