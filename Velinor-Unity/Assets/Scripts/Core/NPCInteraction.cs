using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class NPCInteraction : MonoBehaviour
{
    // === PER-NPC DATA ===
    public string npcName = "Male Villager";
    public string[] npcDialogueLines = new string[] { "Hello there, what can I do for you?" };
    public string[] npcOptions = new string[] { "What's your name?", "I don't need anything." };
    
    // === SHARED UI REFERENCES (assigned once, used by all NPCs) ===
    public Canvas dialogueCanvas;
    public TextMeshProUGUI dialogueText;
    public GameObject optionButton1;
    public GameObject optionButton2;
    
    // === INTERNAL STATE ===
    private bool isDialogueOpen = false;
    private bool playerInRange = false;
    private int currentDialogueIndex = 0;
    private float dialogueInputCooldown = 0.15f;
    private float lastDialogueCloseTime = -1f;
    
    // === CACHED COMPONENTS ===
    private Transform dialoguePanel;
    private Button button1;
    private Button button2;
    private TextMeshProUGUI button1Text;
    private TextMeshProUGUI button2Text;
    private SimplePlayerMovement playerMovement;

    void Awake()
    {
        CacheReferences();
    }

    void CacheReferences()
    {
        // Cache dialogue UI components (called once at initialization)
        if (dialogueCanvas != null)
            dialoguePanel = dialogueCanvas.transform.Find("DialoguePanel");

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

        // Cache player movement script for locking/unlocking
        GameObject playerObj = GameObject.FindGameObjectWithTag("Player");
        if (playerObj != null)
            playerMovement = playerObj.GetComponent<SimplePlayerMovement>();
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
            playerInRange = true;
    }

    void OnTriggerStay(Collider other)
    {
        // Only process if player is in range and no dialogue already open
        if (!other.CompareTag("Player") || isDialogueOpen)
            return;

        // Show interaction prompt
        InteractionUI.Instance?.ShowPrompt($"Press E to talk to {npcName}");

        // Check debounce timer before allowing dialogue open
        bool canOpenDialogue = (Time.time - lastDialogueCloseTime) >= dialogueInputCooldown;
        if (Input.GetKeyDown(KeyCode.E) && canOpenDialogue)
        {
            Debug.Log($"🟣 E-KEY PRESSED - Talking to {npcName}");
            OpenDialogue();
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = false;
            InteractionUI.Instance?.HidePrompt();
            CloseDialogue();
        }
    }

    void OpenDialogue()
    {
        isDialogueOpen = true;
        currentDialogueIndex = 0;  // Start at first dialogue line
        Debug.Log($"🟣 OpenDialogue called for {npcName}");

        // LOCK PLAYER MOVEMENT
        if (playerMovement != null)
            playerMovement.LockMovement(true);

        // UNLOCK CURSOR FOR UI INTERACTION
        Cursor.lockState = CursorLockMode.Confined;

        // Show dialogue UI
        if (dialoguePanel != null)
            dialoguePanel.gameObject.SetActive(true);

        // Display this NPC's first dialogue line
        if (dialogueText != null && currentDialogueIndex < npcDialogueLines.Length)
            dialogueText.text = npcDialogueLines[currentDialogueIndex];

        // Set Button 1: Ask for next dialogue (or close if at end)
        if (optionButton1 != null)
        {
            optionButton1.SetActive(true);
            if (button1Text != null)
                button1Text.text = (currentDialogueIndex < npcDialogueLines.Length - 1) ? "Continue" : npcOptions[0];

            if (button1 != null)
            {
                button1.onClick.RemoveAllListeners();
                button1.onClick.AddListener(OnButton1Click);
            }
        }

        // Set Button 2: Close dialogue
        if (optionButton2 != null)
        {
            optionButton2.SetActive(true);
            if (button2Text != null)
                button2Text.text = npcOptions[1];

            if (button2 != null)
            {
                button2.onClick.RemoveAllListeners();
                button2.onClick.AddListener(CloseDialogue);
            }
        }
    }

    void OnButton1Click()
    {
        Debug.Log($"🟢 BUTTON 1 CLICKED - {npcName}");
        
        // Move to next dialogue line if available
        if (currentDialogueIndex < npcDialogueLines.Length - 1)
        {
            currentDialogueIndex++;
            if (dialogueText != null && currentDialogueIndex < npcDialogueLines.Length)
                dialogueText.text = npcDialogueLines[currentDialogueIndex];

            // Update button 1 text for next click
            if (button1Text != null)
                button1Text.text = (currentDialogueIndex < npcDialogueLines.Length - 1) ? "Continue" : "Done";
        }
        else
        {
            // At end of dialogue, close on next button click
            CloseDialogue();
        }
    }

    void CloseDialogue()
    {
        Debug.Log($"🟣 CloseDialogue called - {npcName}");
        isDialogueOpen = false;
        lastDialogueCloseTime = Time.time;

        // UNLOCK PLAYER MOVEMENT
        if (playerMovement != null)
            playerMovement.LockMovement(false);

        // LOCK CURSOR FOR GAMEPLAY
        Cursor.lockState = CursorLockMode.Locked;

        // Hide dialogue UI
        if (dialoguePanel != null)
            dialoguePanel.gameObject.SetActive(false);

        // Hide buttons
        if (optionButton1 != null)
            optionButton1.SetActive(false);
        if (optionButton2 != null)
            optionButton2.SetActive(false);
    }
}

