using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Linq;
using Velinor.Core;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Handles ONLY Codex UI (Glyph system)
/// Triggered by: C key + player has received codex from Saori
/// Independent from DialogueUIController and DiaryController
/// 
/// Features:
/// - Display glyphs in a 9-slot grid
/// - Dynamic glyph population and removal
/// - Glyph selection for triglyph panel placement
/// </summary>
public class CodexController : MonoBehaviour
{
    [Header("Codex Panel")]
    public CanvasGroup codexPanel;
    public Transform viewport;
    public Sprite codexBackgroundSprite;

    [Header("Navigation")]
    public TextMeshProUGUI glyphNameText;
    public Button nextPageBtn;
    public Button prevPageBtn;

    [Header("Fonts")]
    public TMP_FontAsset codexFont;

    [Header("Codex Access")]
    public bool requiresCodexDevice = true;
    private bool playerHasCodex = false;

    [Header("Glyph Management")]
    [SerializeField] private GameObject glyphUIPrefab;
    [SerializeField] private List<GlyphSlot> allSlots = new List<GlyphSlot>();  // All 18 slots globally numbered (0-17)

    private List<GlyphUI> activeGlyphs = new List<GlyphUI>();
    private GlyphUI selectedGlyph;
    private GlyphSlot selectedSlot;  // Track which slot is visually highlighted

    private int _currentCodexPage = 0;
    private const int SlotsPerPage = 9;

#if ENABLE_INPUT_SYSTEM
    private InputAction _toggleCodexAction;

    private void OnEnable()
    {
        _toggleCodexAction = new InputAction("ToggleCodex", binding: "<Keyboard>/c");
        _toggleCodexAction.Enable();
    }

    private void OnDisable()
    {
        _toggleCodexAction?.Disable();
    }
#endif

    private Canvas _cachedCanvas;
    private TriglyphPuzzleController _triglyphController; // ← Cache to avoid FindAnyObjectByType every frame

    private void Awake()
    {
        // Mark this controller as persistent across scenes
        DontDestroyOnLoad(gameObject);
        Debug.Log("[Codex] CodexController marked as persistent across scenes");

        // Find CodexPanel in UI_Canvas
        Canvas[] allCanvases = FindObjectsByType<Canvas>();
        foreach (Canvas c in allCanvases)
        {
            if (c.gameObject.name == "UI_Canvas")
            {
                _cachedCanvas = c;

                Transform codexPanelT = FindPanelRecursive(c.transform, "CodexPanel");
                if (codexPanelT != null)
                {
                    codexPanel = codexPanelT.GetComponent<CanvasGroup>();
                    viewport = codexPanelT.Find("Viewport");
                    glyphNameText = codexPanelT.Find("Navigation/GlyphName")?.GetComponent<TextMeshProUGUI>();
                    nextPageBtn = codexPanelT.Find("Navigation/NextBtn")?.GetComponent<Button>();
                    prevPageBtn = codexPanelT.Find("Navigation/PrevBtn")?.GetComponent<Button>();

                    Debug.Log("[Codex] CodexPanel found and assigned");
                }
                break;
            }
        }

        if (nextPageBtn != null) nextPageBtn.onClick.AddListener(NextPage);
        if (prevPageBtn != null) prevPageBtn.onClick.AddListener(PrevPage);

        // Cache TriglyphPuzzleController to check sequence status without FindAnyObjectByType every frame
        _triglyphController = FindAnyObjectByType<TriglyphPuzzleController>();
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
        // Check canvas status at Start
        if (_cachedCanvas != null)
        {
            Debug.Log($"[Codex] Canvas status at Start: Active={_cachedCanvas.gameObject.activeSelf}, Enabled={_cachedCanvas.enabled}");
            if (!_cachedCanvas.gameObject.activeSelf)
            {
                _cachedCanvas.gameObject.SetActive(true);
                Debug.LogWarning("[Codex] Canvas was inactive at Start - re-activating it!");
            }
        }

        if (codexPanel != null)
        {
            codexPanel.alpha = 0f;
            codexPanel.blocksRaycasts = false;
            codexPanel.interactable = false;
            Debug.Log("[Codex] CodexPanel initialized (hidden)");
        }

        // For testing: allow access if not requiring device
        if (!requiresCodexDevice)
        {
            playerHasCodex = true;
            Debug.Log("[Codex] TEST MODE: Codex access enabled (no device required)");
        }
    }

