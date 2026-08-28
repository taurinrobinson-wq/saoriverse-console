using UnityEngine;
using UnityEngine.UI;
using TMPro;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Handles ONLY NPC Dialogue UI
/// Triggered by: E key + player near NPC
/// Not responsible for: Diary (DiaryController), Codex (CodexController)
/// </summary>
public class DialogueUIController : MonoBehaviour
{
    [Header("Dialogue Panel")]
    public CanvasGroup dialoguePanel;
    public TextMeshProUGUI dialogueText;
    public TextMeshProUGUI npcNameText;

    [Header("Fonts")]
    public TMP_FontAsset dialogueFont;

    private Canvas _cachedCanvas;

#if ENABLE_INPUT_SYSTEM
    private InputAction _interactAction;

    private void OnEnable()
    {
        _interactAction = new InputAction("Interact", binding: "<Keyboard>/e");
        _interactAction.Enable();
    }

    private void OnDisable()
    {
        _interactAction?.Disable();
    }
#endif

    private void Awake()
    {
        // Mark this controller as persistent across scenes
        DontDestroyOnLoad(gameObject);
        Debug.Log("[UI] DialogueUIController marked as persistent across scenes");

        // Find DialoguePanel in UI_Canvas
        Canvas[] allCanvases = FindObjectsByType<Canvas>();
        foreach (Canvas c in allCanvases)
        {
            if (c.gameObject.name == "UI_Canvas")
            {
                _cachedCanvas = c;

                Transform dialoguePanelT = FindPanelRecursive(c.transform, "DialoguePanel");
                if (dialoguePanelT != null)
                {
                    dialoguePanel = dialoguePanelT.GetComponent<CanvasGroup>();
                    dialogueText = dialoguePanelT.Find("Text")?.GetComponent<TextMeshProUGUI>();
                    npcNameText = dialoguePanelT.Find("NPCName")?.GetComponent<TextMeshProUGUI>();
                    Debug.Log("[UI] DialoguePanel found and assigned");
                }
                break;
            }
        }
    }

    private Transform FindPanelRecursive(Transform parent, string panelName)
    {
        if (parent.name == panelName)
            return parent;

        foreach (Transform child in parent)
        {
            Transform result = FindPanelRecursive(child, panelName);
            if (result != null)
                return result;
        }
        return null;
    }

    private void Start()
    {
        if (dialoguePanel != null)
        {
            dialoguePanel.alpha = 0f;
            dialoguePanel.blocksRaycasts = false;
            dialoguePanel.interactable = false;
            Debug.Log("[UI] DialoguePanel initialized (hidden)");
        }
    }

    private void Update()
    {
        // FORCE canvas to stay active if it got deactivated
        if (_cachedCanvas != null && !_cachedCanvas.gameObject.activeSelf)
        {
            _cachedCanvas.gameObject.SetActive(true);
            Debug.LogWarning("[UI] Canvas GameObject was deactivated - re-activating it!");
        }

        // Also ensure Canvas component is enabled (DialogueManager disables it)
        if (_cachedCanvas != null && !_cachedCanvas.enabled)
        {
            _cachedCanvas.enabled = true;
            Debug.LogWarning("[UI] Canvas component was disabled - re-enabling it!");
        }

        // E key handling is now done by PlayerController2D5.HandleInteraction()
        // This was a duplicate handler - removed to avoid conflicts

        // Keep this section commented for reference:
        // #if ENABLE_INPUT_SYSTEM
        // if (_interactAction != null && _interactAction.WasPressedThisFrame())
        //     ePressed = true;
        // var keyboard = Keyboard.current;
        // if (keyboard != null && keyboard.eKey.wasPressedThisFrame)
        //     ePressed = true;
        // #endif

        // if (ePressed)
        //     TryInteract();
    }

    private void TryInteract()
    {
        Debug.Log("[UI] E Pressed - This is now handled by PlayerController2D5.HandleInteraction()");
        // E key interaction is handled by PlayerController2D5 which calls Interact() on IInteractable objects
    }

    /// <summary>
    /// Show dialogue from NPC (called by DialogueManager or NPC)
    /// </summary>
    public void ShowDialogue(string npcName, string text)
    {
        if (dialoguePanel == null)
        {
            Debug.LogError("[UI] DialoguePanel not assigned!");
            return;
        }

        if (npcNameText != null) npcNameText.text = npcName;
        if (dialogueText != null) dialogueText.text = text;

        // CRITICAL: Must activate the gameObject AND set alpha for visibility
        dialoguePanel.gameObject.SetActive(true);
        dialoguePanel.alpha = 1f;
        dialoguePanel.blocksRaycasts = true;
        dialoguePanel.interactable = true;
        Debug.Log($"[UI] Showing dialogue from {npcName}");
    }

    /// <summary>
    /// Hide dialogue panel
    /// </summary>
    public void HideDialogue()
    {
        if (dialoguePanel == null) return;

        dialoguePanel.gameObject.SetActive(false);
        dialoguePanel.alpha = 0f;
        dialoguePanel.blocksRaycasts = false;
        dialoguePanel.interactable = false;
        Debug.Log("[UI] Dialogue hidden");
    }

    // ======= NOTIFICATION/SYSTEM EVENT METHODS (for other systems to call) =======

    /// <summary>
    /// Show/hide interaction prompt (called by NPCInteraction, NPCs, etc.)
    /// </summary>
    public void SetNotificationActive(string text, bool active)
    {
        // TODO: Wire to actual notification/prompt UI
        Debug.Log($"[UI] Notification: {text} (Active: {active})");
    }

    /// <summary>
    /// Trigger system events (called by DialogueManager)
    /// Examples: give_device, diary_update, codex_entry_unlock, etc.
    /// </summary>
    public void TriggerSystemEvent(string eventName)
    {
        switch (eventName)
        {
            case "give_device":
                Debug.Log("[UI] EVENT: Player received codex device!");
                // Unlock codex in CodexController
                var codexController = FindAnyObjectByType<CodexController>();
                if (codexController != null)
                {
                    codexController.UnlockCodex();
                    Debug.Log("[UI] CodexController.UnlockCodex() called");
                }
                else
                {
                    Debug.LogWarning("[UI] CodexController not found in scene!");
                }
                break;
            case "diary_update":
                Debug.Log("[UI] EVENT: Diary has been updated");
                break;
            case "codex_entry_unlock":
                Debug.Log("[UI] EVENT: Codex entry unlocked");
                break;
            case "truth_echo_unlock":
                Debug.Log("[UI] EVENT: Truth Echo unlocked in Codex");
                break;
            case "story_scroll_acquire":
                Debug.Log("[UI] EVENT: Story Scroll acquired");
                break;
            case "encounter_complete":
                Debug.Log("[UI] EVENT: Encounter complete");
                break;
            default:
                Debug.Log($"[UI] EVENT: {eventName}");
                break;
        }
    }
}

