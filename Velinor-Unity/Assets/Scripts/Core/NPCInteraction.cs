using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Collections.Generic;

/// <summary>
/// NPCInteraction: Per-NPC dialogue handler with TONE/REMNANTS integration.
/// 
/// Features:
/// - Multi-round dialogue sequences
/// - TONE choice labeling (T/O/N/E)
/// - REMNANTS stat effects
/// - Name reveal mechanics
/// - Consistent button styling
/// </summary>
public class NPCInteraction : MonoBehaviour
{
    [SerializeField] private string npcId = "Ravi";
    
    private bool playerInRange = false;
    private int currentRound = 0;
    private bool dialogueActive = false;
    
    // UI References
    private Canvas dialogueCanvas;
    private TextMeshProUGUI npcNameText;
    private TextMeshProUGUI dialogueBodyText;
    private Button optionButton1;
    private Button optionButton2;
    private Button optionButton3;
    private Button optionButton4;
    private Transform choiceContainer;
    
    // Dialogue Sequence
    private RaviDialogueSequence dialogueSequence;
    
    // NPC Stats (Ravi's canonical values)
    private NPCStats raviStats;

    void Start()
    {
        // Initialize dialogue sequence for Ravi
        dialogueSequence = new RaviDialogueSequence();
        
        // Initialize NPC stats with Ravi's canonical values
        raviStats = new NPCStats
        {
            Resolve = 0.3f,
            Empathy = 0.9f,
            Memory = 0.9f,
            Nuance = 0.7f,
            Authority = 0.3f,
            Need = 0.9f,
            Trust = 0.1f,
            Skepticism = 0.9f
        };
        
        // Cache UI elements
        CacheUIElements();
    }

    void CacheUIElements()
    {
        dialogueCanvas = FindAnyObjectByType<Canvas>();
        if (dialogueCanvas != null && dialogueCanvas.name == "DialogueCanvas")
        {
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            if (panelTransform != null)
            {
                npcNameText = panelTransform.Find("NPCNameText")?.GetComponent<TextMeshProUGUI>();
                dialogueBodyText = panelTransform.Find("DialogueBodyText")?.GetComponent<TextMeshProUGUI>();
                choiceContainer = panelTransform.Find("ChoiceButtonContainer");
                
                if (choiceContainer != null && choiceContainer.childCount >= 4)
                {
                    optionButton1 = choiceContainer.GetChild(0)?.GetComponent<Button>();
                    optionButton2 = choiceContainer.GetChild(1)?.GetComponent<Button>();
                    optionButton3 = choiceContainer.GetChild(2)?.GetComponent<Button>();
                    optionButton4 = choiceContainer.GetChild(3)?.GetComponent<Button>();
                    
                    Debug.Log($"🟣 {npcId}: Cached UI elements");
                }
            }
        }
    }

    void Update()
    {
        // Detect player proximity using OverlapSphere
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
            CloseDialogue();
            HideInteractionPrompt();
        }

        if (!playerInRange) return;

        ShowInteractionPrompt();

        // E key to open dialogue
        if (Input.GetKeyDown(KeyCode.E) && !dialogueActive)
        {
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
        dialogueActive = true;
        currentRound = 0;
        
        if (dialogueCanvas == null)
        {
            CacheUIElements();
        }
        
        ShowDialogueRound();
    }

    void ShowDialogueRound()
    {
        if (currentRound >= dialogueSequence.rounds.Count)
        {
            // Dialogue complete
            Debug.Log($"🟣 {npcId}: Dialogue sequence complete");
            CloseDialogue();
            return;
        }

        Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
        if (panelTransform == null)
        {
            Debug.LogError("DialoguePanel not found!");
            return;
        }

        panelTransform.gameObject.SetActive(true);
        RectTransform panelRect = panelTransform as RectTransform;
        LayoutRebuilder.ForceRebuildLayoutImmediate(panelRect);

        DialogueRound round = dialogueSequence.rounds[currentRound];
        
        // Show NPC name (or "???" if not revealed)
        if (npcNameText != null)
        {
            npcNameText.text = dialogueSequence.playerKnowsName ? "Ravi" : "???";
        }
        
        // Show NPC's line
        if (dialogueBodyText != null)
        {
            dialogueBodyText.text = round.npcLine;
        }

        // Show the 4 TONE choices
        SetupChoiceButtons(round);
    }

    void SetupChoiceButtons(DialogueRound round)
    {
        // Hide all buttons first
        if (optionButton1 != null) optionButton1.gameObject.SetActive(false);
        if (optionButton2 != null) optionButton2.gameObject.SetActive(false);
        if (optionButton3 != null) optionButton3.gameObject.SetActive(false);
        if (optionButton4 != null) optionButton4.gameObject.SetActive(false);

        // Setup each button with corresponding choice
        Button[] buttons = { optionButton1, optionButton2, optionButton3, optionButton4 };
        
        for (int i = 0; i < round.choices.Count && i < buttons.Length; i++)
        {
            DialogueChoice choice = round.choices[i];
            Button btn = buttons[i];
            int choiceIndex = i;  // Capture for closure
            
            SetupChoiceButton(btn, choice, () => OnChoiceSelected(choiceIndex));
        }

        // Force layout rebuild
        if (choiceContainer != null)
        {
            LayoutRebuilder.ForceRebuildLayoutImmediate(choiceContainer as RectTransform);
        }
    }

