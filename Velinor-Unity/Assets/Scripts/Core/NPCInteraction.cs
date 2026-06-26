using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Collections.Generic;
using VelinorGame.Core;

/// <summary>
/// NPCInteraction: Multi-NPC dialogue handler with gate-based progression.
/// 
/// Features:
/// - Multi-NPC support (Ravi, Malrik, Elenya)
/// - Gate-based story progression
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
    
    // Dialogue Sequences - support for multiple NPCs
    private RaviDialogueSequence raviDialogueSequence;
    private MalrikDialogueSequence malrikDialogueSequence;
    private ElenyaDialogueSequence elenyaDialogueSequence;
    
    // Gate evaluator for story progression
    private DialogueGateEvaluator gateEvaluator;
    
    // Current dialogue state
    private object currentDialogueSequence;  // Can be Ravi/Malrik/Elenya sequence
    private string currentSegmentId;  // For gate-based systems
    
    // NPC Stats - public for stat display
    public NPCStats raviStats;
    public NPCStats malrikStats;
    public NPCStats elenyaStats;

    void Start()
    {
        // Initialize gate evaluator (works for all NPCs)
        gateEvaluator = GetComponent<DialogueGateEvaluator>();
        if (gateEvaluator == null)
        {
            gateEvaluator = gameObject.AddComponent<DialogueGateEvaluator>();
        }

        // Initialize appropriate dialogue sequence and NPC stats based on npcId
        if (npcId == "Ravi")
        {
            InitializeRavi();
        }
        else if (npcId == "Malrik")
        {
            InitializeMalrik();
        }
        else if (npcId == "Elenya")
        {
            InitializeElenya();
        }
        else
        {
            Debug.LogError($"Unknown NPC ID: {npcId}. Expected 'Ravi', 'Malrik', or 'Elenya'");
            InitializeRavi();  // Fallback
        }
        
        // Cache UI elements
        CacheUIElements();
    }

    void InitializeRavi()
    {
        // Initialize dialogue sequence for Ravi
        raviDialogueSequence = new RaviDialogueSequence();
        currentDialogueSequence = raviDialogueSequence;
        
        // Load Ravi's REMNANTS stats from NPCRemnantData
        raviStats = NPCRemnantData.GetNPCStats("Ravi");
        
        Debug.Log($"✅ Initialized {npcId} (3-round dialogue)");
        Debug.Log($"🟣 Ravi REMNANTS: Resolve={raviStats.Resolve} Empathy={raviStats.Empathy} Memory={raviStats.Memory} Nuance={raviStats.Nuance} Authority={raviStats.Authority} Need={raviStats.Need} Trust={raviStats.Trust} Skepticism={raviStats.Skepticism}");
    }

    void InitializeMalrik()
    {
        // Load Malrik's dialogue sequence from JSON
        malrikDialogueSequence = GetComponent<MalrikDialogueSequence>();
        if (malrikDialogueSequence == null)
        {
            malrikDialogueSequence = gameObject.AddComponent<MalrikDialogueSequence>();
        }
        currentDialogueSequence = malrikDialogueSequence;
        
        // Load Malrik's REMNANTS stats from NPCRemnantData
        malrikStats = NPCRemnantData.GetNPCStats("Malrik");
        
        Debug.Log($"✅ Initialized {npcId} (8-act gate-based dialogue)");
        Debug.Log($"🟣 Malrik REMNANTS: Resolve={malrikStats.Resolve} Empathy={malrikStats.Empathy} Memory={malrikStats.Memory} Nuance={malrikStats.Nuance} Authority={malrikStats.Authority} Need={malrikStats.Need} Trust={malrikStats.Trust} Skepticism={malrikStats.Skepticism}");
    }

    void InitializeElenya()
    {
        // Load Elenya's dialogue sequence from JSON
        elenyaDialogueSequence = GetComponent<ElenyaDialogueSequence>();
        if (elenyaDialogueSequence == null)
        {
            elenyaDialogueSequence = gameObject.AddComponent<ElenyaDialogueSequence>();
        }
        currentDialogueSequence = elenyaDialogueSequence;
        
        // Load Elenya's REMNANTS stats from NPCRemnantData
        elenyaStats = NPCRemnantData.GetNPCStats("Elenya");
        
        Debug.Log($"✅ Initialized {npcId} (8-act gate-based dialogue)");
        Debug.Log($"🟣 Elenya REMNANTS: Resolve={elenyaStats.Resolve} Empathy={elenyaStats.Empathy} Memory={elenyaStats.Memory} Nuance={elenyaStats.Nuance} Authority={elenyaStats.Authority} Need={elenyaStats.Need} Trust={elenyaStats.Trust} Skepticism={elenyaStats.Skepticism}");
    }

    void CacheUIElements()
    {
        // Find DialogueCanvas specifically by name
        GameObject dialogueCanvasObj = GameObject.Find("DialogueCanvas");
        if (dialogueCanvasObj != null)
        {
            dialogueCanvas = dialogueCanvasObj.GetComponent<Canvas>();
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
        else
        {
            Debug.LogError("DialogueCanvas not found in scene!");
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

        if (npcId == "Ravi")
        {
            // Ravi uses simple 3-round dialogue
            ShowDialogueRound();
        }
        else if (npcId == "Malrik" || npcId == "Elenya")
        {
            // Malrik/Elenya use gate-based dialogue
            ShowGateBasedDialogue();
        }
    }

    void ShowGateBasedDialogue()
    {
        Debug.Log($"🔵 ShowGateBasedDialogue called for {npcId}");
        
        // Get available segments based on gates
        List<object> availableSegments = GetAvailableSegments();
        
        if (availableSegments == null)
        {
            Debug.LogError($"🔴 GetAvailableSegments returned NULL for {npcId}");
            CloseDialogue();
            return;
        }

        Debug.Log($"🟡 Found {availableSegments.Count} available segments for {npcId}");
        
        if (availableSegments.Count == 0)
        {
            Debug.Log($"🔒 No dialogue available for {npcId} (gates not open)");
            CloseDialogue();
            return;
        }

        // For now, show the first available segment
        object segment = availableSegments[0];
        currentSegmentId = GetSegmentId(segment);
        
        Debug.Log($"🟢 Showing segment: {currentSegmentId}");
        ShowGateBasedSegment(segment);
    }

    List<object> GetAvailableSegments()
    {
        if (npcId == "Malrik")
        {
            var malrikSeq = currentDialogueSequence as MalrikDialogueSequence;
            if (malrikSeq != null)
            {
                var segments = malrikSeq.GetAvailableSegments(PlayerStats.Get(), this, "Malrik");
                return new List<object>(segments.ConvertAll(x => (object)x));
            }
        }
        else if (npcId == "Elenya")
        {
            var elenyaSeq = currentDialogueSequence as ElenyaDialogueSequence;
            if (elenyaSeq != null)
            {
                var segments = elenyaSeq.GetAvailableSegments(PlayerStats.Get(), this, "Elenya");
                return new List<object>(segments.ConvertAll(x => (object)x));
            }
        }
        return null;
    }

    string GetSegmentId(object segment)
    {
        if (segment is MalrikDialogueSequence.MalrikSegment malrikSeg)
            return malrikSeg.segmentId;
        if (segment is VelinorGame.Core.ElenyaDialogueSequence.ElenyaSegment elenyaSeg)
            return elenyaSeg.segmentId;
        return "";
    }

    void ShowGateBasedSegment(object segment)
    {
        Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
        if (panelTransform == null)
        {
            Debug.LogError("DialoguePanel not found!");
            return;
        }

        panelTransform.gameObject.SetActive(true);
        RectTransform panelRect = panelTransform as RectTransform;
        LayoutRebuilder.ForceRebuildLayoutImmediate(panelRect);

        // Display NPC name
        if (npcNameText != null)
        {
            npcNameText.text = npcId;
        }

        // Extract dialogue properties using reflection for compatibility
        string npcLine = "";
        List<object> choices = new List<object>();
        
        var npcLineProperty = segment.GetType().GetProperty("npcLine");
        var choicesProperty = segment.GetType().GetProperty("playerChoices");
        
        if (npcLineProperty != null)
            npcLine = (string)npcLineProperty.GetValue(segment);
        
        if (choicesProperty != null)
        {
            var choicesList = choicesProperty.GetValue(segment) as System.Collections.IList;
            if (choicesList != null)
            {
                foreach (var choice in choicesList)
                    choices.Add(choice);
            }
        }

        if (dialogueBodyText != null)
        {
            dialogueBodyText.text = npcLine;
        }

        // Setup buttons with choices
        SetupGateBasedChoiceButtons(choices);
    }

    void SetupGateBasedChoiceButtons(List<object> choices)
    {
        // Hide all buttons first
        if (optionButton1 != null) optionButton1.gameObject.SetActive(false);
        if (optionButton2 != null) optionButton2.gameObject.SetActive(false);
        if (optionButton3 != null) optionButton3.gameObject.SetActive(false);
        if (optionButton4 != null) optionButton4.gameObject.SetActive(false);

        Button[] buttons = { optionButton1, optionButton2, optionButton3, optionButton4 };
        
        for (int i = 0; i < choices.Count && i < buttons.Length; i++)
        {
            object choice = choices[i];
            Button btn = buttons[i];
            int choiceIndex = i;
            
            SetupGateBasedChoiceButton(btn, choice, () => OnGateBasedChoiceSelected(choiceIndex, choices));
        }

        if (choiceContainer != null)
        {
            LayoutRebuilder.ForceRebuildLayoutImmediate(choiceContainer as RectTransform);
        }
    }

    void SetupGateBasedChoiceButton(Button button, object choice, UnityEngine.Events.UnityAction action)
    {
        if (button == null) return;

        button.gameObject.SetActive(true);

        string playerLine = "";
        char toneType = ' ';

        // Handle both DialogueChoice (from Malrik) and ElenyaChoice
        if (choice is DialogueChoice dialogueChoice)
        {
            playerLine = dialogueChoice.playerLine;
            toneType = dialogueChoice.toneType;
        }
        else
        {
            // Try to use reflection for custom choice types
            var playerLineProperty = choice.GetType().GetProperty("playerLine");
            var toneTypeProperty = choice.GetType().GetProperty("toneType");
            
            if (playerLineProperty != null)
                playerLine = (string)playerLineProperty.GetValue(choice);
            if (toneTypeProperty != null)
                toneType = (char)toneTypeProperty.GetValue(choice);
        }

        // Set button text with TONE label
        TextMeshProUGUI btnText = button.GetComponentInChildren<TextMeshProUGUI>();
        if (btnText != null)
        {
            btnText.text = $"({toneType}) {playerLine}";
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

        button.onClick.RemoveAllListeners();
        button.onClick.AddListener(action);
        
        Debug.Log($"🟢 Setup button: ({toneType}) - {playerLine}");
    }

    void OnGateBasedChoiceSelected(int choiceIndex, List<object> choices)
    {
        if (choiceIndex < 0 || choiceIndex >= choices.Count)
            return;

        object choice = choices[choiceIndex];
        
        // Get stat effects - handle both DialogueChoice and custom choice types
        Dictionary<string, float> statEffects = null;
        
        if (choice is DialogueChoice dialogueChoice)
        {
            statEffects = dialogueChoice.remnantEffects;
        }
        else
        {
            // Try to use reflection for custom choice types
            var statEffectsProperty = choice.GetType().GetProperty("statEffects");
            if (statEffectsProperty != null)
                statEffects = (Dictionary<string, float>)statEffectsProperty.GetValue(choice);
        }

        // Apply stat effects appropriately based on NPC
        if (npcId == "Malrik")
        {
            ApplyGateBasedStatEffects(statEffects, malrikStats);
            Debug.Log($"🟢 Malrik choice selected");
        }
        else if (npcId == "Elenya")
        {
            ApplyGateBasedStatEffects(statEffects, elenyaStats);
            Debug.Log($"🟢 Elenya choice selected");
        }

        // Mark this segment as completed
        if (npcId == "Malrik")
        {
            var malrikSeq = currentDialogueSequence as MalrikDialogueSequence;
            if (malrikSeq != null)
                malrikSeq.CompleteSegment(currentSegmentId);
        }
        else if (npcId == "Elenya")
        {
            var elenyaSeq = currentDialogueSequence as VelinorGame.Core.ElenyaDialogueSequence;
            if (elenyaSeq != null)
                elenyaSeq.CompleteSegment(currentSegmentId);
        }

        // Close and prepare for next dialogue
        CloseDialogue();
    }

    void ShowDialogueRound()
    {
        if (raviDialogueSequence == null)
            return;

        if (currentRound >= raviDialogueSequence.rounds.Count)
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

        DialogueRound round = raviDialogueSequence.rounds[currentRound];
        
        // Show NPC name (or "???" if not revealed)
        if (npcNameText != null)
        {
            npcNameText.text = raviDialogueSequence.playerKnowsName ? "Ravi" : "???";
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
        if (raviDialogueSequence == null)
            return;

        DialogueRound round = raviDialogueSequence.rounds[currentRound];
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
            raviDialogueSequence.playerKnowsName = true;
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
        if (currentRound < raviDialogueSequence.rounds.Count)
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

    void ApplyGateBasedStatEffects(Dictionary<string, float> statEffects, NPCStats npcStats)
    {
        if (statEffects == null || npcStats == null)
            return;

        foreach (var kvp in statEffects)
        {
            string statName = kvp.Key;
            float delta = kvp.Value;

            // Apply to NPC stats
            switch (statName)
            {
                case "empathy":
                    npcStats.Empathy = Mathf.Clamp01(npcStats.Empathy + delta);
                    break;
                case "resolve":
                    npcStats.Resolve = Mathf.Clamp01(npcStats.Resolve + delta);
                    break;
                case "memory":
                    npcStats.Memory = Mathf.Clamp01(npcStats.Memory + delta);
                    break;
                case "nuance":
                    npcStats.Nuance = Mathf.Clamp01(npcStats.Nuance + delta);
                    break;
                case "authority":
                    npcStats.Authority = Mathf.Clamp01(npcStats.Authority + delta);
                    break;
                case "need":
                    npcStats.Need = Mathf.Clamp01(npcStats.Need + delta);
                    break;
                case "trust":
                    npcStats.Trust = Mathf.Clamp01(npcStats.Trust + delta);
                    break;
                case "skepticism":
                    npcStats.Skepticism = Mathf.Clamp01(npcStats.Skepticism + delta);
                    break;
                case "observation":
                    // Observation is a player stat, not NPC stat - store as influence for now
                    Debug.LogWarning($"⚠️ Observation effect in NPC choice: {delta}");
                    break;
                case "malrik_influence":
                    // Relationship tracking
                    Debug.Log($"💜 Malrik relationship: +{delta}");
                    break;
                case "elenya_influence":
                    // Relationship tracking
                    Debug.Log($"💚 Elenya relationship: +{delta}");
                    break;
                default:
                    Debug.LogWarning($"⚠️ Unknown stat effect: {statName}");
                    break;
            }

            Debug.Log($"📊 {npcId}.{statName} {(delta > 0 ? "+" : "")}{delta}");
        }
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
