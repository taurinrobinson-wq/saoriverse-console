using UnityEngine;
using UnityEngine.UI;

public class DiagnosticCanvas : MonoBehaviour
{
    void Start()
    {
        // Find main canvas
        Canvas mainCanvas = Object.FindAnyObjectByType<Canvas>();
        
        if (mainCanvas == null)
        {
            Debug.LogError("[DIAGNOSTIC] NO CANVAS FOUND IN SCENE!");
            return;
        }

        Debug.Log($"[DIAGNOSTIC] Canvas found: {mainCanvas.gameObject.name}");
        Debug.Log($"[DIAGNOSTIC] Canvas enabled: {mainCanvas.enabled}");
        Debug.Log($"[DIAGNOSTIC] Canvas GameObject active: {mainCanvas.gameObject.activeSelf}");
        Debug.Log($"[DIAGNOSTIC] Canvas parent active: {mainCanvas.gameObject.transform.parent?.gameObject.activeSelf ?? true}");
        Debug.Log($"[DIAGNOSTIC] Canvas Render Mode: {mainCanvas.renderMode}");
        Debug.Log($"[DIAGNOSTIC] Canvas Sorting Order: {mainCanvas.sortingOrder}");
        Debug.Log($"[DIAGNOSTIC] Canvas Rect: {mainCanvas.GetComponent<RectTransform>().rect}");
        
        GraphicRaycaster gr = mainCanvas.GetComponent<GraphicRaycaster>();
        Debug.Log($"[DIAGNOSTIC] GraphicRaycaster exists: {(gr != null ? "YES" : "NO")}");

        // Check all child panels
        foreach (Transform child in mainCanvas.transform)
        {
            CanvasGroup cg = child.GetComponent<CanvasGroup>();
            Image img = child.GetComponent<Image>();
            RectTransform rt = child.GetComponent<RectTransform>();
            
            Debug.Log($"\n[DIAGNOSTIC] Panel: {child.name}");
            Debug.Log($"  - Active: {child.gameObject.activeSelf}");
            Debug.Log($"  - CanvasGroup exists: {(cg != null ? "YES" : "NO")}");
            if (cg != null)
            {
                Debug.Log($"    - Alpha: {cg.alpha}");
                Debug.Log($"    - Interactable: {cg.interactable}");
                Debug.Log($"    - BlocksRaycasts: {cg.blocksRaycasts}");
            }
            Debug.Log($"  - Image exists: {(img != null ? "YES" : "NO")}");
            if (img != null)
            {
                Debug.Log($"    - Color: {img.color}");
                Debug.Log($"    - Enabled: {img.enabled}");
            }
            Debug.Log($"  - RectTransform size: {rt.sizeDelta}");
            Debug.Log($"  - RectTransform pos: {rt.anchoredPosition}");
        }
    }
}
