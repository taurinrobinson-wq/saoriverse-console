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
    public class StoryChoice
    {
        public string text;              // Choice button label
        public string target;            // Next passage ID
        public Dictionary<string, float> tone_effects = new Dictionary<string, float>();
        public Dictionary<string, float> npc_resonance = new Dictionary<string, float>();
        public string mark_story_beat;
    }

    /// <summary>Deserializes passage objects from story JSON.</summary>
    [System.Serializable]
    public class StoryPassage
    {
        public string pid;               // Passage ID
        public string name;              // Passage name
        public string text;              // Full passage text (may contain inline markup)
        public List<string> tags = new List<string>();
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

    #endregion

    #region UI References

    [SerializeField] private TextMeshProUGUI npcNameText;
    [SerializeField] private TextMeshProUGUI bodyText;
    [SerializeField] private Transform choiceButtonContainer;
    [SerializeField] private GameObject choiceButtonPrefab;
    [SerializeField] private CanvasGroup dialogueCanvasGroup;
    [SerializeField] private Canvas dialogueCanvas;

    #endregion

    #region Initialization

    private bool storyLoaded = false;

    private void Start()
    {
        LoadStoryJson();
    }

    /// <summary>
    /// Load story JSON from Resources folder and deserialize into passages dictionary.
    /// Expected path: Resources/velinor/stories/sample_story.json
    /// </summary>
    private void LoadStoryJson()
    {
        if (storyLoaded)
            return;

        try
        {
            string jsonPath = "velinor/stories/sample_story";
            TextAsset jsonAsset = Resources.Load<TextAsset>(jsonPath);

            if (jsonAsset == null)
            {
                Debug.LogError($"[DialogueManager] Failed to load story JSON from Resources/{jsonPath}");
                return;
            }

            string jsonText = jsonAsset.text;
            StoryJson storyData = JsonUtility.FromJson<StoryJson>(jsonText);

            if (storyData == null || storyData.passages == null)
            {
                Debug.LogError("[DialogueManager] Failed to deserialize story JSON");
                return;
            }

            // Convert passages array into dictionary keyed by pid
            passages = new Dictionary<string, StoryPassage>();
            foreach (StoryPassage passage in storyData.passages)
            {
                passages[passage.pid] = passage;
            }

            storyLoaded = true;
            
            Debug.Log($"[DialogueManager] Story loaded successfully. {passages.Count} passages found. Starting node: {storyData.startnode}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"[DialogueManager] Exception loading story JSON: {ex.Message}");
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
        if (!storyLoaded)
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
        var playerController = FindObjectOfType<PlayerController>();
        if (playerController != null)
            playerController.enabled = false;

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
        var playerController = FindObjectOfType<PlayerController>();
        if (playerController != null)
            playerController.enabled = true;

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

        // Render NPC name
        if (npcNameText != null)
        {
            npcNameText.text = activeNpcId ?? "Unknown";
        }

        // Render passage text
        if (bodyText != null)
        {
            bodyText.text = passage.text;
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

    /// <summary>
    /// Called when player clicks a choice button.
    /// 
    /// Flow:
    /// 1. Apply tone_effects via StatManager.AdjustPlayerTone()
    /// 2. Apply npc_resonance via StatManager.ApplyNpcResonance()
    ///    (StatManager internally cascades changes through influence_map)
    /// 3. Call StatManager.LogEncounter() with the tone_effects
    /// 4. Move to next passage: DisplayPassage(choice.target)
    /// </summary>
    private void OnChoiceSelected(StoryChoice choice)
    {
        if (!isDialogueActive || StatManager.Instance == null)
        {
            Debug.LogWarning("[DialogueManager] Cannot process choice: dialogue inactive or StatManager missing");
            return;
        }

        Debug.Log($"[DialogueManager] Choice selected: {choice.text}");

        // Step 1: Apply tone effects to player TONE
        // Each tone type gets adjusted independently
        if (choice.tone_effects != null && choice.tone_effects.Count > 0)
        {
            foreach (var kvp in choice.tone_effects)
            {
                string toneName = kvp.Key;
                float amount = kvp.Value;

                // Convert tone name string to ToneType enum
                if (System.Enum.TryParse<StatManager.ToneType>(toneName, ignoreCase: true, out var toneType))
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

        // Step 2: Apply NPC resonance
        // Each NPC resonance value is converted to REMNANTS changes and cascaded
        if (choice.npc_resonance != null && choice.npc_resonance.Count > 0)
        {
            foreach (var kvp in choice.npc_resonance)
            {
                string npcName = kvp.Key;
                float resonanceValue = kvp.Value;

                StatManager.Instance.ApplyNpcResonance(npcName, new Dictionary<string, float> { { npcName, resonanceValue } });
                Debug.Log($"[DialogueManager] Applied resonance: {npcName} += {resonanceValue}");
            }
        }

        // Step 3: Log encounter with tone effects
        // StatManager stores a snapshot of all NPC states after this choice
        if (choice.tone_effects != null && choice.tone_effects.Count > 0)
        {
            StatManager.Instance.LogEncounter(choice.tone_effects);
        }

        // Step 4: Move to next passage
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
