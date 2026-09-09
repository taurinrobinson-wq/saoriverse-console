using System;
using System.Collections.Generic;
using System.Collections;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

/// <summary>
/// DialogueManager: Singleton that manages dynamic story narrative progression.
/// Handles T/O/N/E choices, Shared Beats, System Triggers, and Data Hooks.
/// </summary>
public class DialogueManager : MonoBehaviour
{
    #region JSON Data Structures

    [Serializable]
    public class StringFloatEntry { public string key; public float value; }

    [Serializable]
    public class ToneResonanceMap
    {
        public List<StringFloatEntry> entries = new List<StringFloatEntry>();
        public Dictionary<string, float> ToDictionary()
        {
            var dict = new Dictionary<string, float>();
            foreach (var e in entries) if (!string.IsNullOrEmpty(e.key)) dict[e.key] = e.value;
            return dict;
        }
    }

    [Serializable]
    public class RemnantsEffect
    {
        public string target = "activeNpcId";  // "activeNpcId", "Ravi", "Nima", etc.
        public string stat = "";               // "resolve", "trust", "memory", etc.
        public float delta = 0f;               // +0.01 or -0.01
    }

    [Serializable]
    public class RemnantsEffects
    {
        public string target = "activeNpcId";  // "activeNpcId", "Ravi", "Nima", etc.
        public int trust_delta = 0;
        public int alert_delta = 0;
        public int guard_delta = 0;
        public int grief_delta = 0;
        public int reputation_delta = 0;
    }

    [Serializable]
    public class SharedBeatLine
    {
        public string speaker;           // NPC name or "Player" or "Shared"
        public string text;              // The line of dialogue
    }

    [Serializable]
    public class StoryChoice
    {
        [SerializeField] private string tone_str;  // JSON deserializes as string
        public ToneType tone;                       // Runtime enum value
        public string playerLine;        // Button label (player's choice text)
        public string npc_response;      // NPC's response text (matches JSON field name)
        public string npcResponse { get { return npc_response; } set { npc_response = value; } }  // Backward compat property
        public string target;            // Next passage PID
        public string result_text;       // Player action description (e.g., "You approach...")
        public string shared_beat;       // Text shown AFTER choice (string for backward compatibility)
        public List<SharedBeatLine> shared_beat_lines;  // Array for multi-speaker
        public string system_trigger;    // e.g., "give_device"
        public string data_hook;         // e.g., "met_saori=true"
        public ToneResonanceMap tone_effects = new ToneResonanceMap();
        public ToneResonanceMap npc_resonance = new ToneResonanceMap();
        public List<RemnantsEffect> remnants_effects = new List<RemnantsEffect>();  // NEW: Array-based remnants (stat changes)
        public RemnantsEffects remnants_effects_legacy = new RemnantsEffects();  // LEGACY: Old format (for backward compat)

        // Parse tone string to enum after deserialization
        public void ParseTone()
        {
            tone = DialogueManager.ParseTone(tone_str);
            Debug.Log($"[StoryChoice] Parsed tone_str='{tone_str}' to ToneType.{tone}");
        }
    }

    [Serializable]
    public class StoryPassage
    {
        public string pid;
        public string name;
        public string text;              // Initial prompt/setting or NPC dialogue
        public string conversationId;    // Groups related passages into coherent dialogue packages
        public string active_speaker;    // "Player", "Nima", "Ravi", "Shared", etc.
        public string scene_context;     // Optional scene description (not shown in dialogue UI)
        public List<string> required_flags = new List<string>();
        public List<StoryChoice> choices = new List<StoryChoice>();
        public Dictionary<string, string> npc_responses;  // Tone-dependent NPC replies: "Trust" -> "response text"
        public List<SharedBeatLine> shared_beat;  // Multi-speaker lines
        public string system_trigger;    // System events (moved from choice level for NPC-only turns)
        public string data_hook;         // Data hooks (moved from choice level for NPC-only turns)
        public List<BeatSystemTrigger> system_triggers_list = new List<BeatSystemTrigger>();  // Array-based system triggers from beats
    }

    [Serializable]
    public class StoryJson
    {
        public string name;
        public string startnode;
        public List<StoryPassage> passages = new List<StoryPassage>();
    }

    #endregion

    public static DialogueManager Instance { get; private set; }

    [Header("Root Panel")]
    [SerializeField] private Canvas dialogueCanvas;
    public GameObject dialoguePanel => dialogueCanvas != null ? dialogueCanvas.gameObject : null;

    [Header("Text Fields")]
    [SerializeField] private TextMeshProUGUI bodyText;              // Dialogue prompt/passage text
    [SerializeField] private TextMeshProUGUI npcNameText;           // NPC name/speaker
    [SerializeField] private TextMeshProUGUI sharedBeatText;        // Shared beat display

    [Header("Choice Buttons")]
    [SerializeField] private Button btnT;                           // Trust button
    [SerializeField] private Button btnO;                           // Observation button
    [SerializeField] private Button btnN;                           // NarrativePresence button
    [SerializeField] private Button btnE;                           // Empathy button

    [Header("Choice Button Labels")]
    [SerializeField] private TextMeshProUGUI txtT;                  // Trust choice text
    [SerializeField] private TextMeshProUGUI txtO;                  // Observation choice text
    [SerializeField] private TextMeshProUGUI txtN;                  // NarrativePresence choice text
    [SerializeField] private TextMeshProUGUI txtE;                  // Empathy choice text

    [Header("Fallback (Dynamic Spawning)")]
    [SerializeField] private Transform choiceButtonContainer;
    [SerializeField] private GameObject _choiceButtonPrefab;

    // Compatibility Properties for Editor scripts
    public GameObject dialogueUIPanel
    {
        get => dialogueCanvas != null ? dialogueCanvas.gameObject : null;
        set { if (value != null) dialogueCanvas = value.GetComponent<Canvas>(); }
    }
    public TextMeshProUGUI speakerNameText { get => npcNameText; set => npcNameText = value; }
    public TextMeshProUGUI dialogueText { get => bodyText; set => bodyText = value; }
    public Transform choicesContainer { get => choiceButtonContainer; set => choiceButtonContainer = value; }
    public GameObject choiceButtonPrefab { get => _choiceButtonPrefab; set => _choiceButtonPrefab = value; }

    private Dictionary<string, StoryPassage> passages = new Dictionary<string, StoryPassage>();
    private string activeNpcId;
    private string currentConversationId;  // Tracks which conversation is currently active
    private GameObject currentNPCGameObject;  // Stores reference to NPC that initiated dialogue
    private bool isDialogueActive = false;
    private string activeStoryPath = "velinor/stories/sample_story";
    private HashSet<string> revealedNpcNames = new HashSet<string>();  // Track which NPC names have been revealed

    public bool IsDialogueActive => isDialogueActive;
    public event Action OnDialogueEnded;

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        if (Application.isPlaying) DontDestroyOnLoad(gameObject);

        // Canonical validation checks
        if (dialogueCanvas == null) Debug.LogWarning("[DialogueManager] DialogueCanvas is not assigned in Inspector.");
        if (bodyText == null) Debug.LogWarning("[DialogueManager] bodyText is not assigned in Inspector.");
        if (npcNameText == null) Debug.LogWarning("[DialogueManager] npcNameText is not assigned in Inspector.");
        if (sharedBeatText == null) Debug.LogWarning("[DialogueManager] sharedBeatText is not assigned in Inspector.");

        // Button validation
        if (btnT == null) Debug.LogWarning("[DialogueManager] btnT (Trust button) is not assigned in Inspector.");
        if (btnO == null) Debug.LogWarning("[DialogueManager] btnO (Observation button) is not assigned in Inspector.");
        if (btnN == null) Debug.LogWarning("[DialogueManager] btnN (NarrativePresence button) is not assigned in Inspector.");
        if (btnE == null) Debug.LogWarning("[DialogueManager] btnE (Empathy button) is not assigned in Inspector.");

