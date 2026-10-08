using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;
using System.Collections;
using Velinor.UI.Codex;
using Velinor.Core;
using Velinor.Testing;

/// <summary>
/// Manages toggling between Glyphs, Mind Log Primary, and Mind Log Secondary views on the Codex device.
/// 
/// Handles enabling/disabling UI elements when switching between:
/// - Glyphs view: Grid layout with glyph pagination
/// - Mind Log Primary view: 3x3 memory fragment grid with selection
/// - Mind Log Secondary view: Expanded memory view with full text and Back button
/// 
/// Does NOT create UI programmatically—only toggles visibility of existing elements.
/// This preserves all existing systems and dependencies.
/// </summary>
public class CodexViewController : MonoBehaviour
{
    [Header("View Buttons")]
    [SerializeField] private Button glyphsButton;
    [SerializeField] private Button impressionsButton;

    [Header("View Backgrounds")]
    [SerializeField] private GameObject glyphsBackground;
    [SerializeField] private GameObject mindLogBackground;

    [Header("Glyphs View Elements")]
    [SerializeField] private GameObject glyphGrid_Pg1;
    [SerializeField] private GameObject glyphGrid_Pg2;
    [SerializeField] private GameObject glyphsNavigation;

    [Header("Mind Log Primary View Elements")]
    [SerializeField] private GameObject mindLogPrimaryContainer;
    [SerializeField] private MemoryGridUI memoryGridUI;

    [Header("Mind Log Secondary View Elements (Expanded)")]
    [SerializeField] private GameObject mindLogSecondaryContainer;
    [SerializeField] private MemoryExpandedUI memoryExpandedUI;
    [SerializeField] private Button mindLogBackButton;

    [Header("Legacy Impressions Elements (if using old system)")]
    [SerializeField] private GameObject impressionsTextDisplay;
    [SerializeField] private GameObject impressionsPrevButton;
    [SerializeField] private GameObject impressionsNextButton;

    [Header("Testing")]
    [SerializeField] private MemoryFragmentTestSetup testSetup;
    [SerializeField] private bool useTestMemories = true;

    private string currentView = "glyphs"; // Default to glyphs on startup
    private bool testMemoriesInitialized = false;

    // Store listener delegates so they can be properly removed
    private UnityAction onGlyphsButtonClick;
    private UnityAction onImpressionsButtonClick;
    private UnityAction onMindLogBackButtonClick;

    private void Awake()
    {
        // Store strong references to containers immediately
        if (mindLogPrimaryContainer == null)
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
        if (mindLogSecondaryContainer == null)
            mindLogSecondaryContainer = GameObject.Find("MindLogSecondaryContainer");
        if (glyphsBackground == null)
            glyphsBackground = GameObject.Find("GlyphsBackground");

        // Containers are children of CodexPanel which is already marked as DontDestroyOnLoad by CodexController
        // Do NOT mark them individually - this causes conflicts with scene persistence
        
        // Pass container references to CodexController for centralized management
        CodexController codexController = GetComponentInParent<CodexController>();
        if (codexController != null)
        {
            codexController.SetContainerReferences(glyphsBackground, mindLogPrimaryContainer, mindLogSecondaryContainer);
        }
        else
        {
            Debug.LogWarning("[CodexViewController] Could not find CodexController in parent hierarchy");
        }

        // Initialize MindLogPersistence component for container protection
        MindLogPersistence persistence = FindAnyObjectByType<MindLogPersistence>();
        if (persistence == null && Application.isPlaying)
        {
            // Create a GameObject to hold the MindLogPersistence component
            GameObject persistenceHolder = new GameObject("_MindLogPersistenceManager");
            persistence = persistenceHolder.AddComponent<MindLogPersistence>();
            // DO NOT mark persistenceHolder as DontDestroyOnLoad - let it be destroyed normally
            // The persistence data is stored in static Codex unlock state, not the GameObject
            Debug.Log("[CodexViewController] Awake: Created MindLogPersistenceManager");
        }

        // ADD DESTRUCTION TRACKER - will help us catch when containers are destroyed
        if (mindLogPrimaryContainer != null)
        {
            AddDestructionTracker(mindLogPrimaryContainer, "MindLogPrimaryContainer");
            Transform parent = mindLogPrimaryContainer.transform.parent;
            while (parent != null)
            {
                AddDestructionTracker(parent.gameObject, $"MindLogPrimaryContainer parent: {parent.name}");
                parent = parent.parent;
            }
        }
    }