    private void Update()
    {
        // ← SKIP if puzzle sequence is running (let TriggerDoorSequence control the panels)
        if (_triglyphController != null && _triglyphController.IsSequenceInProgress)
        {
            return; // Don't interfere during sequence
        }

        // FORCE canvas to stay active if it got deactivated
        if (_cachedCanvas != null && !_cachedCanvas.gameObject.activeSelf)
        {
            _cachedCanvas.gameObject.SetActive(true);
            Debug.LogWarning("[Codex] Canvas GameObject was deactivated - re-activating it!");
        }

        // Also ensure Canvas component is enabled (DialogueManager disables it)
        if (_cachedCanvas != null && !_cachedCanvas.enabled)
        {
            _cachedCanvas.enabled = true;
            Debug.LogWarning("[Codex] Canvas component was disabled - re-enabling it!");
        }

        bool cPressed = false;

#if ENABLE_INPUT_SYSTEM
        if (_toggleCodexAction != null && _toggleCodexAction.WasPressedThisFrame())
            cPressed = true;

        var keyboard = Keyboard.current;
        if (keyboard != null)
        {
            if (keyboard.cKey.wasPressedThisFrame) cPressed = true;
        }
#endif

        if (cPressed)
        {
            if (playerHasCodex || !requiresCodexDevice)
            {
                ToggleCodex();
            }
            else
            {
                Debug.Log("[Codex] Player does not have codex device yet");
            }
        }

        // Arrow key navigation disabled - only button clicks allowed
        // This ensures UI buttons are the primary interaction method
    }

    public void ToggleCodex()
    {
        if (codexPanel == null)
        {
            Debug.LogError("[Codex] codexPanel is NULL");
            return;
        }

        bool opening = codexPanel.alpha < 0.5f;
        Debug.Log($"[Codex] ToggleCodex: opening={opening}");

        codexPanel.alpha = opening ? 1f : 0f;
        codexPanel.blocksRaycasts = opening;
        codexPanel.interactable = opening;

        // Activate/deactivate viewport
        if (viewport != null)
        {
            viewport.gameObject.SetActive(opening);
            Debug.Log($"[Codex] Viewport set to Active: {opening}");
        }

        if (opening)
        {
            _currentCodexPage = 0;
            UpdateCodexUI();
        }
        else
        {
            // When closing Codex, deselect any selected glyph
            if (selectedSlot != null)
            {
                selectedSlot.Unhighlight();
                selectedSlot = null;
            }
            if (selectedGlyph != null)
            {
                selectedGlyph.Deselect();
                selectedGlyph = null;
            }
        }

        Debug.Log($"[Codex] Codex panel now {(opening ? "OPEN" : "CLOSED")}");
    }

    public void NextPage()
    {
        int maxPages = Mathf.CeilToInt((float)allSlots.Count / SlotsPerPage);
        if (_currentCodexPage < maxPages - 1)
        {
            _currentCodexPage++;
            UpdateCodexUI();
        }
    }

    public void PrevPage()
    {
        if (_currentCodexPage > 0)
        {
            _currentCodexPage--;
            UpdateCodexUI();
        }
    }

