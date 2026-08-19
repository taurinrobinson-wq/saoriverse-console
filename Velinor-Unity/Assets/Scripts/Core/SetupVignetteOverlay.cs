using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Setup helper for creating a vignette overlay in OverlayCanvas
/// Run once in Editor, then delete this script
/// </summary>
public class SetupVignetteOverlay : MonoBehaviour
{
    [ContextMenu("Setup Vignette")]
    public void SetupVignette()
    {
        // Find OverlayCanvas
        Canvas[] allCanvases = FindObjectsByType<Canvas>(FindObjectsSortMode.None);
        Canvas overlayCanvas = null;

        foreach (Canvas canvas in allCanvases)
        {
            if (canvas.gameObject.name == "OverlayCanvas")
            {
                overlayCanvas = canvas;
                break;
            }
        }

        if (overlayCanvas == null)
        {
            Debug.LogError("OverlayCanvas not found in scene!");
            return;
        }

        // Create VignetteOverlay Image
        GameObject vignetteGO = new GameObject("VignetteOverlay");
        vignetteGO.transform.SetParent(overlayCanvas.transform, false);

        Image image = vignetteGO.AddComponent<Image>();
        image.color = Color.white;

        // Make it fill the entire canvas
        RectTransform rectTransform = vignetteGO.GetComponent<RectTransform>();
        rectTransform.anchorMin = Vector2.zero;
        rectTransform.anchorMax = Vector2.one;
        rectTransform.offsetMin = Vector2.zero;
        rectTransform.offsetMax = Vector2.zero;

        // Add VignetteGenerator
        VignetteGenerator vignetteGenerator = vignetteGO.AddComponent<VignetteGenerator>();

        // Optional: adjust settings for your scene
        vignetteGenerator.intensity = 0.75f;
        vignetteGenerator.vignetteColor = new Color(0.09f, 0.09f, 0.09f, 0.85f);

        Debug.Log("Vignette overlay setup complete! You can now delete this SetupVignetteOverlay script.");
    }
}