    private void AddDestructionTracker(GameObject go, string name)
    {
        // Add a simple script to log when this GameObject is destroyed
        if (go.GetComponent<DestructionTracker>() == null)
        {
            DestructionTracker tracker = go.AddComponent<DestructionTracker>();
            tracker.objectName = name;
        }
    }

    private void OnEnable()
    {
        // Only add listeners once; remove old ones first to prevent duplicates
        OnDisable();

        // Create listener delegates and store them as UnityAction
        onGlyphsButtonClick = new UnityAction(() => SwitchView("glyphs"));
        onImpressionsButtonClick = new UnityAction(() => SwitchView("mind_log_primary"));
        onMindLogBackButtonClick = new UnityAction(() => SwitchView("mind_log_primary"));

        // Hook button clicks with stored delegates
        if (glyphsButton != null)
            glyphsButton.onClick.AddListener(onGlyphsButtonClick);
        
        if (impressionsButton != null)
            impressionsButton.onClick.AddListener(onImpressionsButtonClick);

        if (mindLogBackButton != null)
            mindLogBackButton.onClick.AddListener(onMindLogBackButtonClick);

        Debug.Log("[CodexViewController] Button listeners registered");
    }

    private void OnDisable()
    {
        // Remove listeners using the same stored delegates
        if (glyphsButton != null && onGlyphsButtonClick != null)
            glyphsButton.onClick.RemoveListener(onGlyphsButtonClick);
        
        if (impressionsButton != null && onImpressionsButtonClick != null)
            impressionsButton.onClick.RemoveListener(onImpressionsButtonClick);

        if (mindLogBackButton != null && onMindLogBackButtonClick != null)
            mindLogBackButton.onClick.RemoveListener(onMindLogBackButtonClick);

        Debug.Log("[CodexViewController] Button listeners unregistered");
    }

    private void Start()
    {
        // CRITICAL: Lock the Codex by default - it should only be accessible after Saori gives it
        MindLogPersistence.LockCodex();
        Debug.Log("[CodexViewController] Codex LOCKED at start - player must obtain it from Saori");

        // If Codex is locked, don't show any views at all - entire UI should be hidden
        if (!MindLogPersistence.IsCodexUnlocked())
        {
            Debug.Log("[CodexViewController] Codex locked - skipping view initialization");
            return;
        }

        // Initialize to glyphs view on startup - but DON'T disable Mind Log containers yet
        // They need to persist and be available when needed
        ShowGlyphsView();
    }

    /// <summary>
    /// Switch between glyphs, mind_log_primary, and mind_log_secondary views.
    /// Blocks Mind Log access if Codex is locked (not yet obtained from Saori).
    /// </summary>
    public void SwitchView(string viewName)
    {
        if (currentView == viewName) return; // Already on this view

        // Check if trying to access Mind Log views while Codex is locked
        if ((viewName == "mind_log_primary" || viewName == "mind_log_secondary") && !MindLogPersistence.IsCodexUnlocked())
        {
            Debug.LogWarning($"[CodexViewController] BLOCKED: Cannot access Mind Log - Codex is LOCKED! Must obtain it from Saori first.");
            return;
        }

        currentView = viewName;
        Debug.Log($"[CodexViewController] Switching to view: {viewName}");

        switch (viewName)
        {
            case "glyphs":
                ShowGlyphsView();
                break;
            case "mind_log_primary":
                ShowMindLogPrimaryView();
                break;
            case "mind_log_secondary":
                ShowMindLogSecondaryView();
                break;
            default:
                Debug.LogWarning($"[CodexViewController] Unknown view: {viewName}");
                break;
        }
    }

