using UnityEngine;
using TMPro;
using System.Collections.Generic;
using Velinor.Core;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Manages the Triglyph Puzzle workflow:
/// 1. Player selects 3 glyphs from Codex
/// 2. When all 3 selected, shows "Press E to add to panel" prompt
/// 3. Pressing E copies the 3 glyphs to TriglyphPanel and triggers door sequence
/// </summary>
public class TriglyphPuzzleController : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private CodexController codexController;
    [SerializeField] private GameObject codexPanel;
    [SerializeField] private GameObject triglyphPanel;
    [SerializeField] private GameObject mountainOverlay_Sealed;
    [SerializeField] private GameObject mountainOverlay_Unsealed;
    [SerializeField] private Transform doorSprite;

    [Header("Door Animation")]
    [SerializeField] private Vector2 doorOpenPosition = new Vector2(0f, -100f); // UI RectTransform anchoredPosition target (moves up by 100 pixels)
    [SerializeField] private float doorAnimationDuration = 6f; // 6 seconds for clearly visible movement
    [SerializeField] private float panelFadeDuration = 1f; // Time to fade out codex panel
    [SerializeField] private Collider sceneTransitionCollider;
    [SerializeField] private Collider doorCollider;  // Blocks player until puzzle solved, then deactivates

    [Header("Sound Effects")]
    [SerializeField] private AudioClip doorOpenSoundEffect;
    [SerializeField] private AudioClip selectGlyphSound;
    [SerializeField] private AudioClip deselectGlyphSound;
    [SerializeField] private AudioSource audioSource;

    [Header("Victory Message")]
    [SerializeField] private string victoryMessage = "Glyphs Received. Door Activated";

    [Header("Triglyph Slots")]
    [SerializeField] private TriglyphSlot[] triglyphSlots = new TriglyphSlot[3];

    private List<GlyphUI> selectedGlyphs = new List<GlyphUI>();
    private const int RequiredGlyphCount = 3;
    private bool puzzleCompleted = false;
    private bool sequenceInProgress = false; // ← Prevents CodexController from interfering during sequence

#if ENABLE_INPUT_SYSTEM
    private InputAction _confirmPuzzleAction;

    private void OnEnable()
    {
        _confirmPuzzleAction = new InputAction("ConfirmPuzzle", binding: "<Keyboard>/e");
        _confirmPuzzleAction.Enable();
        _confirmPuzzleAction.performed += OnConfirmPuzzle;

        // Get or create AudioSource for door sound
        if (audioSource == null)
        {
            audioSource = GetComponent<AudioSource>();
            if (audioSource == null)
            {
                audioSource = gameObject.AddComponent<AudioSource>();
                audioSource.playOnAwake = false;
            }
        }
    }

    private void OnDisable()
    {
        if (_confirmPuzzleAction != null)
        {
            _confirmPuzzleAction.performed -= OnConfirmPuzzle;
            _confirmPuzzleAction?.Disable();
        }
    }
