using UnityEngine;
using UnityEngine.UI;
using Velinor.Core;

/// <summary>
/// Handles pagination between Glyph Grid pages.
/// Simply toggles GlyphGrid_Pg1 and GlyphGrid_Pg2 visibility.
/// Prevents navigation beyond first/last pages.
/// </summary>
public class GlyphGridPagination : MonoBehaviour
{
    [SerializeField] private GameObject glyphGridPage1;
    [SerializeField] private GameObject glyphGridPage2;
    [SerializeField] private Button btnNext;
    [SerializeField] private Button btnPrev;

    private bool isOnPage1 = true;

    private void Start()
    {
        // Ensure we start on Page 1
        if (glyphGridPage1 != null) glyphGridPage1.SetActive(true);
        if (glyphGridPage2 != null) glyphGridPage2.SetActive(false);
        isOnPage1 = true;

        // Update button states
        UpdateButtonStates();
    }

    /// <summary>
    /// Called by Btn_Next - goes to next page (only if not on last page)
    /// </summary>
    public void NextPage()
    {
        if (!isOnPage1 || glyphGridPage2 == null)
        {
            Debug.LogWarning("[Glyph Pagination] Cannot go to next page - already on last page or Page 2 not found");
            return;
        }

        // Switch to Page 2
        glyphGridPage1.SetActive(false);
        glyphGridPage2.SetActive(true);
        isOnPage1 = false;
        Debug.Log("[Glyph Pagination] Switched to Page 2");

        UpdateButtonStates();
    }

    /// <summary>
    /// Called by Btn_Prev - goes to previous page (only if not on first page)
    /// </summary>
    public void PreviousPage()
    {
        if (isOnPage1 || glyphGridPage1 == null)
        {
            Debug.LogWarning("[Glyph Pagination] Cannot go to previous page - already on first page or Page 1 not found");
            return;
        }

        // Switch to Page 1
        glyphGridPage2.SetActive(false);
        glyphGridPage1.SetActive(true);
        isOnPage1 = true;
        Debug.Log("[Glyph Pagination] Switched to Page 1");

        UpdateButtonStates();
    }

    /// <summary>
    /// Update button interactability based on current page
    /// </summary>
    private void UpdateButtonStates()
    {
        if (btnNext != null)
        {
            // Disable Next button if on last page
            btnNext.interactable = isOnPage1;
        }

        if (btnPrev != null)
        {
            // Disable Prev button if on first page
            btnPrev.interactable = !isOnPage1;
        }
    }

    /// <summary>
    /// Get current page (1 or 2)
    /// </summary>
    public int GetCurrentPage()
    {
        return isOnPage1 ? 1 : 2;
    }
}