        // Button label validation
        if (txtT == null) Debug.LogWarning("[DialogueManager] txtT (Trust label) is not assigned in Inspector.");
        if (txtO == null) Debug.LogWarning("[DialogueManager] txtO (Observation label) is not assigned in Inspector.");
        if (txtN == null) Debug.LogWarning("[DialogueManager] txtN (NarrativePresence label) is not assigned in Inspector.");
        if (txtE == null) Debug.LogWarning("[DialogueManager] txtE (Empathy label) is not assigned in Inspector.");

        // Ensure dialogue canvas is disabled at startup
        if (dialogueCanvas != null)
        {
            dialogueCanvas.enabled = false;
            Debug.Log("[DialogueManager] Dialogue canvas disabled on initialization.");
        }
        if (sharedBeatText != null) sharedBeatText.gameObject.SetActive(false);
    }

    private void Start()
    {
        LoadStory(activeStoryPath);
    }

    public bool LoadStory(string path)
    {
        if (string.IsNullOrEmpty(path)) path = activeStoryPath;
        TextAsset asset = Resources.Load<TextAsset>(path);
        if (asset == null) return false;

        try
        {
            StoryJson data = JsonUtility.FromJson<StoryJson>(asset.text);
            passages.Clear();
            foreach (var p in data.passages)
            {
                // Parse tone strings to enums for all choices
                foreach (var choice in p.choices)
                {
                    choice.ParseTone();
                }
                passages[p.pid] = p;
            }
            activeStoryPath = path;
            Debug.Log($"[DialogueManager] Loaded story with {passages.Count} passages");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[DialogueManager] Load Error: {e.Message}");
            return false;
        }
    }

    public void StartDialogue(string npcId, string startPid) => StartDialogue(npcId, startPid, activeStoryPath);

    public void StartDialogue(string npcId, string startPid, string storyPath, GameObject npcGameObject = null)
    {
        if (!string.IsNullOrEmpty(storyPath) && storyPath != activeStoryPath) LoadStory(storyPath);

        // Auto-resolve startPid to first available or saori_beat_1/market_entry if the specified startPid isn't found
        if (!passages.ContainsKey(startPid))
        {
            if (passages.ContainsKey("market_entry")) startPid = "market_entry";
            else if (passages.ContainsKey("saori_beat_1")) startPid = "saori_beat_1";
            else if (passages.Count > 0) startPid = new List<string>(passages.Keys)[0];
        }

        if (!passages.ContainsKey(startPid)) return;

        // Check if this conversation package has already been completed
        var startPassage = passages[startPid];
        if (!string.IsNullOrEmpty(startPassage.conversationId))
        {
            string completionFlag = $"{startPassage.conversationId}_completed";
            if (GameFlags.Get(completionFlag))
            {
                Debug.Log($"[DialogueManager] Conversation '{startPassage.conversationId}' already completed. Looking for dismissal passage.");
                // Try to find a dismissal passage for this conversation
                string dismissalPid = $"{startPassage.conversationId}_dismissal";
                if (passages.ContainsKey(dismissalPid))
                {
                    startPid = dismissalPid;
                    Debug.Log($"[DialogueManager] Routing to dismissal passage: {dismissalPid}");
                }
                else
                {
                    Debug.LogWarning($"[DialogueManager] No dismissal passage found for conversation '{startPassage.conversationId}'");
                }
            }
        }

        activeNpcId = npcId;
        currentNPCGameObject = npcGameObject;  // Store NPC reference for fade-out

        // Store the conversation ID for later completion tracking
        var finalPassage = passages[startPid];
        currentConversationId = finalPassage.conversationId;
        Debug.Log($"[DialogueManager] Starting dialogue - npcId: {npcId}, conversationId: {currentConversationId}, startPid: {startPid}");

        revealedNpcNames.Clear();  // Reset revealed names for new dialogue
        isDialogueActive = true;

        AutoBindUI();

        // Don't enable dialogueCanvas - let DialogueUIController manage UI_Canvas visibility
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
        DisplayPassage(startPid);
    }

    /// <summary>
    /// New TextAsset-based dialogue loading method for NPCDialogueDriver.
    /// Supports multi-NPC scenes by using conversationId to filter passages.
    /// Handles both passages-based and beats-based JSON formats.
    /// </summary>
    public void StartDialogue(TextAsset jsonFile, string conversationId, string npcName, bool isMultiNpcScene, string startPassageId = "", GameObject npcGameObject = null)
    {
        if (jsonFile == null)
        {
            Debug.LogError("[DialogueManager] StartDialogue: jsonFile is null");
            return;
        }

        try
        {
            // Try parsing as passages-based format first
            StoryJson data = JsonUtility.FromJson<StoryJson>(jsonFile.text);

            if (data != null && data.passages != null && data.passages.Count > 0)
            {
                // Passages-based format
                passages.Clear();
                foreach (var p in data.passages)
                {
                    foreach (var choice in p.choices)
                    {
                        choice.ParseTone();
                    }
                    passages[p.pid] = p;
                }
                Debug.Log($"[DialogueManager] Loaded {passages.Count} passages from {jsonFile.name} for conversation '{conversationId}'");
            }
            else
            {
                // Try parsing as beats-based format
                Debug.Log($"[DialogueManager] No passages found, attempting to parse as beats-based format");
                ConvertBeatsToPassages(jsonFile.text, conversationId);
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[DialogueManager] Error parsing dialogue JSON: {e.Message}");
            return;
        }

        // Determine starting passage
        string startPid = startPassageId;

        // If no start passage specified, find first passage in conversationId
        if (string.IsNullOrEmpty(startPid))
        {
            foreach (var kvp in passages)
            {
                if (kvp.Value.conversationId == conversationId)
                {
                    startPid = kvp.Key;
                    break;
                }
            }
        }

        // Fallback if still not found
        if (string.IsNullOrEmpty(startPid) && passages.Count > 0)
        {
            startPid = new List<string>(passages.Keys)[0];
        }

        if (!passages.ContainsKey(startPid))
        {
            Debug.LogError($"[DialogueManager] Start passage '{startPid}' not found in dialogue JSON");
            return;
        }

        // Setup dialogue context
        activeNpcId = npcName;
        currentNPCGameObject = npcGameObject;
        currentConversationId = conversationId;

        Debug.Log($"[DialogueManager] Starting dialogue from TextAsset: npcName={npcName}, conversationId={conversationId}, startPid={startPid}, isMultiNpc={isMultiNpcScene}");

        // Check if this conversation has already been completed
        string completionFlag = $"{conversationId}_completed";
        if (GameFlags.Get(completionFlag))
        {
            Debug.Log($"[DialogueManager] Conversation '{conversationId}' already completed. Looking for dismissal dialogue.");
            string dismissalPid = $"beat_999";  // Look for dismissal beat (beat ID 999 is reserved for dismissals)

            if (passages.ContainsKey(dismissalPid))
            {
                startPid = dismissalPid;
                Debug.Log($"[DialogueManager] Found dismissal passage: {dismissalPid}");
            }
            else
            {
                Debug.LogWarning($"[DialogueManager] No dismissal passage found for conversation '{conversationId}'");
                // Continue with normal start if no dismissal exists
            }
        }

        revealedNpcNames.Clear();  // Reset revealed names for new dialogue
        isDialogueActive = true;
        AutoBindUI();

        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
        DisplayPassage(startPid);
    }

    /// <summary>
    /// Converts beat-based JSON format to passages for dialogue display.
    /// Maps each beat to a passage entry so the rest of the system can use it.
    /// </summary>
    private void ConvertBeatsToPassages(string jsonText, string conversationId)
    {
        try
        {
            // Create a wrapper to parse beats
            BeatBasedStoryJson beatData = JsonUtility.FromJson<BeatBasedStoryJson>(jsonText);

            if (beatData == null || beatData.beats == null || beatData.beats.Length == 0)
            {
                Debug.LogError("[DialogueManager] Failed to parse beats or beats array is empty");
                return;
            }

            passages.Clear();

            // Convert each beat to a passage entry
            foreach (var beat in beatData.beats)
            {
                string beatPid = $"beat_{beat.id}";

                // Special handling for shared dialogue beats
                if (beat.type == "npc_shared" && beat.shared_dialogue != null && beat.shared_dialogue.Length > 0)
                {
                    // Create passages for each speaker in the shared dialogue
                    for (int i = 0; i < beat.shared_dialogue.Length; i++)
                    {
                        var speaker = beat.shared_dialogue[i];
                        string sharedPid = $"beat_{beat.id}_shared_{i}";

                        // Create auto-advance choice to next shared speaker or next beat
                        StoryChoice autoChoice = new StoryChoice
                        {
                            playerLine = "[Continue]",
                            npcResponse = "",
                            target = (i < beat.shared_dialogue.Length - 1) ? $"beat_{beat.id}_shared_{i + 1}" : $"beat_{beat.next_beat_id}",
                            tone = ToneType.Trust  // Dummy value for auto-advance
                        };

                        StoryPassage sharedPassage = new StoryPassage
                        {
                            pid = sharedPid,
                            conversationId = conversationId,
                            active_speaker = speaker.speaker,
                            text = speaker.text,
                            choices = new List<StoryChoice> { autoChoice }
                        };

                        passages[sharedPid] = sharedPassage;
                    }

                    // Update the main beat to point to the first shared speaker
                    string beatPid_mainShared = $"beat_{beat.id}_shared_0";
                    // Skip the intermediate prompt and jump directly to the first speaker
                    passages[beatPid] = passages[beatPid_mainShared];
                    continue;  // Skip normal choice processing for shared beats
                }

                // Normal beat processing (player posture or npc_turn)
                StoryPassage passage = new StoryPassage
                {
                    pid = beatPid,
                    conversationId = conversationId,
                    active_speaker = beat.active_speaker,
                    text = beat.prompt ?? $"Beat {beat.id}",
                    choices = new List<StoryChoice>()
                };

                // Store system_triggers from beat level
                if (beat.system_triggers != null && beat.system_triggers.Length > 0)
                {
                    StoreSystemTriggersInPassage(passage, beat.system_triggers);
                }

                // Determine target for this beat's choices (where player choices lead)
                string choiceTarget = beat.next_beat_id > 0 ? $"beat_{beat.next_beat_id}" : "DIALOGUE_END";

                // Convert tone choices to story choices
                if (beat.tone_choices != null && beat.tone_choices.Length > 0)
                {
                    foreach (var toneChoice in beat.tone_choices)
                    {
                        StoryChoice choice = new StoryChoice
                        {
                            playerLine = toneChoice.text,
                            npcResponse = toneChoice.npc_response ?? "",
                            result_text = toneChoice.result_text ?? "",  // Player action description
                            target = choiceTarget,  // SET THE TARGET FOR THIS CHOICE
                            tone_effects = new ToneResonanceMap(),
                            npc_resonance = new ToneResonanceMap()
                        };

                        // Convert tone string (T/O/N/E) to ToneType enum
                        choice.tone = ParseTone(toneChoice.tone);

                        // Convert tone effects
                        if (toneChoice.tone_effects != null)
                        {
                            foreach (var effect in toneChoice.tone_effects)
                            {
                                choice.tone_effects.entries.Add(new StringFloatEntry { key = effect.stat, value = effect.delta });
                            }
                        }

                        // Convert remnants effects
                        if (toneChoice.remnants_effects != null)
                        {
                            foreach (var remnant in toneChoice.remnants_effects)
                            {
                                RemnantsEffect remEffect = new RemnantsEffect
                                {
                                    target = remnant.target,
                                    stat = remnant.stat,
                                    delta = remnant.delta
                                };
                                choice.remnants_effects.Add(remEffect);
                            }
                        }

                        passage.choices.Add(choice);
                    }
                }
                else
                {
                    // For NPC turns/player inner with no player choices, create an auto-advance choice
                    if (beat.next_beat_id > 0)
                    {
                        StoryChoice autoChoice = new StoryChoice
                        {
                            playerLine = "[Continue]",
                            npcResponse = "",
                            target = $"beat_{beat.next_beat_id}",
                            tone = ToneType.Trust  // Dummy value for auto-advance
                        };
                        passage.choices.Add(autoChoice);
                    }
                }

                passages[beatPid] = passage;
            }

            Debug.Log($"[DialogueManager] Converted {passages.Count} beats to passages for conversation '{conversationId}'");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"[DialogueManager] Error converting beats to passages: {ex.Message}");
        }
    }

    // Data classes for beat-based format support
    [System.Serializable]
    private class BeatBasedStoryJson
    {
        public string scene_id;
        public string[] required_flags;
        public BeatData[] beats;
    }

    [System.Serializable]
    private class BeatData
    {
        public int id;
        public string type;
        public string active_speaker;
        public string prompt;
        public BeatToneChoice[] tone_choices;
        public BeatSharedDialogue[] shared_dialogue;  // For "npc_shared" type beats
        public BeatSystemTrigger[] system_triggers;   // For system effects
        public int next_beat_id = 0;  // Points to next beat ID, or 0 to end
    }

    [System.Serializable]
    private class BeatSharedDialogue
    {
        public string speaker;
        public string text;
    }

    [System.Serializable]
    public class BeatSystemTrigger
    {
        public string type;
        public string[] data;
    }

    [System.Serializable]
    private class BeatToneChoice
    {
        public string tone;
        public string text;
        public string result_text;  // Player action description (e.g., "You approach...")
        public string npc_response;
        public BeatEffect[] tone_effects;
        public BeatRemnantEffect[] remnants_effects;
    }

    [System.Serializable]
    private class BeatEffect
    {
        public string stat;
        public float delta;
    }

    [System.Serializable]
    private class BeatRemnantEffect
    {
        public string target;
        public string stat;
        public float delta;
    }

    /// <summary>
    /// Check if DialogueManager supports TextAsset-based loading.
    /// Used by NPCDialogueDriver to determine which method to call.
    /// </summary>
    public bool CanLoadFromTextAsset()
    {
        return true; // This method always exists now
    }

    public void AutoBindUI()
    {
        // Check if current references are missing or destroyed (common in DontDestroyOnLoad across scenes)
        if (dialogueCanvas == null || dialogueCanvas.gameObject == null)
        {
            var go = GameObject.Find("DialogueCanvas");
            if (go == null) go = GameObject.Find("UI_Canvas");
            if (go != null) dialogueCanvas = go.GetComponent<Canvas>();

            if (dialogueCanvas == null) dialogueCanvas = FindAnyObjectByType<Canvas>();
        }

        if (dialogueCanvas != null)
        {
            // Always try to re-find these if they are missing or from a different scene
            if (choiceButtonContainer == null || choiceButtonContainer.gameObject == null)
            {
                // Prioritize ChoicesGridContainer or ChoicesContainer
                choiceButtonContainer = dialogueCanvas.transform.Find("DialoguePanel/ChoicesGridContainer");
                if (choiceButtonContainer == null)
                    choiceButtonContainer = dialogueCanvas.transform.Find("DialoguePanel/ChoicesContainer");
                if (choiceButtonContainer == null)
                    choiceButtonContainer = dialogueCanvas.transform.Find("DialoguePanel");
            }

            if (npcNameText == null || npcNameText.gameObject == null) npcNameText = FindTextMeshInCanvas("NPCNameText");
            if (bodyText == null || bodyText.gameObject == null) bodyText = FindTextMeshInCanvas("NPCDialogueText");
            if (sharedBeatText == null || sharedBeatText.gameObject == null) sharedBeatText = FindTextMeshInCanvas("SharedBeatText");

            // Re-bind buttons if they are missing
            if (btnT == null || btnT.gameObject == null) btnT = FindButtonInCanvas("ChoiceButton_T");
            if (btnO == null || btnO.gameObject == null) btnO = FindButtonInCanvas("ChoiceButton_O");
            if (btnN == null || btnN.gameObject == null) btnN = FindButtonInCanvas("ChoiceButton_N");
            if (btnE == null || btnE.gameObject == null) btnE = FindButtonInCanvas("ChoiceButton_E");

            Debug.Log($"[DialogueManager.AutoBindUI] Buttons found - T:{(btnT != null ? "✓" : "✗")} O:{(btnO != null ? "✓" : "✗")} N:{(btnN != null ? "✓" : "✗")} E:{(btnE != null ? "✓" : "✗")}");

            if (txtT == null || txtT.gameObject == null) txtT = FindTextMeshInButton(btnT);
            if (txtO == null || txtO.gameObject == null) txtO = FindTextMeshInButton(btnO);
            if (txtN == null || txtN.gameObject == null) txtN = FindTextMeshInButton(btnN);
            if (txtE == null || txtE.gameObject == null) txtE = FindTextMeshInButton(btnE);

            Debug.Log($"[DialogueManager.AutoBindUI] TextMesh found - T:{(txtT != null ? "✓" : "✗")} O:{(txtO != null ? "✓" : "✗")} N:{(txtN != null ? "✓" : "✗")} E:{(txtE != null ? "✓" : "✗")}");
        }
    }

    private TextMeshProUGUI FindTextMeshInButton(Button btn)
    {
        if (btn == null) return null;
        return btn.GetComponentInChildren<TextMeshProUGUI>();
    }

    private Button FindButtonInCanvas(string name)
    {
        if (dialogueCanvas == null) return null;

        // Try known container first
        if (choiceButtonContainer != null)
        {
            var btnTrans = choiceButtonContainer.Find(name);
            if (btnTrans != null)
            {
                Debug.Log($"[DialogueManager] Found button '{name}' in choiceButtonContainer");
                return btnTrans.GetComponent<Button>();
            }

            var allButtons = choiceButtonContainer.GetComponentsInChildren<Button>(true);
            foreach (var b in allButtons) if (b.name == name)
            {
                Debug.Log($"[DialogueManager] Found button '{name}' via GetComponentsInChildren");
                return b;
            }
        }

        // Fallback to direct path from canvas
        var trans = dialogueCanvas.transform.Find("DialoguePanel/" + name);
        if (trans != null)
        {
            Debug.Log($"[DialogueManager] Found button '{name}' via DialoguePanel path");
            return trans.GetComponent<Button>();
        }

        Debug.LogWarning($"[DialogueManager] ✗ Could not find button '{name}'");
        return null;
    }

    private TextMeshProUGUI FindTextMeshInCanvas(string name)
    {
        if (dialogueCanvas == null) return null;

        if (choiceButtonContainer != null)
        {
            var tTrans = choiceButtonContainer.Find(name);
            if (tTrans != null) return tTrans.GetComponent<TextMeshProUGUI>();

            var allTexts = choiceButtonContainer.GetComponentsInChildren<TextMeshProUGUI>(true);
            foreach (var t in allTexts) if (t.name == name) return t;
        }

        var trans = dialogueCanvas.transform.Find("DialoguePanel/" + name);
        if (trans != null) return trans.GetComponent<TextMeshProUGUI>();

        return null;
    }

    private void DisplayPassage(string pid, bool isFirstPassage = false)
    {
        if (!passages.TryGetValue(pid, out var p)) { EndDialogue(); return; }

        // Check required flags with support for comparison syntax: "flag_name==true", "flag_name==false"
        foreach (var flagExpr in p.required_flags)
        {
            if (!CheckFlagExpression(flagExpr))
            {
                Debug.LogWarning($"[DialogueManager] Required flag check failed: {flagExpr}. Ending dialogue.");
                EndDialogue();
                return;
            }
        }

        // Update DialogueUIController - always clear and show fresh passage
        var dialogueUIController = FindAnyObjectByType<DialogueUIController>();

        // SKIP UI display for shared dialogue beats - they flow seamlessly
        bool isSharedDialogue = !string.IsNullOrEmpty(p.active_speaker) &&
                                (p.active_speaker == "Shared" || p.active_speaker == "shared");

        // Process system triggers BEFORE displaying the passage
        // This ensures name reveals happen before the UI is updated
        if (p.system_triggers_list != null && p.system_triggers_list.Count > 0)
        {
            ProcessSystemTriggersFromPassage(p.system_triggers_list);
        }

        // Process legacy system_trigger string if present
        if (!string.IsNullOrEmpty(p.system_trigger))
        {
            ProcessSystemTrigger(p.system_trigger);
        }

        if (!isSharedDialogue && dialogueUIController != null)
        {
            string displayName = GetDisplayNameForDialogue(activeNpcId);
            string dialogueText = p.text;

            // For multi-speaker passages, show speaker's name (with generic if not revealed)
            if (!string.IsNullOrEmpty(p.active_speaker))
            {
                if (p.active_speaker != "Player")
                {
                    // Use the active speaker (Nima, Ravi, etc.) with appropriate display name
                    displayName = GetDisplayNameForDialogue(p.active_speaker);
                }
                else if (p.active_speaker == "Player")
                {
                    // Format player inner thoughts in italics
                    dialogueText = $"<i>{p.text}</i>";
                    displayName = "";  // No speaker name for inner thoughts
                }
            }

            dialogueUIController.ShowDialogue(displayName, dialogueText);
            // Store active_speaker for UI to use
            dialogueUIController.currentActiveSpeaker = p.active_speaker;
            Debug.Log($"[DialogueManager] Displaying passage: {pid} (speaker: {p.active_speaker}, display name: {displayName})");
        }
        else if (isSharedDialogue)
        {
            Debug.Log($"[DialogueManager] Skipping UI display for shared dialogue beat {pid} - will auto-advance seamlessly");
        }
        else if (dialogueUIController == null)
        {
            Debug.LogError("[DialogueManager] DialogueUIController not found!");
        }

        ClearButtons();
        DisplayChoicesForPassage(pid);
    }

    /// <summary>
    /// Check if a flag expression is satisfied.
    /// Supports: "flag_name" (flag exists and is true), "flag_name==true", "flag_name==false"
    /// </summary>
    private bool CheckFlagExpression(string expr)
    {
        if (string.IsNullOrEmpty(expr)) return true;  // Empty requirement = pass

        // Handle comparison syntax: "flag_name==value"
        if (expr.Contains("=="))
        {
            string[] parts = expr.Split(new string[] { "==" }, System.StringSplitOptions.None);
            if (parts.Length == 2)
            {
                string key = parts[0].Trim();
                string expectedValue = parts[1].Trim().ToLower();

                if (expectedValue == "true")
                    return GameFlags.Get(key, false);
                else if (expectedValue == "false")
                    return !GameFlags.Get(key, false);
            }
        }
        else
        {
            // Simple flag check: "flag_name" means flag must be true
            return GameFlags.Get(expr, false);
        }

        return false;  // Invalid expression = fail
    }

    private void DisplayChoicesForPassage(string pid)
    {
        if (!passages.TryGetValue(pid, out var p)) return;

        // Show player choices if this passage has any choices
        // active_speaker only indicates who is speaking the prompt, not whether player can respond
        bool hasPlayerChoices = p.choices != null && p.choices.Count > 0;
        Debug.Log($"[DialogueManager] DisplayChoicesForPassage - pid: {pid}, active_speaker: '{p.active_speaker}', hasChoices: {hasPlayerChoices}, choicesCount: {p.choices.Count}");

        if (!hasPlayerChoices)
        {
            // No player choices - auto-advance
            // For shared dialogue beats, skip displaying them entirely (seamless flow)
            if (p.active_speaker == "Shared" || p.active_speaker == "shared")
            {
                Debug.Log($"[DialogueManager] Skipping display of shared dialogue beat {pid} - auto-advancing seamlessly");
                // Jump directly to next beat without showing
                StartCoroutine(AutoAdvanceDialogue(pid, skipDisplay: true));
            }
            else
            {
                Debug.Log($"[DialogueManager] No player choices available. Will transition automatically after delay.");
                // Auto-advance after a short delay (user can click to advance)
                StartCoroutine(AutoAdvanceDialogue(pid));
            }
            return;
        }

        // Use explicitly assigned buttons (preferred method)
        if (btnT != null || btnO != null || btnN != null || btnE != null)
        {
            // Map choices to buttons by ToneType
            Button[] buttons = { btnT, btnO, btnN, btnE };
            TextMeshProUGUI[] labels = { txtT, txtO, txtN, txtE };
            ToneType[] tones = { ToneType.Trust, ToneType.Observation, ToneType.NarrativePresence, ToneType.Empathy };
            string[] toneNames = { "Trust", "Observation", "NarrativePresence", "Empathy" };

            Debug.Log($"[DialogueManager] Button state - T:{(btnT != null ? "✓" : "✗")} O:{(btnO != null ? "✓" : "✗")} N:{(btnN != null ? "✓" : "✗")} E:{(btnE != null ? "✓" : "✗")}");
            Debug.Log($"[DialogueManager] Processing {p.choices.Count} choices from passage {p.pid}");

            foreach (var choice in p.choices)
            {
                int toneIndex = -1;
                Debug.Log($"[DialogueManager] Processing choice with tone: {choice.tone}");

                for (int i = 0; i < tones.Length; i++)
                {
                    if (choice.tone == tones[i])
                    {
                        toneIndex = i;
                        Debug.Log($"[DialogueManager] ✓ Tone match found! choice.tone={choice.tone} equals tones[{i}]={tones[i]}");
                        break;
                    }
                }

                if (toneIndex < 0)
                {
                    Debug.LogWarning($"[DialogueManager] ✗ NO TONE MATCH! choice.tone='{choice.tone}' (type: {choice.tone.GetType()})");
                    Debug.LogWarning($"[DialogueManager]   Available tones: {string.Join(", ", tones)}");
                }

                if (toneIndex >= 0 && buttons[toneIndex] != null)
                {
                    Button targetBtn = buttons[toneIndex];
                    targetBtn.gameObject.SetActive(true);

                    if (labels[toneIndex] != null)
                        labels[toneIndex].text = choice.playerLine;

                    targetBtn.onClick.RemoveAllListeners();
                    targetBtn.onClick.AddListener(() => OnChoiceMade(choice));

                    Debug.Log($"[DialogueManager] ✓ Activated button {toneNames[toneIndex]}: '{choice.playerLine}'");
                }
                else
                {
                    Debug.LogWarning($"[DialogueManager] ✗ Could not activate {(toneIndex >= 0 ? toneNames[toneIndex] : "unknown")} - button is null or invalid tone (toneIndex={toneIndex})");
                }
            }
        }
        // Fallback to dynamic button spawning if no static buttons assigned
        else if (_choiceButtonPrefab != null && choiceButtonContainer != null)
        {
            foreach (var choice in p.choices)
            {
                GameObject btnObj = Instantiate(_choiceButtonPrefab, choiceButtonContainer);
                btnObj.GetComponentInChildren<TextMeshProUGUI>().text = choice.playerLine;
                btnObj.GetComponent<Button>().onClick.AddListener(() => OnChoiceMade(choice));
            }
        }
    }

    private IEnumerator AutoAdvanceDialogue(string currentPid, bool skipDisplay = false)
    {
        // For shared dialogue (skipDisplay=true), advance immediately without waiting
        if (!skipDisplay)
        {
            // Display NPC-only turn for a brief moment, allowing player to click to continue
            yield return new WaitForSeconds(1f);
        }
        else
        {
            // Seamless advance for shared dialogue
            yield return new WaitForEndOfFrame();
        }

        // Check if current passage has a target to advance to
        if (passages.TryGetValue(currentPid, out var currentPassage))
        {
            // For shared beats and NPC turns, look for a way to get to next turn
            // This is a simple auto-advance - in a real system, you'd want click-to-continue
            Debug.Log($"[DialogueManager] Auto-advancing from NPC turn: {currentPid}");
        }
    }

    private void OnChoiceMade(StoryChoice choice) => StartCoroutine(ResolveChoice(choice));

    private IEnumerator ResolveChoice(StoryChoice choice)
    {
        ClearButtons();

        // Execute player action if specified (e.g., approach, freeze, wander)
        if (!string.IsNullOrEmpty(choice.result_text) && PlayerActionHandler.Instance != null)
        {
            PlayerActionHandler.Instance.ExecutePlayerAction(choice.result_text);
        }

        // Apply tone effects and resonance
        if (StatManager.Instance != null)
        {
            foreach (var t in choice.tone_effects.ToDictionary())
            {
                StatManager.Instance.AdjustPlayerTone(ParseTone(t.Key), t.Value, activeNpcId);
                if (Velinor.Core.CodexManager.Instance != null)
                {
                    Velinor.Core.CodexManager.Instance.AddEmotionalTag(t.Key);
                }
            }
            StatManager.Instance.ApplyNpcResonance(activeNpcId, choice.npc_resonance.ToDictionary());

            // NEW: Apply direct remnants effects (for multi-NPC encounters)
            ApplyRemnantsEffects(choice.remnants_effects);
        }

        ProcessDataHook(choice.data_hook);
        ProcessSystemTrigger(choice.system_trigger);

        // Build the response text: shared beat (NPC reaction to choice)
        string responseText = "";
        if (!string.IsNullOrEmpty(choice.shared_beat))
        {
            responseText = $"{choice.shared_beat}\n\n";
        }

        // Handle target passage - show NPC response + next prompt immediately
        if (!string.IsNullOrEmpty(choice.target))
        {
            if (choice.target == "DIALOGUE_END")
            {
                EndDialogue();
            }
            else
            {
                // Load next passage to get its prompt text
                if (passages.TryGetValue(choice.target, out var nextPassage))
                {
                    // Use choice's NPC response first (for beats-based format with npc_response field)
                    string npcResponse = choice.npc_response ?? "";
                    
                    // If no direct NPC response on choice, check the next passage for tone-dependent responses
                    if (string.IsNullOrEmpty(npcResponse) && nextPassage.npc_responses != null && nextPassage.npc_responses.Count > 0)
                    {
                        string toneKey = choice.tone.ToString();
                        if (nextPassage.npc_responses.TryGetValue(toneKey, out var toneResponse))
                        {
                            npcResponse = toneResponse;
                            Debug.Log($"[DialogueManager] Using tone-dependent response for {toneKey}: {toneResponse}");
                        }
                    }
                    
                    // If still no NPC response, use the next passage's text (but not for shared dialogue beats)
                    if (string.IsNullOrEmpty(npcResponse))
                    {
                        // Don't use nextPassage.text if it's a shared dialogue beat - those flow seamlessly
                        if (nextPassage.active_speaker != "Shared" && nextPassage.active_speaker != "shared")
                        {
                            npcResponse = nextPassage.text;
                        }
                    }

                    // Combine NPC response with any shared beat
                    string fullText = responseText + npcResponse;

                    // For shared dialogue beats, don't show the NPC response yet - let DisplayPassage handle it
                    bool isSharedTarget = !string.IsNullOrEmpty(nextPassage.active_speaker) &&
                                         (nextPassage.active_speaker == "Ravi" || nextPassage.active_speaker == "Nima");
                    
                    var dialogueUIController = FindAnyObjectByType<DialogueUIController>();
                    if (!isSharedTarget && dialogueUIController != null)
                    {
                        // For regular passages, display the NPC response first
                        string displayName = GetDisplayNameForDialogue(activeNpcId);

                        // Check active speaker for multi-speaker passages
                        if (!string.IsNullOrEmpty(nextPassage.active_speaker) && nextPassage.active_speaker != "Player")
                        {
                            displayName = GetDisplayNameForDialogue(nextPassage.active_speaker);
                        }
                        else if (nextPassage.active_speaker == "Player")
                        {
                            // Format player inner thoughts in italics
                            fullText = $"<i>{fullText}</i>";
                            displayName = "";  // No speaker name for inner thoughts
                        }

                        dialogueUIController.ShowDialogue(displayName, fullText);
                        dialogueUIController.currentActiveSpeaker = nextPassage.active_speaker;
                        Debug.Log($"[DialogueManager] Showing NPC response + next passage: {choice.target} (speaker: {nextPassage.active_speaker}, display name: {displayName})");
                        
                        // For regular passages, just show choices
                        ClearButtons();
                        DisplayChoicesForPassage(choice.target);
                    }
                    else
                    {
                        // For shared dialogue beats, use DisplayPassage to show both text and choices
                        ClearButtons();
                        DisplayPassage(choice.target);
                    }
                }
            }
        }
        else
        {
            EndDialogue();
        }

        yield return null;  // Return control without waiting
    }

    /// <summary>
    /// Apply direct Remnants effects (as array of stat changes).
    /// Each effect specifies target NPC, stat name, and delta value.
    /// If target is "activeNpcId", expands to the currently active NPC.
    /// Otherwise, targets the NPC specified by name (e.g., "Ravi", "Nima").
    /// </summary>
    private void ApplyRemnantsEffects(List<RemnantsEffect> effectsList)
    {
        if (StatManager.Instance == null) return;
        if (effectsList == null || effectsList.Count == 0) return;

        foreach (var effect in effectsList)
        {
            if (effect == null) continue;

            // Determine target NPC: expand "activeNpcId" to actual NPC name
            string targetNpcId = effect.target == "activeNpcId" ? activeNpcId : effect.target;
            if (string.IsNullOrEmpty(targetNpcId)) continue;

            var npcRemnants = StatManager.Instance.GetNpcRemnants(targetNpcId);
            if (npcRemnants == null)
            {
                Debug.LogWarning($"[DialogueManager] No Remnants found for NPC '{targetNpcId}'. Creating new entry.");
                npcRemnants = new Remnants();
                StatManager.Instance.SetNpcRemnants(targetNpcId, npcRemnants);
            }

            // Map stat name string to RemnantType and apply delta
            RemnantType? statType = effect.stat switch
            {
                "resolve" => RemnantType.Resolve,
                "empathy" => RemnantType.Empathy,
                "memory" => RemnantType.Memory,
                "nuance" => RemnantType.Nuance,
                "authority" => RemnantType.Authority,
                "need" => RemnantType.Need,
                "trust" => RemnantType.Trust,
                "skepticism" => RemnantType.Skepticism,
                _ => null
            };

            if (statType.HasValue)
            {
                float current = npcRemnants.Get(statType.Value);
                float newValue = current + effect.delta;
                npcRemnants.Set(statType.Value, newValue);
                Debug.Log($"[DialogueManager] {targetNpcId} {effect.stat}: {current:F3} → {newValue:F3} (delta: {effect.delta:+0.00;-0.00})");
            }
            else
            {
                Debug.LogWarning($"[DialogueManager] Unknown remnants stat: '{effect.stat}'");
            }
        }
    }

    private void ApplyRemnantsEffects(RemnantsEffects effects)
    {
        if (StatManager.Instance == null) return;
        if (effects == null) return;

        // Determine target NPC: expand "activeNpcId" to actual NPC name
        string targetNpcId = effects.target == "activeNpcId" ? activeNpcId : effects.target;
        if (string.IsNullOrEmpty(targetNpcId)) return;

        var npcRemnants = StatManager.Instance.GetNpcRemnants(targetNpcId);
        if (npcRemnants == null)
        {
            Debug.LogWarning($"[DialogueManager] No Remnants found for NPC '{targetNpcId}'. Creating new entry.");
            npcRemnants = new Remnants();
            StatManager.Instance.SetNpcRemnants(targetNpcId, npcRemnants);
        }

        // Apply deltas to corresponding remnants
        // Map: trust_delta -> RemnantType.Trust, alert_delta -> Skepticism, grief_delta -> Need/Memory, etc.
        if (effects.trust_delta != 0)
        {
            float current = npcRemnants.Get(RemnantType.Trust);
            npcRemnants.Set(RemnantType.Trust, current + effects.trust_delta * 0.1f);  // Scale by 0.1 for 0-1 range
            Debug.Log($"[DialogueManager] Applied trust_delta {effects.trust_delta} to {targetNpcId}: {current:F3} -> {npcRemnants.Get(RemnantType.Trust):F3}");
        }

        if (effects.alert_delta != 0)
        {
            float current = npcRemnants.Get(RemnantType.Skepticism);
            npcRemnants.Set(RemnantType.Skepticism, current + effects.alert_delta * 0.1f);
            Debug.Log($"[DialogueManager] Applied alert_delta {effects.alert_delta} to {targetNpcId}: {current:F3} -> {npcRemnants.Get(RemnantType.Skepticism):F3}");
        }

        if (effects.guard_delta != 0)
        {
            float current = npcRemnants.Get(RemnantType.Authority);
            npcRemnants.Set(RemnantType.Authority, current + effects.guard_delta * 0.1f);
            Debug.Log($"[DialogueManager] Applied guard_delta {effects.guard_delta} to {targetNpcId}: {current:F3} -> {npcRemnants.Get(RemnantType.Authority):F3}");
        }

        if (effects.grief_delta != 0)
        {
            float current = npcRemnants.Get(RemnantType.Memory);
            npcRemnants.Set(RemnantType.Memory, current + effects.grief_delta * 0.1f);
            Debug.Log($"[DialogueManager] Applied grief_delta {effects.grief_delta} to {targetNpcId}: {current:F3} -> {npcRemnants.Get(RemnantType.Memory):F3}");
        }

        if (effects.reputation_delta != 0)
        {
            float current = npcRemnants.Get(RemnantType.Resolve);
            npcRemnants.Set(RemnantType.Resolve, current + effects.reputation_delta * 0.1f);
            Debug.Log($"[DialogueManager] Applied reputation_delta {effects.reputation_delta} to {targetNpcId}: {current:F3} -> {npcRemnants.Get(RemnantType.Resolve):F3}");
        }
    }

    private void ProcessDataHook(string hook)
    {
        if (string.IsNullOrEmpty(hook)) return;

        // Support multiple hooks separated by pipe: "flag=value|append_diary:text|another_flag=value"
        string[] hooks = hook.Split('|');
        foreach (var singleHook in hooks)
        {
            string trimmedHook = singleHook.Trim();
            if (string.IsNullOrEmpty(trimmedHook)) continue;

            // Handle flag assignment: "flagname=value"
            if (trimmedHook.Contains("=") && !trimmedHook.StartsWith("append_diary:"))
            {
                string[] parts = trimmedHook.Split('=');
                if (parts.Length == 2)
                {
                    string key = parts[0].Trim();
                    string value = parts[1].Trim();
                    if (bool.TryParse(value, out var boolValue))
                    {
                        GameFlags.Set(key, boolValue);
                        Debug.Log($"[DialogueManager] Data hook: {key} = {boolValue}");
                    }
                }
            }

            // Handle diary append: "append_diary:text"
            if (trimmedHook.StartsWith("append_diary:"))
            {
                string entryText = trimmedHook.Substring("append_diary:".Length);
                if (DiaryManager.Instance != null)
                {
                    DiaryManager.Instance.AddEntry(entryText);
                    Debug.Log($"[DialogueManager] Data hook: appended diary entry");
                }
            }
        }
    }

    /// <summary>
    /// Convert system triggers array into StoryPassage format for later processing.
    /// Triggers are processed when the passage is displayed, not at conversion time.
    /// </summary>
    private void StoreSystemTriggersInPassage(StoryPassage passage, BeatSystemTrigger[] triggers)
    {
        if (triggers == null || triggers.Length == 0) return;

        foreach (var trigger in triggers)
        {
            if (trigger != null && !string.IsNullOrEmpty(trigger.type))
            {
                passage.system_triggers_list.Add(trigger);
            }
        }
    }

    /// <summary>
    /// Process system triggers when a passage is displayed.
    /// Handles diary_append, update_dialogue_names, close_dialogue, etc.
    /// </summary>
    private void ProcessSystemTriggersFromPassage(List<BeatSystemTrigger> triggers)
    {
        foreach (var trigger in triggers)
        {
            if (trigger == null || string.IsNullOrEmpty(trigger.type)) continue;

            if (trigger.type == "diary_append" && trigger.data != null && trigger.data.Length > 0)
            {
                // Map diary key to content and append the entry
                string entryKey = trigger.data[0];
                string entryText = DiaryEntriesMapping.GetEntry(entryKey);
                if (DiaryManager.Instance != null)
                {
                    DiaryManager.Instance.AddEntry(entryText);
                    Debug.Log($"[DialogueManager] System trigger: diary_append '{entryKey}'");
                }
            }
            else if (trigger.type == "update_dialogue_names" && trigger.data != null && trigger.data.Length > 0)
            {
                // Reveal NPC names in this dialogue session
                foreach (string npcName in trigger.data)
                {
                    revealedNpcNames.Add(npcName);
                    Debug.Log($"[DialogueManager] System trigger: update_dialogue_names - revealed '{npcName}'");
                }

                // Update UI to show the currently active NPC's real name
                var ui = FindAnyObjectByType<DialogueUIController>();
                if (ui != null && ui.npcNameText != null && !string.IsNullOrEmpty(activeNpcId))
                {
                    ui.npcNameText.text = activeNpcId;
                    Debug.Log($"[DialogueManager] Updated UI name to '{activeNpcId}'");
                }
            }
            else if (trigger.type == "close_dialogue")
            {
                Debug.Log($"[DialogueManager] System trigger: close_dialogue");
                ProcessSystemTrigger("close_dialogue");
            }
            else if (trigger.type == "activate_proximity_tracker")
            {
                Debug.Log($"[DialogueManager] System trigger: activate_proximity_tracker");

                // Find and activate the proximity tracker
                var tracker = FindAnyObjectByType<ProximityTrackerUI>();
                if (tracker != null)
                {
                    // Look for a glyph collider in the current scene (tagged as "Glyph" or by name)
                    Collider glyphCollider = null;

                    // First try finding by tag
                    GameObject glyphObj = GameObject.FindGameObjectWithTag("Glyph");
                    if (glyphObj != null)
                    {
                        glyphCollider = glyphObj.GetComponent<Collider>();
                    }

                    // Fallback: search by name pattern
                    if (glyphCollider == null)
                    {
                        foreach (Collider col in FindObjectsByType<Collider>())
                        {
                            if (col.name.Contains("Glyph") || col.name.Contains("glyph"))
                            {
                                glyphCollider = col;
                                break;
                            }
                        }
                    }

                    if (glyphCollider != null)
                    {
                        tracker.StartTracking(glyphCollider);
                        Debug.Log($"[DialogueManager] Proximity tracker started for glyph: {glyphCollider.name}");
                    }
                    else
                    {
                        Debug.LogWarning("[DialogueManager] No glyph collider found for proximity tracker");
                    }
                }
                else
                {
                    Debug.LogWarning("[DialogueManager] ProximityTrackerUI not found in scene");
                }
            }
            else if (trigger.type == "codex_pulse" && trigger.data != null && trigger.data.Length > 0)
            {
                string pulseData = trigger.data[0];
                Debug.Log($"[DialogueManager] System trigger: codex_pulse '{pulseData}'");
                ProcessSystemTrigger($"codex_pulse:{pulseData}");
            }
            else
            {
                // Generic trigger passthrough
                Debug.Log($"[DialogueManager] System trigger: {trigger.type}");
                ProcessSystemTrigger(trigger.type);
            }
        }
    }

    private void ProcessSystemTrigger(string trigger)
    {
        if (string.IsNullOrEmpty(trigger)) return;

        // Support multiple triggers separated by pipe: "npc_disappear|diary_update"
        string[] triggers = trigger.Split('|');
        foreach (var singleTrigger in triggers)
        {
            string trimmedTrigger = singleTrigger.Trim();
            if (string.IsNullOrEmpty(trimmedTrigger)) continue;

            var ui = FindAnyObjectByType<DialogueUIController>();
            if (ui != null) ui.TriggerSystemEvent(trimmedTrigger);
        }
    }

    public static ToneType ParseTone(string s)
    {
        if (string.IsNullOrEmpty(s)) return ToneType.Trust;

        // Handle short codes
        if (s.Equals("T", StringComparison.OrdinalIgnoreCase))
            return ToneType.Trust;
        if (s.Equals("O", StringComparison.OrdinalIgnoreCase))
            return ToneType.Observation;
        if (s.Equals("N", StringComparison.OrdinalIgnoreCase))
            return ToneType.NarrativePresence;
        if (s.Equals("E", StringComparison.OrdinalIgnoreCase))
            return ToneType.Empathy;

        // Handle full names and aliases
        if (string.Equals(s, "Truth", StringComparison.OrdinalIgnoreCase))
            return ToneType.Trust;
        if (string.Equals(s, "Narrative", StringComparison.OrdinalIgnoreCase))
            return ToneType.NarrativePresence;

        // Try parsing as full enum name
        return Enum.TryParse<ToneType>(s, true, out var t) ? t : ToneType.Trust;
    }

    /// <summary>
    /// Returns the GameObject of the NPC that initiated the current dialogue
    /// </summary>
    public GameObject GetCurrentNPCGameObject() => currentNPCGameObject;

    /// <summary>
    /// Get the display name for an NPC. If the player hasn't learned their actual name,
    /// show a placeholder like "Older Woman", "Young Woman", "Young Man", etc.
    /// Checks both GameFlags and the current dialogue session's revealed names.
    /// </summary>
    private string GetDisplayNameForDialogue(string npcId)
    {
        // Check if name was revealed in this dialogue session
        if (revealedNpcNames.Contains(npcId))
        {
            Debug.Log($"[DialogueManager] {npcId}: Name revealed in this session - displaying '{npcId}'");
            return npcId;
        }

        // Check if the player has learned this NPC's name via GameFlags
        string learnedNameFlag = $"{npcId.ToLower()}_name_learned";
        if (GameFlags.Get(learnedNameFlag))
        {
            Debug.Log($"[DialogueManager] {npcId}: Name already learned - displaying '{npcId}'");
            revealedNpcNames.Add(npcId);  // Add to session tracking
            return npcId;  // Return actual name
        }

        // Return placeholder name if not yet learned
        string displayName = npcId switch
        {
            "Saori" => "Older Woman",
            "Nima" => "Young Woman",
            "Ravi" => "Young Man",
            _ => npcId  // Fallback to actual name if no placeholder defined
        };

        Debug.Log($"[DialogueManager] {npcId}: Name not yet learned - displaying placeholder '{displayName}'");
        return displayName;
    }

    /// <summary>
    /// Static version for backwards compatibility
    /// </summary>
    public static string GetDisplayName(string npcId)
    {
        // Check if the player has learned this NPC's name
        string learnedNameFlag = $"{npcId.ToLower()}_name_learned";
        if (GameFlags.Get(learnedNameFlag))
        {
            Debug.Log($"[DialogueManager] {npcId}: Name already learned - displaying '{npcId}'");
            return npcId;  // Return actual name
        }

        // Return placeholder name if not yet learned
        string displayName = npcId switch
        {
            "Saori" => "Older Woman",
            "Nima" => "Young Woman",
            "Ravi" => "Young Man",
            _ => npcId  // Fallback to actual name if no placeholder defined
        };

        Debug.Log($"[DialogueManager] {npcId}: Name not yet learned - displaying placeholder '{displayName}'");
        return displayName;
    }

    private void ClearButtons()
    {
        // Clear explicitly assigned buttons
        if (btnT != null) btnT.gameObject.SetActive(false);
        if (btnO != null) btnO.gameObject.SetActive(false);
        if (btnN != null) btnN.gameObject.SetActive(false);
        if (btnE != null) btnE.gameObject.SetActive(false);

        // Clear dynamically spawned buttons (fallback mode)
        if (choiceButtonContainer != null && (btnT == null && btnO == null && btnN == null && btnE == null))
        {
            foreach (Transform child in choiceButtonContainer)
            {
                Destroy(child.gameObject);
            }
        }
    }

    public void EndDialogue()
    {
        // Mark conversation as completed if we have a valid conversation ID
        if (!string.IsNullOrEmpty(currentConversationId))
        {
            string completionFlag = $"{currentConversationId}_completed";
            GameFlags.Set(completionFlag, true);
            Debug.Log($"[DialogueManager] Setting completion flag: {completionFlag}");
        }

        isDialogueActive = false;
        // Don't disable dialogueCanvas - let DialogueUIController manage UI_Canvas

        // Hide dialogue via DialogueUIController
        var controller = FindAnyObjectByType<DialogueUIController>();
        if (controller != null)
        {
            controller.HideDialogue();
            Debug.Log("[DialogueManager] Hiding dialogue via DialogueUIController");
        }

        // Only lock cursor if no other interactive UI panels are active
        if (!IsOtherUIPanelActive())
        {
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
            Debug.Log("[DialogueManager] Cursor locked (no other UI active)");
        }
        else
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
            Debug.Log("[DialogueManager] Cursor unlocked (other UI panel is active)");
        }
        OnDialogueEnded?.Invoke();
    }

    /// <summary>
    /// Check if Codex, Triglyph Puzzle, or other interactive UIs are active
    /// </summary>
    private bool IsOtherUIPanelActive()
    {
        // Check if CodexController has active panel
        var codexController = FindAnyObjectByType<CodexController>();
        if (codexController != null && codexController.codexPanel != null)
        {
            if (codexController.codexPanel.alpha > 0.5f && codexController.codexPanel.interactable)
            {
                Debug.Log("[DialogueManager] CodexPanel is active");
                return true;
            }
        }

        // Check if TriglyphPuzzleController has active panel
        var triglyphController = FindAnyObjectByType<TriglyphPuzzleController>();
        if (triglyphController != null)
        {
            // Try to find triglyph panel in the scene
            var triglyphPanel = GameObject.Find("TriglyphPanel");
            if (triglyphPanel != null && triglyphPanel.activeSelf)
            {
                // Check if it's also visible (has CanvasGroup alpha > 0.5)
                var canvasGroup = triglyphPanel.GetComponent<CanvasGroup>();
                if (canvasGroup == null || canvasGroup.alpha > 0.5f)
                {
                    Debug.Log("[DialogueManager] TriglyphPanel is active");
                    return true;
                }
            }
        }

        return false;
    }

    /// <summary>
    /// Diagnostic method to validate all DialoguePanel wiring.
    /// Run via: Select DialogueManager > Right-click > ValidateDialoguePanel
    /// </summary>
    [ContextMenu("ValidateDialoguePanel")]
    public void ValidateDialoguePanel()
    {
        Debug.Log("═══════════════════════════════════════════════════════════");
        Debug.Log("VALIDATING DIALOGUE PANEL WIRING");
        Debug.Log("═══════════════════════════════════════════════════════════");

        bool allValid = true;

        // Canvas validation
        if (dialogueCanvas != null)
            Debug.Log("✓ DialogueCanvas: ASSIGNED");
        else
        {
            Debug.LogError("✗ DialogueCanvas: NOT ASSIGNED - Panel will not display.");
            allValid = false;
        }

        // Text fields validation
        if (bodyText != null)
            Debug.Log("✓ bodyText: ASSIGNED");
        else
        {
            Debug.LogError("✗ bodyText: NOT ASSIGNED - Dialogue text won't display.");
            allValid = false;
        }

        if (npcNameText != null)
            Debug.Log("✓ npcNameText: ASSIGNED");
        else
        {
            Debug.LogWarning("⚠ npcNameText: NOT ASSIGNED (optional).");
        }

        if (sharedBeatText != null)
            Debug.Log("✓ sharedBeatText: ASSIGNED");
        else
        {
            Debug.LogWarning("⚠ sharedBeatText: NOT ASSIGNED (optional).");
        }

        // Button validation
        Debug.Log("\nCHOICE BUTTONS:");
        if (btnT != null)
            Debug.Log("  ✓ btnT (Trust): ASSIGNED");
        else
        {
            Debug.LogError("  ✗ btnT (Trust): NOT ASSIGNED");
            allValid = false;
        }

        if (btnO != null)
            Debug.Log("  ✓ btnO (Observation): ASSIGNED");
        else
        {
            Debug.LogError("  ✗ btnO (Observation): NOT ASSIGNED");
            allValid = false;
        }

        if (btnN != null)
            Debug.Log("  ✓ btnN (NarrativePresence): ASSIGNED");
        else
        {
            Debug.LogError("  ✗ btnN (NarrativePresence): NOT ASSIGNED");
            allValid = false;
        }

        if (btnE != null)
            Debug.Log("  ✓ btnE (Empathy): ASSIGNED");
        else
        {
            Debug.LogError("  ✗ btnE (Empathy): NOT ASSIGNED");
            allValid = false;
        }

        // Button label validation
        Debug.Log("\nBUTTON LABELS:");
        if (txtT != null)
            Debug.Log("  ✓ txtT (Trust label): ASSIGNED");
        else
        {
            Debug.LogError("  ✗ txtT (Trust label): NOT ASSIGNED");
            allValid = false;
        }

        if (txtO != null)
            Debug.Log("  ✓ txtO (Observation label): ASSIGNED");
        else
        {
            Debug.LogError("  ✗ txtO (Observation label): NOT ASSIGNED");
            allValid = false;
        }

        if (txtN != null)
            Debug.Log("  ✓ txtN (NarrativePresence label): ASSIGNED");
        else
        {
            Debug.LogError("  ✗ txtN (NarrativePresence label): NOT ASSIGNED");
            allValid = false;
        }

        if (txtE != null)
            Debug.Log("  ✓ txtE (Empathy label): ASSIGNED");
        else
        {
            Debug.LogError("  ✗ txtE (Empathy label): NOT ASSIGNED");
            allValid = false;
        }

        // Fallback validation
        Debug.Log("\nFALLBACK (if no static buttons):");
        if (_choiceButtonPrefab != null)
            Debug.Log("  ✓ choiceButtonPrefab: ASSIGNED");
        else
            Debug.LogWarning("  ⚠ choiceButtonPrefab: NOT ASSIGNED (only needed for dynamic mode).");

        if (choiceButtonContainer != null)
            Debug.Log("  ✓ choiceButtonContainer: ASSIGNED");
        else
            Debug.LogWarning("  ⚠ choiceButtonContainer: NOT ASSIGNED (only needed for dynamic mode).");

        Debug.Log("═══════════════════════════════════════════════════════════");
        if (allValid)
            Debug.Log("✓ ALL VALIDATION CHECKS PASSED - DialoguePanel is properly wired!");
        else
            Debug.LogError("✗ VALIDATION FAILED - Fix the missing assignments above.");
        Debug.Log("═══════════════════════════════════════════════════════════");
    }
}