    void SetupChoiceButton(Button button, DialogueChoice choice, UnityEngine.Events.UnityAction action)
    {
        if (button == null) return;

        button.gameObject.SetActive(true);

        // Set button text with TONE label
        TextMeshProUGUI btnText = button.GetComponentInChildren<TextMeshProUGUI>();
        if (btnText != null)
        {
            btnText.text = $"({choice.toneType}) {choice.playerLine}";
        }

        // Ensure consistent dark gray styling
        Image btnImage = button.GetComponent<Image>();
        if (btnImage != null)
        {
            btnImage.color = new Color(0.2f, 0.2f, 0.2f, 1f);
        }

        ColorBlock colors = button.colors;
        colors.normalColor = new Color(0.2f, 0.2f, 0.2f, 1f);
        colors.highlightedColor = new Color(0.3f, 0.3f, 0.3f, 1f);
        colors.pressedColor = new Color(0.1f, 0.1f, 0.1f, 1f);
        button.colors = colors;

        // Set button action
        button.onClick.RemoveAllListeners();
        button.onClick.AddListener(action);
        
        Debug.Log($"🟢 Setup button: ({choice.toneType}) - {choice.playerLine}");
    }

    void OnChoiceSelected(int choiceIndex)
    {
        DialogueRound round = dialogueSequence.rounds[currentRound];
        DialogueChoice choice = round.choices[choiceIndex];

        Debug.Log($"🟢 Player chose ({choice.toneType}): {choice.playerLine}");
        
        // Apply REMNANTS effects
        foreach (var kvp in choice.remnantEffects)
        {
            ApplyRemnantEffect(kvp.Key, kvp.Value);
        }

        // Check for name reveal (NarrativePresence choice)
        if (choice.toneType == 'N')
        {
            dialogueSequence.playerKnowsName = true;
            Debug.Log($"✨ Player learned {npcId}'s name!");
        }

        // Move to next round
        currentRound++;
        
        // Show dialogue panel again
        Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
        if (panelTransform != null)
        {
            panelTransform.gameObject.SetActive(true);
        }

        // Show next round or end dialogue
        if (currentRound < dialogueSequence.rounds.Count)
        {
            ShowDialogueRound();
        }
        else
        {
            CloseDialogue();
        }
    }

    void ApplyRemnantEffect(string remnantName, float delta)
    {
        // Apply to Ravi's stats
        switch (remnantName)
        {
            case "Resolve": raviStats.Resolve = Mathf.Clamp01(raviStats.Resolve + delta * 0.05f); break;
            case "Empathy": raviStats.Empathy = Mathf.Clamp01(raviStats.Empathy + delta * 0.05f); break;
            case "Memory": raviStats.Memory = Mathf.Clamp01(raviStats.Memory + delta * 0.05f); break;
            case "Nuance": raviStats.Nuance = Mathf.Clamp01(raviStats.Nuance + delta * 0.05f); break;
            case "Authority": raviStats.Authority = Mathf.Clamp01(raviStats.Authority + delta * 0.05f); break;
            case "Need": raviStats.Need = Mathf.Clamp01(raviStats.Need + delta * 0.05f); break;
            case "Trust": raviStats.Trust = Mathf.Clamp01(raviStats.Trust + delta * 0.05f); break;
            case "Skepticism": raviStats.Skepticism = Mathf.Clamp01(raviStats.Skepticism + delta * 0.05f); break;
        }
        
        Debug.Log($"📊 {remnantName} {(delta > 0 ? "+" : "")}{delta}: {raviStats.GetRemnant(remnantName):F2}");
    }

    void CloseDialogue()
    {
        dialogueActive = false;
        currentRound = 0;
        
        if (dialogueCanvas != null)
        {
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            if (panelTransform != null)
            {
                panelTransform.gameObject.SetActive(false);
            }
        }
        
        Debug.Log($"🟣 {npcId} dialogue closed");
    }
}

/// <summary>
/// NPCStats: Tracks a single NPC's emotional state.
/// </summary>
public class NPCStats
{
    public float Resolve;
    public float Empathy;
    public float Memory;
    public float Nuance;
    public float Authority;
    public float Need;
    public float Trust;
    public float Skepticism;

    public float GetRemnant(string name)
    {
        return name switch
        {
            "Resolve" => Resolve,
            "Empathy" => Empathy,
            "Memory" => Memory,
            "Nuance" => Nuance,
            "Authority" => Authority,
            "Need" => Need,
            "Trust" => Trust,
            "Skepticism" => Skepticism,
            _ => 0f
        };
    }
}