    /// <summary>
    /// Show the Glyphs grid view with pagination controls.
    /// </summary>
    private void ShowGlyphsView()
    {
        // Enable glyphs background
        if (glyphsBackground != null) glyphsBackground.SetActive(true);
        if (mindLogBackground != null) mindLogBackground.SetActive(false);

        Debug.Log("[CodexViewController] ShowGlyphsView - glyphGrid_Pg1 is null? " + (glyphGrid_Pg1 == null));
        Debug.Log("[CodexViewController] ShowGlyphsView - glyphGrid_Pg2 is null? " + (glyphGrid_Pg2 == null));

        // IMPORTANT: Only enable Page 1 by default. Do NOT enable both pages at once or they'll stack and block input!
        if (glyphGrid_Pg1 != null)
        {
            glyphGrid_Pg1.SetActive(true);
            // Ensure CanvasGroup is interactable (in case it was disabled)
            CanvasGroup cg1 = glyphGrid_Pg1.GetComponent<CanvasGroup>();
            if (cg1 != null)
            {
                cg1.interactable = true;
                cg1.blocksRaycasts = true;
                cg1.alpha = 1f;
                Debug.Log("[CodexViewController] Re-enabled CanvasGroup on GlyphGrid_Pg1");
            }
            else
            {
                Debug.Log("[CodexViewController] No CanvasGroup found on GlyphGrid_Pg1");
            }
        }
        
        // DISABLE Page 2 - it should only be active when user navigates to it
        if (glyphGrid_Pg2 != null)
        {
            glyphGrid_Pg2.SetActive(false);
            CanvasGroup cg2 = glyphGrid_Pg2.GetComponent<CanvasGroup>();
            if (cg2 != null)
            {
                cg2.interactable = false;
                cg2.blocksRaycasts = false;
                Debug.Log("[CodexViewController] Disabled CanvasGroup on GlyphGrid_Pg2");
            }
        }
        
        if (glyphsNavigation != null)
        {
            glyphsNavigation.SetActive(true);
            // Ensure CanvasGroup is interactable
            CanvasGroup cgNav = glyphsNavigation.GetComponent<CanvasGroup>();
            if (cgNav != null)
            {
                cgNav.interactable = true;
                cgNav.blocksRaycasts = true;
                cgNav.alpha = 1f;
            }
        }

        // Disable Mind Log views
        DisableMindLogPrimary();
        DisableMindLogSecondary();

        // Disable legacy impressions elements if they exist
        if (impressionsTextDisplay != null) impressionsTextDisplay.SetActive(false);
        if (impressionsPrevButton != null) impressionsPrevButton.SetActive(false);
        if (impressionsNextButton != null) impressionsNextButton.SetActive(false);

        Debug.Log("[CodexViewController] Glyphs view enabled");
    }