#endif

    /// <summary>
    /// Returns true if the victory sequence is actively running.
    /// Used to prevent CodexController from interfering during the sequence.
    /// </summary>
    public bool IsSequenceInProgress => sequenceInProgress;

    private void Start()
    {
        // Start with no prompt displayed
        Debug.Log("[Triglyph Puzzle] Controller initialized");
    }

    private void Update()
    {
        // Fallback for InputManager if not using InputSystem
#if !ENABLE_INPUT_SYSTEM
        if (Input.GetKeyDown(KeyCode.E) && !puzzleCompleted)
        {
            OnConfirmPuzzle(default);
        }
#endif
    }

    /// <summary>
    /// Called when a glyph is clicked in the Codex
    /// Toggles selection state
    /// </summary>
    public void OnGlyphClickedForPuzzle(GlyphUI glyphUI)
    {
        // Handle deselection (null passed from CodexController toggle)
        if (glyphUI == null)
        {
            return;
        }

        if (puzzleCompleted)
        {
            Debug.Log("[Triglyph Puzzle] Puzzle already completed");
            return;
        }

        // Toggle selection
        if (selectedGlyphs.Contains(glyphUI))
        {
            selectedGlyphs.Remove(glyphUI);
            glyphUI.Deselect();
            PlayDeselectSound();
            Debug.Log($"[Triglyph Puzzle] Deselected {glyphUI.glyphData.glyphName}");
        }
        else
        {
            // Limit to 3 selections
            if (selectedGlyphs.Count < RequiredGlyphCount)
            {
                selectedGlyphs.Add(glyphUI);
                glyphUI.Select();
                PlaySelectSound();
                Debug.Log($"[Triglyph Puzzle] Selected {glyphUI.glyphData.glyphName} ({selectedGlyphs.Count}/{RequiredGlyphCount})");
            }
            else
            {
                Debug.Log("[Triglyph Puzzle] Maximum 3 glyphs selected");
            }
        }

        // Update prompt visibility
        UpdatePrompt();
    }

    /// <summary>
    /// Update the "Press E to add to panel" prompt via notification system
    /// </summary>
    private void UpdatePrompt()
    {
        NotificationPanelController notificationPanel = FindAnyObjectByType<NotificationPanelController>();
        if (notificationPanel == null) return;

        if (selectedGlyphs.Count == RequiredGlyphCount)
        {
            notificationPanel.ShowNotification("Press E to add selected glyphs to panel", duration: 10f);
        }
        else if (selectedGlyphs.Count > 0)
        {
            notificationPanel.ShowNotification($"Select glyphs: {selectedGlyphs.Count}/{RequiredGlyphCount}", duration: 3f);
        }
    }

    /// <summary>
    /// Reset the puzzle selection state when triglyph panel is opened.
    /// Clears any previously selected glyphs and deselects their UI.
    /// </summary>
    public void ResetSelection()
    {
        for (int i = selectedGlyphs.Count - 1; i >= 0; i--)
        {
            if (selectedGlyphs[i] != null)
            {
                selectedGlyphs[i].Deselect();
            }
        }
        selectedGlyphs.Clear();
        Debug.Log("[Triglyph Puzzle] Selection reset for new puzzle session");
    }

    /// <summary>
    /// Play sound when glyph is selected
    /// </summary>
    private void PlaySelectSound()
    {
        if (audioSource != null && selectGlyphSound != null)
        {
            audioSource.PlayOneShot(selectGlyphSound);
            Debug.Log("[Triglyph Puzzle] Playing select glyph sound");
        }
        else if (selectGlyphSound == null)
        {
            Debug.LogWarning("[Triglyph Puzzle] Select glyph sound not assigned in Inspector!");
        }
    }

    /// <summary>
    /// Play sound when glyph is deselected
    /// </summary>
    private void PlayDeselectSound()
    {
        if (audioSource != null && deselectGlyphSound != null)
        {
            audioSource.PlayOneShot(deselectGlyphSound);
            Debug.Log("[Triglyph Puzzle] Playing deselect glyph sound");
        }
        else if (deselectGlyphSound == null)
        {
            Debug.LogWarning("[Triglyph Puzzle] Deselect glyph sound not assigned in Inspector!");
        }
    }

    /// <summary>
    /// Confirm puzzle placement (E key)
    /// </summary>
#if ENABLE_INPUT_SYSTEM
    private void OnConfirmPuzzle(InputAction.CallbackContext context)
#else
    private void OnConfirmPuzzle(object context)
