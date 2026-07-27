using System;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

/// <summary>
/// DialogueManager: Singleton that manages story narrative progression and dialogue UI.
/// 
/// Responsibilities:
/// - Load and parse story JSON (sample_story.json)
/// - Display passages and render choices
/// - Call StatManager to apply tone_effects and npc_resonance
/// - Cascade changes through StatManager (no duplication)
/// - Manage dialogue UI (single shared canvas)
/// 
/// Non-Responsibilities:
/// - Does NOT store TONE or REMNANTS (StatManager owns this)
/// - Does NOT store NPC state (StatManager owns this)
/// - Does NOT simplify the narrative structure
/// - Treats story JSON as authoritative source
/// </summary>
public class DialogueManager : MonoBehaviour
{
    #region Nested JSON Serialization Classes
    
    /// <summary>Deserializes choice objects from story JSON.</summary>
    [System.Serializable]
    public class StringFloatEntry
    {
        public string key;
        public float value;
    }

    [System.Serializable]
    public class StringFloatMap
    {
        public List<StringFloatEntry> entries = new List<StringFloatEntry>();

        public Dictionary<string, float> ToDictionary()
        {
            var result = new Dictionary<string, float>();
            if (entries == null) return result;

            foreach (var entry in entries)
            {
                if (entry == null || string.IsNullOrWhiteSpace(entry.key))
                    continue;

                result[entry.key] = entry.value;
            }

            return result;
        }
    }

    /// <summary>Deserializes choice objects from story JSON.</summary>
    [System.Serializable]
    public class StoryChoice
    {
        public string text;              // Choice button label
        public string target;            // Next passage ID
        public StringFloatMap tone_effects = new StringFloatMap();
        public StringFloatMap npc_resonance = new StringFloatMap();
        public string mark_story_beat;
        public string system_trigger;
        public string data_hook;
    }

    /// <summary>Deserializes passage objects from story JSON.</summary>
    [System.Serializable]
    public class StoryPassage
    {
        public string pid;               // Passage ID
        public string name;              // Passage name
        public string text;              // Full passage text (may contain inline markup)
        public string prompt;            // Optional prompt text from the narrative guide
        public string shared_beat;       // Optional shared beat text from the narrative guide
        public string setting_description;
        public List<string> tags = new List<string>();
        public List<string> required_flags = new List<string>();
        public List<StoryChoice> choices = new List<StoryChoice>();
    }

    /// <summary>Root structure for story JSON deserialization.</summary>
    [System.Serializable]
    public class StoryJson
    {
        public string name;              // Story title
        public string startnode;         // Starting passage ID
        public List<StoryPassage> passages = new List<StoryPassage>();
    }

    #endregion

    #region Singleton

    private static DialogueManager instance;
    public static DialogueManager Instance => instance;

