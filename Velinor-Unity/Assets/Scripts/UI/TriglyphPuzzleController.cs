using UnityEngine;
using TMPro;
using System.Collections.Generic;
using Velinor.Core;

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
    [SerializeField] private TextMeshProUGUI puzzlePromptText;

    [Header("Triglyph Slots")]
    [SerializeField] private TriglyphSlot[] triglyphSlots = new TriglyphSlot[3];

    [Header("Door Animation")]
    [SerializeField] private Vector3 doorOpenPosition = new Vector3(0, 5, 0);
    [SerializeField] private float doorOpenSpeed = 2f;

    private List<GlyphUI> selectedGlyphs = new List<GlyphUI>();
    private const int RequiredGlyphCount = 3;
    private bool puzzleCompleted = false;

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

    private void Start()
    {
        // Hide prompt initially
        if (puzzlePromptText != null)
            puzzlePromptText.text = "";

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
            Debug.Log($"[Triglyph Puzzle] Deselected {glyphUI.GlyphData.glyphName}");
        }
        else
        {
            // Limit to 3 selections
            if (selectedGlyphs.Count < RequiredGlyphCount)
            {
                selectedGlyphs.Add(glyphUI);
                glyphUI.Select();
                Debug.Log($"[Triglyph Puzzle] Selected {glyphUI.GlyphData.glyphName} ({selectedGlyphs.Count}/{RequiredGlyphCount})");
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
    /// Update the "Press E to add to panel" prompt
    /// </summary>
    private void UpdatePrompt()
    {
        if (puzzlePromptText == null) return;

        if (selectedGlyphs.Count == RequiredGlyphCount)
        {
            puzzlePromptText.text = "Press E to add selected glyphs to panel";
            puzzlePromptText.color = new Color(1, 1, 0, 1); // Yellow
        }
        else
        {
            puzzlePromptText.text = $"Select glyphs: {selectedGlyphs.Count}/{RequiredGlyphCount}";
            puzzlePromptText.color = new Color(1, 1, 1, 1); // White
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
                Debug.Log($"[Triglyph Puzzle] Placed {selectedGlyphs[i].GlyphData.glyphName} in slot {i}");
            }
        }

        // Hide prompt
        if (puzzlePromptText != null)
            puzzlePromptText.text = "";

        // Trigger the door sequence
        StartCoroutine(TriggerDoorSequence());
    }

    /// <summary>
    /// Sequence: Hide panels -> Update overlays -> Open door
    /// </summary>
    private System.Collections.IEnumerator TriggerDoorSequence()
    {
        Debug.Log("[Triglyph Puzzle] Starting door sequence...");

        // Disable Codex and Triglyph panels
        if (codexPanel != null) codexPanel.SetActive(false);
        if (triglyphPanel != null) triglyphPanel.SetActive(false);

        yield return new WaitForSeconds(0.5f);

        // Swap overlays
        if (mountainOverlay_Sealed != null) mountainOverlay_Sealed.SetActive(false);
        if (mountainOverlay_Unsealed != null) mountainOverlay_Unsealed.SetActive(true);

        Debug.Log("[Triglyph Puzzle] Mountain unsealed, opening door...");

        // Animate door opening
        yield return StartCoroutine(AnimateDoor());

        puzzleCompleted = true;
        Debug.Log("[Triglyph Puzzle] ✅ Puzzle completed! Player can now transition to next scene.");
    }

    /// <summary>
    /// Animate door lifting upward
    /// </summary>
    private System.Collections.IEnumerator AnimateDoor()
    {
        if (doorSprite == null) yield break;

        Vector3 startPosition = doorSprite.position;
        float elapsedTime = 0f;
        float duration = Vector3.Distance(startPosition, doorOpenPosition) / doorOpenSpeed;

        while (elapsedTime < duration)
        {
            elapsedTime += Time.deltaTime;
            float t = Mathf.Clamp01(elapsedTime / duration);
            doorSprite.position = Vector3.Lerp(startPosition, doorOpenPosition, t);
            yield return null;
        }

        doorSprite.position = doorOpenPosition;
        Debug.Log("[Triglyph Puzzle] Door fully opened");
    }

    /// <summary>
    /// Get whether puzzle is completed
    /// </summary>
    public bool IsPuzzleCompleted()
    {
        return puzzleCompleted;
    }
}