    private void UpdateCodexUI()
    {
        if (codexPanel == null) return;

        if (glyphNameText != null)
        {
            int totalPages = Mathf.CeilToInt((float)allSlots.Count / SlotsPerPage);
            glyphNameText.text = $"Codex - Page {_currentCodexPage + 1} of {totalPages}";
        }

        // Look for pagination grids: GlyphGrid_Pg1, GlyphGrid_Pg2, etc.
        string gridName = $"GlyphGrid_Pg{_currentCodexPage + 1}";
        Transform gridT = codexPanel.transform.Find(gridName);

        if (gridT == null)
        {
            // Fallback: try to find just "GlyphGrid" (non-paginated layout)
            gridT = codexPanel.transform.Find("GlyphGrid");
        }

        if (gridT != null)
        {
            Debug.Log($"[Codex] {gridName} found with {gridT.childCount} children (slots)");

            // Update the grid to display the GlyphSlot components
            // The slots already contain the collected glyphs via SetGlyph()
            for (int i = 0; i < gridT.childCount; i++)
            {
                Transform slotTransform = gridT.GetChild(i);
                GlyphSlot glyphSlot = slotTransform.GetComponent<GlyphSlot>();

                if (glyphSlot != null)
                {
                    // The GlyphSlot already manages its own display
                    // Just ensure it's visible
                    slotTransform.gameObject.SetActive(true);
                    Debug.Log($"[Codex]   Slot_{i}: Active, Filled={glyphSlot.isFilled}");
                }
            }
        }
        else
        {
            Debug.LogWarning($"[Codex] {gridName} not found! Check CodexPanel hierarchy for GlyphGrid_Pg1, GlyphGrid_Pg2, etc.");
        }
    }

    /// <summary>
    /// Call this when player encounters Saori and receives codex device
    /// </summary>
    public void UnlockCodex()
    {
        playerHasCodex = true;
        Debug.Log("[Codex] Codex unlocked! Player can now press C to open Codex");
    }

    /// <summary>
    /// Add a new glyph/entry to codex
    /// </summary>
    public void AddCodexEntry(string entryName)
    {
        Debug.Log($"[Codex] New entry unlocked: {entryName}");
        // TODO: Wire to actual codex data system
    }

    #region === GLYPH MANAGEMENT ===

    /// <summary>
    /// Add a glyph to the active glyphs list and assign it to the next available slot.
    /// </summary>
    public void AddGlyph(GlyphData data)
    {
        if (data == null)
        {
            Debug.LogError("[Codex] Cannot add null glyph data!");
            return;
        }

        // Check if glyph already exists
        if (activeGlyphs.Any(g => g.glyphData == data))
        {
            Debug.LogWarning($"[Codex] Glyph {data.glyphName} already in active list!");
            return;
        }

        // Create GlyphUI instance (inactive - will be displayed via GlyphSlot)
        if (glyphUIPrefab == null)
        {
            Debug.LogError("[Codex] glyphUIPrefab is not assigned!");
            return;
        }

        // Instantiate as child of codex panel but inactive
        Transform parentTransform = codexPanel != null ? codexPanel.transform : null;
        GameObject glyphUIPrefabInstance = Instantiate(glyphUIPrefab, parentTransform);
        glyphUIPrefabInstance.SetActive(false);
        GlyphUI glyphUI = glyphUIPrefabInstance.GetComponent<GlyphUI>();

        if (glyphUI == null)
        {
            Debug.LogError("[Codex] Instantiated prefab does not have GlyphUI component!");
            Destroy(glyphUIPrefabInstance);
            return;
        }

        glyphUI.Initialize(data);
        activeGlyphs.Add(glyphUI);

        // Assign to next available slot
        AssignGlyphToNextAvailableSlot(glyphUI);

        Debug.Log($"[Codex] Added glyph: {data.glyphName}");
    }

    /// <summary>
    /// Remove a glyph from the active glyphs list and clear it from all slots.
    /// </summary>
    public void RemoveGlyph(GlyphData data)
    {
        if (data == null)
        {
            Debug.LogError("[Codex] Cannot remove null glyph data!");
            return;
        }

        GlyphUI glyphToRemove = activeGlyphs.FirstOrDefault(g => g.glyphData == data);
        if (glyphToRemove == null)
        {
            Debug.LogWarning($"[Codex] Glyph {data.glyphName} not found in active list!");
            return;
        }

        activeGlyphs.Remove(glyphToRemove);
        ClearGlyphFromSlots(data);
        Destroy(glyphToRemove.gameObject);

        Debug.Log($"[Codex] Removed glyph: {data.glyphName}");
    }

