using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;
using System.Collections;
using System.Collections.Generic;
using Velinor.UI.Codex;
using Velinor.Core;
using Velinor.Testing;
using Velinor.Management;

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

    // Track last clicked memory slot for double-click detection
    public MemorySlot LastClickedSlot = null;

    private void Awake()
    {
        // Store strong references to containers immediately
        if (mindLogPrimaryContainer == null)
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
        if (mindLogSecondaryContainer == null)
            mindLogSecondaryContainer = GameObject.Find("MindLogSecondaryContainer");
        if (glyphsBackground == null)
            glyphsBackground = GameObject.Find("GlyphsBackground");

        // Containers are children of CodexPanel which is already marked as DontDestroyOnLoad by UI_Canvas parent
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
        // Initialize CanvasGroups on all containers and set them to invisible by default
        InitializeContainerVisibility();
        
        // CRITICAL: Lock the Codex by default - it should only be accessible after Saori gives it
        MindLogPersistence.LockCodex();
        Debug.Log("[CodexViewController] Codex LOCKED at start - player must obtain it from Saori");

        // If Codex is locked, don't show any views at all - entire UI should be hidden
        if (!MindLogPersistence.IsCodexUnlocked())
        {
            Debug.Log("[CodexViewController] Codex locked - skipping view initialization");
            return;
        }

        // Initialize to glyphs view on startup
        ShowGlyphsView();
    }

    /// <summary>
    /// Initialize CanvasGroups on all containers and set them to invisible by default.
    /// This ensures all containers can be toggled via CanvasGroup without SetActive issues.
    /// </summary>
    private void InitializeContainerVisibility()
    {
        // Ensure all containers have CanvasGroups and start invisible
        EnsureCanvasGroup(glyphsBackground, false);
        EnsureCanvasGroup(mindLogPrimaryContainer, false);
        EnsureCanvasGroup(mindLogSecondaryContainer, false);
        
        Debug.Log("[CodexViewController] All containers initialized with CanvasGroups, set to invisible");
    }

    /// <summary>
    /// Ensure a container has a CanvasGroup and set its initial visibility state.
    /// </summary>
    private void EnsureCanvasGroup(GameObject container, bool visible)
    {
        if (container == null) return;

        CanvasGroup cg = container.GetComponent<CanvasGroup>();
        if (cg == null)
        {
            cg = container.AddComponent<CanvasGroup>();
            Debug.Log($"[CodexViewController] Added CanvasGroup to {container.name}");
        }

        cg.alpha = visible ? 1f : 0f;
        cg.interactable = visible;
        cg.blocksRaycasts = visible;
        
        Debug.Log($"[CodexViewController] {container.name} initialized: alpha={cg.alpha}, interactable={cg.interactable}, blocksRaycasts={cg.blocksRaycasts}");
    }

    /// <summary>
    /// Switch between glyphs, mind_log_primary, and mind_log_secondary views.
    /// Blocks Mind Log access if Codex is locked (not yet obtained from Saori).
    /// </summary>
    public void SwitchView(string viewName)
    {
        Debug.Log($"[CodexViewController] *** SWITCHVIEW CALLED: {viewName} ***");
        
        // Check if trying to access Mind Log views while Codex is locked
        if ((viewName == "mind_log_primary" || viewName == "mind_log_secondary") && !MindLogPersistence.IsCodexUnlocked())
        {
            Debug.LogWarning($"[CodexViewController] BLOCKED: Cannot access Mind Log - Codex is LOCKED! Must obtain it from Saori first.");
            return;
        }

        currentView = viewName;
        Debug.Log($"[CodexViewController] *** SWITCHING TO VIEW: {viewName} ***");

        switch (viewName)
        {
            case "glyphs":
                Debug.Log("[CodexViewController] Calling ShowGlyphsView()");
                ShowGlyphsView();
                break;
            case "mind_log_primary":
                Debug.Log("[CodexViewController] Calling ShowMindLogPrimaryView()");
                ShowMindLogPrimaryView();
                break;
            case "mind_log_secondary":
                Debug.Log("[CodexViewController] Calling ShowMindLogSecondaryView()");
                ShowMindLogSecondaryView();
                break;
            default:
                Debug.LogWarning($"[CodexViewController] Unknown view: {viewName}");
                break;
        }
    }

    /// <summary>
    /// Show the Glyphs grid view with pagination controls.
    /// Sets GlyphsBackground.alpha = 1, all others to 0.
    /// </summary>
    private void ShowGlyphsView()
    {
        SetAllContainerAlpha(glyphsBackground, 1f);
        SetAllContainerAlpha(mindLogPrimaryContainer, 0f);
        SetAllContainerAlpha(mindLogSecondaryContainer, 0f);

        // CRITICAL: Ensure container is active in hierarchy
        if (glyphsBackground != null && !glyphsBackground.activeSelf)
        {
            glyphsBackground.SetActive(true);
            Debug.Log("[CodexViewController] Activated glyphsBackground");
        }

        Debug.Log("[CodexViewController] Glyphs view enabled (alpha=1)");
    }

    /// <summary>
    /// Show the Mind Log Primary view (3x3 grid of memory fragments).
    /// Sets MindLogPrimaryContainer.alpha = 1, all others to 0.
    /// </summary>
    private void ShowMindLogPrimaryView()
    {
        Debug.Log("[CodexViewController] ShowMindLogPrimaryView() called");
        
        SetAllContainerAlpha(glyphsBackground, 0f);
        SetAllContainerAlpha(mindLogPrimaryContainer, 1f);
        SetAllContainerAlpha(mindLogSecondaryContainer, 0f);

        // CRITICAL: Ensure containers are active in hierarchy
        // CanvasGroup alpha doesn't help if the GameObject itself is inactive
        if (glyphsBackground != null && !glyphsBackground.activeSelf)
        {
            glyphsBackground.SetActive(true);
            Debug.Log("[CodexViewController] Activated glyphsBackground");
        }
        
        if (mindLogPrimaryContainer != null && !mindLogPrimaryContainer.activeSelf)
        {
            mindLogPrimaryContainer.SetActive(true);
            Debug.Log("[CodexViewController] Activated mindLogPrimaryContainer");
        }
        
        if (mindLogSecondaryContainer != null && !mindLogSecondaryContainer.activeSelf)
        {
            mindLogSecondaryContainer.SetActive(true);
            Debug.Log("[CodexViewController] Activated mindLogSecondaryContainer");
        }
        
        // Initialize test memories on first load if enabled
        if (useTestMemories && !testMemoriesInitialized && testSetup != null)
        {
            testSetup.InitializeTestMemories();
            testMemoriesInitialized = true;
            Debug.Log("[CodexViewController] Test memories initialized");
        }
        else if (useTestMemories && !testMemoriesInitialized && testSetup == null)
        {
            EnsureTestMemoriesExist();
            testMemoriesInitialized = true;
        }
        
        // Populate grid
        StartCoroutine(PopulateGridWithDelay(mindLogPrimaryContainer));
        Debug.Log("[CodexViewController] Mind Log Primary view fully enabled (alpha=1)");
    }

    private System.Collections.IEnumerator PopulateGridWithDelay(GameObject container)
    {
        // Wait one frame to allow all UI components to initialize
        yield return null;

        MemoryGridController gridController = container.GetComponentInChildren<MemoryGridController>();
        if (gridController != null)
        {
            gridController.PopulateFromManager();
            // Force canvas to refresh visuals immediately
            Canvas.ForceUpdateCanvases();
            Debug.Log("[CodexViewController] Grid populated and canvas refreshed");
        }
        else
        {
            Debug.LogWarning("[CodexViewController] MemoryGridController not found in container!");
        }

        // Ensure secondary view is hidden
        DisableMindLogSecondary();

        // Disable legacy impressions elements if they exist
        if (impressionsTextDisplay != null) impressionsTextDisplay.SetActive(false);
        if (impressionsPrevButton != null) impressionsPrevButton.SetActive(false);
        if (impressionsNextButton != null) impressionsNextButton.SetActive(false);

        Debug.Log("[CodexViewController] Mind Log Primary view enabled");
    }

    /// <summary>
    /// Show the Mind Log Secondary view (expanded memory).
    /// Sets MindLogSecondaryContainer.alpha = 1, primary and glyphs to 0.
    /// </summary>
    private void ShowMindLogSecondaryView()
    {
        Debug.Log("[CodexViewController] ShowMindLogSecondaryView() called");
        
        // Hide glyphs and primary, show secondary
        SetAllContainerAlpha(glyphsBackground, 0f);
        SetAllContainerAlpha(mindLogPrimaryContainer, 0f);
        SetAllContainerAlpha(mindLogSecondaryContainer, 1f);

        // CRITICAL: Ensure containers are active in hierarchy
        // CanvasGroup alpha doesn't help if the GameObject itself is inactive
        if (glyphsBackground != null && !glyphsBackground.activeSelf)
        {
            glyphsBackground.SetActive(true);
            Debug.Log("[CodexViewController] Activated glyphsBackground");
        }
        
        if (mindLogPrimaryContainer != null && !mindLogPrimaryContainer.activeSelf)
        {
            mindLogPrimaryContainer.SetActive(true);
            Debug.Log("[CodexViewController] Activated mindLogPrimaryContainer");
        }
        
        if (mindLogSecondaryContainer != null && !mindLogSecondaryContainer.activeSelf)
        {
            mindLogSecondaryContainer.SetActive(true);
            Debug.Log("[CodexViewController] Activated mindLogSecondaryContainer");
        }
        
        Debug.Log("[CodexViewController] Mind Log Secondary view fully enabled (alpha=1)");
    }

    private void DisableMindLogPrimary()
    {
        SetAllContainerAlpha(mindLogPrimaryContainer, 0f);
        Debug.Log("[CodexViewController] MindLogPrimaryContainer hidden (alpha=0)");
    }

    private void DisableMindLogSecondary()
    {
        SetAllContainerAlpha(mindLogSecondaryContainer, 0f);
        Debug.Log("[CodexViewController] MindLogSecondaryContainer hidden (alpha=0)");
    }

    /// <summary>
    /// Set alpha on a container and ALL its children CanvasGroups.
    /// Also sets interactable and blocksRaycasts based on alpha == 1.
    /// Enforces the rule: only one container may have alpha = 1 at a time.
    /// </summary>
    private void SetAllContainerAlpha(GameObject container, float alpha)
    {
        if (container == null) return;

        // Clamp alpha to 0 or 1
        alpha = (alpha >= 0.5f) ? 1f : 0f;

        // Set parent CanvasGroup
        CanvasGroup cg = container.GetComponent<CanvasGroup>();
        if (cg == null)
        {
            cg = container.AddComponent<CanvasGroup>();
        }
        cg.alpha = alpha;
        cg.interactable = (alpha == 1f);
        cg.blocksRaycasts = (alpha == 1f);

        // Set all child CanvasGroups - they follow parent's visibility rules
        CanvasGroup[] childCanvasGroups = container.GetComponentsInChildren<CanvasGroup>();
        foreach (CanvasGroup childCG in childCanvasGroups)
        {
            if (childCG == cg) continue; // Skip parent (already set)
            childCG.interactable = (alpha == 1f);
            childCG.blocksRaycasts = (alpha == 1f);
        }

        Debug.Log($"[CodexViewController] {container.name} set to alpha={alpha} (interactable={cg.interactable}, blocksRaycasts={cg.blocksRaycasts})");
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

    /// <summary>
    /// Create test memories programmatically if MindLogManager is empty.
    /// This ensures the grid always has something to display for testing click functionality.
    /// </summary>
    private void EnsureTestMemoriesExist()
    {
        MindLogManager manager = MindLogManager.GetOrCreate();
        if (manager == null)
        {
            Debug.LogError("[CodexViewController] Failed to get MindLogManager!");
            return;
        }

        // If manager already has logs, don't add more
        if (manager.GetLogCount() > 0)
        {
            Debug.Log($"[CodexViewController] MindLogManager already has {manager.GetLogCount()} logs - skipping test data creation");
            return;
        }

        Debug.Log("[CodexViewController] MindLogManager is empty - creating test memories for UI testing");

        // Create test memories
        var saoriMemory = new MindLogEntry(
            logID: "memory_saori_desert_encounter",
            icon: CreateTestIcon(0),
            summaryText: "Mysterious Encounter",
            fullText: "I met an older woman on the way through the desert. She handed me a strange device without much explanation. There was something knowing in her eyes—as if she recognized me, or perhaps knew something about me that I didn't know myself. The device she gave me feels important, though I can't explain why."
        );
        saoriMemory.AddCombineTag("saori");
        saoriMemory.AddCombineTag("encounter");
        manager.AddLog(saoriMemory);
        Debug.Log("[CodexViewController] Created test memory: memory_saori_desert_encounter");

        // Create a second test memory for variety
        var testMemory2 = new MindLogEntry(
            logID: "memory_test_encounter_2",
            icon: CreateTestIcon(1),
            summaryText: "Another Discovery",
            fullText: "Through my exploration, I've learned more about the world and my place in it. Each encounter brings new insights and questions."
        );
        testMemory2.AddCombineTag("discovery");
        manager.AddLog(testMemory2);
        Debug.Log("[CodexViewController] Created test memory: memory_test_encounter_2");

        // Create a third test memory
        var testMemory3 = new MindLogEntry(
            logID: "memory_test_encounter_3",
            icon: CreateTestIcon(2),
            summaryText: "Glimpse of Truth",
            fullText: "Among the echoes of the past, I found a path forward. The truth, when finally glimpsed, was both simpler and more complex than I expected."
        );
        testMemory3.AddCombineTag("revelation");
        manager.AddLog(testMemory3);
        Debug.Log("[CodexViewController] Created test memory: memory_test_encounter_3");

        Debug.Log("[CodexViewController] Test memories created successfully!");
    }

    /// <summary>
    /// Create a simple placeholder test icon texture.
    /// In production, you'd use real sprite assets.
    /// </summary>
    private Sprite CreateTestIcon(int colorVariant)
    {
        Texture2D texture = new Texture2D(64, 64, TextureFormat.RGBA32, false);
        
        // Use different colors for each test icon
        Color[] colors = new Color[]
        {
            new Color(0.3f, 0.7f, 1f, 1f),   // Blue
            new Color(1f, 0.7f, 0.3f, 1f),   // Orange
            new Color(0.7f, 0.3f, 1f, 1f)    // Purple
        };
        
        Color testColor = colors[colorVariant % colors.Length];
        Color[] pixels = new Color[64 * 64];
        
        for (int i = 0; i < pixels.Length; i++)
        {
            pixels[i] = testColor;
        }
        
        texture.SetPixels(pixels);
        texture.Apply();
        
        Sprite sprite = Sprite.Create(texture, new Rect(0, 0, 64, 64), new Vector2(0.5f, 0.5f), 100);
        sprite.name = $"TestIcon_{colorVariant}";
        
        return sprite;
    }
}
