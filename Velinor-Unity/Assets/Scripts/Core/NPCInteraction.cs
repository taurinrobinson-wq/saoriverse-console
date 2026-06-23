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

    void OnTriggerEnter(Collider other)
    {
        Debug.Log($"🟣 OnTriggerEnter: {other.gameObject.name}, tag: {other.tag}");
    }

    protected virtual void OnTriggerStay(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            float distance = Vector3.Distance(transform.position, other.transform.position);
            if (distance <= interactionRange)
            {
                InteractionUI.Instance?.ShowPrompt($"Press E to talk to {npcName}");

                if (Input.GetKeyDown(KeyCode.E))
                {
                    Debug.Log($"🟣 Talking to {npcName}");
                    OpenDialogue();
                }
            }
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            InteractionUI.Instance?.HidePrompt();
            CloseDialogue();
        }
    }

    void OpenDialogue()
    {
        Debug.Log($"🟣 OpenDialogue called. Canvas: {dialogueCanvas}");
        if (dialogueCanvas != null)
        {
            dialogueCanvas.gameObject.SetActive(true);
            // Find and show the dialogue panel
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            Debug.Log($"🟣 Panel found: {panelTransform}");
            if (panelTransform != null)
                panelTransform.gameObject.SetActive(true);
        }

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
        {
            // Hide the dialogue panel
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            if (panelTransform != null)
                panelTransform.gameObject.SetActive(false);
        }
        if (optionButton1 != null)
            optionButton1.SetActive(false);
        if (optionButton2 != null)
            optionButton2.SetActive(false);
    }
}
