using UnityEngine;
using UnityEngine.UI;
using Velinor.Core;

/// <summary>
/// Handles pagination between Glyph Grid pages.
/// Simply toggles GlyphGrid_Pg1 and GlyphGrid_Pg2 visibility.
/// </summary>
public class GlyphGridPagination : MonoBehaviour
{
    [SerializeField] private GameObject glyphGridPage1;
    [SerializeField] private GameObject glyphGridPage2;

    private bool isOnPage1 = true;

    private void Start()
    {
        // Ensure we start on Page 1
        if (glyphGridPage1 != null) glyphGridPage1.SetActive(true);
        if (glyphGridPage2 != null) glyphGridPage2.SetActive(false);
        isOnPage1 = true;
    }

    /// <summary>
    /// Called by Btn_Next - goes to next page
    /// </summary>
    public void NextPage()
    {
        if (isOnPage1)
        {
            // Switch to Page 2
            glyphGridPage1.SetActive(false);
            glyphGridPage2.SetActive(true);
            isOnPage1 = false;
            Debug.Log("[Glyph Pagination] Switched to Page 2");
        }
        else
        {
            // Loop back to Page 1
            glyphGridPage2.SetActive(false);
            glyphGridPage1.SetActive(true);
            isOnPage1 = true;
            Debug.Log("[Glyph Pagination] Switched to Page 1");
        }
    }

    /// <summary>
    /// Called by Btn_Prev - goes to previous page
    /// </summary>
    public void PreviousPage()
    {
        if (isOnPage1)
        {
            // Loop to Page 2
            glyphGridPage1.SetActive(false);
            glyphGridPage2.SetActive(true);
            isOnPage1 = false;
            Debug.Log("[Glyph Pagination] Switched to Page 2");
        }
        else
        {
            // Switch to Page 1
            glyphGridPage2.SetActive(false);
            glyphGridPage1.SetActive(true);
            isOnPage1 = true;
            Debug.Log("[Glyph Pagination] Switched to Page 1");
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
