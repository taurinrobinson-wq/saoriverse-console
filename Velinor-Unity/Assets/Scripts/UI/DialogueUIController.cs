using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

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
                Debug.Log("[UI] EVENT: NPC fading out");
                FadeOutNPC();
                break;
            default:
                Debug.Log($"[UI] EVENT: {eventName}");
                break;
        }
    }

    /// <summary>
    /// Fade out the NPC character sprite/renderer over time (for narrative departures)
    /// Searches the scene for the NPC's SpriteRenderer component and fades it
    /// </summary>
    private void FadeOutNPC()
    {
        Debug.Log("[UI] FadeOutNPC() called - searching for NPC renderer to fade out");

        List<SkinnedMeshRenderer> skinnedMeshRenderers = new List<SkinnedMeshRenderer>();
        SpriteRenderer spriteRenderer = null;
        GameObject npcGameObject = DialogueManager.Instance.GetCurrentNPCGameObject();

        // If we have the NPC GameObject reference, search within it
        if (npcGameObject != null)
        {
            Debug.Log($"[UI] Searching for renderers within NPC: {npcGameObject.name}");

            // Priority 1: Collect ALL SkinnedMeshRenderers (3D rigged characters often have multiple parts)
            var allSkinnedMeshRenderers = npcGameObject.GetComponentsInChildren<SkinnedMeshRenderer>();
            foreach (var smr in allSkinnedMeshRenderers)
            {
                string name = smr.gameObject.name.ToLower();
                if (!name.Contains("background") && !name.Contains("effect") && !name.Contains("particle"))
                {
                    skinnedMeshRenderers.Add(smr);
                    Debug.Log($"[UI] Found NPC SkinnedMeshRenderer in hierarchy: {smr.gameObject.name}");
                }
            }

            // Fallback: Look for SpriteRenderer if no SkinnedMeshRenderers found
            if (skinnedMeshRenderers.Count == 0)
            {
                var spriteRenderersInNPC = npcGameObject.GetComponentsInChildren<SpriteRenderer>();
                foreach (var sr in spriteRenderersInNPC)
                {
                    string name = sr.gameObject.name.ToLower();
                    if (!name.Contains("background") && !name.Contains("effect") && !name.Contains("particle"))
                    {
                        spriteRenderer = sr;
                        Debug.Log($"[UI] Found NPC SpriteRenderer in hierarchy: {sr.gameObject.name}");
                        break;
                    }
                }
            }
        }

        // If found SkinnedMeshRenderers, fade them all out
        if (skinnedMeshRenderers.Count > 0)
        {
            Debug.Log($"[UI] Starting fade-out for {skinnedMeshRenderers.Count} SkinnedMeshRenderer(s)");
            StartCoroutine(FadeOutMultipleSkinnedMeshCoroutine(skinnedMeshRenderers, 1.5f));
        }
        // Otherwise try SpriteRenderer
        else if (spriteRenderer != null)
        {
            Debug.Log($"[UI] Starting SpriteRenderer fade-out for {spriteRenderer.gameObject.name}");
            StartCoroutine(FadeOutSpriteCoroutine(spriteRenderer, 1.5f));
        }
        else
        {
            Debug.LogWarning("[UI] NPC renderer not found. Ensure the NPC has a SkinnedMeshRenderer or SpriteRenderer component.");
        }
    }

    /// <summary>
    /// Coroutine to fade out a SkinnedMeshRenderer's material alpha over specified duration
    /// </summary>
    private System.Collections.IEnumerator FadeOutSkinnedMeshCoroutine(SkinnedMeshRenderer skinnedMeshRenderer, float duration)
    {
        float elapsed = 0f;
        Material materialInstance = new Material(skinnedMeshRenderer.material);
        skinnedMeshRenderer.material = materialInstance;
        Color startColor = materialInstance.color;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float alpha = Mathf.Lerp(1f, 0f, elapsed / duration);
            Color newColor = startColor;
            newColor.a = alpha;
            materialInstance.color = newColor;
            yield return null;
        }

        // Ensure alpha is exactly 0 at end
        Color finalColor = startColor;
        finalColor.a = 0f;
        materialInstance.color = finalColor;
        Debug.Log("[UI] NPC SkinnedMeshRenderer fade-out complete");
    }

    /// <summary>
    /// Coroutine to fade out multiple SkinnedMeshRenderers' material alpha over specified duration
    /// </summary>
    private System.Collections.IEnumerator FadeOutMultipleSkinnedMeshCoroutine(List<SkinnedMeshRenderer> skinnedMeshRenderers, float duration)
    {
        // Create material instances for each renderer
        List<Material> materialInstances = new List<Material>();
        List<Color> startColors = new List<Color>();

        foreach (var smr in skinnedMeshRenderers)
        {
            Material materialInstance = new Material(smr.material);
            smr.material = materialInstance;
            materialInstances.Add(materialInstance);
            startColors.Add(materialInstance.color);
        }

        float elapsed = 0f;
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float alpha = Mathf.Lerp(1f, 0f, elapsed / duration);

            // Update all materials in parallel
            for (int i = 0; i < materialInstances.Count; i++)
            {
                Color newColor = startColors[i];
                newColor.a = alpha;
                materialInstances[i].color = newColor;
            }
            yield return null;
        }

        // Ensure alpha is exactly 0 at end for all materials
        for (int i = 0; i < materialInstances.Count; i++)
        {
            Color finalColor = startColors[i];
            finalColor.a = 0f;
            materialInstances[i].color = finalColor;
        }
        Debug.Log("[UI] NPC SkinnedMeshRenderer fade-out complete");
    }

    /// <summary>
    /// Coroutine to fade out a SpriteRenderer's alpha over specified duration
    /// </summary>
    private System.Collections.IEnumerator FadeOutSpriteCoroutine(SpriteRenderer spriteRenderer, float duration)
    {
        float elapsed = 0f;
        Color startColor = spriteRenderer.color;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float alpha = Mathf.Lerp(1f, 0f, elapsed / duration);
            Color newColor = startColor;
            newColor.a = alpha;
            spriteRenderer.color = newColor;
            yield return null;
        }

        // Ensure alpha is exactly 0 at end
        Color finalColor = startColor;
        finalColor.a = 0f;
        spriteRenderer.color = finalColor;
        Debug.Log("[UI] NPC sprite fade-out complete");
    }
}

