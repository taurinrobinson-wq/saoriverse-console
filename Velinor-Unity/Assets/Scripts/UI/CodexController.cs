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
    public Image codexImage;
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
    [SerializeField] private List<GlyphSlot> slotsPage1 = new List<GlyphSlot>();
    [SerializeField] private List<GlyphSlot> slotsPage2 = new List<GlyphSlot>();

    private List<GlyphUI> activeGlyphs = new List<GlyphUI>();
    private GlyphUI selectedGlyph;

    private int _currentCodexPage = 0;
    private const int GlyphsPerPage = 9;

#if ENABLE_INPUT_SYSTEM
    private InputAction _toggleCodexAction;
    private InputAction _leftAction;
    private InputAction _rightAction;

    private void OnEnable()
    {
        _toggleCodexAction = new InputAction("ToggleCodex", binding: "<Keyboard>/c");
        _leftAction = new InputAction("Left", binding: "<Keyboard>/leftArrow");
        _rightAction = new InputAction("Right", binding: "<Keyboard>/rightArrow");

        _toggleCodexAction.Enable();
        _leftAction.Enable();
        _rightAction.Enable();
    }

    private void OnDisable()
    {
        _toggleCodexAction?.Disable();
        _leftAction?.Disable();
        _rightAction?.Disable();
    }
#endif

    private Canvas _cachedCanvas;

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
                    codexImage = codexPanelT.GetComponent<Image>();
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

        // Assign the codex background sprite if provided
        if (codexImage != null && codexBackgroundSprite != null)
        {
            codexImage.sprite = codexBackgroundSprite;
            codexImage.type = Image.Type.Simple;
            codexImage.preserveAspect = true;
            Debug.Log($"[Codex] Codex background sprite assigned: {codexBackgroundSprite.name}");
            Debug.Log($"[Codex] Image component: enabled={codexImage.enabled}, raycastTarget={codexImage.raycastTarget}");
        }
        else if (codexImage != null && codexBackgroundSprite == null)
        {
            Debug.LogWarning("[Codex] codexBackgroundSprite is not assigned in Inspector!");
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
        bool leftPressed = false;
        bool rightPressed = false;

#if ENABLE_INPUT_SYSTEM
        if (_toggleCodexAction != null && _toggleCodexAction.WasPressedThisFrame())
            cPressed = true;

        if (_leftAction != null && _leftAction.WasPressedThisFrame())
            leftPressed = true;

        if (_rightAction != null && _rightAction.WasPressedThisFrame())
            rightPressed = true;

        var keyboard = Keyboard.current;
        if (keyboard != null)
        {
            if (keyboard.cKey.wasPressedThisFrame) cPressed = true;
            if (keyboard.leftArrowKey.wasPressedThisFrame) leftPressed = true;
            if (keyboard.rightArrowKey.wasPressedThisFrame) rightPressed = true;
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

        if (codexPanel != null && codexPanel.alpha > 0.5f)
        {
            if (leftPressed) PrevPage();
            if (rightPressed) NextPage();
        }
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

        // Set image color to WHITE so sprite shows (not black)
        if (codexImage != null)
        {
            codexImage.color = opening ? new Color(1, 1, 1, 1f) : new Color(1, 1, 1, 0);
            Debug.Log($"[Codex] Image color set to {codexImage.color}");
        }

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

        Debug.Log($"[Codex] Codex panel now {(opening ? "OPEN" : "CLOSED")}");
    }

    public void NextPage()
    {
        _currentCodexPage++;
        UpdateCodexUI();
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

        // Get glyphs from database
        var allGlyphs = GlyphsDatabase.GetAllGlyphs();

        if (glyphNameText != null)
        {
            int totalPages = Mathf.CeilToInt((float)allGlyphs.Count / GlyphsPerPage);
            glyphNameText.text = $"Codex - Page {_currentCodexPage + 1} of {totalPages}";
        }

        // Populate the glyph grid with sprites
        Transform gridT = codexPanel.transform.Find("GlyphGrid");
        if (gridT != null)
        {
            Debug.Log($"[Codex] GlyphGrid found with {gridT.childCount} children (slots)");

            for (int i = 0; i < gridT.childCount; i++)
            {
                Transform slot = gridT.GetChild(i);
                Image slotImage = slot.GetComponent<Image>();

                // Calculate which glyph to show on this page
                int glyphIndex = (_currentCodexPage * GlyphsPerPage) + i;

                if (slotImage == null)
                {
                    slotImage = slot.gameObject.AddComponent<Image>();
                }

                if (glyphIndex < allGlyphs.Count)
                {
                    // Show glyph sprite
                    slotImage.sprite = allGlyphs[glyphIndex].sprite;
                    slotImage.color = Color.white;

                    // Try to add GlyphSelectable component for interaction
                    if (slot.GetComponent<GlyphSelectable>() == null)
                    {
                        GlyphSelectable glyphSelect = slot.gameObject.AddComponent<GlyphSelectable>();
                        glyphSelect.SetGlyphName(allGlyphs[glyphIndex].name);
                    }

                    Debug.Log($"[Codex]   Slot_{i}: {allGlyphs[glyphIndex].name}");
                }
                else
                {
                    // Empty slot
                    slotImage.sprite = null;
                    slotImage.color = new Color(0.15f, 0.15f, 0.15f, 1f);
                }
            }
        }
        else
        {
            Debug.LogWarning("[Codex] GlyphGrid not found!");
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

        // Create GlyphUI instance
        if (glyphUIPrefab == null)
        {
            Debug.LogError("[Codex] glyphUIPrefab is not assigned!");
            return;
        }

        GameObject glyphUIPrefabInstance = Instantiate(glyphUIPrefab);
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
    /// Assign a glyph to the next available slot (page 1 first, then page 2).
    /// </summary>
    private void AssignGlyphToNextAvailableSlot(GlyphUI glyph)
    {
        if (glyph == null) return;

        // Try page 1 slots first
        foreach (var slot in slotsPage1)
        {
            if (slot != null && !slot.isFilled)
            {
                slot.SetGlyph(glyph);
                Debug.Log($"[Codex] Assigned {glyph.glyphData.glyphName} to Page 1 slot");
                return;
            }
        }

        // Try page 2 slots
        foreach (var slot in slotsPage2)
        {
            if (slot != null && !slot.isFilled)
            {
                slot.SetGlyph(glyph);
                Debug.Log($"[Codex] Assigned {glyph.glyphData.glyphName} to Page 2 slot");
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
        // Clear from page 1
        foreach (var slot in slotsPage1)
        {
            if (slot != null && slot.glyphUI != null && slot.glyphUI.glyphData == data)
            {
                slot.Clear();
            }
        }

        // Clear from page 2
        foreach (var slot in slotsPage2)
        {
            if (slot != null && slot.glyphUI != null && slot.glyphUI.glyphData == data)
            {
                slot.Clear();
            }
        }
    }

    /// <summary>
    /// Called when a glyph is selected (usually from a slot button click).
    /// </summary>
    public void OnGlyphSelected(GlyphUI glyph)
    {
        if (glyph == null) return;

        // Deselect previous glyph
        if (selectedGlyph != null)
        {
            selectedGlyph.Deselect();
        }

        selectedGlyph = glyph;
        selectedGlyph.Select();

        // Update the glyph name display
        if (glyphNameText != null)
        {
            glyphNameText.text = glyph.glyphData.glyphName;
        }

        // Notify puzzle controller for puzzle selection tracking
        // (separate from codex "viewing" selection)
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
