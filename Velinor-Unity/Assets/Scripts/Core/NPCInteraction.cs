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
    public GameObject interactPrompt;
    
    private bool playerInRange = false;
    private int dialogueState = 0;

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = true;
            if (interactPrompt != null)
                interactPrompt.SetActive(true);
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = false;
            if (interactPrompt != null)
                interactPrompt.SetActive(false);
            CloseDialogue();
        }
    }

    void Update()
    {
        if (playerInRange && Input.GetKeyDown(KeyCode.E))
        {
            OpenDialogue();
        }
    }

    void OpenDialogue()
    {
        if (dialogueCanvas != null)
            dialogueCanvas.gameObject.SetActive(true);
        
        dialogueState = 0;

        if (dialogueText != null)
            dialogueText.text = "Hello there, what can I do for you?";

        if (optionButton1 != null)
            optionButton1.SetActive(true);
        if (optionButton2 != null)
            optionButton2.SetActive(true);

        if (optionButton1 != null)
        {
            TextMeshProUGUI buttonText = optionButton1.GetComponentInChildren<TextMeshProUGUI>();
            if (buttonText != null)
                buttonText.text = "What's your name?";

            Button button = optionButton1.GetComponent<Button>();
            if (button != null)
            {
                button.onClick.RemoveAllListeners();
                button.onClick.AddListener(AskName);
            }
        }

        if (optionButton2 != null)
        {
            TextMeshProUGUI buttonText = optionButton2.GetComponentInChildren<TextMeshProUGUI>();
            if (buttonText != null)
                buttonText.text = "I don't need anything.";

            Button button = optionButton2.GetComponent<Button>();
            if (button != null)
            {
                button.onClick.RemoveAllListeners();
                button.onClick.AddListener(CloseDialogue);
            }
        }
    }

    void AskName()
    {
        if (dialogueText != null)
            dialogueText.text = "It's Ravi. I gotta go.";

        if (optionButton1 != null)
            optionButton1.SetActive(true);
        if (optionButton2 != null)
            optionButton2.SetActive(false);

        if (optionButton1 != null)
        {
            TextMeshProUGUI buttonText = optionButton1.GetComponentInChildren<TextMeshProUGUI>();
            if (buttonText != null)
                buttonText.text = "Okay.";

            Button button = optionButton1.GetComponent<Button>();
            if (button != null)
            {
                button.onClick.RemoveAllListeners();
                button.onClick.AddListener(CloseDialogue);
            }
        }
    }

    void CloseDialogue()
    {
        if (dialogueCanvas != null)
            dialogueCanvas.gameObject.SetActive(false);
        if (optionButton1 != null)
            optionButton1.SetActive(false);
        if (optionButton2 != null)
            optionButton2.SetActive(false);
        
        dialogueState = 0;
    }
}
