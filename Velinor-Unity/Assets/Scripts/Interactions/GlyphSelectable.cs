using UnityEngine;
using UnityEngine.EventSystems;

/// <summary>
/// Makes a glyph selectable by clicking on it.
/// Attached to each glyph icon in the triglyph close-up panel UI.
/// </summary>
public class GlyphSelectable : MonoBehaviour, IPointerClickHandler
{
    [SerializeField] private string glyphName; // e.g., "Glyph of Sorrow"
    [SerializeField] private CanvasGroup canvasGroup; // for visual feedback

    private bool isSelected = false;
    private GlyphPlacementManager placementManager;

    private void Start()
    {
        // Find the placement manager in the scene
        placementManager = FindAnyObjectByType<GlyphPlacementManager>();

        if (canvasGroup == null)
            canvasGroup = GetComponent<CanvasGroup>();
    }

    public void OnPointerClick(PointerEventData eventData)
    {
        SelectGlyph();
    }

    private void SelectGlyph()
    {
        isSelected = true;

        // Visual feedback: increase alpha or highlight
        if (canvasGroup != null)
            canvasGroup.alpha = 1f;

        // Notify the placement manager
        if (placementManager != null)
            placementManager.SelectGlyph(glyphName, this);
    }

    public void Deselect()
    {
        isSelected = false;
        if (canvasGroup != null)
            canvasGroup.alpha = 0.6f;
    }

    public void SetGlyphName(string name)
    {
        glyphName = name;
    }

    public bool IsSelected => isSelected;
    public string GlyphName => glyphName;
}
