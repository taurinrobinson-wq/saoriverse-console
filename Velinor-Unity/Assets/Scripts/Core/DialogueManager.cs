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
        public string npcResponse;       // NPC's response text
        public string target;            // Next passage PID
        public string shared_beat;       // Text shown AFTER choice (string for backward compatibility)
        public List<SharedBeatLine> shared_beat_lines;  // Array for multi-speaker
        public string system_trigger;    // e.g., "give_device"
        public string data_hook;         // e.g., "met_saori=true"
        public ToneResonanceMap tone_effects = new ToneResonanceMap();
        public ToneResonanceMap npc_resonance = new ToneResonanceMap();

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
    private bool isDialogueActive = false;
    private string activeStoryPath = "velinor/stories/sample_story";

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

    public void StartDialogue(string npcId, string startPid, string storyPath)
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

        // Store the conversation ID for later completion tracking
        var finalPassage = passages[startPid];
        currentConversationId = finalPassage.conversationId;
        Debug.Log($"[DialogueManager] Starting dialogue - npcId: {npcId}, conversationId: {currentConversationId}, startPid: {startPid}");

        isDialogueActive = true;

        AutoBindUI();

        // Don't enable dialogueCanvas - let DialogueUIController manage UI_Canvas visibility
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
        DisplayPassage(startPid);
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
        foreach (var flag in p.required_flags) { if (!GameFlags.Get(flag)) { EndDialogue(); return; } }

        // Update DialogueUIController - always clear and show fresh passage
        var dialogueUIController = FindAnyObjectByType<DialogueUIController>();
        if (dialogueUIController != null)
        {
            string displayName = GetDisplayName(activeNpcId);

            // For multi-speaker passages, show first speaker's name or use active_speaker
            if (!string.IsNullOrEmpty(p.active_speaker))
            {
                if (p.active_speaker == "Shared" && p.shared_beat != null && p.shared_beat.Count > 0)
                {
                    // For shared beats, show the first speaker's name
                    displayName = p.shared_beat[0].speaker;
                }
                else if (p.active_speaker != "Player")
                {
                    // Use the active speaker (Nima, Ravi, etc.)
                    displayName = p.active_speaker;
                }
            }

            dialogueUIController.ShowDialogue(displayName, p.text);
            // Store active_speaker for UI to use
            dialogueUIController.currentActiveSpeaker = p.active_speaker;
            Debug.Log($"[DialogueManager] Displaying passage: {pid} (speaker: {p.active_speaker}, display name: {displayName})");
        }
        else
        {
            Debug.LogError("[DialogueManager] DialogueUIController not found!");
        }

        ClearButtons();
        DisplayChoicesForPassage(pid);
    }

    private void DisplayChoicesForPassage(string pid)
    {
        if (!passages.TryGetValue(pid, out var p)) return;

        // Only show choices if this is a Player turn
        bool isPlayerTurn = string.IsNullOrEmpty(p.active_speaker) || p.active_speaker == "Player";
        Debug.Log($"[DialogueManager] DisplayChoicesForPassage - pid: {pid}, active_speaker: '{p.active_speaker}', isPlayerTurn: {isPlayerTurn}, choicesCount: {p.choices.Count}");

        if (!isPlayerTurn)
        {
            // This is an NPC turn or shared beat - don't show choices
            Debug.Log($"[DialogueManager] NPC/Shared turn detected - no choices shown. Will transition automatically after delay.");
            // Auto-advance after a short delay (user can click to advance)
            StartCoroutine(AutoAdvanceDialogue(pid));
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

    private IEnumerator AutoAdvanceDialogue(string currentPid)
    {
        // Display NPC-only turn for a brief moment, allowing player to click to continue
        // For now, just show it for 1 second then auto-advance
        // TODO: Add click-to-continue mechanic
        yield return new WaitForSeconds(1f);

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
                    string npcResponse = nextPassage.text;

                    // Check if this passage has tone-dependent responses
                    if (nextPassage.npc_responses != null && nextPassage.npc_responses.Count > 0)
                    {
                        string toneKey = choice.tone.ToString();
                        if (nextPassage.npc_responses.TryGetValue(toneKey, out var toneResponse))
                        {
                            npcResponse = toneResponse;
                            Debug.Log($"[DialogueManager] Using tone-dependent response for {toneKey}: {toneResponse}");
                        }
                    }

                    // Combine NPC response with next passage's prompt
                    string fullText = responseText + npcResponse;

                    // Display combined text and immediately show next choices
                    var dialogueUIController = FindAnyObjectByType<DialogueUIController>();
                    if (dialogueUIController != null)
                    {
                        string displayName = GetDisplayName(activeNpcId);

                        // Check active speaker for multi-speaker passages
                        if (!string.IsNullOrEmpty(nextPassage.active_speaker) && nextPassage.active_speaker != "Player")
                        {
                            displayName = nextPassage.active_speaker;
                        }

                        dialogueUIController.ShowDialogue(displayName, fullText);
                        dialogueUIController.currentActiveSpeaker = nextPassage.active_speaker;
                        Debug.Log($"[DialogueManager] Showing NPC response + next passage: {choice.target} (speaker: {nextPassage.active_speaker}, display name: {displayName})");
                    }

                    // Set up choices from the target passage
                    ClearButtons();
                    DisplayChoicesForPassage(choice.target);
                }
            }
        }
        else
        {
            EndDialogue();
        }

        yield return null;  // Return control without waiting
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
        if (string.Equals(s, "Truth", StringComparison.OrdinalIgnoreCase))
            return ToneType.Trust;
        if (string.Equals(s, "Narrative", StringComparison.OrdinalIgnoreCase))
            return ToneType.NarrativePresence;
        return Enum.TryParse<ToneType>(s, true, out var t) ? t : ToneType.Trust;
    }

    /// <summary>
    /// Get the display name for an NPC. If the player hasn't learned their actual name,
    /// show a placeholder like "Older Woman", "Young Woman", "Young Man", etc.
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
