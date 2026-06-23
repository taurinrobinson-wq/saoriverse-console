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

        // Set up listeners once instead of RemoveAllListeners every time dialogue opens
        if (button1 != null)
        {
            button1.onClick.RemoveAllListeners();
            button1.onClick.AddListener(AskName);
        }
        if (button2 != null)
        {
            button2.onClick.RemoveAllListeners();
            button2.onClick.AddListener(CloseDialogue);
        }
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
            playerInRange = true;
    }

    protected virtual void OnTriggerStay(Collider other)
    {
        // Only process if player and not already in dialogue
        if (!other.CompareTag("Player") || isDialogueOpen)
            return;

        // Show interaction prompt
        InteractionUI.Instance?.ShowPrompt($"Press E to talk to {npcName}");

        // Check debounce and E-key press
        bool canOpenDialogue = (Time.time - lastDialogueCloseTime) >= dialogueInputCooldown;
        if (Input.GetKeyDown(KeyCode.E) && canOpenDialogue)
            OpenDialogue();
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
        }

        if (optionButton2 != null)
        {
            optionButton2.SetActive(true);
            if (button2Text != null)
                button2Text.text = "I don't need anything.";
        }
    }

    void AskName()
    {
        if (dialogueText != null)
            dialogueText.text = "It's Ravi. I gotta go.";

        if (optionButton1 != null)
        {
            optionButton1.SetActive(true);
            if (button1Text != null)
                button1Text.text = "Okay.";
        }

        if (optionButton2 != null)
            optionButton2.SetActive(false);
    }

    void CloseDialogue()
    {
        isDialogueOpen = false;
        lastDialogueCloseTime = Time.time;

        // Use cached panel reference instead of searching with Transform.Find
        if (dialoguePanel != null)
            dialoguePanel.gameObject.SetActive(false);

        if (optionButton1 != null)
            optionButton1.SetActive(false);
        if (optionButton2 != null)
            optionButton2.SetActive(false);
    }
}