    private void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;
        DontDestroyOnLoad(gameObject);
    }

    #endregion

    #region State

    private Dictionary<string, StoryPassage> passages = new Dictionary<string, StoryPassage>();
    private string currentPassageId;
    private string activeNpcId;
    private bool isDialogueActive = false;
    private string activeStoryResourcePath = "velinor/stories/sample_story";

    public event Action OnDialogueEnded;
    public bool IsDialogueActive => isDialogueActive;

    #endregion

    #region UI References

    [SerializeField] private TextMeshProUGUI npcNameText;
    [SerializeField] private TextMeshProUGUI bodyText;
    [SerializeField] private Transform choiceButtonContainer;
    [SerializeField] private GameObject choiceButtonPrefab;
    [SerializeField] private CanvasGroup dialogueCanvasGroup;
    [SerializeField] private Canvas dialogueCanvas;

    // Public properties for editor setup access
    public TextMeshProUGUI NpcNameText { get => npcNameText; set => npcNameText = value; }
    public TextMeshProUGUI BodyText { get => bodyText; set => bodyText = value; }
    public Transform ChoiceButtonContainer { get => choiceButtonContainer; set => choiceButtonContainer = value; }
    public GameObject ChoiceButtonPrefab { get => choiceButtonPrefab; set => choiceButtonPrefab = value; }
    public CanvasGroup DialogueCanvasGroup { get => dialogueCanvasGroup; set => dialogueCanvasGroup = value; }
    public Canvas DialogueCanvas { get => dialogueCanvas; set => dialogueCanvas = value; }

    #endregion

    #region Initialization

    private bool storyLoaded = false;

    private void Start()
    {
        LoadStoryFromResource(activeStoryResourcePath);
    }

    /// <summary>
    /// Load story JSON from Resources folder and deserialize into passages dictionary.
    /// </summary>
    public bool LoadStoryFromResource(string resourcePath)
    {
        if (string.IsNullOrEmpty(resourcePath))
            resourcePath = activeStoryResourcePath;

        if (storyLoaded && resourcePath == activeStoryResourcePath)
            return true;

        try
        {
            TextAsset jsonAsset = Resources.Load<TextAsset>(resourcePath);
            if (jsonAsset == null)
            {
                Debug.LogError($"[DialogueManager] Failed to load story JSON from Resources/{resourcePath}");
                return false;
            }

            Debug.Log($"[DialogueManager] Loaded TextAsset: {jsonAsset.name}");
            string jsonText = jsonAsset.text;
            StoryJson storyData = JsonUtility.FromJson<StoryJson>(jsonText);

            if (storyData == null || storyData.passages == null)
            {
                Debug.LogError("[DialogueManager] Failed to deserialize story JSON");
                return false;
            }

            passages = new Dictionary<string, StoryPassage>();
            foreach (StoryPassage passage in storyData.passages)
            {
                passages[passage.pid] = passage;
            }

            activeStoryResourcePath = resourcePath;
            storyLoaded = true;
            Debug.Log($"[DialogueManager] Story loaded successfully. {passages.Count} passages found.");
            return true;
        }
        catch (Exception ex)
        {
            Debug.LogError($"[DialogueManager] Exception loading story JSON: {ex.Message}");
            return false;
        }
    }

    #endregion

    #region Public API

    /// <summary>
    /// Start dialogue with specific NPC at starting passage.
    /// This is called by NPCInteraction.cs when player interacts with NPC.
    /// </summary>
    /// <param name="npcId">NPC identifier (e.g., "Ravi", "Nima") - must match npc_profiles.json keys</param>
    /// <param name="startingPassageId">Starting passage ID (e.g., "ravi_dialogue")</param>
    public void StartDialogue(string npcId, string startingPassageId)
    {
        StartDialogue(npcId, startingPassageId, activeStoryResourcePath);
    }

    public void StartDialogue(string npcId, string startingPassageId, string storyResourcePath)
    {
        if (!LoadStoryFromResource(storyResourcePath))
        {
            Debug.LogWarning("[DialogueManager] Story not loaded yet");
            return;
        }

        if (!passages.ContainsKey(startingPassageId))
        {
            Debug.LogError($"[DialogueManager] Starting passage '{startingPassageId}' not found in story");
            return;
        }

        activeNpcId = npcId;
        isDialogueActive = true;
        
        // Show UI
        if (dialogueCanvas != null)
            dialogueCanvas.enabled = true;

        // Lock cursor and disable player movement
        Cursor.lockState = CursorLockMode.None;
        // Note: PlayerController may not exist; this is optional
        var playerController = FindAnyObjectByType<MonoBehaviour>(FindObjectsInactive.Exclude);
        if (playerController != null && playerController.TryGetComponent<CharacterController>(out var charController))
        {
            // If player has CharacterController, we'll disable the root GameObject
            playerController.enabled = false;
        }

        // Display starting passage
        DisplayPassage(startingPassageId);

        Debug.Log($"[DialogueManager] Dialogue started with NPC '{npcId}' at passage '{startingPassageId}'");
    }

    /// <summary>
    /// End current dialogue and return to gameplay.
    /// </summary>
    public void EndDialogue()
    {
        if (!isDialogueActive)
            return;

        isDialogueActive = false;
        activeNpcId = null;
        currentPassageId = null;

        // Hide UI
        if (dialogueCanvas != null)
            dialogueCanvas.enabled = false;

        // Clear choice buttons
        if (choiceButtonContainer != null)
        {
            foreach (Transform child in choiceButtonContainer)
            {
                Destroy(child.gameObject);
            }
        }

        // Re-lock cursor and re-enable player movement
        Cursor.lockState = CursorLockMode.Locked;
        // Note: Re-enable player movement if it was disabled
        var playerController = FindAnyObjectByType<MonoBehaviour>(FindObjectsInactive.Exclude);
        if (playerController != null && playerController.TryGetComponent<CharacterController>(out var charController))
        {
            playerController.enabled = true;
        }

        OnDialogueEnded?.Invoke();
        Debug.Log("[DialogueManager] Dialogue ended");
    }

    #endregion

    #region Passage Display

    /// <summary>
    /// Display a passage: render text, show NPC name, render choice buttons.
    /// Each button calls OnChoiceSelected when clicked.
    /// </summary>
    private void DisplayPassage(string passageId)
    {
        if (!passages.ContainsKey(passageId))
        {
            Debug.LogError($"[DialogueManager] Passage '{passageId}' not found");
            return;
        }

        StoryPassage passage = passages[passageId];
        currentPassageId = passageId;

        if (passage.required_flags != null && passage.required_flags.Count > 0)
        {
            foreach (string requiredFlag in passage.required_flags)
            {
                if (!GameFlags.Get(requiredFlag))
                {
                    Debug.LogWarning($"[DialogueManager] Passage '{passageId}' blocked by missing flag '{requiredFlag}'.");
                    EndDialogue();
                    return;
                }
            }
        }

        // Render NPC name
        if (npcNameText != null)
        {
            npcNameText.text = activeNpcId ?? "Unknown";
        }

        // Render passage text
        if (bodyText != null)
        {
            string displayText = passage.text;
            if (string.IsNullOrWhiteSpace(displayText))
            {
                List<string> parts = new List<string>();
                if (!string.IsNullOrWhiteSpace(passage.prompt)) parts.Add(passage.prompt);
                if (!string.IsNullOrWhiteSpace(passage.shared_beat)) parts.Add(passage.shared_beat);
                displayText = string.Join("\n\n", parts);
            }

            bodyText.text = displayText;
        }

        // Clear previous choice buttons
        ClearChoiceButtons();

        // Render choice buttons
        if (passage.choices != null && passage.choices.Count > 0)
        {
            foreach (StoryChoice choice in passage.choices)
            {
                CreateChoiceButton(choice);
            }
        }
        else
        {
            // No choices - end dialogue automatically
            Debug.Log("[DialogueManager] Passage has no choices. Ending dialogue.");
            Invoke(nameof(EndDialogue), 2f);
        }

        Debug.Log($"[DialogueManager] Displayed passage: {passageId}");
    }

    #endregion

    #region Choice Button Management

    /// <summary>
    /// Create a button for a choice and add to UI.
    /// </summary>
    private void CreateChoiceButton(StoryChoice choice)
    {
        if (choiceButtonContainer == null || choiceButtonPrefab == null)
        {
            Debug.LogError("[DialogueManager] choiceButtonContainer or choiceButtonPrefab not assigned");
            return;
        }

        GameObject buttonObj = Instantiate(choiceButtonPrefab, choiceButtonContainer);
        Button button = buttonObj.GetComponent<Button>();
        TextMeshProUGUI buttonText = buttonObj.GetComponentInChildren<TextMeshProUGUI>();

        if (button == null)
        {
            Debug.LogError("[DialogueManager] Choice button prefab missing Button component");
            Destroy(buttonObj);
            return;
        }

        if (buttonText != null)
        {
            buttonText.text = choice.text;
        }

        // Create a local copy to avoid closure issues
        StoryChoice localChoice = choice;
        button.onClick.AddListener(() => OnChoiceSelected(localChoice));

        Debug.Log($"[DialogueManager] Created choice button: {choice.text}");
    }

    /// <summary>
    /// Remove all choice buttons from the UI.
    /// </summary>
    private void ClearChoiceButtons()
    {
        if (choiceButtonContainer == null)
            return;

        foreach (Transform child in choiceButtonContainer)
        {
            Destroy(child.gameObject);
        }
    }

    #endregion

    #region Choice Resolution

    private bool TryResolveToneType(string toneName, out ToneType toneType)
    {
        toneType = default;
        if (string.IsNullOrWhiteSpace(toneName))
            return false;

        if (Enum.TryParse<ToneType>(toneName, ignoreCase: true, out toneType))
            return true;

        switch (toneName.ToLowerInvariant())
        {
            case "courage":
                toneType = ToneType.Truth;
                return true;
            case "wisdom":
                toneType = ToneType.Observation;
                return true;
            case "narrativepresence":
            case "narrative_presence":
                toneType = ToneType.NarrativePresence;
                return true;
            case "truth":
                toneType = ToneType.Truth;
                return true;
            case "observation":
                toneType = ToneType.Observation;
                return true;
            case "empathy":
                toneType = ToneType.Empathy;
                return true;
            default:
                return false;
        }
    }

    private void HandleChoiceHooks(StoryChoice choice)
    {
        if (!string.IsNullOrWhiteSpace(choice.system_trigger))
        {
            if (choice.system_trigger.StartsWith("transition:", StringComparison.OrdinalIgnoreCase))
            {
                string sceneName = choice.system_trigger.Substring("transition:".Length).Trim();
                if (SceneTransitionManager.Instance != null)
                    SceneTransitionManager.Instance.TransitionToScene(sceneName);
            }
        }

        if (!string.IsNullOrWhiteSpace(choice.data_hook))
        {
            if (choice.data_hook.StartsWith("set_flag:", StringComparison.OrdinalIgnoreCase))
            {
                string flagExpression = choice.data_hook.Substring("set_flag:".Length).Trim();
                string[] parts = flagExpression.Split('=');
                if (parts.Length == 2)
                {
                    string flagName = parts[0].Trim();
                    bool flagValue = bool.TryParse(parts[1].Trim(), out var parsed) ? parsed : true;
                    GameFlags.Set(flagName, flagValue);
                }
            }
        }
    }

    /// <summary>
    /// Called when player clicks a choice button.
    /// </summary>
    private void OnChoiceSelected(StoryChoice choice)
    {
        if (!isDialogueActive || StatManager.Instance == null)
        {
            Debug.LogWarning("[DialogueManager] Cannot process choice: dialogue inactive or StatManager missing");
            return;
        }

        Debug.Log($"[DialogueManager] Choice selected: {choice.text}");

        var toneEffects = choice.tone_effects?.ToDictionary() ?? new Dictionary<string, float>();
        if (toneEffects.Count > 0)
        {
            foreach (var kvp in toneEffects)
            {
                string toneName = kvp.Key;
                float amount = kvp.Value;

                if (TryResolveToneType(toneName, out var toneType))
                {
                    StatManager.Instance.AdjustPlayerTone(toneType, amount, activeNpcId);
                    Debug.Log($"[DialogueManager] Applied tone effect: {toneName} += {amount}");
                }
                else
                {
                    Debug.LogWarning($"[DialogueManager] Unknown tone type: {toneName}");
                }
            }
        }

        var npcResonance = choice.npc_resonance?.ToDictionary() ?? new Dictionary<string, float>();
        if (npcResonance.Count > 0)
        {
            foreach (var kvp in npcResonance)
            {
                string npcName = kvp.Key;
                float resonanceValue = kvp.Value;

                StatManager.Instance.ApplyNpcResonance(npcName, new Dictionary<string, float> { { npcName, resonanceValue } });
                Debug.Log($"[DialogueManager] Applied resonance: {npcName} += {resonanceValue}");
            }
        }

        if (toneEffects.Count > 0)
        {
            StatManager.Instance.LogEncounter(toneEffects);
        }

        HandleChoiceHooks(choice);

        string targetPassageId = choice.target;
        if (string.IsNullOrEmpty(targetPassageId))
        {
            Debug.LogWarning("[DialogueManager] Choice has no target passage. Ending dialogue.");
            EndDialogue();
            return;
        }

        DisplayPassage(targetPassageId);
    }

    #endregion
}