    /// <summary>
    /// Assign a glyph to the next available slot in global sequence (0-17).
    /// </summary>
    private void AssignGlyphToNextAvailableSlot(GlyphUI glyph)
    {
        if (glyph == null) return;

        Debug.Log($"[Codex] Looking for slot... Total slots: {allSlots.Count}");

        // Iterate through all slots in global order
        foreach (var slot in allSlots)
        {
            if (slot != null && !slot.isFilled)
            {
                slot.SetGlyph(glyph);
                Debug.Log($"[Codex] Assigned {glyph.glyphData.glyphName} to next available slot");
                return;
            }
        }

        Debug.LogWarning($"[Codex] No available slots for {glyph.glyphData.glyphName}!");
    }

    /// <summary>
    /// Clear a glyph from all slots where it appears.
    /// </summary>
    private void ClearGlyphFromSlots(GlyphData data)
    {
        // Clear from all slots
        foreach (var slot in allSlots)
        {
            if (slot != null && slot.glyphUI != null && slot.glyphUI.glyphData == data)
            {
                slot.Clear();
            }
        }
    }

    /// <summary>
    /// Called when a glyph is selected (usually from a slot button click).
    /// Toggles selection if clicking the same glyph twice.
    /// </summary>
    public void OnGlyphSelected(GlyphUI glyph)
    {
        if (glyph == null) return;

        // Check if clicking the same glyph again (toggle behavior)
        if (selectedGlyph == glyph)
        {
            Debug.Log($"[Codex] Toggling off glyph: {glyph.glyphData.glyphName}");
            selectedGlyph.Deselect();
            selectedGlyph = null;

            if (selectedSlot != null)
            {
                selectedSlot.Unhighlight();
                selectedSlot = null;
            }

            if (glyphNameText != null)
            {
                glyphNameText.text = "Codex";
            }

            // Notify puzzle controller of deselection
            NotifyPuzzleController(null);
            return;
        }

        // Deselect previous glyph and unhighlight its slot
        if (selectedGlyph != null)
        {
            Debug.Log($"[Codex] Deselecting previous glyph: {selectedGlyph.glyphData.glyphName}");
            selectedGlyph.Deselect();
        }

        if (selectedSlot != null)
        {
            Debug.Log($"[Codex] Unhighlighting previous slot: {selectedSlot.gameObject.name}");
            selectedSlot.Unhighlight();
        }

        // Select new glyph
        selectedGlyph = glyph;
        selectedGlyph.Select();

        // Find and highlight the slot containing this glyph
        foreach (var slot in allSlots)
        {
            if (slot != null && slot.glyphUI == glyph)
            {
                selectedSlot = slot;
                slot.Highlight();
                Debug.Log($"[Codex] Highlighting slot: {slot.gameObject.name}");
                break;
            }
        }

        // Update the glyph name display
        if (glyphNameText != null)
        {
            glyphNameText.text = glyph.glyphData.glyphName;
        }

        // Notify puzzle controller for puzzle selection tracking
        NotifyPuzzleController(glyph);

        Debug.Log($"[Codex] Glyph selected: {glyph.glyphData.glyphName}");
    }

    /// <summary>
    /// Notify the puzzle controller when a glyph is clicked
    /// This allows the puzzle controller to track selections independently
    /// </summary>
    private void NotifyPuzzleController(GlyphUI glyph)
    {
        TriglyphPuzzleController puzzleController = FindAnyObjectByType<TriglyphPuzzleController>();
        if (puzzleController != null)
        {
            puzzleController.OnGlyphClickedForPuzzle(glyph);
        }
    }

    /// <summary>
    /// Called when a slot is clicked (for potential future interactions).
    /// </summary>
    public void OnSlotClicked(GlyphSlot slot)
    {
        if (slot == null || slot.glyphUI == null) return;

        Debug.Log($"[Codex] Slot clicked with glyph: {slot.glyphUI.glyphData.glyphName}");
        OnGlyphSelected(slot.glyphUI);
    }

    #endregion
}