    /// <summary>
    /// Show the Mind Log Primary view (3x3 grid of memory fragments).
    /// </summary>
    private void ShowMindLogPrimaryView()
    {
        // CRITICAL: Immediately re-find the container if reference is null or destroyed
        // This can happen if the container is destroyed/recreated or reference is lost
        if (mindLogPrimaryContainer == null)
        {
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
            if (mindLogPrimaryContainer == null)
            {
                // Try to find it in scene root
                Canvas[] allCanvases = FindObjectsOfType<Canvas>();
                foreach (Canvas canvas in allCanvases)
                {
                    Transform found = canvas.transform.Find("CodexPanel/MindLogPrimaryContainer");
                    if (found != null)
                    {
                        mindLogPrimaryContainer = found.gameObject;
                        Debug.Log("[CodexViewController] Found MindLogPrimaryContainer via hierarchy search");
                        break;
                    }
                }
                
                if (mindLogPrimaryContainer == null)
                {
                    Debug.LogError("[CodexViewController] FATAL: MindLogPrimaryContainer not found in scene! Checked both GameObject.Find() and hierarchy search.");
                    return;
                }
            }
            Debug.Log("[CodexViewController] Re-found MindLogPrimaryContainer (reference was null)");
        }

        Debug.Log("[CodexViewController] ===== START ShowMindLogPrimaryView =====");
        
        if (mindLogPrimaryContainer == null)
        {
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
            Debug.Log($"[CodexViewController] Had to re-find MindLogPrimaryContainer: {(mindLogPrimaryContainer != null ? "FOUND" : "NOT FOUND")}");
        }
        
        if (mindLogPrimaryContainer != null)
        {
            Debug.Log($"[CodexViewController] MindLogPrimaryContainer state BEFORE any changes:");
            Debug.Log($"  - activeSelf: {mindLogPrimaryContainer.activeSelf}");
            Debug.Log($"  - activeInHierarchy: {mindLogPrimaryContainer.activeInHierarchy}");
            Debug.Log($"  - Parent: {mindLogPrimaryContainer.transform.parent?.name ?? "ROOT"}");
            Debug.Log($"  - Parent active: {(mindLogPrimaryContainer.transform.parent != null ? mindLogPrimaryContainer.transform.parent.gameObject.activeSelf : true)}");
        }
        
        // Initialize test memories on first load if enabled and assigned
        if (useTestMemories && !testMemoriesInitialized && testSetup != null)
        {
            testSetup.InitializeTestMemories();
            testMemoriesInitialized = true;
            Debug.Log("[CodexViewController] Test memories initialized successfully!");
        }
        else if (useTestMemories && !testMemoriesInitialized && testSetup == null)
        {
            Debug.Log("[CodexViewController] Test Setup not assigned - using manual loader instead.");
        }

        // CRITICAL: Ensure Canvas hierarchy is active before enabling container
        Canvas uiCanvas = FindAnyObjectByType<Canvas>();
        if (uiCanvas != null && !uiCanvas.gameObject.activeSelf)
        {
            uiCanvas.gameObject.SetActive(true);
            Debug.Log("[CodexViewController] UI_Canvas was inactive - activated it");
        }

        // Ensure CodexPanel (container's parent) is active
        GameObject codexPanel = GameObject.Find("UI_Canvas/CodexPanel");
        if (codexPanel != null && !codexPanel.activeSelf)
        {
            codexPanel.SetActive(true);
            Debug.Log("[CodexViewController] CodexPanel was inactive - activated it");
        }

        // Disable glyphs background and ENABLE Mind Log background
        if (glyphsBackground != null) glyphsBackground.SetActive(false);
        if (mindLogBackground != null) mindLogBackground.SetActive(true);

        // Get the persistence helper to protect the container
        MindLogPersistence persistence = FindAnyObjectByType<MindLogPersistence>();
        if (persistence != null)
        {
            persistence.ProtectPrimaryContainer();
            Debug.Log("[CodexViewController] MindLogPersistence activated to protect container");
        }
        else
        {
            Debug.LogWarning("[CodexViewController] MindLogPersistence not found - container may become invisible!");
        }

        // Disable glyphs view elements
        if (glyphGrid_Pg1 != null)
        {
            glyphGrid_Pg1.SetActive(false);
            CanvasGroup cg1 = glyphGrid_Pg1.GetComponent<CanvasGroup>();
            if (cg1 != null)
            {
                cg1.interactable = false;
                cg1.blocksRaycasts = false;
            }
        }
        
        if (glyphGrid_Pg2 != null)
        {
            glyphGrid_Pg2.SetActive(false);
            CanvasGroup cg2 = glyphGrid_Pg2.GetComponent<CanvasGroup>();
            if (cg2 != null)
            {
                cg2.interactable = false;
                cg2.blocksRaycasts = false;
            }
        }
        
        if (glyphsNavigation != null)
        {
            glyphsNavigation.SetActive(false);
            CanvasGroup cgNav = glyphsNavigation.GetComponent<CanvasGroup>();
            if (cgNav != null)
            {
                cgNav.interactable = false;
                cgNav.blocksRaycasts = false;
            }
        }

        // Enable Mind Log Primary view
        if (mindLogPrimaryContainer == null)
        {
            Debug.LogError("[CodexViewController] MindLogPrimaryContainer reference is null! This should have been set in Awake()");
            return;
        }

        Debug.Log($"[CodexViewController] MindLogPrimaryContainer current active state: {mindLogPrimaryContainer.activeSelf}");
        Debug.Log($"[CodexViewController] MindLogPrimaryContainer parent: {mindLogPrimaryContainer.transform.parent?.name ?? "ROOT"}");
        
        // Ensure all parent GameObjects in the hierarchy are active
        Transform current = mindLogPrimaryContainer.transform.parent;
        while (current != null)
        {
            if (!current.gameObject.activeSelf)
            {
                current.gameObject.SetActive(true);
                Debug.Log($"[CodexViewController] Activated parent: {current.name}");
            }
            current = current.parent;
        }
        
        mindLogPrimaryContainer.SetActive(true);
        Debug.Log($"[CodexViewController] MindLogPrimaryContainer set to active: {mindLogPrimaryContainer.activeSelf}");
        
        // Containers persist via CodexPanel's DontDestroyOnLoad (set by CodexController)
        // Do NOT re-apply DontDestroyOnLoad here - it causes conflicts
        Transform root = mindLogPrimaryContainer.transform.root;
        Debug.Log($"[CodexViewController] Root parent: {root.name}");
        
        CanvasGroup cgPrimary = mindLogPrimaryContainer.GetComponent<CanvasGroup>();
        if (cgPrimary != null)
        {
            cgPrimary.interactable = true;
            cgPrimary.blocksRaycasts = true;
            cgPrimary.alpha = 1f;
            Debug.Log("[CodexViewController] CanvasGroup on MindLogPrimaryContainer configured");
            Debug.Log($"[CodexViewController] CanvasGroup VERIFIED AFTER SET: alpha={cgPrimary.alpha}, interactable={cgPrimary.interactable}, blocksRaycasts={cgPrimary.blocksRaycasts}");
        }
        else
        {
            Debug.LogWarning("[CodexViewController] No CanvasGroup found on MindLogPrimaryContainer - adding one");
            cgPrimary = mindLogPrimaryContainer.AddComponent<CanvasGroup>();
            cgPrimary.interactable = true;
            cgPrimary.blocksRaycasts = true;
            cgPrimary.alpha = 1f;
            Debug.Log($"[CodexViewController] Added CanvasGroup VERIFIED AFTER SET: alpha={cgPrimary.alpha}, interactable={cgPrimary.interactable}, blocksRaycasts={cgPrimary.blocksRaycasts}");
        }

        // Populate grid from MindLogManager
        MemoryGridController gridController = mindLogPrimaryContainer.GetComponentInChildren<MemoryGridController>();
        if (gridController != null)
        {
            gridController.PopulateFromManager();
        }
        else
        {
            Debug.LogWarning("[CodexViewController] MemoryGridController not found in MindLogPrimaryContainer!");
        }

        // Disable Mind Log Secondary view
        DisableMindLogSecondary();

        // Disable legacy impressions elements if they exist
        if (impressionsTextDisplay != null) impressionsTextDisplay.SetActive(false);
        if (impressionsPrevButton != null) impressionsPrevButton.SetActive(false);
        if (impressionsNextButton != null) impressionsNextButton.SetActive(false);

        // FINAL DIAGNOSTIC: Check state just before reporting success
        Debug.Log($"[CodexViewController] ===== FINAL CHECK BEFORE 'view enabled' =====");
        Debug.Log($"[CodexViewController] MindLogPrimaryContainer.activeSelf: {mindLogPrimaryContainer.activeSelf}");
        Debug.Log($"[CodexViewController] MindLogPrimaryContainer.activeInHierarchy: {mindLogPrimaryContainer.activeInHierarchy}");
        if (!mindLogPrimaryContainer.activeInHierarchy)
        {
            Debug.LogError("[CodexViewController] CRITICAL: Container is active=true but NOT visible in hierarchy!");
            Transform checkParent = mindLogPrimaryContainer.transform.parent;
            int depth = 0;
            while (checkParent != null && depth < 5)
            {
                Debug.LogError($"[CodexViewController] Parent depth {depth}: {checkParent.name} - activeSelf={checkParent.gameObject.activeSelf}, activeInHierarchy={checkParent.gameObject.activeInHierarchy}");
                checkParent = checkParent.parent;
                depth++;
            }
        }

        Debug.Log("[CodexViewController] Mind Log Primary view enabled");
    }