#endif
    {
        if (puzzleCompleted || selectedGlyphs.Count != RequiredGlyphCount)
        {
            return;
        }

        Debug.Log("[Triglyph Puzzle] Confirming puzzle placement...");
        PlaceGlyphsOnPanel();
    }

    /// <summary>
    /// Place selected glyphs on TriglyphPanel and trigger sequence
    /// </summary>
    private void PlaceGlyphsOnPanel()
    {
        // Validate we have 3 slots
        if (triglyphSlots.Length != 3)
        {
            Debug.LogError("[Triglyph Puzzle] TriglyphPanel doesn't have exactly 3 slots!");
            return;
        }

        // Place each glyph in corresponding slot
        for (int i = 0; i < selectedGlyphs.Count; i++)
        {
            if (triglyphSlots[i] != null)
            {
                triglyphSlots[i].SetGlyph(selectedGlyphs[i]);
                Debug.Log($"[Triglyph Puzzle] Placed {selectedGlyphs[i].glyphData.glyphName} in slot {i}");
            }
        }

        // Hide prompt
        NotificationPanelController notificationPanel = FindAnyObjectByType<NotificationPanelController>();
        if (notificationPanel != null)
            notificationPanel.ShowNotification("", duration: 0.1f);

        // Trigger the door sequence
        StartCoroutine(TriggerDoorSequence());
    }

    /// <summary>
    /// Sequence: Display victory message -> Hide puzzle panel -> Play sound -> Update overlays -> Open door -> Fade codex panel -> Activate scene collider
    /// (TriglyphPanel hidden at START to unblock view; CodexPanel faded at END after animation completes)
    /// </summary>
    private System.Collections.IEnumerator TriggerDoorSequence()
    {
        sequenceInProgress = true; // ← LOCK: Prevent CodexController from interfering
        Debug.Log("[Triglyph Puzzle] Starting door sequence...");

        // Display victory message
        NotificationPanelController notificationPanel = FindAnyObjectByType<NotificationPanelController>();
        if (notificationPanel != null)
        {
            notificationPanel.ShowNotification(victoryMessage, duration: 5f);
            Debug.Log($"[Triglyph Puzzle] Displayed message: {victoryMessage}");
        }

        // FADE OUT TRIGLYPH PANEL - it blocks the door view
        if (triglyphPanel != null)
        {
            yield return StartCoroutine(FadeOutPanel(triglyphPanel, 0.5f));
            Debug.Log("[Triglyph Puzzle] Triglyph panel faded out");
        }
        else
        {
            Debug.LogWarning("[Triglyph Puzzle] ⚠️ triglyphPanel reference NOT SET in Inspector!");
        }

        // Play door opening sound effect
        if (doorOpenSoundEffect != null && audioSource != null)
        {
            audioSource.PlayOneShot(doorOpenSoundEffect);
            Debug.Log("[Triglyph Puzzle] Playing door opening sound");
        }
        else if (doorOpenSoundEffect != null)
        {
            AudioSource.PlayClipAtPoint(doorOpenSoundEffect, transform.position);
            Debug.Log("[Triglyph Puzzle] Playing door opening sound (via PlayClipAtPoint)");
        }

        yield return new WaitForSeconds(0.5f);

        // Swap overlays
        if (mountainOverlay_Sealed != null) mountainOverlay_Sealed.SetActive(false);
        if (mountainOverlay_Unsealed != null) mountainOverlay_Unsealed.SetActive(true);

        Debug.Log("[Triglyph Puzzle] Mountain unsealed, opening door...");

        // Animate door opening (6 seconds linear movement - now clearly visible)
        yield return StartCoroutine(AnimateDoor());

        // ACTIVATE COLLIDERS BEFORE fading canvas (so coroutine doesn't stop if TriglyphPuzzleController is disabled)
        Debug.Log("[Triglyph Puzzle] ===== ATTEMPTING COLLIDER ACTIVATION =====");
        Debug.Log($"[Triglyph Puzzle] sceneTransitionCollider reference status: {(sceneTransitionCollider != null ? "ASSIGNED" : "NULL - will auto-find")}");
        Debug.Log($"[Triglyph Puzzle] doorCollider reference status: {(doorCollider != null ? "ASSIGNED" : "NULL")}");

        if (sceneTransitionCollider == null)
        {
            Debug.Log("[Triglyph Puzzle] sceneTransitionCollider is null, attempting to find it...");

            // Try to find it via ProximityTransitionZone first
            ProximityTransitionZone transitionZone = FindAnyObjectByType<ProximityTransitionZone>();
            if (transitionZone != null)
            {
                sceneTransitionCollider = transitionZone.GetComponent<Collider>();
                Debug.Log($"[Triglyph Puzzle] Found ProximityTransitionZone, collider retrieved: {(sceneTransitionCollider != null ? "SUCCESS" : "FAILED")}");
            }

            // Try to find by GameObject name
            if (sceneTransitionCollider == null)
            {
                Debug.Log("[Triglyph Puzzle] Trying to find SceneCollider or similar named GameObject...");
                GameObject sceneColliderGO = GameObject.Find("SceneCollider");
                if (sceneColliderGO == null)
                    sceneColliderGO = GameObject.Find("Scene Collider");
                if (sceneColliderGO == null)
                    sceneColliderGO = GameObject.Find("SceneTransition");
                if (sceneColliderGO == null)
                    sceneColliderGO = GameObject.Find("TransitionZone");

                if (sceneColliderGO != null)
                {
                    sceneTransitionCollider = sceneColliderGO.GetComponent<Collider>();
                    Debug.Log($"[Triglyph Puzzle] Found {sceneColliderGO.name}, collider retrieved: {(sceneTransitionCollider != null ? "SUCCESS" : "FAILED")}");
                }
                else
                {
                    Debug.LogWarning("[Triglyph Puzzle] Could not find SceneCollider by name, searching for any disabled collider with 'scene' in parent name...");
                    Collider[] allColliders = FindObjectsByType<Collider>();
                    foreach (Collider col in allColliders)
                    {
                        if (!col.enabled && (col.gameObject.name.ToLower().Contains("scene") || col.transform.parent?.name.ToLower().Contains("scene") == true))
                        {
                            sceneTransitionCollider = col;
                            Debug.Log($"[Triglyph Puzzle] Found disabled collider in '{col.gameObject.name}'");
                            break;
                        }
                    }
                }
            }
        }

        if (sceneTransitionCollider != null)
        {
            Debug.Log($"[Triglyph Puzzle] Scene collider BEFORE: enabled={sceneTransitionCollider.enabled}, isTrigger={sceneTransitionCollider.isTrigger}, name={sceneTransitionCollider.gameObject.name}");
            sceneTransitionCollider.enabled = true;
            Debug.Log($"[Triglyph Puzzle] Scene collider AFTER: enabled={sceneTransitionCollider.enabled}");
            Debug.Log($"[Triglyph Puzzle] ✅ Scene transition collider ACTIVATED. New state: {sceneTransitionCollider.enabled}");
        }
        else
        {
            Debug.LogError("[Triglyph Puzzle] ⚠️ FAILED TO FIND COLLIDER! Check the scene hierarchy for a disabled collider that should trigger scene transition.");
        }

        // Deactivate DoorCollider to allow player to pass through
        if (doorCollider != null)
        {
            Debug.Log($"[Triglyph Puzzle] Door collider BEFORE: enabled={doorCollider.enabled}, isTrigger={doorCollider.isTrigger}, name={doorCollider.gameObject.name}");
            doorCollider.enabled = false;
            Debug.Log($"[Triglyph Puzzle] Door collider AFTER: enabled={doorCollider.enabled}");
            Debug.Log($"[Triglyph Puzzle] ✅ Door collider DEACTIVATED. Player can now pass through.");
        }
        else
        {
            Debug.LogWarning("[Triglyph Puzzle] ⚠️ doorCollider NOT assigned in Inspector! Door will remain blocked.");
        }

        // NOW FADE OUT THE CODEX PANEL smoothly (after colliders are activated)
        Debug.Log("[Triglyph Puzzle] About to start FadeOutPanel coroutine...");
        yield return StartCoroutine(FadeOutPanel(codexPanel, panelFadeDuration));
        Debug.Log("[Triglyph Puzzle] *** FADEOUTPANEL COMPLETED - RESUMING MAIN COROUTINE ***");

        try
        {
            Debug.Log("[Triglyph Puzzle] Panels hidden - NOW unlocking CodexController");

            // UNLOCK CodexController AFTER fade completes (not before!)
            // This prevents CodexController from re-enabling the Codex during the fade-out
            sequenceInProgress = false;
            Debug.Log("[Triglyph Puzzle] sequenceInProgress set to FALSE");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"[Triglyph Puzzle] Exception after FadeOutPanel: {ex.Message}\n{ex.StackTrace}");
            throw;
        }

        puzzleCompleted = true;
        Debug.Log("[Triglyph Puzzle] ✅ Puzzle completed! Player can now transition to next scene.");
    }

    /// <summary>
    /// Animate door lifting upward via UI RectTransform (linear over doorAnimationDuration seconds)
    /// </summary>
    private System.Collections.IEnumerator AnimateDoor()
    {
        if (doorSprite == null) yield break;

        RectTransform doorRect = doorSprite.GetComponent<RectTransform>();
        if (doorRect == null) yield break;

        Vector2 startPosition = doorRect.anchoredPosition;
        float elapsedTime = 0f;

        while (elapsedTime < doorAnimationDuration)
        {
            elapsedTime += Time.deltaTime;
            float t = Mathf.Clamp01(elapsedTime / doorAnimationDuration);
            doorRect.anchoredPosition = Vector2.Lerp(startPosition, doorOpenPosition, t);
            Debug.Log($"[Triglyph Puzzle] Door animating: {doorRect.anchoredPosition} (t={t:F2})");
            yield return null;
        }

        doorRect.anchoredPosition = doorOpenPosition;
        Debug.Log("[Triglyph Puzzle] Door fully opened");
    }

    /// <summary>
    /// Fade out a panel's CanvasGroup alpha over time, then disable it
    /// </summary>
    private System.Collections.IEnumerator FadeOutPanel(GameObject panel, float duration)
    {
        if (panel == null) yield break;

        CanvasGroup canvasGroup = panel.GetComponent<CanvasGroup>();
        if (canvasGroup == null)
        {
            canvasGroup = panel.AddComponent<CanvasGroup>();
        }

        float elapsedTime = 0f;
        while (elapsedTime < duration)
        {
            elapsedTime += Time.deltaTime;
            float t = Mathf.Clamp01(elapsedTime / duration);
            canvasGroup.alpha = Mathf.Lerp(1f, 0f, t);
            yield return null;
        }

        canvasGroup.alpha = 0f;
        panel.SetActive(false);
        Debug.Log($"[Triglyph Puzzle] Panel faded and disabled");
    }

    /// <summary>
    /// Get whether puzzle is completed
    /// </summary>
    public bool IsPuzzleCompleted()
    {
        return puzzleCompleted;
    }
}
