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

    [Header("Puzzle Mode")]
    [SerializeField] private GameObject triglyphPanelUI;  // Reference to puzzle panel to detect if puzzle mode is active

    [Header("Mind Log Containers")]
    public GameObject glyphsBackground;
    public GameObject mindLogPrimaryContainer;
    public GameObject mindLogSecondaryContainer;

    [Header("Audio")]
    [SerializeField] private AudioClip selectGlyphSound;
    [SerializeField] private AudioClip deselectGlyphSound;
    private AudioSource audioSource;

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
    private List<GlyphUI> selectedGlyphs = new List<GlyphUI>();  // Support multi-selection
    private GlyphSlot selectedSlot;  // Track which slot is visually highlighted

    private int _currentCodexPage = 0;
    private const int SlotsPerPage = 9;

#if ENABLE_INPUT_SYSTEM
    private InputAction _toggleCodexAction;

    private void OnEnable()
    {
        _toggleCodexAction = new InputAction("ToggleCodex", binding: "<Keyboard>/c");
        _toggleCodexAction.Enable();

        // Get or create AudioSource for sound effects
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
        _toggleCodexAction?.Disable();
    }
#endif

    private Canvas _cachedCanvas;
    private TriglyphPuzzleController _triglyphController; // ← Cache to avoid FindAnyObjectByType every frame

    private void Awake()
    {
        // Persist ONLY the CodexPanel root, not individual controllers
        // This prevents multiple DontDestroyOnLoad conflicts
        GameObject panelObj = GameObject.Find("UI_Canvas/CodexPanel");
        if (panelObj != null)
        {
            DontDestroyOnLoad(panelObj);
            Debug.Log("[Codex] CodexPanel marked as persistent across scenes");
        }
        else
        {
            Debug.LogError("[Codex] CodexPanel not found at UI_Canvas/CodexPanel!");
        }

        InitializeReferences();
    }

    private void InitializeReferences()
    {
        // Find CodexPanel in UI_Canvas
        GameObject panelObj = GameObject.Find("UI_Canvas/CodexPanel");
        if (panelObj != null)
        {
            codexPanel = panelObj.GetComponent<CanvasGroup>();
            
            // New Hierarchy: CodexPanel -> GlyphsBackground -> [Children]
            Transform glyphsBG = panelObj.transform.Find("GlyphsBackground");
            if (glyphsBG != null)
            {
                viewport = glyphsBG.Find("Viewport");
                glyphNameText = glyphsBG.Find("Navigation/GlyphName")?.GetComponent<TextMeshProUGUI>();
                
                nextPageBtn = glyphsBG.Find("Navigation/NextBtn")?.GetComponent<Button>();
                if (nextPageBtn == null) nextPageBtn = glyphsBG.Find("Navigation/Btn_Next")?.GetComponent<Button>();
                
                prevPageBtn = glyphsBG.Find("Navigation/PrevBtn")?.GetComponent<Button>();
                if (prevPageBtn == null) prevPageBtn = glyphsBG.Find("Navigation/Btn_Prev")?.GetComponent<Button>();
            }
            else
            {
                // Fallback to root (original logic)
                viewport = panelObj.transform.Find("Viewport");
                glyphNameText = panelObj.transform.Find("Navigation/GlyphName")?.GetComponent<TextMeshProUGUI>();
                nextPageBtn = panelObj.transform.Find("Navigation/NextBtn")?.GetComponent<Button>();
                prevPageBtn = panelObj.transform.Find("Navigation/PrevBtn")?.GetComponent<Button>();
            }

            Debug.Log("[Codex] CodexPanel references initialized successfully.");
        }
        else
        {
            Debug.LogError("[Codex] CodexPanel not found at UI_Canvas/CodexPanel!");
        }

        if (nextPageBtn != null) nextPageBtn.onClick.AddListener(NextPage);
        if (prevPageBtn != null) prevPageBtn.onClick.AddListener(PrevPage);

        // Auto-discover GlyphSlots in the CodexPanel hierarchy
        DiscoverGlyphSlots();

        // Cache TriglyphPuzzleController
        _triglyphController = FindAnyObjectByType<TriglyphPuzzleController>();
    }

    /// <summary>
    /// Automatically discover all GlyphSlot components in the codex panel hierarchy.
    /// This ensures slots are populated even if they weren't manually assigned in Inspector.
    /// </summary>
    private void DiscoverGlyphSlots()
    {
        if (codexPanel == null)
        {
            Debug.LogWarning("[Codex] Cannot discover slots - codexPanel is null!");
            return;
        }

        // Clear existing list to avoid duplicates
        allSlots.Clear();

        // Find all GlyphSlot components in the codex panel hierarchy
        GlyphSlot[] foundSlots = codexPanel.GetComponentsInChildren<GlyphSlot>(includeInactive: true);
        
        if (foundSlots.Length == 0)
        {
            Debug.LogError("[Codex] No GlyphSlot components found in CodexPanel hierarchy! Check your UI structure.");
            return;
        }

        // Add slots to list in order
        foreach (GlyphSlot slot in foundSlots)
        {
            if (slot != null)
            {
                allSlots.Add(slot);
            }
        }

        Debug.Log($"[Codex] Auto-discovered {allSlots.Count} GlyphSlots in CodexPanel hierarchy");

        // Auto-discover triglyphPanelUI if not assigned
        if (triglyphPanelUI == null)
        {
            triglyphPanelUI = GameObject.Find("UI_Canvas/TriglyphPuzzlePanel");
            if (triglyphPanelUI != null)
            {
                Debug.Log("[Codex] Auto-discovered TriglyphPuzzlePanel in scene");
            }
            else
            {
                Debug.LogWarning("[Codex] TriglyphPuzzlePanel not found in scene - puzzle mode may not work correctly");
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
        {
            cPressed = true;
            Debug.Log("[Codex] C key detected via InputAction");
        }

        var keyboard = Keyboard.current;
        if (keyboard != null && keyboard.cKey.wasPressedThisFrame)
        {
            cPressed = true;
            Debug.Log("[Codex] C key detected via Keyboard.current");
        }
#else
        // FALLBACK: Check for C key using legacy input
        if (Input.GetKeyDown(KeyCode.C))
        {
            cPressed = true;
            Debug.Log("[Codex] C key detected via Input.GetKeyDown (legacy)");
        }
#endif

        if (cPressed)
        {
            Debug.Log($"[Codex] C key pressed! playerHasCodex={playerHasCodex}, requiresCodexDevice={requiresCodexDevice}");
            if (playerHasCodex || !requiresCodexDevice)
            {
                Debug.Log("[Codex] Conditions met - calling ToggleCodex()");
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
        // Re-verify references before toggling
        if (codexPanel == null) InitializeReferences();

        if (codexPanel == null)
        {
            Debug.LogError("[Codex] codexPanel is NULL even after re-initialization!");
            return;
        }

        bool opening = codexPanel.alpha < 0.5f;

        // When opening codex, rediscover slots in case we loaded a new scene
        if (opening && allSlots.Count == 0)
        {
            Debug.Log("[Codex] Opening codex with no slots - rediscovering slots...");
            DiscoverGlyphSlots();
        }

        // GUARD: Do not allow toggling during puzzle sequence
        TriglyphPuzzleController triglyph = FindAnyObjectByType<TriglyphPuzzleController>();
        if (triglyph != null && triglyph.IsSequenceInProgress)
        {
            Debug.Log("[Codex] Cannot toggle - puzzle sequence in progress!");
            return;
        }

        // GUARD: Do not allow re-opening if codexPanel is deactivated
        if (!codexPanel.gameObject.activeSelf && codexPanel.alpha < 0.5f)
        {
            Debug.Log("[Codex] Cannot toggle - codexPanel GameObject is deactivated!");
            return;
        }

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
            
            // Set default view to Glyphs
            CodexViewController viewCtrl = codexPanel.GetComponent<CodexViewController>();
            if (viewCtrl != null)
            {
                viewCtrl.SwitchView("glyphs");
            }

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
            if (selectedGlyphs.Count > 0)
            {
                foreach (var sel in selectedGlyphs)
                {
                    sel.Deselect();
                }
                selectedGlyphs.Clear();
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

        if (glyphNameText != null && selectedGlyphs.Count == 0)
        {
            int totalPages = Mathf.CeilToInt((float)allSlots.Count / SlotsPerPage);
            glyphNameText.text = $"Codex - Page {_currentCodexPage + 1} of {totalPages}";
            Debug.Log("[Codex] UpdateCodexUI: glyphNameText updated with page number (no glyphs selected)");
        }
        else if (selectedGlyphs.Count > 0 && glyphNameText != null)
        {
            Debug.Log("[Codex] UpdateCodexUI: glyphs are selected, skipping page text update");
        }

        // Look for pagination grids: GlyphGrid_Pg1, GlyphGrid_Pg2, etc.
        string gridName = $"GlyphGrid_Pg{_currentCodexPage + 1}";
        
        Transform glyphsBG = codexPanel.transform.Find("GlyphsBackground");
        Transform gridT = glyphsBG != null ? glyphsBG.Find(gridName) : codexPanel.transform.Find(gridName);

        if (gridT == null && glyphsBG != null)
        {
            // Fallback: try to find just "GlyphGrid"
            gridT = glyphsBG.Find("GlyphGrid");
        }
        else if (gridT == null)
        {
             gridT = codexPanel.transform.Find("GlyphGrid");
        }

        if (gridT != null)
        {
            Debug.Log($"[Codex] {gridName} found with {gridT.childCount} children (slots)");

            // Hide other pages if they exist
            if (glyphsBG != null)
            {
                foreach (Transform child in glyphsBG)
                {
                    if (child.name.StartsWith("GlyphGrid_Pg") && child.name != gridName)
                    {
                        child.gameObject.SetActive(false);
                    }
                }
            }

            gridT.gameObject.SetActive(true);

            // Update the grid to display the GlyphSlot components
            for (int i = 0; i < gridT.childCount; i++)
            {
                Transform slotTransform = gridT.GetChild(i);
                GlyphSlot glyphSlot = slotTransform.GetComponent<GlyphSlot>();

                if (glyphSlot != null)
                {
                    slotTransform.gameObject.SetActive(true);
                    // Debug.Log($"[Codex]   Slot_{i}: Active, Filled={glyphSlot.isFilled}");
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
        Debug.Log("[Codex] ========== CODEX UNLOCKED ==========");
        Debug.Log($"[Codex] playerHasCodex = {playerHasCodex}");
        Debug.Log("[Codex] Player can now press C to open Codex");

        // Show notification to player
        var notificationPanel = FindAnyObjectByType<NotificationPanelController>();
        if (notificationPanel != null)
        {
            notificationPanel.ShowNotification("Codex Received. Press C to access.", duration: 5f);
        }
        else
        {
            Debug.LogWarning("[Codex] NotificationPanel not found - notification not shown");
        }
    }

    /// <summary>
    /// Set references to all three UI containers. Called by CodexViewController during setup.
    /// This centralizes container management and allows MindLogPersistence to access them reliably.
    /// </summary>
    public void SetContainerReferences(GameObject glyphsBg, GameObject primaryContainer, GameObject secondaryContainer)
    {
        glyphsBackground = glyphsBg;
        mindLogPrimaryContainer = primaryContainer;
        mindLogSecondaryContainer = secondaryContainer;
        
        Debug.Log("[CodexController] Container references set:");
        Debug.Log($"  - Glyphs Background: {(glyphsBackground != null ? glyphsBackground.name : "NULL")}");
        Debug.Log($"  - Mind Log Primary: {(mindLogPrimaryContainer != null ? mindLogPrimaryContainer.name : "NULL")}");
        Debug.Log($"  - Mind Log Secondary: {(mindLogSecondaryContainer != null ? mindLogSecondaryContainer.name : "NULL")}");
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

        // Safety check: ensure slots are discovered
        if (allSlots.Count == 0)
        {
            Debug.LogWarning("[Codex] No slots available when adding glyph - attempting to discover slots...");
            DiscoverGlyphSlots();
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
    /// Handles all UI feedback (sounds, highlights, name display) regardless of mode.
    /// Optionally notifies TriglyphPuzzleController if puzzle mode is active.
    /// </summary>
    public void OnGlyphSelected(GlyphUI glyph)
    {
        if (glyph == null) return;

        Debug.Log($"[Codex] OnGlyphSelected called for: {glyph.glyphData.glyphName}");

        // ===== ALWAYS DO: General Codex UI Feedback =====
        // This happens whether in puzzle mode or not

        // Find and highlight the slot for this glyph
        Debug.Log($"[Codex] Looking for slot with glyphUI, allSlots.Count = {allSlots.Count}");
        GlyphSlot glyphSlot = null;
        foreach (var slot in allSlots)
        {
            if (slot != null && slot.glyphUI == glyph)
            {
                glyphSlot = slot;
                break;
            }
        }

        // Check if clicking the same glyph again (toggle/deselect behavior)
        if (selectedGlyphs.Contains(glyph))
        {
            Debug.Log($"[Codex] Toggling off glyph: {glyph.glyphData.glyphName}");
            selectedGlyphs.Remove(glyph);
            glyph.Deselect();

            // Play deselect sound
            PlayDeselectSound();

            // Unhighlight the slot
            if (glyphSlot != null)
            {
                glyphSlot.Unhighlight();
            }

            // Update name display (show last selected or default)
            if (glyphNameText != null)
            {
                glyphNameText.text = selectedGlyphs.Count > 0 ? selectedGlyphs.Last().glyphData.glyphName : "Codex";
            }

            // Notify puzzle controller of deselection (always, for immediate state sync)
            bool isPuzzleModeOnDeselect = triglyphPanelUI != null && triglyphPanelUI.activeSelf;
            if (isPuzzleModeOnDeselect)
            {
                Debug.Log($"[Codex] Notifying TriglyphPuzzleController to deselect: {glyph.glyphData.glyphName}");
                NotifyPuzzleControllerDeselect(glyph);
            }
            return;
        }

        // Add new glyph to selection (multi-select)
        selectedGlyphs.Add(glyph);
        glyph.Select();

        // Play select sound
        PlaySelectSound();

        // Highlight the slot
        if (glyphSlot != null)
        {
            glyphSlot.Highlight();
            Debug.Log($"[Codex] ✓ Highlighted slot: {glyphSlot.gameObject.name}");
        }

        // Update the glyph name display (show most recent selection)
        if (glyphNameText != null)
        {
            Debug.Log($"[Codex] Setting glyphNameText to '{glyph.glyphData.glyphName}'");
            glyphNameText.text = glyph.glyphData.glyphName;
        }

        // ===== OPTIONALLY DO: Puzzle-Specific Behavior =====
        // If puzzle mode is active, notify the puzzle controller with the most recently selected glyph
        bool isPuzzleMode = triglyphPanelUI != null && triglyphPanelUI.activeSelf;
        if (isPuzzleMode)
        {
            Debug.Log($"[Codex] Puzzle mode active - notifying TriglyphPuzzleController with most recent selection");
            NotifyPuzzleController(glyph);
        }
        else
        {
            Debug.Log($"[Codex] Codex viewing mode - puzzle controller not notified");
        }

        Debug.Log($"[Codex] Glyph selected: {glyph.glyphData.glyphName}. Total selected: {selectedGlyphs.Count}");
    }

    /// <summary>
    /// Play sound when glyph is selected
    /// </summary>
    private void PlaySelectSound()
    {
        if (audioSource != null && selectGlyphSound != null)
        {
            audioSource.PlayOneShot(selectGlyphSound);
            Debug.Log("[Codex] Playing select glyph sound");
        }
        else if (selectGlyphSound == null)
        {
            Debug.LogWarning("[Codex] Select glyph sound not assigned in Inspector!");
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
            Debug.Log("[Codex] Playing deselect glyph sound");
        }
        else if (deselectGlyphSound == null)
        {
            Debug.LogWarning("[Codex] Deselect glyph sound not assigned in Inspector!");
        }
    }

    /// <summary>
    /// Notify the puzzle controller when a glyph is clicked
    /// This allows the puzzle controller to track selections independently
    /// </summary>
    private void NotifyPuzzleController(GlyphUI glyph)
    {
        // Use cached controller instead of expensive FindAnyObjectByType
        if (_triglyphController != null)
        {
            _triglyphController.OnGlyphClickedForPuzzle(glyph);
        }
        else
        {
            // Fallback: Try to find it once if not cached
            _triglyphController = FindAnyObjectByType<TriglyphPuzzleController>();
            if (_triglyphController != null)
            {
                _triglyphController.OnGlyphClickedForPuzzle(glyph);
            }
        }
    }

    /// <summary>
    /// Notify the puzzle controller to deselect a specific glyph
    /// This ensures state stays in sync when deselecting
    /// </summary>
    private void NotifyPuzzleControllerDeselect(GlyphUI glyph)
    {
        // Use cached controller instead of expensive FindAnyObjectByType
        if (_triglyphController != null)
        {
            _triglyphController.OnGlyphDeselectedFromCodex(glyph);
        }
        else
        {
            // Fallback: Try to find it once if not cached
            _triglyphController = FindAnyObjectByType<TriglyphPuzzleController>();
            if (_triglyphController != null)
            {
                _triglyphController.OnGlyphDeselectedFromCodex(glyph);
            }
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