    /// <summary>
    /// Show the Mind Log Secondary view (expanded memory with full text and back button).
    /// </summary>
    private void ShowMindLogSecondaryView()
    {
        // CRITICAL: Ensure Canvas hierarchy is active before enabling container
        Canvas uiCanvas = FindAnyObjectByType<Canvas>();
        if (uiCanvas != null && !uiCanvas.gameObject.activeSelf)
        {
            uiCanvas.gameObject.SetActive(true);
            Debug.Log("[CodexViewController] UI_Canvas was inactive - activated it");
        }

        // Ensure CodexPanel (container's parent) is active
        GameObject codexPanel = GameObject.Find("UI_Canvas/CodexPanel");
        if (codexPanel != null && !codexPanel.activeSelf)
        {
            codexPanel.SetActive(true);
            Debug.Log("[CodexViewController] CodexPanel was inactive - activated it");
        }

        // Enable mind log background (different from glyphs/primary)
        if (glyphsBackground != null) glyphsBackground.SetActive(false);
        if (mindLogBackground != null) mindLogBackground.SetActive(true);

        // Get the persistence helper to protect the container
        MindLogPersistence persistence = FindAnyObjectByType<MindLogPersistence>();
        if (persistence != null)
        {
            persistence.ProtectSecondaryContainer();
            Debug.Log("[CodexViewController] MindLogPersistence activated to protect secondary container");
        }
        else
        {
            Debug.LogWarning("[CodexViewController] MindLogPersistence not found - secondary container may become invisible!");
        }

        // Disable glyphs view elements
        if (glyphGrid_Pg1 != null)
        {
            glyphGrid_Pg1.SetActive(false);
            CanvasGroup cg1 = glyphGrid_Pg1.GetComponent<CanvasGroup>();
            if (cg1 != null)
            {
                cg1.interactable = false;
                cg1.blocksRaycasts = false;
            }
        }
        
        if (glyphGrid_Pg2 != null)
        {
            glyphGrid_Pg2.SetActive(false);
            CanvasGroup cg2 = glyphGrid_Pg2.GetComponent<CanvasGroup>();
            if (cg2 != null)
            {
                cg2.interactable = false;
                cg2.blocksRaycasts = false;
            }
        }
        
        if (glyphsNavigation != null)
        {
            glyphsNavigation.SetActive(false);
            CanvasGroup cgNav = glyphsNavigation.GetComponent<CanvasGroup>();
            if (cgNav != null)
            {
                cgNav.interactable = false;
                cgNav.blocksRaycasts = false;
            }
        }

        // Disable Mind Log Primary view
        DisableMindLogPrimary();

        // Enable Mind Log Secondary view and ALL its children
        if (mindLogSecondaryContainer != null)
        {
            // Ensure all parent GameObjects in the hierarchy are active
            Transform current = mindLogSecondaryContainer.transform.parent;
            while (current != null)
            {
                if (!current.gameObject.activeSelf)
                {
                    current.gameObject.SetActive(true);
                    Debug.Log($"[CodexViewController] Activated parent: {current.name}");
                }
                current = current.parent;
            }

            mindLogSecondaryContainer.SetActive(true);
            
            // Ensure the secondary container has the same position as the primary container
            RectTransform secondaryRect = mindLogSecondaryContainer.GetComponent<RectTransform>();
            if (secondaryRect != null)
            {
                // Match the primary container's anchoring
                secondaryRect.anchorMin = Vector2.zero;
                secondaryRect.anchorMax = Vector2.one;
                secondaryRect.offsetMin = Vector2.zero;
                secondaryRect.offsetMax = Vector2.zero;
                secondaryRect.anchoredPosition = Vector2.zero;
                
                // Force canvas update to apply changes
                Canvas.ForceUpdateCanvases();
                Debug.Log($"[CodexViewController] Secondary container position reset to: {secondaryRect.anchoredPosition}");
            }
            
            CanvasGroup cgSecondary = mindLogSecondaryContainer.GetComponent<CanvasGroup>();
            if (cgSecondary != null)
            {
                cgSecondary.interactable = true;
                cgSecondary.blocksRaycasts = true;
                cgSecondary.alpha = 1f;
            }

            // Disable layout groups to prevent automatic repositioning during child enable
            LayoutGroup layoutGroup = mindLogSecondaryContainer.GetComponent<LayoutGroup>();
            if (layoutGroup != null)
            {
                layoutGroup.enabled = false;
            }

            // Enable all children of the secondary container (including TextDisplay, PrevButton, NextButton)
            foreach (Transform child in mindLogSecondaryContainer.transform)
            {
                child.gameObject.SetActive(true);
                Debug.Log($"[CodexViewController] Enabled child: {child.name}");
            }

            // Only disable legacy impressions elements if they exist AND are NOT part of the secondary container
            if (impressionsTextDisplay != null && !impressionsTextDisplay.transform.IsChildOf(mindLogSecondaryContainer.transform))
                impressionsTextDisplay.SetActive(false);
            if (impressionsPrevButton != null && !impressionsPrevButton.transform.IsChildOf(mindLogSecondaryContainer.transform))
                impressionsPrevButton.SetActive(false);
            if (impressionsNextButton != null && !impressionsNextButton.transform.IsChildOf(mindLogSecondaryContainer.transform))
                impressionsNextButton.SetActive(false);
        }

        Debug.Log("[CodexViewController] Mind Log Secondary view enabled");
    }

