using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using Velinor.Core;

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
    public string currentActiveSpeaker = "Player";  // Track who is speaking for UI logic

#if ENABLE_INPUT_SYSTEM
    private InputAction _interactAction;

    private void OnEnable()
    {
        _interactAction = new InputAction("Interact", binding: "<Keyboard>/g");
        _interactAction.Enable();
    }

    private void OnDisable()
    {
        _interactAction?.Disable();
    }
#endif

    /// <summary>
    /// Check if CodexController has active glyphs that need clicking
    /// </summary>
    private bool IsCodexActive()
    {
        var codexController = FindAnyObjectByType<CodexController>();
        if (codexController == null) return false;

        // Check if codex panel is visible and interactable
        return codexController.codexPanel != null &&
               codexController.codexPanel.alpha > 0.5f &&
               codexController.codexPanel.interactable;
    }

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
                    // Look for NPCDialogueText, then fall back to Text
                    dialogueText = dialoguePanelT.Find("NPCDialogueText")?.GetComponent<TextMeshProUGUI>();
                    if (dialogueText == null)
                        dialogueText = dialoguePanelT.Find("Text")?.GetComponent<TextMeshProUGUI>();

                    // Look for NPC name text with multiple variations
                    npcNameText = dialoguePanelT.Find("NPCNameText")?.GetComponent<TextMeshProUGUI>();
                    if (npcNameText == null)
                        npcNameText = dialoguePanelT.Find("NPCName")?.GetComponent<TextMeshProUGUI>();
                    if (npcNameText == null)
                        npcNameText = dialoguePanelT.Find("NPC Name")?.GetComponent<TextMeshProUGUI>();
                    if (npcNameText == null)
                        npcNameText = dialoguePanelT.Find("NpcName")?.GetComponent<TextMeshProUGUI>();
                    if (npcNameText == null)
                    {
                        // Log all children for debugging
                        Debug.LogWarning("[UI] Could not find NPC name text component. DialoguePanel children:");
                        foreach (Transform child in dialoguePanelT)
                        {
                            Debug.LogWarning($"  - {child.name} (TextMeshProUGUI: {child.GetComponent<TextMeshProUGUI>() != null})");
                        }
                    }
                    Debug.Log($"[UI] DialoguePanel found and assigned (dialogueText: {(dialogueText != null ? "✓" : "✗")}, npcNameText: {(npcNameText != null ? "✓" : "✗")})");
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
    /// Clears previous text and starts fresh
    /// </summary>
    public void ShowDialogue(string npcName, string text)
    {
        if (dialoguePanel == null)
        {
            Debug.LogError("[UI] DialoguePanel not assigned!");
            return;
        }

        // For initial dialogue, clear everything
        if (npcNameText != null)
        {
            npcNameText.text = "";
            npcNameText.text = npcName;
            Debug.Log($"[UI] Set NPC name to: {npcName}");
        }
        else
        {
            Debug.LogWarning("[UI] npcNameText is null - cannot set NPC name!");
        }
        if (dialogueText != null)
        {
            dialogueText.text = "";
            dialogueText.text = text;
            dialogueText.ForceMeshUpdate();
            Debug.Log($"[UI] Set dialogue text (length: {text.Length})");
        }

        // Activate the panel
        dialoguePanel.gameObject.SetActive(true);
        dialoguePanel.alpha = 1f;

        // If codex is active, don't block raycasts so glyphs can be clicked
        // Dialogue buttons should still work even with blocksRaycasts = false
        dialoguePanel.blocksRaycasts = !IsCodexActive();

        dialoguePanel.interactable = true;
        Debug.Log($"[UI] Showing dialogue from {npcName} (blocksRaycasts: {dialoguePanel.blocksRaycasts})");
    }

    /// <summary>
    /// Append dialogue text for continuous conversation
    /// Adds to existing text instead of replacing it
    /// </summary>
    public void AppendDialogue(string text)
    {
        if (dialoguePanel == null || dialogueText == null)
            return;

        if (!string.IsNullOrEmpty(text))
        {
            dialogueText.text += text;
            dialogueText.ForceMeshUpdate();
            Debug.Log("[UI] Appended text to dialogue");
        }
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
            case "npc_disappear":
                Debug.Log("[UI] EVENT: NPC exiting stage left");
                ExitNPCStageLeft();
                break;
            default:
                Debug.Log($"[UI] EVENT: {eventName}");
                break;
        }
    }

    /// <summary>
    /// NPC exits stage left: first turns to face left, then walks off-screen
    /// Disables animator and billboard effect to allow proper rotation control
    /// </summary>
    private void ExitNPCStageLeft()
    {
        GameObject npcGameObject = DialogueManager.Instance.GetCurrentNPCGameObject();
        if (npcGameObject == null)
        {
            Debug.LogError("[UI] No NPC GameObject - cannot exit");
            return;
        }

        // Disable the billboard LookAt effect in NPCDialogueDriver (or legacy SaoriNPC)
        NPCDialogueDriver npcDriver = npcGameObject.GetComponent<NPCDialogueDriver>();
        if (npcDriver != null)
        {
            npcDriver.SetExitingState(true);
            Debug.Log("[UI] NPCDialogueDriver billboard effect disabled for exit");
        }
        else
        {
            // Fallback for legacy SaoriNPC if NPCDialogueDriver not found
            SaoriNPC saoriNPC = npcGameObject.GetComponent<SaoriNPC>();
            if (saoriNPC != null)
            {
                saoriNPC.SetExitingState(true);
                Debug.Log("[UI] SaoriNPC billboard effect disabled for exit (legacy)");
            }
        }

        // CRITICAL: Disable animator immediately so it doesn't interfere with our transform changes
        Animator npcAnimator = npcGameObject.GetComponent<Animator>();
        if (npcAnimator != null)
        {
            npcAnimator.enabled = false;
            Debug.Log("[UI] NPC animator DISABLED to prevent animation interference");
        }

        // Force X rotation to 0
        Transform npcTransform = npcGameObject.transform;
        Vector3 currentEuler = npcTransform.localEulerAngles;
        currentEuler.x = 0f;
        npcTransform.localEulerAngles = currentEuler;
        Debug.Log($"[UI] NPC localRotation.x set to 0");
        StartCoroutine(ExitNPCStageLeftSequence(npcGameObject));
    }

    /// <summary>
    /// Exit sequence: turn left (0.8s), then walk off screen (2.5s)
    /// Animator is already disabled, so we just move the transform
    /// </summary>
    private System.Collections.IEnumerator ExitNPCStageLeftSequence(GameObject npcGameObject)
    {
        Transform transform = npcGameObject.transform;
        Vector3 startPosition = transform.position;
        Vector3 startEuler = transform.localEulerAngles;

        // Phase 1: Rotation to face left (0.8 seconds)
        Debug.Log("[UI] Phase 1: Turning to face left");

        float turnDuration = 0.8f;
        float elapsed = 0f;

        while (elapsed < turnDuration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / turnDuration;
            float easeT = 1f - Mathf.Pow(1f - t, 2f); // Ease-out

            Vector3 currentEuler = transform.localEulerAngles;
            currentEuler.y = Mathf.Lerp(startEuler.y, 270f, easeT);
            currentEuler.x = 0f; // Force X to 0 every frame
            transform.localEulerAngles = currentEuler;

            yield return null;
        }

        // Ensure final rotation (X must be exactly 0)
        Vector3 finalEuler = transform.localEulerAngles;
        finalEuler.y = 270f;
        finalEuler.x = 0f;
        transform.localEulerAngles = finalEuler;

        Debug.Log($"[UI] Turn complete - final rotation: {transform.localEulerAngles}");

        // Phase 2: Walk off screen (2.5 seconds)
        Debug.Log("[UI] Phase 2: Walking off screen");

        float walkDuration = 2.5f;
        elapsed = 0f;
        Vector3 targetPosition = startPosition;
        targetPosition.x = -10f;

        while (elapsed < walkDuration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / walkDuration;

            // Linear movement during walk
            transform.position = Vector3.Lerp(startPosition, targetPosition, t);

            // Keep X rotation at 0 throughout walk
            Vector3 currentEuler = transform.localEulerAngles;
            currentEuler.x = 0f;
            transform.localEulerAngles = currentEuler;

            yield return null;
        }

        // Ensure final position and rotation
        transform.position = targetPosition;
        finalEuler = transform.localEulerAngles;
        finalEuler.x = 0f;
        transform.localEulerAngles = finalEuler;

        Debug.Log("[UI] NPC walk complete - disabling renderers");
        // Disable all renderers
        SkinnedMeshRenderer[] skinnedMeshRenderers = npcGameObject.GetComponentsInChildren<SkinnedMeshRenderer>();
        foreach (var smr in skinnedMeshRenderers)
        {
            smr.enabled = false;
        }

        Debug.Log("[UI] NPC has left the scene");
    }


}

