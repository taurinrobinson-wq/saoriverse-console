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

    [Header("Sound Effects")]
    [SerializeField] private AudioClip doorOpenSoundEffect;
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
            Debug.Log($"[Triglyph Puzzle] Deselected {glyphUI.glyphData.glyphName}");
        }
        else
        {
            // Limit to 3 selections
            if (selectedGlyphs.Count < RequiredGlyphCount)
            {
                selectedGlyphs.Add(glyphUI);
                glyphUI.Select();
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

        // IMMEDIATELY DISABLE CODEX CANVAS to prevent it from re-enabling during animation
        if (codexPanel != null)
        {
            Canvas codexCanvas = codexPanel.GetComponent<Canvas>();
            if (codexCanvas != null)
            {
                codexCanvas.enabled = false;
                Debug.Log("[Triglyph Puzzle] Codex Canvas disabled to prevent re-enabling");
            }
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

        // FADE OUT THE CODEX PANEL smoothly (not instant)
        yield return StartCoroutine(FadeOutPanel(codexPanel, panelFadeDuration));

        Debug.Log("[Triglyph Puzzle] Panels hidden");

        // Activate scene transition collider
        Debug.Log("[Triglyph Puzzle] Attempting to activate scene transition collider...");
        Debug.Log($"[Triglyph Puzzle] sceneTransitionCollider reference status: {(sceneTransitionCollider != null ? "NOT NULL" : "NULL")}");

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
            else
            {
                Debug.Log("[Triglyph Puzzle] ProximityTransitionZone not found, trying to find SceneCollider GameObject...");
                // Try to find by GameObject name
                GameObject sceneColliderGO = GameObject.Find("SceneCollider");
                if (sceneColliderGO != null)
                {
                    sceneTransitionCollider = sceneColliderGO.GetComponent<Collider>();
                    Debug.Log($"[Triglyph Puzzle] Found SceneCollider GameObject, collider retrieved: {(sceneTransitionCollider != null ? "SUCCESS" : "FAILED")}");
                }
                else
                {
                    Debug.LogError("[Triglyph Puzzle] Could not find SceneCollider GameObject!");
                }
            }
        }

        if (sceneTransitionCollider != null)
        {
            Debug.Log($"[Triglyph Puzzle] Enabling collider. Current state: {sceneTransitionCollider.enabled}");
            sceneTransitionCollider.enabled = true;
            Debug.Log($"[Triglyph Puzzle] ✅ Scene transition collider ACTIVATED. New state: {sceneTransitionCollider.enabled}");
        }
        else
        {
            Debug.LogError("[Triglyph Puzzle] ⚠️ FAILED TO FIND COLLIDER! Cannot enable transition zone.");
        }

        puzzleCompleted = true;
        sequenceInProgress = false; // ← UNLOCK: Sequence complete, CodexController can update again
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