    private void DisableMindLogPrimary()
    {
        if (mindLogPrimaryContainer != null)
        {
            // CRITICAL: NEVER call SetActive(false) on this container
            // It can cause it to be destroyed by competing systems
            // ONLY use CanvasGroup to hide it
            CanvasGroup cgPrimary = mindLogPrimaryContainer.GetComponent<CanvasGroup>();
            if (cgPrimary != null)
            {
                cgPrimary.alpha = 0f;  // Invisible
                cgPrimary.interactable = false;
                cgPrimary.blocksRaycasts = false;
                Debug.Log("[CodexViewController] MindLogPrimaryContainer hidden via CanvasGroup ONLY (SetActive NOT called - prevents destruction)");
            }
            else
            {
                // If no CanvasGroup, add one
                cgPrimary = mindLogPrimaryContainer.AddComponent<CanvasGroup>();
                cgPrimary.alpha = 0f;
                cgPrimary.interactable = false;
                cgPrimary.blocksRaycasts = false;
                Debug.Log("[CodexViewController] Added CanvasGroup and hid MindLogPrimaryContainer (SetActive NOT called)");
            }

            // Unprotect only AFTER we've safely hidden it via CanvasGroup
            MindLogPersistence persistence = FindAnyObjectByType<MindLogPersistence>();
            if (persistence != null)
            {
                persistence.UnprotectPrimaryContainer();
                Debug.Log("[CodexViewController] Unprotected container after CanvasGroup hide");
            }
        }
    }

