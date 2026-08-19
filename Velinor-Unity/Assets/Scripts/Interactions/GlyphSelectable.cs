using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;

/// <summary>
/// Makes a glyph selectable by clicking on it.
/// Attached to each glyph icon in the codex/triglyph panel.
/// Shows selection feedback with green glow and displays glyph name.
/// </summary>
public class GlyphSelectable : MonoBehaviour, IPointerClickHandler
{
    [SerializeField] private string glyphName; // e.g., "Glyph of Sorrow"
    [SerializeField] private CanvasGroup canvasGroup; // for visual feedback
    [SerializeField] private TextMeshProUGUI glyphNameDisplay; // text showing selected glyph name

    private bool isSelected = false;
    private GlyphPlacementManager placementManager;
    private Outline outline;
    private Color originalColor;

    private void Start()
    {
        // Find the placement manager in the scene
        placementManager = FindAnyObjectByType<GlyphPlacementManager>();

        if (canvasGroup == null)
            canvasGroup = GetComponent<CanvasGroup>();

        // Add outline for glow effect
        outline = GetComponent<Outline>();
        if (outline == null)
            outline = gameObject.AddComponent<Outline>();

        outline.enabled = false; // Start disabled

        // Store original color
        Image img = GetComponent<Image>();
        if (img != null)
            originalColor = img.color;
    }

    public void OnPointerClick(PointerEventData eventData)
    {
        SelectGlyph();
    }

    private void SelectGlyph()
    {
        isSelected = true;

        // Show green glow outline
        if (outline != null)
        {
            outline.enabled = true;
            outline.effectColor = new Color(0, 1, 0, 1); // Green
            outline.effectDistance = new Vector2(0.3f, 0.3f);
        }

        // Visual feedback: brighten image
        if (canvasGroup != null)
            canvasGroup.alpha = 1f;

        // Display glyph name
        if (glyphNameDisplay != null)
            glyphNameDisplay.text = glyphName;

        // Notify the placement manager
        if (placementManager != null)
            placementManager.SelectGlyph(glyphName, this);
    }

    public void Deselect()
    {
        isSelected = false;

        // Remove green glow
        if (outline != null)
            outline.enabled = false;

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
