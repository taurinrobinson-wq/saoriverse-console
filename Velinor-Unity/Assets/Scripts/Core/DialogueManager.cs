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

    [Header("UI References")]
    [SerializeField] private Canvas dialogueCanvas;
    [SerializeField] private TextMeshProUGUI npcNameText;
    [SerializeField] private TextMeshProUGUI bodyText;
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
        if (dialogueCanvas != null) dialogueCanvas.enabled = false;
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

    private void AutoBindUI()
    {
        if (dialogueCanvas == null) dialogueCanvas = FindAnyObjectByType<Canvas>();
        if (dialogueCanvas != null)
        {
            if (npcNameText == null) npcNameText = FindTextMeshInCanvas("NPCLineText");
            if (bodyText == null) bodyText = FindTextMeshInCanvas("DialogueBodyText");
            if (choiceButtonContainer == null) choiceButtonContainer = dialogueCanvas.transform.Find("DialoguePanel");
        }
    }

    private Button FindButtonInCanvas(string name)
    {
        if (dialogueCanvas == null) return null;
        var trans = dialogueCanvas.transform.Find("DialoguePanel/" + name);
        if (trans != null) return trans.GetComponent<Button>();
        return null;
    }

    private TextMeshProUGUI FindTextMeshInCanvas(string name)
    {
        if (dialogueCanvas == null) return null;
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

        // Check for pre-placed static buttons
        Button btnT = FindButtonInCanvas("ChoiceButton_T");
        Button btnO = FindButtonInCanvas("ChoiceButton_O");
        Button btnN = FindButtonInCanvas("ChoiceButton_N");
        Button btnE = FindButtonInCanvas("ChoiceButton_E");

        if (btnT != null || btnO != null || btnN != null || btnE != null)
        {
            foreach (var choice in p.choices)
            {
                Button targetBtn = null;

                switch (choice.tone)
                {
                    case ToneType.Trust:
                        targetBtn = btnT;
                        break;

                    case ToneType.Observation:
                        targetBtn = btnO;
                        break;

                    case ToneType.NarrativePresence:
                        targetBtn = btnN;
                        break;

                    case ToneType.Empathy:
                        targetBtn = btnE;
                        break;
                }

                if (targetBtn != null)
                {
                    targetBtn.gameObject.SetActive(true);
                    var textMesh = targetBtn.GetComponentInChildren<TextMeshProUGUI>();
                    if (textMesh != null) textMesh.text = choice.playerLine;
                    targetBtn.onClick.RemoveAllListeners();
                    targetBtn.onClick.AddListener(() => OnChoiceMade(choice));
                }
            }
        }
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
        Button btnT = FindButtonInCanvas("ChoiceButton_T");
        Button btnO = FindButtonInCanvas("ChoiceButton_O");
        Button btnN = FindButtonInCanvas("ChoiceButton_N");
        Button btnE = FindButtonInCanvas("ChoiceButton_E");

        if (btnT != null || btnO != null || btnN != null || btnE != null)
        {
            if (btnT != null) btnT.gameObject.SetActive(false);
            if (btnO != null) btnO.gameObject.SetActive(false);
            if (btnN != null) btnN.gameObject.SetActive(false);
            if (btnE != null) btnE.gameObject.SetActive(false);
        }
        else if (choiceButtonContainer != null && choiceButtonContainer.name != "DialoguePanel")
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
}