    private void DisableMindLogSecondary()
    {
        if (mindLogSecondaryContainer != null)
        {
            // CRITICAL: NEVER call SetActive(false) on this container
            // It can cause it to be destroyed by competing systems
            // ONLY use CanvasGroup to hide it
            CanvasGroup cgSecondary = mindLogSecondaryContainer.GetComponent<CanvasGroup>();
            if (cgSecondary != null)
            {
                cgSecondary.alpha = 0f;  // Invisible
                cgSecondary.interactable = false;
                cgSecondary.blocksRaycasts = false;
                Debug.Log("[CodexViewController] MindLogSecondaryContainer hidden via CanvasGroup ONLY (SetActive NOT called - prevents destruction)");
            }
            else
            {
                // If no CanvasGroup, add one
                cgSecondary = mindLogSecondaryContainer.AddComponent<CanvasGroup>();
                cgSecondary.alpha = 0f;
                cgSecondary.interactable = false;
                cgSecondary.blocksRaycasts = false;
                Debug.Log("[CodexViewController] Added CanvasGroup and hid MindLogSecondaryContainer (SetActive NOT called)");
            }

            // Unprotect only AFTER we've safely hidden it via CanvasGroup
            MindLogPersistence persistence = FindAnyObjectByType<MindLogPersistence>();
            if (persistence != null)
            {
                persistence.UnprotectSecondaryContainer();
                Debug.Log("[CodexViewController] Unprotected secondary container after CanvasGroup hide");
            }
        }
    }

