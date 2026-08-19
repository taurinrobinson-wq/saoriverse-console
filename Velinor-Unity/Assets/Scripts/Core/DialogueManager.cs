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
    public class StoryChoice
    {
        public ToneType tone;            // Explicit tone type (canonical)
        public string playerLine;        // Button label (player's choice text)
        public string npcResponse;       // NPC's response text
        public string target;            // Next passage PID
        public string shared_beat;       // Text shown AFTER choice
        public string system_trigger;    // e.g., "give_device"
        public string data_hook;         // e.g., "met_saori=true"
        public ToneResonanceMap tone_effects = new ToneResonanceMap();
        public ToneResonanceMap npc_resonance = new ToneResonanceMap();
    }

    [Serializable]
    public class StoryPassage
    {
        public string pid;
        public string name;
        public string text;              // Initial prompt/setting
        public List<string> required_flags = new List<string>();
        public List<StoryChoice> choices = new List<StoryChoice>();
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
    public GameObject dialogueUIPanel { 
        get => dialogueCanvas != null ? dialogueCanvas.gameObject : null; 
        set { if (value != null) dialogueCanvas = value.GetComponent<Canvas>(); }
    }
    public TextMeshProUGUI speakerNameText { get => npcNameText; set => npcNameText = value; }
    public TextMeshProUGUI dialogueText { get => bodyText; set => bodyText = value; }
    public Transform choicesContainer { get => choiceButtonContainer; set => choiceButtonContainer = value; }
    public GameObject choiceButtonPrefab { get => _choiceButtonPrefab; set => _choiceButtonPrefab = value; }

    private Dictionary<string, StoryPassage> passages = new Dictionary<string, StoryPassage>();
    private string activeNpcId;
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
            foreach (var p in data.passages) passages[p.pid] = p;
            activeStoryPath = path;
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

        activeNpcId = npcId;
        isDialogueActive = true;
        
        AutoBindUI();

        if (dialogueCanvas != null) dialogueCanvas.enabled = true;
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
            
            if (txtT == null || txtT.gameObject == null) txtT = FindTextMeshInButton(btnT);
            if (txtO == null || txtO.gameObject == null) txtO = FindTextMeshInButton(btnO);
            if (txtN == null || txtN.gameObject == null) txtN = FindTextMeshInButton(btnN);
            if (txtE == null || txtE.gameObject == null) txtE = FindTextMeshInButton(btnE);
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
            if (btnTrans != null) return btnTrans.GetComponent<Button>();
            
            var allButtons = choiceButtonContainer.GetComponentsInChildren<Button>(true);
            foreach (var b in allButtons) if (b.name == name) return b;
        }

        // Fallback to direct path from canvas
        var trans = dialogueCanvas.transform.Find("DialoguePanel/" + name);
        if (trans != null) return trans.GetComponent<Button>();
        
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

    private void DisplayPassage(string pid)
    {
        if (!passages.TryGetValue(pid, out var p)) { EndDialogue(); return; }
        foreach (var flag in p.required_flags) { if (!GameFlags.Get(flag)) { EndDialogue(); return; } }

        if (npcNameText != null) npcNameText.text = activeNpcId;
        if (bodyText != null) bodyText.text = p.text;

        ClearButtons();

        // Use explicitly assigned buttons (preferred method)
        if (btnT != null || btnO != null || btnN != null || btnE != null)
        {
            // Map choices to buttons by ToneType
            Button[] buttons = { btnT, btnO, btnN, btnE };
            TextMeshProUGUI[] labels = { txtT, txtO, txtN, txtE };
            ToneType[] tones = { ToneType.Trust, ToneType.Observation, ToneType.NarrativePresence, ToneType.Empathy };

            foreach (var choice in p.choices)
            {
                int toneIndex = -1;
                for (int i = 0; i < tones.Length; i++)
                {
                    if (choice.tone == tones[i])
                    {
                        toneIndex = i;
                        break;
                    }
                }

                if (toneIndex >= 0 && buttons[toneIndex] != null)
                {
                    Button targetBtn = buttons[toneIndex];
                    targetBtn.gameObject.SetActive(true);
                    
                    if (labels[toneIndex] != null)
                        labels[toneIndex].text = choice.playerLine;
                    
                    targetBtn.onClick.RemoveAllListeners();
                    targetBtn.onClick.AddListener(() => OnChoiceMade(choice));
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

    private void OnChoiceMade(StoryChoice choice) => StartCoroutine(ResolveChoice(choice));

    private IEnumerator ResolveChoice(StoryChoice choice)
    {
        ClearButtons();
        if (StatManager.Instance != null)
        {
            foreach (var t in choice.tone_effects.ToDictionary())
            {
                StatManager.Instance.AdjustPlayerTone(ParseTone(t.Key), t.Value, activeNpcId);
                // Dynamically register emotional tags in the player's Codex state
                if (Velinor.Core.CodexManager.Instance != null)
                {
                    Velinor.Core.CodexManager.Instance.AddEmotionalTag(t.Key);
                }
            }
            StatManager.Instance.ApplyNpcResonance(activeNpcId, choice.npc_resonance.ToDictionary());
        }

        ProcessDataHook(choice.data_hook);
        ProcessSystemTrigger(choice.system_trigger);

        if (!string.IsNullOrEmpty(choice.shared_beat))
        {
            var sharedBeatText = FindTextMeshInCanvas("SharedBeatText");
            if (sharedBeatText != null)
            {
                sharedBeatText.text = choice.shared_beat;
                sharedBeatText.gameObject.SetActive(true);
                yield return new WaitForSeconds(4f);
                sharedBeatText.gameObject.SetActive(false);
                sharedBeatText.text = "";
            }
            else
            {
                bodyText.text = choice.shared_beat;
                yield return new WaitForSeconds(4f);
            }
        }

        if (!string.IsNullOrEmpty(choice.target)) DisplayPassage(choice.target);
        else EndDialogue();
    }

    private void ProcessDataHook(string hook)
    {
        if (string.IsNullOrEmpty(hook)) return;
        if (hook.Contains("=")) {
            string[] parts = hook.Split('=');
            if (parts.Length == 2) GameFlags.Set(parts[0].Trim(), bool.Parse(parts[1].Trim()));
        }
        if (hook.StartsWith("append_diary:")) DiaryManager.Instance?.AddEntry(hook.Substring("append_diary:".Length));
    }

    private void ProcessSystemTrigger(string trigger)
    {
        if (string.IsNullOrEmpty(trigger)) return;
        var ui = FindAnyObjectByType<DialogueUIController>();
        if (ui != null) ui.TriggerSystemEvent(trigger);
    }

    private ToneType ParseTone(string s)
    {
        if (string.Equals(s, "Truth", StringComparison.OrdinalIgnoreCase))
            return ToneType.Trust;
        if (string.Equals(s, "Narrative", StringComparison.OrdinalIgnoreCase))
            return ToneType.NarrativePresence;
        return Enum.TryParse<ToneType>(s, true, out var t) ? t : ToneType.Trust;
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
        isDialogueActive = false;
        if (dialogueCanvas != null) dialogueCanvas.enabled = false;
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
        OnDialogueEnded?.Invoke();
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
