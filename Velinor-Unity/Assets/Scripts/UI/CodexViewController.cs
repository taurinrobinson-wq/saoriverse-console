using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Manages toggling between Glyphs and Impressions views on the Codex device.
/// 
/// Handles enabling/disabling UI elements when switching between:
/// - Glyphs view: Grid layout with glyph pagination
/// - Impressions view: Text entries with navigation
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

    [Header("Impressions View Elements")]
    [SerializeField] private GameObject impressionsTextDisplay;
    [SerializeField] private GameObject impressionsPrevButton;
    [SerializeField] private GameObject impressionsNextButton;

    private string currentView = "glyphs"; // Default to glyphs on startup

    private void OnEnable()
    {
        // Hook button clicks
        if (glyphsButton != null)
            glyphsButton.onClick.AddListener(() => SwitchView("glyphs"));
        
        if (impressionsButton != null)
            impressionsButton.onClick.AddListener(() => SwitchView("impressions"));
    }

    private void OnDisable()
    {
        // Unhook to prevent duplicate listeners
        if (glyphsButton != null)
            glyphsButton.onClick.RemoveListener(() => SwitchView("glyphs"));
        
        if (impressionsButton != null)
            impressionsButton.onClick.RemoveListener(() => SwitchView("impressions"));
    }

    private void Start()
    {
        // Initialize to glyphs view on startup
        SwitchView("glyphs");
    }

    /// <summary>
    /// Switch between glyphs and impressions views.
    /// </summary>
    public void SwitchView(string viewName)
    {
        if (currentView == viewName) return; // Already on this view

        currentView = viewName;
        Debug.Log($"[CodexViewController] Switching to view: {viewName}");

        if (viewName == "glyphs")
        {
            ShowGlyphsView();
        }
        else if (viewName == "impressions")
        {
            ShowImpressionsView();
        }
    }

    /// <summary>
    /// Show the Glyphs grid view with pagination controls.
    /// </summary>
    private void ShowGlyphsView()
    {
        // Enable backgrounds
        if (glyphsBackground != null) glyphsBackground.SetActive(true);
        if (mindLogBackground != null) mindLogBackground.SetActive(false);

        // Enable glyphs view elements
        if (glyphGrid_Pg1 != null) glyphGrid_Pg1.SetActive(true);
        if (glyphGrid_Pg2 != null) glyphGrid_Pg2.SetActive(true);
        if (glyphsNavigation != null) glyphsNavigation.SetActive(true);

        // Disable impressions view elements
        if (impressionsTextDisplay != null) impressionsTextDisplay.SetActive(false);
        if (impressionsPrevButton != null) impressionsPrevButton.SetActive(false);
        if (impressionsNextButton != null) impressionsNextButton.SetActive(false);

        Debug.Log("[CodexViewController] Glyphs view enabled");
    }

    /// <summary>
    /// Show the Impressions text view with page navigation.
    /// </summary>
    private void ShowImpressionsView()
    {
        // Enable backgrounds
        if (glyphsBackground != null) glyphsBackground.SetActive(false);
        if (mindLogBackground != null) mindLogBackground.SetActive(true);

        // Disable glyphs view elements
        if (glyphGrid_Pg1 != null) glyphGrid_Pg1.SetActive(false);
        if (glyphGrid_Pg2 != null) glyphGrid_Pg2.SetActive(false);
        if (glyphsNavigation != null) glyphsNavigation.SetActive(false);

        // Enable impressions view elements
        if (impressionsTextDisplay != null) impressionsTextDisplay.SetActive(true);
        if (impressionsPrevButton != null) impressionsPrevButton.SetActive(true);
        if (impressionsNextButton != null) impressionsNextButton.SetActive(true);

        // Update Mind Log entries if component exists
        if (mindLogBackground != null)
        {
            var diaryCtrl = mindLogBackground.GetComponent<DiaryController>();
            if (diaryCtrl != null)
            {
                diaryCtrl.SetEntriesFromManager();
            }
        }

        Debug.Log("[CodexViewController] Impressions view enabled");
    }

    /// <summary>
    /// Get the currently active view.
    /// </summary>
    public string GetCurrentView() => currentView;
}