    /// <summary>
    /// Get the currently active view.
    /// </summary>
    public string GetCurrentView() => currentView;

    /// <summary>
    /// Called by MemoryGridUI when a memory fragment is double-clicked and expanded.
    /// Switches to the Mind Log Secondary view.
    /// </summary>
    private void OnMemoryFragmentExpanded(MemoryFragment fragment)
    {
        Debug.Log($"[CodexViewController] Memory fragment expanded: {fragment?.fragmentID ?? "null"}");
        SwitchView("mind_log_secondary");
    }

    /// <summary>
    /// Called by MemoryExpandedUI when the Back button is clicked.
    /// Switches back to the Mind Log Primary view.
    /// </summary>
    private void OnExpandedMemoryClosed(MemoryFragment fragment)
    {
        Debug.Log($"[CodexViewController] Expanded memory closed for: {fragment?.fragmentID ?? "null"}");
        SwitchView("mind_log_primary");
    }

    /// <summary>
    /// Diagnostic coroutine to log container state changes after activation.
    /// </summary>
    private IEnumerator LogContainerState(string containerType)
    {
        GameObject container = containerType == "Primary" ? mindLogPrimaryContainer : mindLogSecondaryContainer;
        
        for (int i = 0; i < 10; i++)
        {
            yield return new WaitForEndOfFrame();
            
            if (container == null)
            {
                Debug.LogWarning($"[CodexViewController] Container became null during frame {i}");
                yield break;
            }
            
            bool activeInHierarchy = container.activeInHierarchy;
            bool activeSelf = container.activeSelf;
            bool parentActive = container.transform.parent != null && container.transform.parent.gameObject.activeInHierarchy;
            
            Debug.Log($"[CodexViewController] Frame {i}: {containerType} - activeSelf={activeSelf}, activeInHierarchy={activeInHierarchy}, parentActive={parentActive}");
            
            if (!activeInHierarchy && activeSelf)
            {
                Debug.LogError($"[CodexViewController] ALERT: {containerType} is activeSelf=true but activeInHierarchy=false! Parent must be inactive!");
                
                // Walk up the hierarchy and log all parent states
                Transform current = container.transform.parent;
                int depth = 0;
                while (current != null && depth < 10)
                {
                    Debug.LogError($"[CodexViewController] Parent at depth {depth}: {current.name}, activeSelf={current.gameObject.activeSelf}, activeInHierarchy={current.gameObject.activeInHierarchy}");
                    current = current.parent;
                    depth++;
                }
            }
        }
    }
}
