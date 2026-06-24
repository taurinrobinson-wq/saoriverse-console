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
                    Debug.Log($"🟣 E-KEY PRESSED - Talking to {npcName}");
                    OpenDialogue();
                }
            }
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            Debug.Log($"🟣 Player left NPC interaction range");
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
            {
                panelTransform.gameObject.SetActive(true);
                Debug.Log($"🟣 Panel ACTIVATED - should be visible now");
            }
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
                Debug.Log($"🟢 Button 1 setup - interactable: {button.interactable}");
                button.onClick.RemoveAllListeners();
                button.onClick.AddListener(AskName);
                button.onClick.AddListener(() => Debug.Log("🟢 BUTTON 1 CLICKED"));
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
                Debug.Log($"🔴 Button 2 setup - interactable: {button.interactable}");
                button.onClick.RemoveAllListeners();
                button.onClick.AddListener(CloseDialogue);
                button.onClick.AddListener(() => Debug.Log("🔴 BUTTON 2 CLICKED"));
            }
        }
    }

    void AskName()
    {
        Debug.Log($"🟢 AskName called!");
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
                button.onClick.AddListener(() => Debug.Log("🟢 BUTTON 1 CLICKED (Okay)"));
            }
        }
    }

    void CloseDialogue()
    {
        Debug.Log($"🟣 CloseDialogue called!");
        if (dialogueCanvas != null)
        {
            // Hide the dialogue panel
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            if (panelTransform != null)
            {
                panelTransform.gameObject.SetActive(false);
                Debug.Log($"🟣 Panel DEACTIVATED");
            }
        }
        if (optionButton1 != null)
            optionButton1.SetActive(false);
        if (optionButton2 != null)
            optionButton2.SetActive(false);
    }
}
            optionButton2.SetActive(false);
    }
}

