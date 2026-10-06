using UnityEngine;
using UnityEngine.UI;
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

    private void OnEnable()
    {
        // Hook button clicks
        if (glyphsButton != null)
            glyphsButton.onClick.AddListener(() => SwitchView("glyphs"));
        
        if (impressionsButton != null)
            impressionsButton.onClick.AddListener(() => SwitchView("mind_log_primary"));

        if (mindLogBackButton != null)
            mindLogBackButton.onClick.AddListener(() => SwitchView("mind_log_primary"));
    }

    private void OnDisable()
    {
        // Unhook to prevent duplicate listeners
        if (glyphsButton != null)
            glyphsButton.onClick.RemoveListener(() => SwitchView("glyphs"));
        
        if (impressionsButton != null)
            impressionsButton.onClick.RemoveListener(() => SwitchView("mind_log_primary"));

        if (mindLogBackButton != null)
            mindLogBackButton.onClick.RemoveListener(() => SwitchView("mind_log_primary"));
    }

    private void Start()
    {
        // Initialize to glyphs view on startup
        SwitchView("glyphs");
    }

    /// <summary>
    /// Switch between glyphs, mind_log_primary, and mind_log_secondary views.
    /// </summary>
    public void SwitchView(string viewName)
    {
        if (currentView == viewName) return; // Already on this view

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

        // Disable glyphs background and enable Mind Log Primary Container
        if (glyphsBackground != null) glyphsBackground.SetActive(false);
        if (mindLogBackground != null) mindLogBackground.SetActive(false);

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
        if (mindLogPrimaryContainer != null)
        {
            mindLogPrimaryContainer.SetActive(true);
            CanvasGroup cgPrimary = mindLogPrimaryContainer.GetComponent<CanvasGroup>();
            if (cgPrimary != null)
            {
                cgPrimary.interactable = true;
                cgPrimary.blocksRaycasts = true;
                cgPrimary.alpha = 1f;
            }
        }

        // Disable Mind Log Secondary view
        DisableMindLogSecondary();

        // Disable legacy impressions elements if they exist
        if (impressionsTextDisplay != null) impressionsTextDisplay.SetActive(false);
        if (impressionsPrevButton != null) impressionsPrevButton.SetActive(false);
        if (impressionsNextButton != null) impressionsNextButton.SetActive(false);

        Debug.Log("[CodexViewController] Mind Log Primary view enabled");
    }

    /// <summary>
    /// Show the Mind Log Secondary view (expanded memory with full text and back button).
    /// </summary>
    private void ShowMindLogSecondaryView()
    {
        // Enable mind log background (different from glyphs/primary)
        if (glyphsBackground != null) glyphsBackground.SetActive(false);
        if (mindLogBackground != null) mindLogBackground.SetActive(true);

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
            mindLogPrimaryContainer.SetActive(false);
            CanvasGroup cgPrimary = mindLogPrimaryContainer.GetComponent<CanvasGroup>();
            if (cgPrimary != null)
            {
                cgPrimary.interactable = false;
                cgPrimary.blocksRaycasts = false;
            }
        }
    }

    private void DisableMindLogSecondary()
    {
        if (mindLogSecondaryContainer != null)
        {
            mindLogSecondaryContainer.SetActive(false);
            CanvasGroup cgSecondary = mindLogSecondaryContainer.GetComponent<CanvasGroup>();
            if (cgSecondary != null)
            {
                cgSecondary.interactable = false;
                cgSecondary.blocksRaycasts = false;
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
}
